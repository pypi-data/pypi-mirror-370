# -*- coding: UTF-8 -*-
import warnings
import numpy as np
import pandas as pd
from itertools import product

from dataquant.apis.base import get_data
from dataquant.utils.convert import convert_fields
from dataquant.utils.datetime_func import get_current_date

__all__ = [
    "get_level_info",
    "get_index_info",
    "get_index_data"
]


def get_level_info(lvl_code=None, lvl_orde=None, lvl_name=None, cols=None, rslt_type=0):
    """
    获取分类信息

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
            'firs_lvl_code', 'firs_lvl_name', 'secd_lvl_code', 'secd_lvl_name',
            'thir_lvl_code', 'thir_lvl_name', 'four_lvl_code', 'four_lvl_name'
        ]

    if lvl_code is None and lvl_orde is None and lvl_name is None:
        warnings.warn("函数[get_level_info]的参数"
                      "(lvl_code, lvl_orde, lvl_name)"
                      "不能全部为空")
        return None

    if (lvl_orde is not None and lvl_name is None) \
            or (lvl_orde is None and lvl_name is not None):
        warnings.warn("函数[get_level_info]的参数"
                      "(lvl_orde, lvl_name)"
                      "必须同时输入")
        return None

    params = {
        "lvl_code": lvl_code,
        "lvl_orde": lvl_orde,
        "lvl_name": lvl_name,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("ic/get_level_info", **params)


def get_index_info(indx_code_list=None, indx_abbr_list=None, lvl_code=None,
                   publ_freq=None, src_name=None, cols=None, rslt_type=0):
    """
    获取产业链基本信息

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
            'src_name', 'meas_name', 'calb_name', 'strt_date', 'end_date', 'indx_stat', 'unit_name',
            'firs_lvl_code', 'firs_lvl_name', 'secd_lvl_code', 'secd_lvl_name',
            'thir_lvl_code', 'thir_lvl_name', 'four_lvl_code', 'four_lvl_name'
        ]

    params = {
        "indx_code_list": indx_code_list,
        "indx_abbr_list": indx_abbr_list,
        "lvl_code": lvl_code,
        "publ_freq": publ_freq,
        "src_name": src_name,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("ic/get_index_info", **params)


def get_index_data(indx_code_list, strt_date, end_date=None, date_type=1,
                   fill_mode=3, is_delt=0, cols=None, rslt_type=0):
    """
    获取所有指标

    """

    int_param = \
        [
            'is_delt'
        ]
    float_param = \
        [
            'data_val'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_code', 'data_date', 'data_val', 'pbsh_time', 'is_delt'
        ]

    fix_cols = ['indx_code', 'data_date', 'pbsh_time']
    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)

    if end_date is None:
        end_date = get_current_date()

    if indx_code_list and strt_date:
        params = {
            "indx_code_list": indx_code_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "date_type": date_type,
            "fill_mode": fill_mode,
            "is_delt": is_delt,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        result = get_data("ic/get_index_data", **params)
        if result is None:
            return

        return result

    else:
        warnings.warn("函数[get_index_data]的参数(indx_code_list, strt_date, end_date)为必填项")
        return None
