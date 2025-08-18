# -*- coding: utf-8 -*-
import io
import time
import six
import abc
import warnings
import requests
import numpy as np
import pandas as pd
import json
import urllib3
import pyarrow as pa
import pyarrow.feather as feather


from dataquant.utils.common import (
    ConnectionStatus,
    ERROR_NO,
    ERROR_INFO,
    DATA
)
from dataquant.utils.error import (
    ConnectionException,
    ConnectionTimeOut,
    RequestTimeOut,
    RequestException,
    GatewayException,
    ServerException,
    GATEWAY_ERROR_DICT,
    SERVER_ERROR_DICT,
)


class AbstractConnection(six.with_metaclass(abc.ABCMeta)):
    """
    连接抽象类
    """
    def create(self, *args, **kwargs):
        """
        创建连接对象
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def connect(self, timeout=5):
        """
        启动连接
        :param timeout:
        :return:
        """
        raise NotImplementedError

    def set_timeout(self, timeout):
        """
        设置超时时间
        :param timeout:
        :return:
        """
        raise NotImplementedError

    def send(self, *args, **kwargs):
        """
        同步发送数据
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def async_send(self, *args, **kwargs):
        """
        异步发送数据
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def receive(self, *args, **kwargs):
        """
        接收数据
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def status(self):
        """
        连接状态
        :return:
        """
        raise NotImplementedError

    def check(self):
        """
        检查连接是否可用
        :return:
        """
        raise NotImplementedError

    def error(self):
        """
        连接错误信息
        :return:
        """
        raise NotImplementedError

    def close(self):
        """
        关闭链接
        :return:
        """
        raise NotImplementedError


class Connection(object):
    """
    连接工厂类
    """
    @classmethod
    def get_connection(cls, config):
        from dataquant.utils.common import Protocol
        protocol = config.get("protocol")
        conn_timeout = config.get("connect_timeout")
        try:
            with ConnectionContext(conn_timeout):
                return globals()[Protocol[protocol].value]().create(config)
        except KeyError:
            raise RuntimeError("创建链接对象失败,请检查配置信息是否正确？config={}".format(config))


class HttpConnection(AbstractConnection):
    """
    HTTP连接对象类
    """

    def create(self, config):
        """
        创建连接对象
        :param config:
        :return:
        """
        # 解析config文件中的信息
        url = config.get("url")
        auth = config.get("auth")

        assert url
        assert auth

        self._url = url
        self._user = auth.get("username")
        self._pwd = auth.get("password")
        self._timeout = config.get("request_timeout")
        self._page_size = config.get("page_size")

        assert self._user
        assert self._pwd

        self._conn = requests.Session()
        self._status = ConnectionStatus.Connected
        self._conn_u3 = urllib3.PoolManager()
        return self

    def set_timeout(self, timeout):
        """
        设置超时时间
        :param timeout:
        :return:
        """
        self._timeout = timeout

    def _build_data(self, **kwargs):
        api_type = kwargs.get("api_type", "normal")
        if api_type in {"normal"}:
            data = {
                "params": kwargs,
                "page_no": kwargs.get("page_no", "1"),
                "page_size": kwargs.get("page_size", self._page_size),
            }
        elif api_type in {"quote", "kline", "summary"}:
            data = {
                "params": kwargs
            }
        elif api_type in {"sql"}:
            data = {
                "params": kwargs
            }
        else:
            raise RuntimeError("未知的API类型，当前仅支持normal/quote/kline")
        return data

    def _build_ret(self, rsp, **kwargs):
        api_type = kwargs.get("api_type", "normal")
        ret = {}
        # 拆卸其他返回参数，处理DF,常规处理模式
        if api_type == "normal":
            df = pd.DataFrame()
            for k, v in rsp.items():
                if k == "data":
                    if isinstance(rsp[k], dict):
                        for dk, dv in rsp[k].items():
                            if dk not in {"rows"}:
                                ret[dk] = dv
                                
                else:
                    ret[k] = v
            if rsp.get("data"):
                df = pd.DataFrame(rsp["data"]["rows"])
            self._mod_ret_df(df, kwargs, ret)
        # 行情接口处理模式
        elif api_type in ("quote", "kline", "summary"):
            df = pd.DataFrame()
            if rsp['data_type'] == 'data':
                ret['page_num'] = rsp['page_num']
                data_bin = rsp['content']
                format_type = kwargs.get('format', 'Arrow')

                if api_type == "kline":
                    # 不复权Kline数据，返回格式为Parquet/Arrow格式
                    # 前复权Kline数据，返回格式为CSV格式
                    # 后复权Kline数据，1d以上返回Parquet/Arrow格式，其余返回CSV格式
                    if kwargs.get('candle_mode', '0') == '0':
                        pass
                    elif kwargs.get('candle_mode', '0') == '1':
                        format_type = 'CSVWithNames'
                    elif kwargs.get('candle_mode', '0') == '2':
                        # if kwargs.get('candle_period', '6') in ('6', '7', '8', '9'):
                        #     pass
                        # else:
                        #     format_type = 'CSVWithNames'

                        format_type = 'CSVWithNames'
                elif api_type == "summary":
                    format_type = 'TSVWithNames'
                
                try:
                    if format_type == 'CSVWithNames':
                        df = pd.read_csv(io.StringIO(data_bin.decode('utf8')), sep=',')
                    elif format_type == 'Parquet':
                        df = pd.read_parquet(io.BytesIO(data_bin))
                    elif format_type == 'Arrow':
                        df = feather.read_feather(pa.py_buffer(data_bin))
                    elif format_type == 'TSVWithNames':
                        df = pd.read_csv(io.StringIO(data_bin.decode('utf8')), sep='\t', names=kwargs['fix_cols'])
                    pass
                except Exception as e:
                    warn_str = "数据转换异常,错误说明={},数据长度={}".format(str(e),len(data_bin))
                    warnings.warn(warn_str)
                    pass
            else:
                format_type = 'json'
                for k, v in rsp.items():
                    if k == "data":
                        if isinstance(rsp[k], dict):
                            for dk, dv in rsp[k].items():
                                if dk not in {"cols", "items"}:
                                    ret[dk] = dv
                    else:
                        ret[k] = v

            # 20220806 行情单独处理
            self._mod_ret_df_quote(df, kwargs, ret,format_type)
        # SQL接口处理模式
        elif api_type == "sql":
            ret = dict()
            ret['result_code'] = rsp['result_code']
            ret['result_msg'] = rsp['result_msg']
            tmp_rsp = rsp['data'].replace('null', '\"\"')
            ret['data'] = pd.DataFrame(eval(tmp_rsp))

        return ret

    def _mod_ret_df(self, df, kwargs, ret):
        # DF后期加工
        df.columns = df.columns.map(lambda x: x.lower())
        if not df.empty:
            if isinstance(kwargs['cols'], list):
                df = df[kwargs['cols']]
            elif isinstance(kwargs['cols'], str):
                cols = kwargs['cols'].replace(' ', '')
                df = df[cols.split(',')]

            for int_type in kwargs.get("int_param"):
                if int_type in df.columns:
                    df[int_type] = pd.Series(df[int_type], dtype='int64')
            for float_type in kwargs.get("float_param"):
                if float_type in df.columns:
                    df[float_type] = pd.Series(df[float_type], dtype='float64')
        else:
            ret["data"] = None
            return

        if not(kwargs.get("rslt_type", 0)):
            ret["data"] = df
        elif kwargs.get("rslt_type", 0) == 1:
            ret["data"] = np.array(df.to_records(index=False))
        else:
            raise ValueError("rslt_type must in (0,1)")

    def _mod_ret_df_quote(self, df, kwargs, ret, format_type):
        if (not df.empty) and len(df) > 0:
            # 20220818 前复权数据类型规整,但本质是tsv,csv需要
            if format_type == 'CSVWithNames':
                for int_type in kwargs.get("int_param"):
                    if int_type in df.columns:
                        df[int_type] = pd.Series(df[int_type], dtype='float64')
                for float_type in kwargs.get("float_param"):
                    if float_type in df.columns:
                        df[float_type] = pd.Series(df[float_type], dtype='float64')
            pass
        else:
            df = None
        ret["data"] = df
        return

    def send(self, method, **kwargs):
        """
        同步发送数据
        :param method:
        :param kwargs:
        :return:
        """

        api_type = kwargs.get("api_type", "normal")
        # 已连接状态时
        if self.check():
            if self._user == "license":
                url = "".join((self._url, "/", method, "?app_key=", self._pwd))
            else:
                raise RuntimeError("当前只支持license登录方式")

            data = self._build_data(**kwargs)

            try:
                response_u3 = self._conn_u3.request(
                    'POST',
                    url,
                    body=json.dumps(data),
                    headers={'Content-Type': 'application/json', 'Accept-Encoding': 'br,gzip,deflate'},
                    timeout=self._timeout)
                response = ResponseU3(response_u3)
            except requests.exceptions.ConnectTimeout as ex:
                raise RequestTimeOut(ex)
            # 状态码200表示请求成功
            if response.status_code == 200:
                # requests获取后直接调用json()方法转变为python字典请求获取HttpResponse对象
                if api_type in {'quote', 'kline', 'summary'}:
                    rsp = {
                        'data_type':None,
                        'content': response.content,
                        'result_code': '0',
                        'page_num': 1,
                    }
                    if 'page_num' in kwargs:
                        rsp['page_num'] = kwargs['page_num']
                    if response.content[0:1] == b'{':
                        rsp = response.json()
                        rsp['data_type'] = 'json'
                        if "result_code" not in rsp:
                            if "resultCode" in rsp:
                                rsp['result_code'] = rsp["resultCode"]
                            else:
                                rsp['result_code'] = '0'
                        if "result_msg" not in rsp:
                            if "resultMsg" in rsp:
                                rsp['result_msg'] = rsp["resultMsg"]
                            else:
                                rsp['result_msg'] = ''
                    else:
                        rsp['data_type'] = 'data'

                else:
                    rsp = response.json() # 180ms
                # 从数据服务返回的数据
                if "result_code" in rsp:
                    if int(rsp["result_code"]) == 0:
                        ret = self._build_ret(rsp, **kwargs)
                        return ret
                    # 获取error中异常信息
                    if SERVER_ERROR_DICT.get(int(rsp["result_code"]), None):
                        # warnings.warn("app_key权限认证失败，请联系管理员，error_info={}".format(rsp["resultMsg"]))
                        # warnings.warn("app_key权限已过期，请重新申请，申请站点：{}".format(rsp["resultMsg"]))
                        warn_str = "请求异常，异常信息：{}".format(rsp["result_msg"])
                        warnings.warn(warn_str)
                        raise RequestException(rsp["result_msg"])
                    else:
                        warn_str = "获取数据异常，path={}，params={}，error_info={}".format(
                            method, kwargs, rsp["result_msg"])
                        warnings.warn(warn_str)
                        raise RequestException("请求发生未定义错误，错误信息：{}".format(rsp["result_msg"]))
            elif 400 <= response.status_code < 500:
                if api_type == 'quote': # 行情接口
                    warn_str = "服务异常，异常信息：{}".format(response.text)
                    warnings.warn(warn_str)
                    raise ServerException(response.text)
                else:
                    rsp = response.json()
                # 从新版网关返回异常
                if ERROR_NO in rsp:
                    # 获取错误代码
                    if GATEWAY_ERROR_DICT.get(rsp[ERROR_NO], None):
                        warnings.warn("网关返回错误，错误信息：{}".format(rsp[ERROR_INFO]))
                        raise GatewayException(rsp[ERROR_INFO])
                    else:
                        raise GatewayException("网关发生未定义错误，错误信息：{}".format(rsp[ERROR_INFO]))
                # 从老版网关返回异常
                elif DATA in rsp:
                    if isinstance(rsp[DATA], list):
                        error_dict = rsp[DATA][0]
                    else:
                        error_dict = rsp[DATA]

                    if GATEWAY_ERROR_DICT.get(error_dict[ERROR_NO], None):
                        warnings.warn("网关返回错误，错误信息：{}".format(error_dict[ERROR_INFO]))
                        raise GatewayException(error_dict[ERROR_INFO])
                    else:
                        raise GatewayException("网关发生未定义错误，错误信息：{}".format(error_dict[ERROR_INFO]))
                else:
                    warnings.warn("网关返回未定义异常，异常信息：{}".format(response.text))
                    raise GatewayException(response.text)
            # 服务错误
            elif 500 <= response.status_code < 601:
                warnings.warn("服务异常，异常信息：{}".format(response.text))
                raise ServerException(response.text)
            # 其他流程错误
            else:
                warnings.warn("异常流程，返回信息：{}".format(response.text))
                raise Exception(response.text)
        # 如果没连接则raise连接异常
        raise ConnectionException("连接已关闭，无法获取数据")

    def async_send(self, *args, **kwargs):
        """
        异步发送数据
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def receive(self, *args, **kwargs):
        """
        接收数据
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def status(self):
        """
        连接状态
        :return:
        """
        return self._status

    def check(self):
        return self._status in [ConnectionStatus.Connected, ConnectionStatus.SafeConnected]

    def error(self):
        """
        连接错误信息
        :return:
        """
        raise NotImplementedError

    def close(self):
        """
        关闭链接
        :return:
        """
        self._conn.close()
        self._status = ConnectionStatus.Disconnected


class ConnectionContext(object):
    def __init__(self, timeout=5):
        assert timeout
        self.timeout = timeout
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if time.time() - self.start > self.timeout:
            raise ConnectionTimeOut


class ResponseU3(object):
    def __init__(self,resp_u3):
        self.status_code = resp_u3.status
        self.content = resp_u3.data
        self.ori_resp = resp_u3

    @property
    def text(self):
        return self.content.decode(errors='backslashreplace')

    def json(self):
        return json.loads(self.text)
