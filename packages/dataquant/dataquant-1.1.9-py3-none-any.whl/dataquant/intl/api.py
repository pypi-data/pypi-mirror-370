# -*- coding: UTF-8 -*-
import warnings
import numpy as np
import pandas as pd

from dataquant.apis.base import get_data
from dataquant.utils.convert import convert_fields
from dataquant.utils.datetime_func import get_current_date

__all__ = [
    "get_product_info",
    "get_product_value"
]


def get_product_info(symbol=None, product=None, proxy_status=None, alive_status=None, admin_name=None, cols=None, rslt_type=0):
    """
    获取内部产品基本信息

    """

    int_param = \
        [
            'risk_level', 'investment_type', 'proxy_status', 'alive_status', 'product', 'issue_start_date','issue_end_date',
            'start_date', 'end_date', 'return_type', 'return_mode', 'trade_product_type', 'untrade_product_type', 'private_fund_type',
            'public_fund_type'
        ]
    float_param = \
        [
            'issue_price', 'par_value', 'alive_term', 'scale', 'total_shares'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    # else:
    #     cols = [
    #         'symbol'
    #         ,'chinese_name'
    #         ,'chinese_abbr_name'
    #         ,'risk_level'
    #         ,'investment_type'
    #         ,'proxy_status'
    #         ,'alive_status'
    #         ,'product'
    #         ,'admin_name'
    #         ,'admin_abbr_name'
    #         ,'issue_start_date'
    #         ,'issue_end_date'
    #         ,'issue_price'
    #         ,'par_value'
    #         ,'start_date'
    #         ,'end_date'
    #         ,'alive_term'
    #         ,'return_type'
    #         ,'return_mode'
    #         ,'trade_product_type'
    #         ,'untrade_product_type'
    #         ,'private_fund_type'
    #         ,'public_fund_type'
    #         ,'scale'
    #         ,'total_shares'
    #     ]

    # if symbol:
    if isinstance(symbol, str):
        symbol = symbol.split(',')

    params = {
        "symbol": symbol,
        "product": product,
        "proxy_status": proxy_status,
        "alive_status": alive_status,
        "admin_name": admin_name,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("intl/get_product_info", **params)

    # else:
    #     warnings.warn("函数[get_nav]的参数(fund_code)为必填项")
    #     return None


def get_product_value(symbol=None, start_date=None, end_date=None, cols=None, rslt_type=0):
    """
    获取内部产品净值

    """

    int_param = \
        [
            'date'
        ]
    float_param = \
        [
            'unit_value', 'total_value', 'daily_return', 'weekly_return', 'monthly_return', 'quarter_return',
            'semiannual_return', 'annual_return', 'current_year_return', 'cumulative_return'

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    # else:
    #     cols = [
    #         'symbol', 'date',
    #         'unit_value', 'total_value', 'daily_return', 'weekly_return', 'monthly_return', 'quarter_return',
    #         'semiannual_return', 'annual_return', 'current_year_return', 'cumulative_return'
    #     ]

    if symbol is None or start_date is None \
            or end_date is None:
        warnings.warn("函数[intl/get_product_value]的参数"
                      "(symbol, start_date, end_date)"
                      "不能为空")
        return None

    if isinstance(symbol, str):
        symbol = symbol.split(',')

    params = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("intl/get_product_value", **params)






