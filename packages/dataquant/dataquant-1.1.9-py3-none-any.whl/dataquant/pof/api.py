# -*- coding: UTF-8 -*-
import warnings
import numpy as np
import pandas as pd

from dataquant.apis.base import get_data
from dataquant.utils.convert import convert_fields
from dataquant.utils.datetime_func import get_current_date

__all__ = [
    "get_nav",
    "get_fund_info",
    "get_all_funds",
    "get_fund_fee",
    "get_fund_attributes",
    "get_company_info",
    "get_all_companies",
    "get_company_shareholder",
    "get_company_honor",
    "get_personnel_honor",
    "get_fund_honor",
    "get_personnel_info",
    "get_all_personnel",
    "get_personnel_company_map",
    "get_assets_allocation",
    "get_industry_sw",
    "get_industry_zz",
    "get_industry_zx",
    "get_allocation_jc",
    "get_bond_attribution",
    "get_futures_assets_allocation",
    "get_performance",
    "get_performance_topn",
    "get_strategy_tree",
    "get_company_fund_map",
    "get_manager_fund_map",
    "get_personnel_company_map",
    "get_personnel_position",
    "get_strategy_fund_map",
    "get_benchmark_fund_map",
    "get_index_confidence",
    "get_index_info",
    "get_dividends",
    "get_fund_rank",
    "get_adjusted_risk_index",
    "get_capture_return",
    "get_fund_portfolio",
    "get_assets_position",
    "get_relative_value_allocation",
    "get_index_value"
]


def get_nav(fund_code=None, fund_code_list=None, strt_date='19900101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金净值

    """

    int_param = \
        [
            'ishigh_or_low', 'nav_src'
        ]
    float_param = \
        [
            'unit_nv', 'bons_reiv_unit_nv',
            'bons_no_reiv_unit_nv', 'tohigh_nav_ratio'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_date', 'unit_nv', 'bons_reiv_unit_nv',
            'bons_no_reiv_unit_nv', 'ishigh_or_low', 'tohigh_nav_ratio', 'nav_src'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_nav", **params)
    elif fund_code_list:
        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_nav", **params)

    else:
        warnings.warn("函数[get_nav]的参数(fund_code)为必填项")
        return None


def get_fund_info(fund_code_list=None, fund_cn_abbr_list=None, fund_cn_fn_list=None,
                  kord_num_list=None, cols=None, rslt_type=0):
    """
    获取基金基本信息

    """

    int_param = \
        [
            'fund_type', 'fund_stat', 'firs_stra', 'secd_stra',
            'thir_stra', 'durt'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'fund_cn_abbr', 'fund_cn_fn', 'fund_type', 'setp_date',
            'kord_date', 'kord_num', 'corp_id', 'corp_cn_fn', 'corp_cn_abbr',
            'fund_stat', 'fund_mngr', 'firs_stra', 'secd_stra', 'thir_stra',
            'lock_pd', 'clos_pd', 'open_pd', 'pri_basi_id', 'durt', 'ivsm_scop',
            'fund_stra_desc', 'cstdins_id', 'brok_id', 'brok_futr_id'
        ]

    if fund_code_list is None and fund_cn_abbr_list is None \
            and fund_cn_fn_list is None and kord_num_list is None:
        warnings.warn("函数[get_fund_info]的参数"
                      "(fund_code_list, fund_cn_abbr_list, fund_cn_fn_list, kord_num_list)"
                      "不能全部为空")
        return None

    if isinstance(fund_code_list, str):
        fund_code_list = fund_code_list.split(',')

    if isinstance(fund_cn_abbr_list, str):
        fund_cn_abbr_list = fund_cn_abbr_list.split(',')

    if isinstance(fund_cn_fn_list, str):
        fund_cn_fn_list = fund_cn_fn_list.split(',')

    if isinstance(kord_num_list, str):
        kord_num_list = kord_num_list.split(',')

    params = {
        "fund_code_list": fund_code_list,
        "fund_cn_abbr_list": fund_cn_abbr_list,
        "fund_cn_fn_list": fund_cn_fn_list,
        "kord_num_list": kord_num_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_fund_info", **params)


def get_all_funds(qury_date, fund_stat=2, cols=None, rslt_type=0):
    """
    获取所有基金

    """

    int_param = \
        [
            'fund_stat', 'perf_basi'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'fund_cn_abbr', 'fund_cn_fn', 'corp_cn_abbr', 'fund_mngr',
            'perf_strt_date', 'clr_date', 'fund_stat', 'pri_basi_id', 'perf_basi'
        ]

    if qury_date:
        params = {
            "qury_date": qury_date,
            "fund_stat": fund_stat,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_all_funds", **params)
    else:
        warnings.warn("函数[get_all_funds]的参数(qury_date)为必填项")
        return None


def get_fund_fee(fund_code_list, cols=None, rslt_type=0):
    """
    获取基金费率

    """

    int_param = \
        [
        ]
    float_param = \
        [
            'min_scrp_shr', 'appd_scrp_shr', 'max_scrp_fee', 'max_redp_fee',
            'purs_fee', 'ivsm_advr_fee', 'mngr_aep', 'cstd_fee', 'perf_remu',
            'warl', 'stopl', 'oper_serv_fee'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'min_scrp_shr', 'appd_scrp_shr', 'max_scrp_fee',
            'scrp_fee_expl', 'max_redp_fee', 'redp_fee_expl', 'expl_ahed_app_time',
            'aep_accr_pd', 'purs_fee', 'purs_fee_expl', 'ivsm_advr_fee', 'mngr_aep',
            'cstd_fee', 'perf_remu', 'perf_remu_expl', 'accr_mode', 'accr_freq',
            'accr_day_type', 'warl', 'stopl', 'stopl_expl', 'oper_serv_fee'
        ]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_fund_fee", **params)
    else:
        warnings.warn("函数[get_fund_fee]的参数(fund_code_list)为必填项")
        return None


def get_fund_attributes(fund_code_list, cols=None, rslt_type=0):
    """
    获取基金属性

    """

    int_param = \
        [
            'is_mstfd', 'is_umbrl', 'tot_flag', 'is_shr', 'fee_clas_a', 'fee_clas_oth'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'is_mstfd', 'is_umbrl', 'tot_flag', 'is_shr', 'fee_clas_a', 'fee_clas_oth'
        ]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_fund_attributes", **params)
    else:
        warnings.warn("函数[get_fund_attributes]的参数(fund_code_list)为必填项")
        return None


def get_company_info(corp_id_list=None, corp_cn_abbr_list=None, corp_cn_fn_list=None, cols=None, rslt_type=0):
    """
    获取基金相关公司信息

    """

    int_param = \
        [
            'corp_type', 'reg_stat', 'mem_type', 'ins_clas_code', 'corp_ast_scal'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'corp_id', 'corp_cn_fn', 'corp_cn_abbr', 'corp_type', 'setp_date',
            'unif_soci_cred_code', 'city', 'prov', 'cntr', 'reg_city', 'reg_prov',
            'reg_cntr', 'reg_stat', 'reg_date', 'mem_type', 'ins_clas_code', 'corp_ast_scal'
        ]

    if corp_id_list is None and corp_cn_abbr_list is None and corp_cn_fn_list is None:
        warnings.warn("函数[get_company_info]的参数"
                      "(corp_id_list, corp_cn_abbr_list, corp_cn_fn_list)"
                      "不能全部为空")
        return None

    if isinstance(corp_id_list, str):
        corp_id_list = corp_id_list.split(',')

    if isinstance(corp_cn_abbr_list, str):
        corp_cn_abbr_list = corp_cn_abbr_list.split(',')

    if isinstance(corp_cn_fn_list, str):
        corp_cn_fn_list = corp_cn_fn_list.split(',')

    params = {
        "corp_id_list": corp_id_list,
        "corp_cn_abbr_list": corp_cn_abbr_list,
        "corp_cn_fn_list": corp_cn_fn_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_company_info", **params)


def get_all_companies(city, reg_stat=2, corp_ast_scal=None, corp_type=None, cols=None, rslt_type=0):
    """
    获取所有公司

    """

    int_param = \
        [
            'corp_type', 'reg_stat', 'mem_type', 'ins_clas_code', 'corp_ast_scal'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'corp_id', 'corp_cn_fn', 'corp_cn_abbr', 'corp_type',
            'setp_date', 'unif_soci_cred_code', 'city', 'prov', 'cntr',
            'reg_city', 'reg_prov', 'reg_cntr', 'reg_stat', 'reg_date',
            'mem_type', 'ins_clas_code', 'corp_ast_scal'
        ]

    if city:
        params = {
            "city": city,
            "reg_stat": reg_stat,
            "corp_ast_scal": corp_ast_scal,
            "corp_type": corp_type,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_all_companies", **params)
    else:
        warnings.warn("函数[get_all_companies]的参数(city)为必填项")
        return None


def get_company_shareholder(corp_id_list, is_last=1, cols=None, rslt_type=0):
    """
    获取公司股权结构信息

    """

    int_param = \
        [
            'crrc', 'shah_type', 'data_src', 'is_last'
        ]
    float_param = \
        [
            'hold_rati', 'sscr_amt', 'paid_amt'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'corp_id', 'shah_id', 'shah_name', 'hold_rati', 'sscr_amt',
            'sscr_date', 'paid_amt', 'paid_date', 'crrc', 'shah_type',
            'inpt_date', 'data_src', 'is_last'
        ]

    if corp_id_list:

        if isinstance(corp_id_list, str):
            corp_id_list = corp_id_list.split(',')

        params = {
            "corp_id_list": corp_id_list,
            "is_last": is_last,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_company_shareholder", **params)
    else:
        warnings.warn("函数[get_company_shareholder]的参数(corp_id_list)为必填项")
        return None


def get_company_honor(corp_id_list, cols=None, rslt_type=0):
    """
    获取公司荣誉信息

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
            'corp_id', 'corp_cn_fn', 'earn_year', 'prze_name', 'prze_sitm', 'org_name'
        ]

    if corp_id_list:

        if isinstance(corp_id_list, str):
            corp_id_list = corp_id_list.split(',')

        params = {
            "corp_id_list": corp_id_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_company_honor", **params)
    else:
        warnings.warn("函数[get_company_honor]的参数(corp_id_list)为必填项")
        return None


def get_personnel_honor(prsn_id_list, cols=None, rslt_type=0):
    """
    获取公司历史管理规模

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
            'prsn_id', 'prsn_name', 'earn_date', 'prze_name', 'prze_sitm', 'org_name'
        ]

    if prsn_id_list:

        if isinstance(prsn_id_list, str):
            prsn_id_list = prsn_id_list.split(',')

        params = {
            "prsn_id_list": prsn_id_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_personnel_honor", **params)
    else:
        warnings.warn("函数[get_personnel_honor]的参数(prsn_id_list)为必填项")
        return None


def get_fund_honor(fund_code_list, cols=None, rslt_type=0):
    """
    获取基金荣誉信息

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
            'fund_code', 'fund_name', 'earn_year', 'prze_name', 'prze_sitm', 'org_name'
        ]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_fund_honor", **params)
    else:
        warnings.warn("函数[get_fund_honor]的参数(fund_code_list)为必填项")
        return None


def get_personnel_info(prsn_id_list=None, prsn_name_list=None, cols=None, rslt_type=0):
    """
    获取人员信息

    """

    int_param = \
        [
            'occu_bkgd', 'occu_year', 'sex', 'edu', 'is_qlfy'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'prsn_id', 'prsn_name', 'occu_bkgd', 'occu_strt_year',
            'occu_year', 'sex', 'edu', 'intr', 'qlfy_mode', 'is_qlfy',
            'prze_name'
        ]

    if prsn_id_list is None and prsn_name_list is None:
        warnings.warn("函数[get_personnel_info]的参数"
                      "(prsn_id_list, prsn_name_list)"
                      "不能全部为空")
        return None

    if isinstance(prsn_id_list, str):
        prsn_id_list = prsn_id_list.split(',')

    if isinstance(prsn_name_list, str):
        prsn_name_list = prsn_name_list.split(',')

    params = {
        "prsn_id_list": prsn_id_list,
        "prsn_name_list": prsn_name_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_personnel_info", **params)


def get_all_personnel(edu=5, occu_bkgd=13, is_qlfy=1, cols=None, rslt_type=0):
    """
    获取所有人员

    """

    int_param = \
        [
            'occu_bkgd', 'occu_year', 'sex', 'edu', 'is_qlfy'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'prsn_id', 'prsn_name', 'occu_bkgd', 'occu_strt_year',
            'occu_year', 'sex', 'edu', 'intr', 'qlfy_mode', 'is_qlfy',
            'prze_name'
        ]

    params = {
        "edu": edu,
        "occu_bkgd": occu_bkgd,
        "is_qlfy": is_qlfy,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_all_personnel", **params)


def get_personnel_company_map(prsn_id_list=None, corp_id_list=None, cols=None, rslt_type=0):
    """
    获取基金人员与公司映射

    """

    int_param = \
        [
            'corp_onum', 'prsn_onum', 'is_core',
            'is_incl', 'is_leav', 'is_exec', 'is_legp'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'prsn_id', 'corp_id', 'corp_onum', 'prsn_onum', 'is_core',
            'is_incl', 'is_leav', 'is_exec', 'is_legp', 'strt_date', 'end_date'
        ]

    if isinstance(prsn_id_list, str):
        prsn_id_list = prsn_id_list.split(',')

    if isinstance(corp_id_list, str):
        corp_id_list = corp_id_list.split(',')

    params = {
        "prsn_id_list": prsn_id_list,
        "corp_id_list": corp_id_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_personnel_company_map", **params)


def get_assets_allocation(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金大类资产配置

    """

    int_param = \
        [
            'data_type', 'max_ctb'
        ]
    float_param = \
        [
            'alpha', 'csi300_agil', 'csi300_ctb',
            'cnbd_agil', 'cnbd_ctb', 'megr_futr_agil', 'megr_futr_ctb',
            'cash_agil', 'cash_ctb', 'crrc_perf_beta', 'crrc_perf_ctb',
            'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'data_type', 'alpha', 'csi300_agil',
            'csi300_ctb', 'cnbd_agil', 'cnbd_ctb', 'megr_futr_agil', 'megr_futr_ctb',
            'cash_agil', 'cash_ctb', 'crrc_perf_beta', 'crrc_perf_ctb',
            'max_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_assets_allocation", **params)
    else:
        warnings.warn("函数[get_assets_allocation]的参数(fund_code)为必填项")
        return None


def get_industry_sw(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金申万行业配置

    """

    int_param = \
        [
            'data_type', 'max_ctb'
        ]
    float_param = \
        [
            'alpha',
            'sw_110_agil', 'sw_110_ctb', 'sw_210_agil', 'sw_210_ctb',
            'sw_220_agil', 'sw_220_ctb', 'sw_230_agil', 'sw_230_ctb',
            'sw_240_agil', 'sw_240_ctb', 'sw_270_beta', 'sw_270_ctb',
            'sw_280_beta', 'sw_280_ctb', 'sw_330_beta', 'sw_330_ctb',
            'sw_340_beta', 'sw_340_ctb', 'sw_350_beta', 'sw_350_ctb',
            'sw_360_beta', 'sw_360_ctb', 'sw_370_beta', 'sw_370_ctb',
            'sw_410_beta', 'sw_410_ctb', 'sw_420_beta', 'sw_420_ctb',
            'sw_430_beta', 'sw_430_ctb', 'sw_450_beta', 'sw_450_ctb',
            'sw_460_beta', 'sw_460_ctb', 'sw_480_beta', 'sw_480_ctb',
            'sw_490_beta', 'sw_490_ctb', 'sw_510_beta', 'sw_510_ctb',
            'sw_610_beta', 'sw_610_ctb', 'sw_620_beta', 'sw_620_ctb',
            'sw_630_beta', 'sw_630_ctb', 'sw_640_beta', 'sw_640_ctb',
            'sw_650_beta', 'sw_650_ctb', 'sw_710_beta', 'sw_710_ctb',
            'sw_720_beta', 'sw_720_ctb', 'sw_730_beta', 'sw_730_ctb',
            'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'data_type', 'alpha',
            'sw_110_agil', 'sw_110_ctb', 'sw_210_agil', 'sw_210_ctb',
            'sw_220_agil', 'sw_220_ctb', 'sw_230_agil', 'sw_230_ctb',
            'sw_240_agil', 'sw_240_ctb', 'sw_270_beta', 'sw_270_ctb',
            'sw_280_beta', 'sw_280_ctb', 'sw_330_beta', 'sw_330_ctb',
            'sw_340_beta', 'sw_340_ctb', 'sw_350_beta', 'sw_350_ctb',
            'sw_360_beta', 'sw_360_ctb', 'sw_370_beta', 'sw_370_ctb',
            'sw_410_beta', 'sw_410_ctb', 'sw_420_beta', 'sw_420_ctb',
            'sw_430_beta', 'sw_430_ctb', 'sw_450_beta', 'sw_450_ctb',
            'sw_460_beta', 'sw_460_ctb', 'sw_480_beta', 'sw_480_ctb',
            'sw_490_beta', 'sw_490_ctb', 'sw_510_beta', 'sw_510_ctb',
            'sw_610_beta', 'sw_610_ctb', 'sw_620_beta', 'sw_620_ctb',
            'sw_630_beta', 'sw_630_ctb', 'sw_640_beta', 'sw_640_ctb',
            'sw_650_beta', 'sw_650_ctb', 'sw_710_beta', 'sw_710_ctb',
            'sw_720_beta', 'sw_720_ctb', 'sw_730_beta', 'sw_730_ctb',
            'max_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_industry_sw", **params)
    else:
        warnings.warn("函数[get_industry_sw]的参数(fund_code)为必填项")
        return None


def get_industry_zz(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金中证行业配置

    """

    int_param = \
        [
            'data_type', 'max_ctb'
        ]
    float_param = \
        [
            'alpha', 'zz_00_beta',
            'zz_00_ctb', 'zz_01_beta', 'zz_01_ctb', 'zz_02_beta', 'zz_02_ctb',
            'zz_03_beta', 'zz_03_ctb', 'zz_04_beta', 'zz_04_ctb', 'zz_05_beta',
            'zz_05_ctb', 'zz_06_beta', 'zz_06_ctb', 'zz_07_beta', 'zz_07_ctb',
            'zz_08_beta', 'zz_08_ctb', 'zz_09_beta', 'zz_09_ctb ', 'crrc_perf_beta',
            'crrc_perf_ctb', 'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'data_type', 'alpha', 'zz_00_beta',
            'zz_00_ctb', 'zz_01_beta', 'zz_01_ctb', 'zz_02_beta', 'zz_02_ctb',
            'zz_03_beta', 'zz_03_ctb', 'zz_04_beta', 'zz_04_ctb', 'zz_05_beta',
            'zz_05_ctb', 'zz_06_beta', 'zz_06_ctb', 'zz_07_beta', 'zz_07_ctb',
            'zz_08_beta', 'zz_08_ctb', 'zz_09_beta', 'zz_09_ctb', 'crrc_perf_beta',
            'crrc_perf_ctb', 'max_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_industry_zz", **params)
    else:
        warnings.warn("函数[get_industry_zz]的参数(fund_code)为必填项")
        return None


def get_industry_zx(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金中信行业配置

    """

    int_param = \
        [
            'data_type', 'max_ctb'
        ]
    float_param = \
        [
            'alpha',
            'citc_finl_agil', 'citc_finl_ctb', 'citc_pd_agil',
            'citc_pd_ctb', 'citc_cons_agil', 'citc_cons_ctb',
            'citc_grow_agil', 'citc_grow_ctb', 'citc_stb_agil',
            'citc_stb_ctb', 'crrc_perf_beta', 'crrc_perf_ctb',
            'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'data_type', 'alpha',
            'citc_finl_agil', 'citc_finl_ctb', 'citc_pd_agil',
            'citc_pd_ctb', 'citc_cons_agil', 'citc_cons_ctb',
            'citc_grow_agil', 'citc_grow_ctb', 'citc_stb_agil',
            'citc_stb_ctb', 'crrc_perf_beta', 'crrc_perf_ctb',
            'max_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_industry_zx", **params)
    else:
        warnings.warn("函数[get_industry_zx]的参数(fund_code)为必填项")
        return None


def get_allocation_jc(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金巨潮行业配置

    """

    int_param = \
        [
            'data_type', 'max_ctb'
        ]
    float_param = \
        [
            'alpha', 'makt_grow_agil',
            'makt_grow_ctb', 'makt_val_agil', 'makt_val_ctb', 'midg_grow_agil',
            'midg_grow_ctb', 'midg_val_agil', 'midg_val_ctb', 'smalp_grow_agil',
            'smalp_grow_ctb', 'smalp_val_agil', 'smalp_val_ctb', 'crrc_perf_beta',
            'crrc_perf_ctb', 'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'data_type', 'alpha', 'makt_grow_agil',
            'makt_grow_ctb', 'makt_val_agil', 'makt_val_ctb', 'midg_grow_agil',
            'midg_grow_ctb', 'midg_val_agil', 'midg_val_ctb', 'smalp_grow_agil',
            'smalp_grow_ctb', 'smalp_val_agil', 'smalp_val_ctb', 'crrc_perf_beta',
            'crrc_perf_ctb', 'max_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_allocation_jc", **params)
    else:
        warnings.warn("函数[get_allocation_jc]的参数(fund_code)为必填项")
        return None


def get_bond_attribution(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金债券因子暴露

    """

    int_param = \
        [
        ]
    float_param = \
        [
            'alpha',
            'durt_mag_perf_beta', 'durt_mag_perf_ctb', 'maty_stru_perf_beta',
            'maty_stru_perf_ctb', 'max_maty_perf_beta', 'max_maty_perf_ctb',
            'cbnd_perf_beta', 'cbnd_perf_ctb', 'max_payf_cbnd_perf_beta',
            'max_payf_cbnd_perf_ctb', 'cvtb_perf_beta', 'cvtb_perf_ctb',
            'crrc_perf_beta', 'crrc_perf_ctb', 'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'alpha',
            'durt_mag_perf_beta', 'durt_mag_perf_ctb', 'maty_stru_perf_beta',
            'maty_stru_perf_ctb', 'max_maty_perf_beta', 'max_maty_perf_ctb',
            'cbnd_perf_beta', 'cbnd_perf_ctb', 'max_payf_cbnd_perf_beta',
            'max_payf_cbnd_perf_ctb', 'cvtb_perf_beta', 'cvtb_perf_ctb',
            'crrc_perf_beta', 'crrc_perf_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_bond_attribution", **params)
    else:
        warnings.warn("函数[get_bond_attribution]的参数(fund_code)为必填项")
        return None


def get_futures_assets_allocation(fund_code, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金期货配置

    """

    int_param = \
        [
            'data_type', 'max_ctb'
        ]
    float_param = \
        [
            'alpha',
            'csi300_agil', 'csi300_ctb', 'agri_pd_agil', 'agri_pd_ctb',
            'idst_futr_indx_agil', 'idst_futr_indx_ctb', 'crrc_perf_beta',
            'crrc_perf_ctb', 'rsdu', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'nv_pbsh_date', 'data_type', 'alpha',
            'csi300_agil', 'csi300_ctb', 'agri_pd_agil', 'agri_pd_ctb',
            'idst_futr_indx_agil', 'idst_futr_indx_ctb', 'crrc_perf_beta',
            'crrc_perf_ctb', 'max_ctb', 'rsdu', 'fitgdn'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_futures_assets_allocation", **params)
    else:
        warnings.warn("函数[get_futures_assets_allocation]的参数(fund_code)为必填项")
        return None


def get_performance(fund_code=None, fund_code_list=None, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金统计收益

    """

    int_param = \
        [

        ]
    float_param = \
        [
            'aggr_nav',
            'ror_1m', 'ror_1m_basi', 'ror_3m', 'ror_3m_basi', 'ror_6m',
            'ror_6m_basi', 'ror_1y', 'ror_1y_basi', 'ror_2y',
            'ror_2y_basi', 'aror_2y', 'aror_2y_basi', 'ror_3y', 'ror_3y_basi',
            'ror_3y_a', 'aror_3y_basi', 'ror_ytd', 'ror_ytd_basi', 'ror_incep',
            'ror_incep_basi', 'aror_incep', 'aror_incep_basi'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'aggr_nav_date', 'end_date', 'aggr_nav',
            'ror_1m', 'ror_1m_basi', 'ror_3m', 'ror_3m_basi', 'ror_6m',
            'ror_6m_basi', 'ror_1y', 'ror_1y_basi', 'ror_2y',
            'ror_2y_basi', 'aror_2y', 'aror_2y_basi', 'ror_3y', 'ror_3y_basi',
            'ror_3y_a', 'aror_3y_basi', 'ror_ytd', 'ror_ytd_basi', 'ror_incep',
            'ror_incep_basi', 'aror_incep', 'aror_incep_basi'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code:
        params = {
            "fund_code": fund_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_performance", **params)
    elif fund_code_list:
        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_performance", **params)
    else:
        warnings.warn("函数[get_performance]的参数(fund_code或fund_code_list)不能全部为空")
        return None


def get_performance_topn(firs_stra=1, yld_type=1, topN=10, cols=None, rslt_type=0):
    """
    获取私募基金收益排行榜

    """

    int_param = \
        [
            'firs_stra', 'secd_stra', 'thir_stra'
        ]
    float_param = \
        [
            'ror_1m', 'ror_3m',
            'ror_6m', 'ror_1y', 'ror_2y', 'ror_3y', 'ror_ytd'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'end_date', 'fund_cn_abbr', 'fund_mngr',
            'firs_stra', 'secd_stra', 'thir_stra', 'ror_1m', 'ror_3m',
            'ror_6m', 'ror_1y', 'ror_2y', 'ror_3y', 'ror_ytd'
        ]

    params = {
        "firs_stra": firs_stra,
        "yld_type": yld_type,
        "topN": topN,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_performance_topn", **params)


def get_strategy_tree(stra_code=1, cols=None, rslt_type=0):
    """
    获取私募基金收益排行榜

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
            'firs_stra', 'firs_stra_name', 'secd_stra', 'secd_stra_name', 'thir_stra', 'thir_stra_name'
        ]

    if stra_code < 0:
        warnings.warn("函数[stra_code]的参数"
                      "(stra_code)"
                      "必须大于等于1")
        return None

    params = {
        "stra_code": stra_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_strategy_tree", **params)


def get_company_fund_map(fund_code_list=None, corp_id_list=None, cols=None, rslt_type=0):
    """
    获取基金与基金公司映射关系

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
            'fund_code', 'fund_cn_abbr', 'fund_cn_fn', 'corp_id', 'setp_date'
        ]

    if fund_code_list is None and corp_id_list is None:
        warnings.warn("函数[get_company_fund_map]的参数"
                      "(fund_code_list, corp_id_list)"
                      "不能全部为空")
        return None

    if isinstance(fund_code_list, str):
        fund_code_list = fund_code_list.split(',')

    if isinstance(corp_id_list, str):
        corp_id_list = corp_id_list.split(',')

    params = {
        "fund_code_list": fund_code_list,
        "corp_id_list": corp_id_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_company_fund_map", **params)


def get_manager_fund_map(fund_code_list=None, fund_mngr_id_list=None, cols=None, rslt_type=0):
    """
    获取基金与基金经理映射关系

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
            'fund_code', 'fund_mngr_id', 'mngr_strt_date', 'mngr_end_date'
        ]

    if isinstance(fund_code_list, str):
        fund_code_list = fund_code_list.split(',')

    if isinstance(fund_mngr_id_list, str):
        fund_mngr_id_list = fund_mngr_id_list.split(',')

    params = {
        "fund_code_list": fund_code_list,
        "fund_mngr_id_list": fund_mngr_id_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_manager_fund_map", **params)


def get_personnel_company_map(corp_id_list=None, prsn_id_list=None, cols=None, rslt_type=0):
    """
    获取人员公司任职映射关系

    """

    int_param = \
        [
            'corp_onum', 'prsn_onum',
            'is_core', 'is_incl', 'is_leav', 'is_exec', 'is_legp'
        ]
    float_param = \
        [
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'prsn_id', 'corp_id', 'corp_onum', 'prsn_onum',
            'is_core', 'is_incl', 'is_leav', 'is_exec', 'is_legp',
            'strt_date', 'end_date'
        ]

    if corp_id_list is None and prsn_id_list is None:
        warnings.warn("函数[get_personnel_company_map]的参数"
                      "(corp_id_list, prsn_id_list)"
                      "不能全部为空")
        return None

    if isinstance(corp_id_list, str):
        corp_id_list = corp_id_list.split(',')

    if isinstance(prsn_id_list, str):
        prsn_id_list = prsn_id_list.split(',')

    params = {
        "corp_id_list": corp_id_list,
        "prsn_id_list": prsn_id_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_personnel_company_map", **params)


def get_personnel_position(prsn_id_list=None, cols=None, rslt_type=0):
    """
    获取人员职务信息

    """

    int_param = \
        [
            'pos_orde'
        ]
    float_param = \
        [
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'prsn_id', 'corp_id', 'pos_type', 'pos', 'dept', 'strt_date', 'end_date', 'pos_orde'
        ]

    if isinstance(prsn_id_list, str):
        prsn_id_list = prsn_id_list.split(',')

    params = {
        "prsn_id_list": prsn_id_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_personnel_position", **params)


def get_strategy_fund_map(fund_code_list=None, stra_code=None, cols=None, rslt_type=0):
    """
    获取基金与策略映射关系

    """

    int_param = \
        [
            'firs_stra', 'secd_stra', 'thir_stra', 'src_type'
        ]
    float_param = \
        [
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'firs_stra', 'secd_stra', 'thir_stra', 'src_type'
        ]

    if fund_code_list is None and stra_code is None:
        warnings.warn("函数[get_strategy_fund_map]的参数"
                      "(fund_code_list, stra_code)"
                      "不能全部为空")
        return None
    elif stra_code is not None \
            and stra_code < 1000 \
            and stra_code != 1:
        warnings.warn("函数[get_strategy_fund_map]的参数"
                      "(stra_code)"
                      "有效范围应大于1000")
        return None

    if isinstance(fund_code_list, str):
        fund_code_list = fund_code_list.split(',')

    if stra_code == None:
        stra_code = 1

    params = {
        "fund_code_list": fund_code_list,
        "stra_code": stra_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_strategy_fund_map", **params)


def get_benchmark_fund_map(fund_code_list=None, pri_basi_id_list=None, cols=None, rslt_type=0):
    """
    获取基金与基准映射关系

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
            'fund_code', 'fund_cn_abbr', 'fund_cn_fn', 'pri_basi_id', 'perf_basi'
        ]

    if fund_code_list is None and pri_basi_id_list is None:
        warnings.warn("函数[get_benchmark_fund_map]的参数"
                      "(fund_code_list, pri_basi_id_list)"
                      "不能全部为空")
        return None

    if isinstance(fund_code_list, str):
        fund_code_list = fund_code_list.split(',')

    if isinstance(pri_basi_id_list, str):
        pri_basi_id_list = pri_basi_id_list.split(',')

    params = {
        "fund_code_list": fund_code_list,
        "pri_basi_id_list": pri_basi_id_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_benchmark_fund_map", **params)


def get_index_confidence(strt_mth, end_mth, cols=None, rslt_type=0):
    """
    获取对冲基金经理信心指数

    """

    int_param = \
        [
            'indx_val',
            'mkt_expe_indx', 'pos_plan_indx', 'me_extrm_optimstc',
            'me_optimstc', 'me_nturl', 'me_psmstc', 'me_extrm_psmstc',
            'pp_extrm_grow', 'pp_grow', 'pp_unchg', 'pp_redc', 'pp_extrm_redc'
        ]
    float_param = \
        [
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_id', 'indx_code', 'indx_date', 'indx_val',
            'mkt_expe_indx', 'pos_plan_indx', 'me_extrm_optimstc',
            'me_optimstc', 'me_nturl', 'me_psmstc', 'me_extrm_psmstc',
            'pp_extrm_grow', 'pp_grow', 'pp_unchg', 'pp_redc', 'pp_extrm_redc'
        ]

    if strt_mth is None or end_mth is None:
        warnings.warn("函数[get_index_confidence]的参数"
                      "(strt_mth, end_mth)"
                      "不能为空")
        return None

    if len(strt_mth) == 6:
        strt_mth = '%s01' % strt_mth
    if len(end_mth) == 6:
        end_mth = '%s31' % end_mth

    if strt_mth and end_mth:
        params = {
            "strt_mth": strt_mth,
            "end_mth": end_mth,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_index_confidence", **params)
    else:
        warnings.warn("函数[get_index_confidence]的参数(strt_mth, end_mth)为必填项")
        return None


def get_index_info(indx_id_list=None, indx_code_list=None, cols=None, rslt_type=0):
    """
    获取指数基本信息

    """

    int_param = \
        [
            'indx_type', 'indx_area_flag', 'publ_freq',
            'cal_crrc', 'ctrt_freq', 'adj_freq'
        ]
    float_param = \
        [
            'init_val'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_id', 'indx_type', 'indx_code', 'indx_name', 'indx_cn_abbr',
            'indx_area_flag', 'ind_prov_id', 'publ_freq', 'publ_date',
            'init_val', 'cal_crrc', 'cal_mode', 'wght_mode', 'scre_mode',
            'ctrt_freq', 'adj_freq'
        ]

    if indx_id_list is None and indx_code_list is None:
        warnings.warn("函数[get_index_info]的参数"
                      "(indx_id_list, indx_code_list)"
                      "不能全部为空")
        return None

    if isinstance(indx_id_list, str):
        indx_id_list = indx_id_list.split(',')

    if isinstance(indx_code_list, str):
        indx_code_list = indx_code_list.split(',')

    params = {
        "indx_id_list": indx_id_list,
        "indx_code_list": indx_code_list,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_index_info", **params)


def get_dividends(fund_code_list, cols=None, rslt_type=0):
    """
    获取分红信息

    """

    int_param = \
        [
            'divd_type', 'src_type'
        ]
    float_param = \
        [
            'divd_rati'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'divd_date', 'divd_type', 'divd_rati', 'src_type'
        ]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_dividends", **params)
    else:
        warnings.warn("函数[get_dividends]的参数(fund_code_list)为必填项")
        return None


def get_fund_rank(fund_code_list, strt_mth='190001', end_mth=None, cols=None, rslt_type=0):
    """
    获取私募基金收益排名

    """

    int_param = \
        [
            'abs_ror_1m', 'relt_ror_1m', 'abs_ror_3m', 'relt_ror_3m', 'abs_ror_6m',
            'relt_ror_6m', 'abs_ror_1y', 'relt_ror_1y', 'abs_ror_2y', 'relt_ror_2y',
            'abs_ror_3y', 'relt_ror_3y', 'abs_ror_4y', 'relt_ror_4y', 'abs_ror_5y',
            'relt_ror_5y', 'abs_ror_ytd', 'relt_ror_ytd', 'abs_ror_incep', 'relt_ror_incep',
            'abs_maxdrad_1y', 'relt_maxdrad_1y', 'abs_maxdrad_2y', 'relt_maxdrad_2y', 'abs_maxdrad_3y',
            'relt_maxdrad_3y', 'abs_maxdrad_4y', 'relt_maxdrad_4y', 'abs_maxdrad_5y', 'relt_maxdrad_5y',
            'abs_adjror_1y', 'relt_adjror_1y', 'abs_adjror_2y', 'relt_adjror_2y', 'abs_adjror_3y',
            'relt_adjror_3y', 'abs_adjror_4y', 'relt_adjror_4y', 'abs_adjror_5y', 'relt_adjror_5y',
            'abs_upcaptr_1y', 'relt_upcaptr_1y', 'abs_upcaptr_2y', 'relt_upcaptr_2y', 'abs_upcaptr_3y',
            'relt_upcaptr_3y', 'abs_upcaptr_4y', 'relt_upcaptr_4y', 'abs_upcaptr_5y', 'relt_upcaptr_5y',
            'abs_downcaptr_1y', 'relt_downcaptr_1y', 'abs_downcaptr_2y', 'relt_downcaptr_2y', 'abs_downcaptr_3y',
            'relt_downcaptr_3y', 'abs_downcaptr_4y', 'relt_downcaptr_4y', 'abs_downcaptr_5y', 'relt_downcaptr_5y',
            'abs_shap_1y', 'relt_shap_1y', 'abs_shap_2y', 'relt_shap_2y', 'abs_shap_3y', 'relt_shap_3y',
            'abs_shap_5y', 'relt_shap_5y', 'abs_stddev_1y', 'relt_stddev_1y', 'abs_stddev_2y', 'relt_stddev_2y',
            'abs_stddev_3y', 'relt_stddev_3y', 'abs_stddev_5y', 'relt_stddev_5y'
        ]
    float_param = \
        [

        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'clas_id', 'cal_mth',
            'abs_ror_1m', 'relt_ror_1m', 'abs_ror_3m', 'relt_ror_3m', 'abs_ror_6m',
            'relt_ror_6m', 'abs_ror_1y', 'relt_ror_1y', 'abs_ror_2y', 'relt_ror_2y',
            'abs_ror_3y', 'relt_ror_3y', 'abs_ror_4y', 'relt_ror_4y', 'abs_ror_5y',
            'relt_ror_5y', 'abs_ror_ytd', 'relt_ror_ytd', 'abs_ror_incep', 'relt_ror_incep',
            'abs_maxdrad_1y', 'relt_maxdrad_1y', 'abs_maxdrad_2y', 'relt_maxdrad_2y', 'abs_maxdrad_3y',
            'relt_maxdrad_3y', 'abs_maxdrad_4y', 'relt_maxdrad_4y', 'abs_maxdrad_5y', 'relt_maxdrad_5y',
            'abs_adjror_1y', 'relt_adjror_1y', 'abs_adjror_2y', 'relt_adjror_2y', 'abs_adjror_3y',
            'relt_adjror_3y', 'abs_adjror_4y', 'relt_adjror_4y', 'abs_adjror_5y', 'relt_adjror_5y',
            'abs_upcaptr_1y', 'relt_upcaptr_1y', 'abs_upcaptr_2y', 'relt_upcaptr_2y', 'abs_upcaptr_3y',
            'relt_upcaptr_3y', 'abs_upcaptr_4y', 'relt_upcaptr_4y', 'abs_upcaptr_5y', 'relt_upcaptr_5y',
            'abs_downcaptr_1y', 'relt_downcaptr_1y', 'abs_downcaptr_2y', 'relt_downcaptr_2y', 'abs_downcaptr_3y',
            'relt_downcaptr_3y', 'abs_downcaptr_4y', 'relt_downcaptr_4y', 'abs_downcaptr_5y', 'relt_downcaptr_5y',
            'abs_shap_1y', 'relt_shap_1y', 'abs_shap_2y', 'relt_shap_2y', 'abs_shap_3y', 'relt_shap_3y',
            'abs_shap_5y', 'relt_shap_5y', 'abs_stddev_1y', 'relt_stddev_1y', 'abs_stddev_2y', 'relt_stddev_2y',
            'abs_stddev_3y', 'relt_stddev_3y', 'abs_stddev_5y', 'relt_stddev_5y'
        ]

    if end_mth is None:
        end_mth = get_current_date()[0: 6]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_mth": strt_mth,
            "end_mth": end_mth,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_fund_rank", **params)
    else:
        warnings.warn("函数[get_fund_rank]的参数(fund_code_list)为必填项")
        return None


def get_adjusted_risk_index(fund_code_list, strt_mth='190001', end_mth=None, cols=None, rslt_type=0):
    """
    获取调整后风险指标

    """

    int_param = \
        [

        ]
    float_param = \
        [
            'shap_1m', 'shap_3m', 'shap_6m', 'shap_1y',
            'shap_2y', 'shap_3y', 'shap_4y', 'shap_5y', 'shap_10y', 'shap_incep',
            'shap_ytd', 'sotn_1m', 'sotn_3m', 'sotn_6m', 'sotn_1y', 'sotn_2y',
            'sotn_3y', 'sotn_4y', 'sotn_5y', 'sotn_10y', 'sotn_incep', 'sotn_ytd',
            'sotn_mar_1y', 'sotn_mar_2y', 'sotn_mar_3y', 'sotn_mar_4y', 'sotn_mar_5y',
            'sotn_mar_10y', 'sotn_mar_incep', 'sotn_mar_ytd', 'tryn_1m', 'tryn_3m',
            'tryn_6m', 'tryn_1y', 'tryn_2y', 'tryn_3y', 'tryn_4y', 'tryn_5y', 'tryn_10y',
            'tryn_incep', 'tryn_ytd', 'jesn_6m', 'jesn_1y', 'jesn_2y', 'jesn_3y', 'jesn_4y',
            'jesn_5y', 'jesn_10y', 'jesn_incep', 'jesn_ytd', 'calm_1y', 'calm_2y', 'calm_3y',
            'calm_4y', 'calm_5y', 'calm_10y', 'calm_incep', 'calm_ytd', 'omega_1y', 'omega_2y',
            'omega_3y', 'omega_4y', 'omega_5y', 'omega_10y', 'omega_incep', 'omega_ytd', 'kappa_1y',
            'kappa_2y', 'kappa_3y', 'kappa_4y', 'kappa_5y', 'kappa_10y', 'kappa_incep', 'kappa_ytd'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'cal_mth', 'shap_1m', 'shap_3m', 'shap_6m', 'shap_1y',
            'shap_2y', 'shap_3y', 'shap_4y', 'shap_5y', 'shap_10y', 'shap_incep',
            'shap_ytd', 'sotn_1m', 'sotn_3m', 'sotn_6m', 'sotn_1y', 'sotn_2y',
            'sotn_3y', 'sotn_4y', 'sotn_5y', 'sotn_10y', 'sotn_incep', 'sotn_ytd',
            'sotn_mar_1y', 'sotn_mar_2y', 'sotn_mar_3y', 'sotn_mar_4y', 'sotn_mar_5y',
            'sotn_mar_10y', 'sotn_mar_incep', 'sotn_mar_ytd', 'tryn_1m', 'tryn_3m',
            'tryn_6m', 'tryn_1y', 'tryn_2y', 'tryn_3y', 'tryn_4y', 'tryn_5y', 'tryn_10y',
            'tryn_incep', 'tryn_ytd', 'jesn_6m', 'jesn_1y', 'jesn_2y', 'jesn_3y', 'jesn_4y',
            'jesn_5y', 'jesn_10y', 'jesn_incep', 'jesn_ytd', 'calm_1y', 'calm_2y', 'calm_3y',
            'calm_4y', 'calm_5y', 'calm_10y', 'calm_incep', 'calm_ytd', 'omega_1y', 'omega_2y',
            'omega_3y', 'omega_4y', 'omega_5y', 'omega_10y', 'omega_incep', 'omega_ytd', 'kappa_1y',
            'kappa_2y', 'kappa_3y', 'kappa_4y', 'kappa_5y', 'kappa_10y', 'kappa_incep', 'kappa_ytd'
        ]

    if end_mth is None:
        end_mth = get_current_date()[0: 6]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_mth": strt_mth,
            "end_mth": end_mth,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_adjusted_risk_index", **params)
    else:
        warnings.warn("函数[get_adjusted_risk_index]的参数(fund_code_list)为必填项")
        return None


def get_capture_return(fund_code_list, strt_mth='190001', end_mth=None, cols=None, rslt_type=0):
    """
    获取基金上行|下行捕获率

    """

    int_param = \
        [

        ]
    float_param = \
        [
            'upcaptr_ror_1y', 'upcaptr_ror_2y', 'upcaptr_ror_3y', 'upcaptr_ror_4y',
            'upcaptr_ror_5y', 'upcaptr_ror_10y', 'upcaptr_ror_incep', 'upcaptr_ror_ytd', 'downcaptr_ror_1y',
            'downcaptr_ror_2y', 'downcaptr_ror_3y', 'downcaptr_ror_4y', 'downcaptr_ror_5y', 'downcaptr_ror_10y',
            'downcaptr_ror_incep', 'downcaptr_ror_ytd', 'upcaptr_1y', 'upcaptr_2y', 'upcaptr_3y', 'upcaptr_4y',
            'upcaptr_5y', 'upcaptr_10y', 'upcaptr_incep', 'upcaptr_ytd', 'downcaptr_1y', 'downcaptr_2y', 'downcaptr_3y',
            'downcaptr_4y', 'downcaptr_5y', 'downcaptr_10y', 'downcaptr_incep', 'downcaptr_ytd'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'cal_mth', 'upcaptr_ror_1y', 'upcaptr_ror_2y', 'upcaptr_ror_3y', 'upcaptr_ror_4y',
            'upcaptr_ror_5y', 'upcaptr_ror_10y', 'upcaptr_ror_incep', 'upcaptr_ror_ytd', 'downcaptr_ror_1y',
            'downcaptr_ror_2y', 'downcaptr_ror_3y', 'downcaptr_ror_4y', 'downcaptr_ror_5y', 'downcaptr_ror_10y',
            'downcaptr_ror_incep', 'downcaptr_ror_ytd', 'upcaptr_1y', 'upcaptr_2y', 'upcaptr_3y', 'upcaptr_4y',
            'upcaptr_5y', 'upcaptr_10y', 'upcaptr_incep', 'upcaptr_ytd', 'downcaptr_1y', 'downcaptr_2y', 'downcaptr_3y',
            'downcaptr_4y', 'downcaptr_5y', 'downcaptr_10y', 'downcaptr_incep', 'downcaptr_ytd'
        ]

    if end_mth is None:
        end_mth = get_current_date()[0: 6]

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_mth": strt_mth,
            "end_mth": end_mth,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_capture_return", **params)
    else:
        warnings.warn("函数[get_capture_return]的参数(fund_code_list)为必填项")
        return None


def get_fund_portfolio(fund_code_list, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金重仓股统计

    """

    int_param = \
        [
            'sec_type'
        ]
    float_param = \
        [
            'sec_mkt_val', 'nv_rati', 'hldp', 'hldp_rati'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'stat_date', 'scr_num', 'scr_type', 'scr_mkt_val', 'nv_rati', 'hldp', 'hldp_rati'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_fund_portfolio", **params)
    else:
        warnings.warn("函数[get_fund_portfolio]的参数(fund_code_list)为必填项")
        return None


def get_assets_position(fund_code_list, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金资产持仓

    """

    int_param = \
        [
            'scr_type'
        ]
    float_param = \
        [
            'hldp'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'stat_date', 'scr_type', 'scr_mkt_val', 'hldp'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_assets_position", **params)
    else:
        warnings.warn("函数[get_assets_position]的参数(fund_code_list)为必填项")
        return None


def get_relative_value_allocation(fund_code_list, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金相对价值配置

    """

    int_param = \
        [
            'samp_num'
        ]
    float_param = \
        [
            'mkt_beta', 'big_smal_beta', 'grow_beta',
            'hedg_beta', 'crrc_beta', 'relt_beta', 'mkt_contrb', 'big_smal_contrb',
            'grow_contrb', 'hedg_contrb', 'crrc_contrb', 'relt_contrv', 'alpha',
            'rsdu', 'eval_rati', 'fitgdn'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'fund_code', 'end_date', 'mkt_beta', 'big_smal_beta', 'grow_beta',
            'hedg_beta', 'crrc_beta', 'relt_beta', 'mkt_contrb', 'big_smal_contrb',
            'grow_contrb', 'hedg_contrb', 'crrc_contrb', 'relt_contrv', 'alpha',
            'rsdu', 'eval_rati', 'fitgdn', 'samp_num'
        ]

    if end_date is None:
        end_date = get_current_date()

    if fund_code_list:

        if isinstance(fund_code_list, str):
            fund_code_list = fund_code_list.split(',')

        params = {
            "fund_code_list": fund_code_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("pof/get_relative_value_allocation", **params)
    else:
        warnings.warn("函数[get_relative_value_allocation]的参数(fund_code_list)为必填项")
        return None


def get_index_value(indx_id_list=None, indx_code_list=None, strt_date='19000101', end_date=None, cols=None, rslt_type=0):
    """
    获取融智指数

    """

    int_param = \
        [
            'weeks', 'year', 'incl_cal_fund_vol'
        ]
    float_param = \
        [
            'indx_val'
        ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indx_id', 'indx_code', 'end_date', 'weeks', 'year',
            'indx_val', 'incl_cal_fund_vol'
        ]

    if end_date is None:
        end_date = get_current_date()

    if indx_id_list is None and indx_code_list is None:
        warnings.warn("函数[get_index_value]的参数"
                      "(indx_id_list, indx_code_list)"
                      "不能全部为空")
        return None

    if isinstance(indx_id_list, str):
        indx_id_list = indx_id_list.split(',')

    if isinstance(indx_code_list, str):
        indx_code_list = indx_code_list.split(',')

    params = {
        "indx_id_list": indx_id_list,
        "indx_code_list": indx_code_list,
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("pof/get_index_value", **params)


