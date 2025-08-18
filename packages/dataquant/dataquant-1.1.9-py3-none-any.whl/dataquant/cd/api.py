# -*- coding: UTF-8 -*-
import warnings
import numpy as np
import pandas as pd
from itertools import product

from dataquant.apis.base import get_data
from dataquant.utils.convert import convert_fields
from dataquant.utils.datetime_func import get_current_date

__all__ = [
    "get_ic_index_info",
    "get_ic_index_data"
]


def get_ic_index_info(indx_code_list=None, indx_abbr_list=None, lvl_code=None,
                      cols=None, rslt_type=0):
    """
    获取产业链特色数据信息

    """

    int_param = \
        [
        ]
    float_param = \
        [
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'indx_name', 'indx_abbr', 'data_val', 'publ_freq',
            'src_name', 'meas_name', 'calb_name', 'strt_date', 'end_date',
            'indx_stat', 'firs_lvl_code', 'firs_lvl_name', 'secd_lvl_code',
            'secd_lvl_name', 'thir_lvl_code', 'thir_lvl_name', 'four_lvl_code',
            'four_lvl_name', 'five_lvl_code', 'five_lvl_name', 'six_lvl_code',
            'six_lvl_name', 'sevn_lvl_code', 'sevn_lvl_name'
        ]

    params = {
        "indx_code_list": indx_code_list,
        "indx_abbr_list": indx_abbr_list,
        "lvl_code": lvl_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_ic_index_info", **params)


def get_ic_index_data(indx_code, strt_date=19900101, end_date=None, cols=None, **kwargs):
    """
    获取产业链特色数据

    """

    params = {
        'strt_date': strt_date,
        'end_date': end_date,
        'cols': cols
    }
    params.update(**kwargs)

    if isinstance(cols, list):
        cols = ','.join(cols)

    if cols:
        if len({'indx_code', 'data_date'} & set(cols.split(','))) == 0:
            warnings.warn("出参[indx_code, data_date]参数未指定")

    if indx_code:
        if indx_code == 'IDST0003':
            return get_st_multitb_0003(**params)
        elif indx_code == 'IDZN0140':
            return get_zn_multitb_0140(**params)
        elif indx_code == 'IDZN0141':
            return get_zn_multitb_0141(**params)
        elif indx_code == 'IDZN0142':
            return get_zn_multitb_0142(**params)
        elif indx_code == 'IDZN0143':
            return get_zn_multitb_0143(**params)
        elif indx_code == 'IDZN0144':
            return get_zn_multitb_0144(**params)
        elif indx_code == 'IDZN0145':
            return get_zn_multitb_0145(**params)
        elif indx_code == 'IDZN0146':
            return get_zn_multitb_0146(**params)
        elif indx_code == 'IDZN0147':
            return get_zn_multitb_0147(**params)
        elif indx_code == 'IDZN0148':
            return get_zn_multitb_0148(**params)
        elif indx_code == 'IDZN0149':
            return get_zn_multitb_0149(**params)
        elif indx_code == 'IDZN0150':
            return get_zn_multitb_0150(**params)
        elif indx_code == 'IDZN0151':
            return get_zn_multitb_0151(**params)
        else:
            return None
    else:
        warnings.warn("函数[get_ic_index_data]的参数(indx_code)为必填项")
        return None


def get_st_multitb_0003(strt_date=19900101, end_date=None, regi_name=None, cols=None):
    """
    获取建筑钢材日出库量

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['dirt_out', 'drum_out', 'scrw_out', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'regi_name', 'dirt_out', 'drum_out', 'scrw_out', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(regi_name, list):
        regi_name = ','.join(regi_name)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "regi_name": regi_name,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_st_multitb_0003", **params)


def get_zn_multitb_0140(strt_date=19900101, end_date=None, cols=None):
    """
    获取焦化产能调研数据

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['add_cap', 'del_cap', 'net_add_cap', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'add_cap', 'del_cap', 'net_add_cap', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0140", **params)


def get_zn_multitb_0141(strt_date=19900101, end_date=None, area_name=None, prov_name=None,
                        city_name=None, cnty_name=None, corp_type=None, jl_craft=None, cap_chg=None,
                        prd_stat=None, buld_stat=None, cols=None):
    """
    获取煤焦产能企业统计

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['desn_cap', 'chmb_high', 'jl_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'corp_code', 'area_name', 'prov_name', 'city_name', 'cnty_name', 'corp_type',
            'jl_craft', 'desn_cap', 'chmb_high', 'jl_num', 'cap_chg', 'prd_stat', 'buld_stat', 'exec_year', 'exec_mth',
            'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(prov_name, list):
        prov_name = ','.join(prov_name)

    if isinstance(city_name, list):
        city_name = ','.join(city_name)

    if isinstance(cnty_name, list):
        cnty_name = ','.join(cnty_name)

    if isinstance(corp_type, list):
        corp_type = ','.join(corp_type)

    if isinstance(jl_craft, list):
        jl_craft = ','.join(jl_craft)

    if isinstance(cap_chg, list):
        cap_chg = ','.join(cap_chg)

    if isinstance(prd_stat, list):
        prd_stat = ','.join(prd_stat)

    if isinstance(buld_stat, list):
        buld_stat = ','.join(buld_stat)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "prov_name": prov_name,
        "city_name": city_name,
        "cnty_name": cnty_name,
        "corp_type": corp_type,
        "jl_craft": jl_craft,
        "cap_chg": cap_chg,
        "prd_stat": prd_stat,
        "buld_stat": buld_stat,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0141", **params)


def get_zn_multitb_0142(strt_date=19900101, end_date=None, area_name=None, cols=None):
    """
    获取铁矿石高炉开工率（按区域）

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['bf_oper_rati', 'cap_util_rati', 'act_prd_out_ad', 'oh_prd_out_ad', 'lmt_prd_out_ad', 'prof_rati',
                 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'area_name', 'bf_oper_rati', 'cap_util_rati', 'act_prd_out_ad', 'oh_prd_out_ad',
            'lmt_prd_out_ad', 'prof_rati', 'is_delt'
        ]
    
    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0142", **params)


def get_zn_multitb_0143(strt_date=19900101, end_date=None, prov_name=None, prd_scal=None, cols=None):
    """
    获取铁矿石高炉开工率（按规模）

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['bf_oper_rati', 'cap_util_rati', 'act_prd_out_ad', 'oh_prd_out_ad', 'lmt_prd_out_ad', 'prof_rati',
                 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'prov_name', 'prd_scal', 'bf_oper_rati', 'cap_util_rati', 'act_prd_out_ad',
            'oh_prd_out_ad', 'lmt_prd_out_ad', 'prof_rati', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(prov_name, list):
        prov_name = ','.join(prov_name)

    if isinstance(prd_scal, list):
        prd_scal = ','.join(prd_scal)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "prov_name": prov_name,
        "prd_scal": prd_scal,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0143", **params)


def get_zn_multitb_0144(strt_date=19900101, end_date=None, area_name=None, calb_type=None, cols=None):
    """
    获取铁矿石港口库存（粗粉）

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'prd_type', 'samp_name', 'area_name', 'calb_type', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(calb_type, list):
        calb_type = ','.join(calb_type)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "calb_type": calb_type,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0144", **params)


def get_zn_multitb_0145(strt_date=19900101, end_date=None, area_name=None, calb_type=None, cols=None):
    """
    获取铁矿石港口库存（块矿）

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'prd_type', 'samp_name', 'area_name', 'calb_type', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(calb_type, list):
        calb_type = ','.join(calb_type)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "calb_type": calb_type,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0145", **params)


def get_zn_multitb_0146(strt_date=19900101, end_date=None, area_name=None, var_type=None,
                        var_own=None, cols=None):
    """
    获取铁矿石港口库存（主流品种）

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'area_name', 'var_type', 'var_own', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(var_type, list):
        var_type = ','.join(var_type)

    if isinstance(var_own, list):
        var_own = ','.join(var_own)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "var_type": var_type,
        "var_own": var_own,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0146", **params)


def get_zn_multitb_0147(strt_date=19900101, end_date=None, area_name=None, calb_type=None, cols=None):
    """
    获取铁矿石港口库存（货主性质）

    """

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'area_name', 'calb_type', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(calb_type, list):
        calb_type = ','.join(calb_type)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "calb_type": calb_type,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0147", **params)


def get_zn_multitb_0148(strt_date=19900101, end_date=None, area_name=None, calb_type=None, cols=None):
    """
    获取铁矿石港口库存（球团）

    """
    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'area_name', 'calb_type', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(calb_type, list):
        calb_type = ','.join(calb_type)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "calb_type": calb_type,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0148", **params)


def get_zn_multitb_0149(strt_date=19900101, end_date=None, area_name=None, calb_type=None, cols=None):
    """
    获取铁矿石港口库存（精粉）

    """
    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'area_name', 'calb_type', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(calb_type, list):
        calb_type = ','.join(calb_type)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "calb_type": calb_type,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0149", **params)


def get_zn_multitb_0150(strt_date=19900101, end_date=None, area_name=None, prd_clas=None, var_name=None,
                        cols=None):
    """
    获取铁矿石港口库存（品位）

    """
    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_num', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'area_name', 'prd_clas', 'var_name', 'inv_num', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)
    cols = ','.join(cols)

    if isinstance(area_name, list):
        area_name = ','.join(area_name)

    if isinstance(prd_clas, list):
        prd_clas = ','.join(prd_clas)

    if isinstance(var_name, list):
        var_name = ','.join(var_name)

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "prd_clas": prd_clas,
        "var_name": var_name,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0150", **params)


def get_zn_multitb_0151(strt_date=19900101, end_date=None, area_name=None, cols=None):
    """
    获取铁矿石港口库存（总览）

    """
    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    int_param = ['inv_tot', 'inv_fo', 'inv_lo', 'inv_pllt', 'inv_pp', 'inv_mgaf', 'inv_mgbf', 'inv_mzaf', 'inv_mqk',
                 'inv_mqt', 'mgaf_rati', 'mgbf_rati', 'mzaf_rati', 'mqt_rati', 'is_delt']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'samp_name', 'area_name', 'inv_tot', 'inv_fo', 'inv_lo', 'inv_pllt', 'inv_pp',
            'inv_mgaf', 'inv_mgbf', 'inv_mzaf', 'inv_mqk', 'inv_mqt', 'mgaf_rati', 'mgbf_rati', 'mzaf_rati', 'mqt_rati',
            'is_delt'
        ]

    params = {
        "strt_date": strt_date,
        "end_date": end_date,
        "area_name": area_name,
        "cols": cols,

        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("cd/get_zn_multitb_0151", **params)


