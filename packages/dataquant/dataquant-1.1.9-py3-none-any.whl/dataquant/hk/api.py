# -*- coding: UTF-8 -*-

import re
import os
import time
import mmap
import gevent
import platform
import warnings
import pandas as pd
import numpy as np
from functools import wraps
import traceback
import socket
from concurrent.futures import as_completed, ThreadPoolExecutor

from dataquant.apis.base import get_data, get_qdata
from dataquant.utils.convert import convert_fields, sort_merge_df, sort_merge_df_dic
from dataquant.utils.datetime_func import get_current_date
from dataquant.utils.config import read_config
from dataquant.utils.error import MaxTryExceed, RunTimeError

__all__ = [
    # 新增港股新表查询接口；20240606 shenfc
    "get_tick",#快照
    "get_deal",#逐笔成交
    "get_oddlot_order",#碎股
    "get_broker_queue",#经纪商队列
    "get_index_tick",#指数快照
    "get_security_info", #获取港股基本信息
    "get_stk_rstr_fctr", #获取港股复权因子信息
    "get_kline" #获取港股k线行情
]


# 请求服务端URL

#新增港股请求服务端URL
URL_GET_HKSTK_TICK = 'get_hkstock_snapshot'#快照
URL_GET_HKSTK_DEAL = 'get_hkstock_tick'#逐笔成交
URL_GET_HKSTK_ODD = 'get_hkstock_odd'#碎股
URL_GET_HKSTK_BROKER = 'get_hkstock_broker'#经纪商队列
URL_GET_HKSTK_INDEX = 'get_hkstock_index'#指数快照
URL_GET_HKSTK_KLINE = 'get_hkstock_kline'#k线行情



# 代码与证券类型映射
CODE_SECURITY_MAP = {}


global CONFIG_PAGE_SIZE, PARALLEL_NUM, PARALLEL_MODE, EXECUTOR, EXECUTOR_INNER, \
    HF_SORT_COLS, KLINED_SORT_COLS, KLINEM_SORT_COLS, PROCESS_MMAP

if platform.system().lower() == 'windows':
    PROCESS_MMAP = mmap.mmap(-1, 1, tagname='dataquant_sdk_pid')
else:
    MMAP_FILE = open('/dev/shm/dataquant_sdk_pid', 'w+b')
    MMAP_FILE.write(b"\x00")
    MMAP_FILE.flush()
    PROCESS_MMAP = mmap.mmap(MMAP_FILE.fileno(), 1, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ | mmap.PROT_WRITE)

PROCESS_MMAP.seek(0)
if PROCESS_MMAP.read() != b'\x31':
    PROCESS_MMAP.seek(0)
    PROCESS_MMAP.write(b"\x00")
    PROCESS_MMAP.flush()


def reset():
    PROCESS_MMAP.seek(0)
    PROCESS_MMAP.write(b"\x00")
    PROCESS_MMAP.flush()


def load_basic_info():
    int_param = []
    float_param = []

    params = {
        "mkt_code_list": ['XHKG'],
        "cols": ['scr_num', 'scr_name', 'scr_abbr', 'scr_code', 'mkt_code', 'scr_clas', 'list_date'],
        "int_param": int_param,
        "float_param": float_param
    }
    result = get_data("get_scr_basc_info", **params)
    global CODE_SECURITY_MAP
    CODE_SECURITY_MAP = result.set_index('scr_num')['scr_clas'].to_dict()


reset()


def load_conf():
    global CONFIG_PAGE_SIZE, PARALLEL_NUM, PARALLEL_MODE, EXECUTOR, EXECUTOR_INNER, \
        HF_SORT_COLS, KLINED_SORT_COLS, KLINEM_SORT_COLS
    CONFIG = read_config()['system']
    CONFIG_PAGE_SIZE = CONFIG.get('page_size')
    PARALLEL_NUM = CONFIG.get("quote_parallel")
    PARALLEL_MODE = CONFIG.get("parallel_mode")
    if PARALLEL_MODE == 'Thread':
        EXECUTOR = ThreadPoolExecutor(max_workers=PARALLEL_NUM)
        EXECUTOR_INNER = ThreadPoolExecutor(max_workers=PARALLEL_NUM)
    elif PARALLEL_MODE == 'Coroutine':
        from gevent import monkey
        monkey.patch_all()
        from gevent.pool import Pool as gPool
        EXECUTOR = gPool(PARALLEL_NUM)
        EXECUTOR_INNER = gPool(PARALLEL_NUM)
        EXECUTOR.submit = EXECUTOR.spawn
        EXECUTOR_INNER.submit = EXECUTOR_INNER.spawn
    HF_SORT_COLS = {
        'hkstock': list(CONFIG.get('quote_hf_hkstock_sort').split(',')),
    }
    KLINED_SORT_COLS = {
        'hkstock': list(CONFIG.get('quote_kd_hkstock_sort').split(',')),
    }
    KLINEM_SORT_COLS = {
        'hkstock': list(CONFIG.get('quote_km_hkstock_sort').split(',')),
    }


load_conf()
_config = read_config()['system']

TWO_STEP_QUERY = False  # 20220812 行情请求是否使用分页模式（第一步获取总条数，第二步实际查询）
ONE_STEP_NUM = 9999999  # 20220812 一步请求的最大请求数量需要很大以覆盖所有情况

KLINE_CODE_GROUP = 10
HF_DAY_DELTA = 1
HF_CODE_GROUP = 1
KLINE_DAY_DELTA = 90

KLINE_DAY_DELTA_CANDLE_PERIOD = {
    '1m', '1',
    '5m', '2',
    '15m', '3',
    '30m', '4',
    '1h', '5',
    '1d', '6',
    # '1w': '7',
    # '1M': '8',
    # '1y': '9',
    '2h', '11',
    '3h', '12',
    '4h', '13',
    '10m', '14'
}


CANDLE_PERIOD_MAP = {
    '1m': '1',
    '5m': '2',
    '15m': '3',
    '30m': '4',
    '1h': '5',
    '1d': '6',
    '1w': '7',
    '1M': '8',
    '1y': '9',
    '2h': '11',
    '3h': '12',
    '4h': '13',
    '10m': '14'
}


CANDLE_MODE_MAP = {
    None: '0',
    'pre': '1',
    'post': '2'
}



def bind(_socket=None):
    if _socket is None:
        PROCESS_MMAP.seek(0)
        # 共享区域没有数据，则写入对应数据
        if PROCESS_MMAP.read() == b'\x00':
            # 执行绑定操作
            PROCESS_MMAP.seek(0)
            PROCESS_MMAP.write(b'\x31')
            PROCESS_MMAP.flush()

            # 检验绑定是否成功
            PROCESS_MMAP.seek(0)
            if PROCESS_MMAP.read() == b'\x31':
                return True
            else:
                return False

        else:
            return False
    else:
        try:
            _socket.bind(('127.0.0.1', _config["bind_port"]))
            return True
        except Exception as ex:
            return False


def unbind(_socket=None):
    if _socket is None:
        PROCESS_MMAP.seek(0)
        PROCESS_MMAP.write(b'\x00')
        PROCESS_MMAP.flush()
    else:
        _socket.close()


def wait_until_bind(count=10000, time_delta=1.0):
    def decorate(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            # 尝试进行绑定
            bind_method = _config.get("bind_method", "socket")
            if bind_method == 'socket':
                _socket = socket.socket()
            else:
                _socket = None
            cnt = 0
            while True:
                if bind(_socket):
                    try:
                        return func(*args, **kwargs)
                    except:
                        print(f"进程{os.getpid()}运行函数报错")
                        print(traceback.format_exc())
                        raise RunTimeError("运行时报错")
                    finally:
                        unbind(_socket)

                else:
                    cnt += 1
                    if cnt > count:
                        raise MaxTryExceed(f"进程{os.getpid()}等待次数超过上线")
                    if cnt % 60 == 0:
                        print(f"进程{os.getpid()}正常排队查询")
                time.sleep(time_delta)
        return wrap
    return decorate


def quote_single_part(method, params, two_step: bool = TWO_STEP_QUERY):
    init_count = 0  # 初次查询已获取的条数
    init_page = 0  # 初次查询已获取的页数
    total_pages = 0
    df_dic = {}

    # 两步模式下第一步获取总条数以取得分页
    if two_step:
        # 约定使用0作为条数查询
        params['total_num'] = 0
        init_result = get_qdata(method, **params)
        if str(init_result.get('result_code', '0')) != '0':
            raise Exception('异常代码[%s], 异常信息[%s]' % (init_result['result_code'], init_result['result_msg']))
        if init_result['data'] is not None:
            init_count = len(init_result['data'])
            df_dic[0] = init_result['data']
        total_pages = (init_result['total_num'] + params['page_size'] - 1 - init_count) // params['page_size']
        # 只可能是1或0，表示初次查询是否返回值，否则有问题
        init_page = init_count // params['page_size']

    if two_step and total_pages > init_page:
        _parts = []
        for i in range(init_page + 1, total_pages + 1):
            params['total_num'] = init_result['total_num']
            params['page_num'] = i
            _part = EXECUTOR_INNER.submit(get_qdata, method=method, **params)
            _parts.append(_part)

        for _p in as_completed(_parts):
            try:
                if _p is None:
                    continue
                elif _p.result() is None:
                    continue

                result_data = _p.result()

                df_part = result_data['data']
                if len(df_part) > 0:
                    df_part.index = df_part.index + (result_data['page_num'] - 1) * params['page_size']
                    df_dic[result_data['page_num']] = df_part

            except Exception as ex:
                raise Exception("并发处理异常，异常函数[%s]" % method)
        df = sort_merge_df_dic(df_dic)
    else:
        # 一步模式请求所有数据
        params['total_num'] = ONE_STEP_NUM
        params['page_size'] = ONE_STEP_NUM
        result = get_qdata(method, **params)
        if str(result.get('result_code', '0')) != '0':
            raise Exception('异常代码[%s], 异常信息[%s]' % (result['result_code'], result['result_msg']))
        df = result['data']
    ret = {'method': method, 'params': params, 'data': df, }
    return ret


def get_exchange_calendar(mkt_code, strt_date='19900101', end_date=None, trdy_flag=None, cols=None, rslt_type=0):
    """
    获取交易所交易日日历，包括：上海证券交易所，深圳证券交易所等。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = ['mkt_code', 'busi_date', 'trdy_flag']

    if mkt_code:
        params = {
            "mkt_code": mkt_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "trdy_flag": trdy_flag,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_exch_trd_cldr", **params)
    else:
        warnings.warn("函数[get_exchange_calendar]的参数(mkt_code)为必填项")
        return None

#20250327 新增港股K线查询
def _async_get_kline_data(func, scr_num_list, start_date, end_date,
                          candle_period, candle_mode, columns, code_type):
    """
    异步获取K线数据
    """

    if code_type == 'hkstock':
        int_param = ['trd_vol', 'macth_items']

        float_param = ['open_px', 'high_px', 'low_px', 'close_px', 'trd_amt', 'interest', 'preclose_px']
    else:
        int_param = ['trd_vol', 'position', 'preposition']
        float_param = ['open_px', 'high_px', 'low_px', 'close_px', 'preclose_px',
                       'up_limit', 'down_limit', 'settlement_px', 'presettlement_px',
                       'avg_px', 'trd_amt', 'up_low', 'up_low_rate', 'up_low_k', 'up_low_rate_k']

    if columns:
        # 分钟级别K线
        if int(CANDLE_PERIOD_MAP[candle_period]) < int(CANDLE_PERIOD_MAP['1d']) or int(CANDLE_PERIOD_MAP[candle_period]) == 14:
            if code_type == 'hkstock':
                fix_cols = \
                    ['scr_num', 'date_time', 'min_time']
            # else:
            #     fix_cols = \
            #         ['scr_num', 'date_time', 'action_date', 'min_time']
        else:
            fix_cols = \
                ['scr_num', 'date_time']

        if isinstance(columns, str):
            columns = columns.split(',')
        tmp_cols = fix_cols + columns
        columns = list(set(tmp_cols))
        columns.sort(key=tmp_cols.index)

        int_param = \
            list(set(int_param).intersection(set(columns)))
        float_param = \
            list(set(float_param).intersection(set(columns)))

        if isinstance(columns, list):
            columns = ','.join(columns)

    current_date = get_current_date()
    if start_date is None and end_date is None:
        df = get_exchange_calendar('XHKG', end_date=current_date, trdy_flag=1)
        if df.shape[0] > 2:
            start_date = end_date = df['busi_date'].tolist()[-2]
        else:
            start_date = end_date = current_date
    elif start_date is None:
        start_date = end_date
    elif end_date is None:
        end_date = start_date

    trading_day = [start_date]
    if start_date != end_date:
        df = get_exchange_calendar('XHKG', start_date, end_date, trdy_flag=1)
        if df is None:
            return None
        trading_day = df['busi_date'].tolist()

        # 根据查询日期跨度判断采用的股票代码步长
        scr_num_list = regroup_scr_nums(scr_num_list, 1)

    else:
        # 根据查询日期跨度判断采用的股票代码步长
        scr_num_list = regroup_scr_nums(scr_num_list, KLINE_CODE_GROUP)

    if candle_period in KLINE_DAY_DELTA_CANDLE_PERIOD:
        # 仅对日K或更短周期的蜡烛图做按天切分
        day_delta = KLINE_DAY_DELTA if KLINE_DAY_DELTA < len(trading_day) else len(trading_day)
        _start_date_list = trading_day[::day_delta]
        _end_date_list = trading_day[day_delta - 1::day_delta]
        if len(_start_date_list) != len(_end_date_list):
            _end_date_list.append(trading_day[-1])
    else:
        _start_date_list = [start_date]
        _end_date_list = [end_date]

    _futures = []
    params_list = []
    for _idx in range(len(_start_date_list)):
        for _scr in scr_num_list:
            params = {
                "scr_num_list": _scr.replace('.XHKG', '.HK'),
                "candle_period": CANDLE_PERIOD_MAP[candle_period],
                "candle_mode": CANDLE_MODE_MAP[candle_mode],
                "strt_date": _start_date_list[_idx],
                "end_date": _end_date_list[_idx],
                "cols": columns,
                "api_type": "kline",
                "int_param": int_param,
                "float_param": float_param
            }
            params_list.append(params)

    for params in params_list:
        _future = EXECUTOR.submit(get_qdata, method=func, **params)
        _futures.append(_future)

    dfs = collect_dfs_parallel(func, _futures)

    # 分钟K线
    if int(CANDLE_PERIOD_MAP[candle_period]) < int(CANDLE_PERIOD_MAP['1d']) or int(CANDLE_PERIOD_MAP[candle_period]) == 14:
        global KLINEM_SORT_COLS
        result = sort_merge_df(dfs, KLINEM_SORT_COLS[code_type])
    else:
        global KLINED_SORT_COLS
        result = sort_merge_df(dfs, KLINED_SORT_COLS[code_type])
    return result

@wait_until_bind()
def get_kline(scr_num_list, candle_period='1d', candle_mode=None, strt_date=None, end_date=None,
              cols=None, rslt_type=0):
    """
    批量获取不同种类的K线历史数据查询

    """

    if scr_num_list is None:
        warnings.warn("函数[get_kline]的参数(scr_num_list)为必填项")
        return None

    if isinstance(scr_num_list, str):
        scr_num_list = scr_num_list.split(',')

    stk_list = []

    global CODE_SECURITY_MAP
    if len(CODE_SECURITY_MAP) == 0:
        load_basic_info()

#因代码表不全暂不检查
    # scr_code_list = \
    #     [
    #         _code for _code in scr_num_list if _code.split('.')[1] in ['XHKG']
    #     ]
    #
    # noexist_code_list = set(scr_code_list) - set(list(CODE_SECURITY_MAP.keys()))
    # if len(noexist_code_list):
    #     warnings.warn("函数[scr_num_list]中指定代码不存在[%s]" % ''.join(noexist_code_list))
    #     return None

    try:
        for _scr in scr_num_list:
            _market_code = _scr.split('.')[1]
            stk_list.append(_scr)
            # if CODE_SECURITY_MAP[_scr] == 'STOCK':
            #     stk_list.append(_scr)
    except IndexError:
        raise Exception('scr_num_list输入格式异常[%s]' % scr_num_list)

    stk_result = None
    if len(stk_list) > 0:
        stk_result = _async_get_kline_data(
            URL_GET_HKSTK_KLINE, stk_list, strt_date, end_date, candle_period,
            candle_mode, cols, 'hkstock'
        )
    #
    # if len(bond_list) > 0:
    #     bond_result = _async_get_kline_data(
    #         URL_GET_BND_KLINE, bond_list, strt_date, end_date, candle_period,
    #         candle_mode, cols, 'bond'
    #     )
    #
    # if len(fund_list) > 0:
    #     fund_result = _async_get_kline_data(
    #         URL_GET_FND_KLINE, fund_list, strt_date, end_date, candle_period,
    #         candle_mode, cols, 'fund'
    #     )
    #
    # if len(futu_list) > 0:
    #     futu_candle_mode = None
    #     futu_result = _async_get_kline_data(
    #         URL_GET_FUT_KLINE, futu_list, strt_date, end_date, candle_period,
    #         futu_candle_mode, cols, 'future'
    #     )

    final_result = None
    concat_list = []
    if stk_result is not None:
        concat_list.append(stk_result)
    # if bond_result is not None:
    #     concat_list.append(bond_result)
    # if fund_result is not None:
    #     concat_list.append(fund_result)
    # if futu_result is not None:
    #     concat_list.append(futu_result)

    if len(concat_list) > 1:
        final_result = pd.concat(
            concat_list,
            axis=0, sort=False, ignore_index=True
        )
    elif len(concat_list) == 1:
        final_result = concat_list[0]

    final_result = convert_result_data(final_result, rslt_type)

    return final_result

def _async_get_hf_data(func, scr_num_list, start_time, end_time, columns, code_type):
    """
    异步获取高频数据
    """
    # future和hkstock默认用的单日起止时间
    day_end_time = '235959'
    day_start_time = '000000'

    scr_num_list = regroup_scr_nums(scr_num_list, HF_CODE_GROUP)

    if HF_DAY_DELTA > 0:
        # 获取交易日
        if start_time[: 8] == end_time[: 8]:
            trading_day = [start_time[: 8]]
        else:
            #20240606 新增港股交易日判斷
            if code_type == "hkstock" :
                df = get_exchange_calendar('XHKG', start_time[: 8], end_time[: 8], trdy_flag=1)
                if df is None:
                    df = get_exchange_calendar('XHKG', trdy_flag=1).tail(1)
            else:
                df = get_exchange_calendar('XSHG', start_time[: 8], end_time[: 8], trdy_flag=1)
                if df is None:
                    df = get_exchange_calendar('XSHG', trdy_flag=1).tail(1)
            trading_day = df['busi_date'].tolist()

    params_list = []
    _futures = []
    if HF_DAY_DELTA > 0:
        day_delta = HF_DAY_DELTA if HF_DAY_DELTA < len(trading_day) else len(trading_day)
        _start_date_list = trading_day[::day_delta]
        _end_date_list = trading_day[day_delta - 1::day_delta]
        if len(_start_date_list) != len(_end_date_list):
            _end_date_list.append(trading_day[-1])

        for _idx in range(len(_start_date_list)):
            _start_time = _start_date_list[_idx]
            _end_time = _end_date_list[_idx]
            if _idx == 0 and _start_time == start_time[: 8]:
                _start_time = start_time
            if _idx == len(trading_day) - 1 and _end_time == end_time[: 8]:
                _end_time = end_time
                if len(end_time) == 8:
                    end_time = '%s%s' % (end_time, day_end_time)

            for _s in scr_num_list:
                params = {
                    "scr_num": _s,
                    "strt_time": _start_time,
                    "end_time": _end_time,
                    "cols": columns,
                }
                params_list.append(params)

    else: # if SPILIT_DAY > 0
        _start_time = start_time
        _end_time = end_time
        for _s in scr_num_list:
            params = {
                "scr_num": _s,
                "strt_time": _start_time,
                "end_time": _end_time,
                "cols": columns,
            }
            params_list.append(params)

    for params in params_list:
        _future = EXECUTOR.submit(func, **params)
        _futures.append(_future)

    dfs = collect_dfs_parallel(func, _futures)

    global HF_SORT_COLS
    result = sort_merge_df(dfs, HF_SORT_COLS[code_type])
    return result


def regroup_scr_nums(scr_num_list, group_num):
    scr_num_list.sort() # 否则合并时可能排序顺序不对
    new_list = list([','.join(scr_num_list[i:i+group_num]) for i in range(0, len(scr_num_list), group_num)])
    return new_list


def convert_result_data(df, rslt_type):
    rslt = None
    if df is not None:
        if rslt_type == 0:
            rslt = df
        else:
            rslt = df.values
    return rslt

def collect_dfs_parallel(func, _futures):
    dfs = []
    if PARALLEL_MODE in {'Coroutine'}:
        gevent.joinall(_futures)
        for _f in _futures:
            try:
                if _f is None:
                    continue
                elif _f.value is None:
                    continue
                elif _f.value['data'] is None:
                    continue

                if len(_f.value['data']) > 0:
                    dfs.append(_f.value['data'])
            except Exception as ex:
                warn_str = "并发处理异常，异常函数[%s]" % func
                warnings.warn(warn_str)
                # raise Exception("并发处理异常，异常函数[%s]" % func)
    else:
        for _f in as_completed(_futures):
            try:
                if _f is None:
                    continue
                elif _f.result() is None:
                    continue
                elif _f.result()['data'] is None:
                    continue

                if len(_f.result()['data']) > 0:
                    dfs.append(_f.result()['data'])
            except Exception as ex:
                import traceback
                warn_str = "并发处理异常，异常函数[%s]，异常信息[%s]" % (func, traceback.format_exc())
                warnings.warn(warn_str)
    return dfs

#20240628 add 港股基本信息接口
def get_security_info(scr_num_list=None, scr_type_list=None, cols=None):
    """
    获取港股的基本信息

    """
    int_param = []
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code',
            'scr_num',
            'scr_abbr',
            'scr_name',
            'mkt_code',
            'list_stat',
            'list_date',
            'delt_date',
            'scr_type',
            'scr_boar_type_code',
            'ofer_crrc_code',
            'trd_unit',
            'isin_num'
        ]

    params = {
        "scr_num_list": scr_num_list,
        "scr_type_list": scr_type_list,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_hkscr_basc_info", **params)

#20240628 add 港股复权因子接口
def get_stk_rstr_fctr(scr_num_list=None, strt_date=None, end_date=None, cols=None):
    """
    获取港股复权因子信息

    """
    int_param = []
    float_param = ['accu_rstr_cnst', 'aacu_rstr_fctr', 'aggr_accu_rstr_cnst', 'aggr_accu_rstr_fctr']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num',
            'scr_code',
            'dr_day',
            'accu_rstr_cnst',
            'accu_rstr_fctr',
            'aggr_accu_rstr_cnst',
            'aggr_accu_rstr_fctr',
            'aggr_rati_rstr_fctr',
            'info_mine',
            'exd_if_susp',
            'next_resup_date',
        ]

    params = {
        "scr_num_list": scr_num_list,
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_hkstk_rstr_fctr", **params)




#20240606 新增港股查询api
@wait_until_bind()
def get_deal(scr_num_list, strt_time, end_time, cols=None, rslt_type=0):
    """
    获取港股逐笔成交数据
    """

    if scr_num_list is None or strt_time is None or end_time is None:
        warnings.warn("函数[hk.get_deal]的参数(scr_num_list, strt_time, end_time)为必填项")
        return None

    if isinstance(scr_num_list, str):
        scr_num_list = scr_num_list.split(',')

    stk_list = []

    global CODE_SECURITY_MAP
    if len(CODE_SECURITY_MAP) == 0:
        load_basic_info()

    scr_code_list = \
        [
            _code for _code in scr_num_list if _code.split('.')[1] in ['XHKG']
        ]


    noexist_code_list = set(scr_code_list) - set(list(CODE_SECURITY_MAP.keys()))
    if len(noexist_code_list):
        warnings.warn("函数[scr_num_list]中指定代码不存在[%s]" % ''.join(noexist_code_list))
        return None



    try:

        stk_list = [_scr.replace('.XHKG', '.HK') for _scr in scr_num_list]

    except IndexError:
        raise Exception('scr_num_list输入格式异常[%s]' % scr_num_list)

    stk_result = None
    if len(stk_list) > 0:
        stk_result = _async_get_hf_data(
            get_hkstock_deal, stk_list, strt_time, end_time,
            cols, 'hkstock'
        )

    final_result = None
    concat_list = []
    if stk_result is not None:
        concat_list.append(stk_result)

    if len(concat_list) > 1:
        final_result = pd.concat(
            concat_list,
            axis=0, sort=False, ignore_index=True
        )
    elif len(concat_list) == 1:
        final_result = concat_list[0]

    final_result = convert_result_data(final_result, rslt_type)

    return final_result

def get_hkstock_deal(scr_num, strt_time=None, end_time=None, cols=None, rslt_type=0):
    """
    批量获取港股逐笔成交数据

    """

    int_param = [
        'total_num', 'page_num', 'total_pages',
        't_id', 'qty'
    ]
    float_param = [
        'price'
    ]
    if cols:
        fix_cols = \
            ['scr_num', 'date_time']
        if isinstance(cols, str):
            cols = cols.split(',')
        tmp_cols = fix_cols + cols
        cols = list(set(tmp_cols))
        cols.sort(key=tmp_cols.index)

        int_param = list(set(int_param).intersection(set(cols)))
        float_param = list(set(float_param).intersection(set(cols)))

        if isinstance(cols, list):
            cols = ','.join(cols)

    if scr_num:
        params = {
            "scr_num": scr_num,
            "strt_time": strt_time,
            "end_time": end_time,
            "cols": cols,
            "page_num": 1,
            "page_size": CONFIG_PAGE_SIZE,
            "rslt_type": rslt_type,
            "api_type": "quote",
            "int_param": int_param,
            "float_param": float_param
        }

        # 20220812 统一改为与期货快照一致
        quote_data = quote_single_part(URL_GET_HKSTK_DEAL, params)
        return quote_data

    else:
        warnings.warn("函数[get_hkstock_deal]的参数(scr_num)为必填项")
        return None


@wait_until_bind()
def get_tick(scr_num_list, strt_time, end_time, cols=None, rslt_type=0):
    """
    获取港股快照数据
    """

    if scr_num_list is None or strt_time is None or end_time is None:
        warnings.warn("函数[get_tick]的参数(scr_num_list, strt_time, end_time)为必填项")
        return None

    if isinstance(scr_num_list, str):
        scr_num_list = scr_num_list.split(',')

    stk_list = []

    global CODE_SECURITY_MAP
    if len(CODE_SECURITY_MAP) == 0:
        load_basic_info()

    scr_code_list = \
        [
            _code for _code in scr_num_list if _code.split('.')[1] in ['XHKG']
        ]


    noexist_code_list = set(scr_code_list) - set(list(CODE_SECURITY_MAP.keys()))
    if len(noexist_code_list):
        warnings.warn("函数[scr_num_list]中指定代码不存在[%s]" % ''.join(noexist_code_list))
        return None

    try:
        stk_list = [_scr.replace('.XHKG', '.HK') for _scr in scr_num_list]
    except IndexError:
        raise Exception('scr_num_list输入格式异常[%s]' % scr_num_list)

    stk_result = None
    if len(stk_list) > 0:
        stk_result = _async_get_hf_data(
            get_hkstock_tick, stk_list, strt_time, end_time,
            cols, 'hkstock'
        )

    final_result = None
    concat_list = []
    if stk_result is not None:
        concat_list.append(stk_result)

    if len(concat_list) > 1:
        final_result = pd.concat(
            concat_list,
            axis=0, sort=False, ignore_index=True
        )
    elif len(concat_list) == 1:
        final_result = concat_list[0]

    final_result = convert_result_data(final_result, rslt_type)

    return final_result

def get_hkstock_tick(scr_num, strt_time=None, end_time=None, cols=None, rslt_type=0):
    """
    批量获取股票代码快照数据

    """

    int_param = [
        'total_num', 'page_num', 'total_pages',
        'volume', 'shortsell_volume', 'ie_volume', 'noliquidity_providers', 'lpb_no',
        'bid_size1', 'bid_size2', 'bid_size3', 'bid_size4', 'bid_size5',
        'bid_size6', 'bid_size7', 'bid_size8', 'bid_size9', 'bid_size10',
        'bid_order1', 'bid_order2', 'bid_order3', 'bid_order4', 'bid_order5',
        'bid_order6', 'bid_order7', 'bid_order8', 'bid_order9', 'bid_order10',
        'offer_size1', 'offer_size2', 'offer_size3', 'offer_size4', 'offer_size5',
        'offer_size6', 'offer_size7', 'offer_size8', 'offer_size9', 'offer_size10',
        'offer_order1', 'offer_order2', 'offer_order3', 'offer_order4', 'offer_order5',
        'offer_order6', 'offer_order7', 'offer_order8', 'offer_order9', 'offer_order10'
    ]
    float_param = [
        'turnover', 'high_px', 'low_px', 'last_px', 'shortsell_turnover', 'nominal_px', 'close_px',
        'ie_price', 'refer_price', 'lower', 'upper', 'order_imbal_quantity', 'yield', 'open_px', 'preclose_px',
        'bid_price1', 'bid_price2', 'bid_price3', 'bid_price4', 'bid_price5',
        'bid_price6', 'bid_price7', 'bid_price8', 'bid_price9', 'bid_price10',
        'offer_price1', 'offer_price2', 'offer_price3', 'offer_price4', 'offer_price5',
        'offer_price6', 'offer_price7', 'offer_price8', 'offer_price9', 'offer_price10'

    ]
    if cols:
        fix_cols = \
            ['scr_num', 'date_time']
        if isinstance(cols, str):
            cols = cols.split(',')
        tmp_cols = fix_cols + cols
        cols = list(set(tmp_cols))
        cols.sort(key=tmp_cols.index)

        int_param = list(set(int_param).intersection(set(cols)))
        float_param = list(set(float_param).intersection(set(cols)))

        if isinstance(cols, list):
            cols = ','.join(cols)

    if scr_num:
        params = {
            "scr_num": scr_num,
            "strt_time": strt_time,
            "end_time": end_time,
            "cols": cols,
            "page_num": 1,
            "page_size": CONFIG_PAGE_SIZE,
            "rslt_type": rslt_type,
            "api_type": "quote",
            "int_param": int_param,
            "float_param": float_param
        }

        # 20220812 统一改为与期货快照一致
        quote_data = quote_single_part(URL_GET_HKSTK_TICK, params)
        return quote_data

    else:
        warnings.warn("函数[get_hkstock_tick]的参数(scr_num)为必填项")
        return None

@wait_until_bind()
def get_oddlot_order(scr_num_list, strt_time, end_time, cols=None, rslt_type=0):
    """
    获取港股碎股数据
    """

    if scr_num_list is None or strt_time is None or end_time is None:
        warnings.warn("函数[get_odd]的参数(scr_num_list, strt_time, end_time)为必填项")
        return None

    if isinstance(scr_num_list, str):
        scr_num_list = scr_num_list.split(',')

    stk_list = []

    global CODE_SECURITY_MAP
    if len(CODE_SECURITY_MAP) == 0:
        load_basic_info()

    scr_code_list = \
        [
            _code for _code in scr_num_list if _code.split('.')[1] in ['XHKG']
        ]

    noexist_code_list = set(scr_code_list) - set(list(CODE_SECURITY_MAP.keys()))
    if len(noexist_code_list):
        warnings.warn("函数[scr_num_list]中指定代码不存在[%s]" % ''.join(noexist_code_list))
        return None

    try:
        stk_list = [_scr.replace('.XHKG', '.HK') for _scr in scr_num_list]

    except IndexError:
        raise Exception('scr_num_list输入格式异常[%s]' % scr_num_list)

    stk_result = None
    if len(stk_list) > 0:
        stk_result = _async_get_hf_data(
            get_hkstock_odd, stk_list, strt_time, end_time,
            cols, 'hkstock'
        )

    final_result = None
    concat_list = []
    if stk_result is not None:
        concat_list.append(stk_result)

    if len(concat_list) > 1:
        final_result = pd.concat(
            concat_list,
            axis=0, sort=False, ignore_index=True
        )
    elif len(concat_list) == 1:
        final_result = concat_list[0]

    final_result = convert_result_data(final_result, rslt_type)

    return final_result

def get_hkstock_odd(scr_num, strt_time=None, end_time=None, cols=None, rslt_type=0):
    """
    批量获取港股碎股数据

    """

    int_param = [
        'total_num', 'page_num', 'total_pages',
        'order_id', 'qty', 'broker_id'
    ]
    float_param = [
        'price'
    ]
    if cols:
        fix_cols = \
            ['scr_num', 'date_time']
        if isinstance(cols, str):
            cols = cols.split(',')
        tmp_cols = fix_cols + cols
        cols = list(set(tmp_cols))
        cols.sort(key=tmp_cols.index)

        int_param = list(set(int_param).intersection(set(cols)))
        float_param = list(set(float_param).intersection(set(cols)))

        if isinstance(cols, list):
            cols = ','.join(cols)

    if scr_num:
        params = {
            "scr_num": scr_num,
            "strt_time": strt_time,
            "end_time": end_time,
            "cols": cols,
            "page_num": 1,
            "page_size": CONFIG_PAGE_SIZE,
            "rslt_type": rslt_type,
            "api_type": "quote",
            "int_param": int_param,
            "float_param": float_param
        }

        # 20220812 统一改为与期货快照一致
        quote_data = quote_single_part(URL_GET_HKSTK_ODD, params)
        return quote_data

    else:
        warnings.warn("函数[get_hkstock_odd]的参数(scr_num)为必填项")
        return None

@wait_until_bind()
def get_broker_queue(scr_num_list, strt_time, end_time, cols=None, rslt_type=0):
    """
    获取港股经纪商队列数据
    """

    if scr_num_list is None or strt_time is None or end_time is None:
        warnings.warn("函数[get_broker]的参数(scr_num_list, strt_time, end_time)为必填项")
        return None

    if isinstance(scr_num_list, str):
        scr_num_list = scr_num_list.split(',')

    stk_list = []

    global CODE_SECURITY_MAP
    if len(CODE_SECURITY_MAP) == 0:
        load_basic_info()

    scr_code_list = \
        [
            _code for _code in scr_num_list if _code.split('.')[1] in ['XHKG']
        ]


    noexist_code_list = set(scr_code_list) - set(list(CODE_SECURITY_MAP.keys()))
    if len(noexist_code_list):
        warnings.warn("函数[scr_num_list]中指定代码不存在[%s]" % ''.join(noexist_code_list))
        return None

    try:

        stk_list = [_scr.replace('.XHKG', '.HK') for _scr in scr_num_list]

    except IndexError:
        raise Exception('scr_num_list输入格式异常[%s]' % scr_num_list)

    stk_result = None
    if len(stk_list) > 0:
        stk_result = _async_get_hf_data(
            get_hkstock_broker, stk_list, strt_time, end_time,
            cols, 'hkstock'
        )

    final_result = None
    concat_list = []
    if stk_result is not None:
        concat_list.append(stk_result)

    if len(concat_list) > 1:
        final_result = pd.concat(
            concat_list,
            axis=0, sort=False, ignore_index=True
        )
    elif len(concat_list) == 1:
        final_result = concat_list[0]

    final_result = convert_result_data(final_result, rslt_type)

    return final_result

def get_hkstock_broker(scr_num, strt_time=None, end_time=None, cols=None, rslt_type=0):
    """
    批量获取港股经纪商队列数据

    """

    int_param = [
        'total_num', 'page_num', 'total_pages',
        'side', 'count'
    ]
    float_param = []
    if cols:
        fix_cols = \
            ['scr_num', 'date_time']
        if isinstance(cols, str):
            cols = cols.split(',')
        tmp_cols = fix_cols + cols
        cols = list(set(tmp_cols))
        cols.sort(key=tmp_cols.index)

        int_param = list(set(int_param).intersection(set(cols)))
        float_param = list(set(float_param).intersection(set(cols)))

        if isinstance(cols, list):
            cols = ','.join(cols)

    if scr_num:
        params = {
            "scr_num": scr_num,
            "strt_time": strt_time,
            "end_time": end_time,
            "cols": cols,
            "page_num": 1,
            "page_size": CONFIG_PAGE_SIZE,
            "rslt_type": rslt_type,
            "api_type": "quote",
            "int_param": int_param,
            "float_param": float_param
        }

        # 20220812 统一改为与期货快照一致
        quote_data = quote_single_part(URL_GET_HKSTK_BROKER, params)
        return quote_data

    else:
        warnings.warn("函数[get_hkstock_broker]的参数(scr_num)为必填项")
        return None

@wait_until_bind()
def get_index_tick(scr_num_list, strt_time, end_time, cols=None, rslt_type=0):
    """
    获取港股指数快照数据
    """

    if scr_num_list is None or strt_time is None or end_time is None:
        warnings.warn("函数[get_index_tick]的参数(scr_num_list, strt_time, end_time)为必填项")
        return None

    if isinstance(scr_num_list, str):
        scr_num_list = scr_num_list.split(',')

    stk_list = []

    global CODE_SECURITY_MAP
    if len(CODE_SECURITY_MAP) == 0:
        load_basic_info()

    scr_code_list = \
        [
            _code for _code in scr_num_list if _code.split('.')[1] in ['XHKG']
        ]

#     等待港股代码服务完成后开放
#     noexist_code_list = set(scr_code_list) - set(list(CODE_SECURITY_MAP.keys()))
#     if len(noexist_code_list):
#         warnings.warn("函数[scr_num_list]中指定代码不存在[%s]" % ''.join(noexist_code_list))
#         return None

    try:

        stk_list = [_scr.replace('.XHKG', '.HK') for _scr in scr_num_list]

    except IndexError:
        raise Exception('scr_num_list输入格式异常[%s]' % scr_num_list)

    stk_result = None
    if len(stk_list) > 0:
        stk_result = _async_get_hf_data(
            get_hkstock_index, stk_list, strt_time, end_time,
            cols, 'hkstock'
        )

    final_result = None
    concat_list = []
    if stk_result is not None:
        concat_list.append(stk_result)

    if len(concat_list) > 1:
        final_result = pd.concat(
            concat_list,
            axis=0, sort=False, ignore_index=True
        )
    elif len(concat_list) == 1:
        final_result = concat_list[0]

    #因index原始数据存在重复，对index_tick返回数据进行去重

    if final_result is not None:
        final_result.drop_duplicates(subset=['scr_num', 'date_time'], keep='first', inplace=True)
        final_result = convert_result_data(final_result, rslt_type)

    return final_result

def get_hkstock_index(scr_num, strt_time=None, end_time=None, cols=None, rslt_type=0):
    """
    批量获取港股指数快照数据

    """

    int_param = [
        'total_num', 'page_num', 'total_pages',
        'index_volume'
    ]
    float_param = [
        'index_value', 'netchg_prevday', 'high', 'low', 'eas_value', 'index_turnover',
        'open', 'close', 'prevses_close', 'netchg_prevday_pct'
    ]
    if cols:
        fix_cols = \
            ['scr_num', 'date_time']
        if isinstance(cols, str):
            cols = cols.split(',')
        tmp_cols = fix_cols + cols
        cols = list(set(tmp_cols))
        cols.sort(key=tmp_cols.index)

        int_param = list(set(int_param).intersection(set(cols)))
        float_param = list(set(float_param).intersection(set(cols)))

        if isinstance(cols, list):
            cols = ','.join(cols)

    if scr_num:
        params = {
            "scr_num": scr_num,
            "strt_time": strt_time,
            "end_time": end_time,
            "cols": cols,
            "page_num": 1,
            "page_size": CONFIG_PAGE_SIZE,
            "rslt_type": rslt_type,
            "api_type": "quote",
            "int_param": int_param,
            "float_param": float_param
        }

        # 20220812 统一改为与期货快照一致
        quote_data = quote_single_part(URL_GET_HKSTK_INDEX, params)
        return quote_data

    else:
        warnings.warn("函数[get_hkstock_index]的参数(scr_num)为必填项")
        return None




