# -*- coding: UTF-8 -*-
import warnings
import numpy as np
import pandas as pd

from dataquant.apis.base import get_data
from dataquant.utils.convert import convert_fields
from dataquant.utils.datetime_func import get_current_date

__all__ = [
    "get_exchange_calendar",
    "get_index_info",
    "get_index_components",
    "get_security_info",
    "get_future_contract",
    "get_industry_mapping",
    "get_stock_industry",
    "get_stock_industry_change",
    "get_exright_factor",
    "get_ins_basc_info",
    "get_dominant",
    "get_index_weights",
    "get_index_altt_components",
    "get_commodity_index_quote",
    "get_security_index_quote",

    # ================================= 后续开放内容 ================================= #
    "get_stk_susp_info",
    "get_stk_st_flag",
    "get_stk_basc_affi",
    "get_bsht",
    "get_cfst",
    "get_proft",
    "get_fin_indx",
    "get_stk_plac_info",
    "get_stk_divd_info",
    "get_stk_addi",
    "get_ins_mngr_info",
    "get_ins_mngr_chg",
    "get_ins_capt_chg",
    "get_ins_top10_shah",
    "get_ins_top10_cir_shah",
    "get_rstk_drrt",
    "get_rstk_drrt_dtl",
    "get_prof_pred",
    "get_marg_scr",
    "get_stk_bloc_rep",
    "get_stk_bloc_recd",
    "get_fund_basc_info",
    "get_cifd_fund_basc_info",
    "get_fund_feer_info",
    "get_fund_rat_info",
    "get_fund_nav_info",
    "get_fund_shr_chg",
    "get_fund_perf_indx",
    "get_fund_ast_cfg_info",
    "get_fund_hldp_dtl",
    "get_crrc_fund_payf_info",
    "get_etf_daly_pr_info",
    "get_opt_contr_info",
    "get_opt_underlying",
    "get_opt_contr_by_date",
    "get_stock_px_limit"
]


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

    if mkt_code == 'XSHE':
        mkt_code = 'XSHG'

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


def get_index_info(scr_num_list=None, indx_elem_type_code=None, indx_rels_ins_name=None,
                   indx_wght_type_code=None, cols=None, rslt_type=0):
    """
    获取国内外指数的基本要素信息，包括指数名称、交易代码、发布机构、发布日期、基日、基点、指数系列、样本证券类型、样本交
    易市场、加权方式、指数类型等。

    """

    int_param = []
    float_param = ['indx_basd_pont']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'indx_basd_pont'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'indx_type_code', 'indx_rels_ins_name', 'indx_basd',
            'indx_basd_pont', 'puse_date', 'indx_elem_type_code', 'indx_wght_type_code', 'indx_cal_type_code'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "indx_elem_type_code": indx_elem_type_code,
        "indx_rels_ins_name": indx_rels_ins_name,
        "indx_wght_type_code": indx_wght_type_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_indx_basc_info", **params)


def get_index_components(scr_num_list=None, trad_date=None, cols=None, rslt_type=0):
    """
    获取指数的成分构成情况，包括指数成分股名称、成分股代码、入选日期、剔除日期等。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'trad_date', 'scr_code', 'scr_num', 'scr_abbr', 'mkt_code',
            'indx_type_code', 'elem_scr_code', 'elem_scr_num', 'elem_scr_abbr', 'elem_mkt_code'
        ]

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "intv_strt_date": trad_date,
            "intv_end_date": trad_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_indx_elem", **params)
    else:
        warnings.warn("函数[get_index_components]的参数(scr_num_list)为必填项")
        return None


def get_security_info(scr_num_list=None, mkt_code=None, cols=None):
    """
    获取股票的基本信息，包含股票交易代码及其简称、股票类型、上市状态、上市板块、上市日期等；上市状态为最新数据，不显示历
    史变动信息（含科创板）。

    """
    STOCK = ['XSHG', 'XSHE', 'XHKG']
    FUTURE = ['XZCE', 'XDCE', 'XSGE', 'CCFX', 'XINE']

    _stk_num_list = []
    _fut_num_list = []

    # 同时输入scr_num_list和mkt_code，以输入代码优先
    result = {}
    return_data = None
    if scr_num_list and mkt_code:
        mkt_code = None
    elif mkt_code:
        if mkt_code == "XHKG":
            result['hkstock'] = _get_hkstock_info(mkt_code=mkt_code, cols=cols)

        elif mkt_code in STOCK:
            result['stock'] = _get_stock_info(mkt_code=mkt_code, cols=cols)
            result['bond'] = _get_bond_info(mkt_code=mkt_code, cols=cols)
            result['fund'] = _get_fund_info(mkt_code=mkt_code, cols=cols)


            return result
        elif mkt_code in FUTURE:
            result['future'] = _get_future_info(mkt_code=mkt_code, cols=cols)
            return result

    if scr_num_list is None and mkt_code is None:
        result['stock'] = _get_stock_info()
        return result

    if scr_num_list:
        if isinstance(scr_num_list, str):
            scr_num_list = scr_num_list.split(',')

        for _scr in scr_num_list:
            if _scr[0].isdigit():
                _stk_num_list.append(_scr)
            else:
                _fut_num_list.append(_scr)

    if len(_stk_num_list) > 0:
        result['stock'] = _get_stock_info(_stk_num_list, mkt_code, cols)
        result['bond'] = _get_bond_info(_stk_num_list, mkt_code, cols)
        result['fund'] = _get_fund_info(_stk_num_list, mkt_code, cols)
        result['hkstock'] = _get_hkstock_info(_stk_num_list, mkt_code, cols)
    if len(_fut_num_list) > 0:
        result['future'] = _get_future_info(_fut_num_list, mkt_code, cols)

    return result


def _get_stock_info(scr_num_list=None, mkt_code=None, cols=None):
    """

    """

    int_param = []
    float_param = ['tot_capt']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'stk_abbr', 'stk_name', 'mkt_code',
            'list_stat', 'list_date', 'delt_date', 'stk_type', 'astk_boar_type_code',
            'ofer_crrc_code', 'cont_addr', 'main_busi', 'tot_capt'
        ]

    params = {
        "scr_num_list": scr_num_list,
        "stk_type": "01",
        "mkt_code": mkt_code,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_stk_basc_info", **params)

# 20240609 add 港股基本信息api
def _get_hkstock_info(scr_num_list=None, mkt_code=None, cols=None):
    """

    """

    int_param = []
    float_param = ['tot_capt']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'stk_abbr', 'stk_name', 'mkt_code',
            'list_stat', 'list_date', 'delt_date', 'stk_type', 'astk_boar_type_code',
            'ofer_crrc_code', 'cont_addr', 'main_busi', 'tot_capt'
        ]

    params = {
        "scr_num_list": scr_num_list,
        "mkt_code": "XHKG",
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_stk_basc_info", **params)

def _get_bond_info(scr_num_list=None, mkt_code=None, cols=None):
    """

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'scr_name', 'mkt_code', 'list_stat',
            'list_date', 'delt_date', 'bond_type', 'ofer_crrc_code'
        ]

    params = {
        "scr_num_list": scr_num_list,
        "mkt_code": mkt_code,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_bond_basc_info", **params)


def _get_fund_info(scr_num_list=None, mkt_code=None, cols=None):
    """

    """

    int_param = ['mng_ins_num', 'trus_ins_num', ]
    float_param = ['cir_shr']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'scr_abbr', 'mkt_code', 'fund_type',
            'oper_mode_code', 'qdii_flag', 'etf_flag', 'lof_flag', 'list_stat',
            'mngr_name', 'setp_date', 'at_pd_date', 'list_date', 'delt_date',
            'mng_ins_num', 'mng_ins_abbr', 'mng_ins_name', 'trus_ins_num',
            'trus_ins_abbr', 'trus_ins_name', 'ivsm_scop', 'ivsm_tgt',
            'perf_cont_basi', 'cir_shr'
        ]

    params = {
        "scr_num_list": scr_num_list,
        "mkt_code": mkt_code,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_fund_basc_info", **params)


def _get_future_info(scr_num_list=None, mkt_code=None, cols=None):
    """

    """

    int_param = []
    float_param = ['min_mar', 'last_deli_date']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'fut_abbr', 'mkt_code', 'mkt_abbr', 'cont_type', 'cont_mth', 'dely_meth',
            'futr_var_code', 'futr_var_abbr', 'quot_unit', 'tick_sz', 'contr_mtp', 'min_mar', 'list_date',
            'last_trd_date', 'deli_year', 'deli_mth', 'deli_date', 'last_deli_date', 'tx_fee', 'deli_chag',
            'lstg_basi_prc', 'limit_up_down_chg', 'cont_stat'
        ]

    if scr_num_list and '.' not in scr_num_list[0]:
        params = {
            "scr_code_list": scr_num_list,
            "mkt_code": mkt_code,
            "cols": cols,
            "int_param": int_param,
            "float_param": float_param
        }
    else:
        params = {
            "scr_num_list": scr_num_list,
            "mkt_code": mkt_code,
            "cols": cols,
            "int_param": int_param,
            "float_param": float_param
        }

    return get_data("get_fut_basc_info", **params)


def get_future_contract(futr_var_code=None, trad_date=None, cols=None):
    """

    """

    int_param = []
    float_param = ['min_mar', 'last_deli_date']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'fut_abbr', 'mkt_code', 'mkt_abbr', 'cont_type', 'cont_mth', 'dely_meth',
            'futr_var_code', 'futr_var_abbr', 'quot_unit', 'tick_sz', 'contr_mtp', 'min_mar', 'list_date',
            'last_trd_date', 'deli_year', 'deli_mth', 'deli_date', 'last_deli_date', 'tx_fee', 'deli_chag',
            'lstg_basi_prc', 'limit_up_down_chg', 'cont_stat'
        ]

    params = {
        "futr_var_code": futr_var_code,
        "trad_date": trad_date,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_fut_trd_contr", **params)


def get_industry_mapping(indt_clas_std_code, indt_code_list=None, indt_prn_code_list=None,
                         indt_lvl_list=None, cols=None, rslt_type=0):
    """
    获取针对机构、证券的行业分类说明，覆盖证监会行业2012、申万行业、中证行业、GICS行业、沪深市场板块等分类体系。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'indt_code', 'indt_name', 'indt_prn_code', 'indt_lvl', 'indt_clas_std_code'
        ]

    if indt_code_list is not None:
        indt_prn_code_list = None
        indt_lvl_list = None
    elif indt_code_list is None and indt_prn_code_list is not None:
        indt_lvl_list = None

    if indt_clas_std_code:
        params = {
            "indt_clas_std_code": indt_clas_std_code,
            "indt_code_list": indt_code_list,
            "indt_prn_code_list": indt_prn_code_list,
            "indt_lvl_list": indt_lvl_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_scr_indt_clas", **params)
    else:
        warnings.warn("函数[get_industry_mapping]的参数(indt_clas_std_code)为必填项")
        return None


def get_stock_industry(scr_num_list=None, trad_date=None, clas_code=None, cols=None,
                       rslt_type=0):
    """
    获取沪深股票所属行业信息，输入证券代码则返回证券所属行业，输入行业编码及行业代码则返回行业所含的全部证券

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'trad_date', 'scr_num', 'clas_code', 'clas_name',
            'firs_clas_indu_code', 'firs_clas_indu_name', 'secd_clas_indu_code', 'secd_clas_indu_name',
            'thir_clas_indu_code', 'thir_clas_indu_name', 'four_clas_indu_code', 'four_clas_indu_name'
        ]

    if clas_code is None:
        clas_code = '38'

    if scr_num_list is None:
        scr_num_list = get_security_info()['scr_num'].tolist()

    params = {
        "scr_num_list": scr_num_list,
        "trad_date": trad_date,
        "clas_code": clas_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_stk_indt_clas", **params)


def get_stock_industry_change(scr_num_list=None, clas_code=None, cols=None,
                              rslt_type=0):
    """
    获取沪深股票所属行业信息，输入证券代码则返回证券所属行业，输入行业编码及行业代码则返回行业所含的全部证券

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'clas_code', 'clas_name', 'pub_date', 'cacl_date',
            'firs_clas_indu_code', 'firs_clas_indu_name',
            'secd_clas_indu_code', 'secd_clas_indu_name',
            'thir_clas_indu_code', 'thir_clas_indu_name',
            'four_clas_indu_code', 'four_clas_indu_name', 'vali_flag'
        ]

    if clas_code is None:
        clas_code = '38'

    if scr_num_list is None:
        scr_num_list = get_security_info()['stock']['scr_num'].tolist()

    params = {
        "scr_num_list": scr_num_list,
        "clas_code": clas_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_stk_indt_info", **params)


def get_exright_factor(scr_num_list, strt_date=None, end_date=None, cols=None, rslt_type=0):
    """
    获取股票复权因子数据。

    """

    int_param = ['addi_prc']
    float_param = [
        'bons_amt', 'sdvd_rati', 'tfsh_rati', 'plac_rati', 'plac_prc', 'addi_rati', 'accu_rstr_cnst',
        'thim_accu_rstr_fctr', 'aggr_accu_rstr_fctr', 'rati_rstr_cnst', 'thim_rati_rstr_fctr',
        'forward_rstr_fctr', 'aggr_rati_rstr_fctr'
    ]
    if cols:
        int_param = list({'addi_prc'}.intersection(set(convert_fields(cols))))
        float_param = list(
            {'bons_amt', 'sdvd_rati', 'tfsh_rati', 'plac_rati', 'plac_prc', 'addi_rati', 'accu_rstr_cnst',
             'thim_accu_rstr_fctr', 'aggr_accu_rstr_fctr', 'rati_rstr_cnst', 'thim_rati_rstr_fctr', 'forward_rstr_fctr',
             'aggr_rati_rstr_fctr'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'mkt_code', 'equi_reg_date', 'dr_day', 'bons_amt', 'sdvd_rati', 'tfsh_rati',
            'plac_rati', 'plac_prc', 'addi_prc', 'accu_rstr_cnst', 'thim_accu_rstr_fctr', 'forward_rstr_fctr',
            'aggr_rati_rstr_fctr',
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stk_rstr_fctr", **params)
    else:
        warnings.warn("函数[get_exright_factor]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_dominant(futr_var_code, strt_date=None, end_date=None, cont_rank=1, calc_mode=1, cols=None):
    """
    获取期货主力合约信息
    """

    int_param = []
    float_param = ['min_mar', 'last_deli_date']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'busi_date', 'fut_abbr', 'mkt_code', 'mkt_abbr', 'cont_type', 'cont_mth', 'dely_meth',
            'futr_var_code', 'futr_var_abbr', 'quot_unit', 'tick_sz', 'contr_mtp', 'min_mar', 'list_date',
            'last_trd_date', 'deli_year', 'deli_mth', 'deli_date', 'last_deli_date', 'tx_fee', 'deli_chag',
            'lstg_basi_prc', 'limit_up_down_chg', 'cont_stat'
        ]

    if strt_date is None:
        strt_date = get_current_date()
    if end_date is None:
        end_date = get_current_date()

    if futr_var_code:
        params = {
            "futr_var_code": futr_var_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cont_rank": cont_rank,
            "calc_mode": calc_mode,
            "cols": cols,
            "int_param": int_param,
            "float_param": float_param
        }

        return get_data("get_fut_main_contr", **params)
    else:
        warnings.warn("函数[get_dominant]的参数(futr_var_code)为必填项")
        return None


def get_index_weights(scr_num_list, trad_date=None, cols=None, rslt_type=0):
    """
    获取指数成分股权重，包括成分股名称、成分股代码、权重生效日、成分股权重等。其中，中债指数按日更新，上证、中证、深证、
    国证等股票指数按月更新。

    """

    int_param = []
    float_param = ['elem_wght']
    if cols:
        int_param = list({}.intersection(set(convert_fields(cols))))
        float_param = list({'elem_wght'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'indx_type_code', 'elem_scr_code', 'elem_scr_num',
            'elem_scr_abbr', 'elem_mkt_code', 'trad_date', 'elem_wght'
        ]

    if trad_date is None:
        trad_date = get_current_date()

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "trad_date": trad_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_indx_elem_wght", **params)
    else:
        warnings.warn("函数[get_indx_weights]的参数(scr_num_list)为必填项")
        return None


def get_index_altt_components(scr_num_list, trad_date=None, cols=None,
                              rslt_type=0):
    """
    获取指数的备选成分构成情况，包括指数成分股名称、成分股代码、入选日期、剔除日期等。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'indx_type_code', 'elem_scr_code', 'elem_scr_num',
            'elem_scr_abbr', 'elem_mkt_code', 'affi_date'
        ]

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "affi_strt_date": trad_date,
            "affi_end_date": trad_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_indx_altt_elem", **params)
    else:
        warnings.warn("函数[get_index_altt_components]的参数(scr_num_list)为必填项")
        return None


def get_commodity_index_quote(scr_num_list, strt_date=None, end_date=None, cols=None,
                              rslt_type=0):
    """
    获取商品指数行情。

    """

    int_param = []
    float_param = ['open_px', 'high_px', 'low_px', 'close_px']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'trade_date', 'scr_num', 'mkt_code',
            'open_px', 'high_px', 'low_px', 'close_px'
        ]

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_comm_indx_quot", **params)
    else:
        warnings.warn("函数[get_commodity_index_quote]的参数(scr_num_list)为必填项")
        return None


def get_security_index_quote(scr_num_list, strt_date=None, end_date=None, cols=None, rslt_type=0):
    """
    获取证券指数行情。

    """

    int_param = []
    float_param = [
        'preclose_px', 'open_px', 'high_px', 'low_px', 'close_px',
        'trd_vol', 'trd_amt', 'chg_pct'
    ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'trade_date', 'scr_num', 'mkt_code',
            'preclose_px', 'open_px', 'high_px', 'low_px', 'close_px',
            'trd_vol', 'trd_amt', 'chg_pct'
        ]

    fix_cols = ['scr_num']
    current_date = get_current_date()
    if strt_date is None and end_date is None:
        df = get_exchange_calendar('XSHG', end_date=current_date, trdy_flag=1)
        if df.shape[0] > 2:
            strt_date = end_date = df['busi_date'].tolist()[-2]
        else:
            strt_date = end_date = current_date
    elif strt_date is None:
        strt_date = end_date
    elif end_date is None:
        end_date = strt_date

    if isinstance(cols, str):
        cols = cols.split(',')
    tmp_cols = fix_cols + cols
    cols = list(set(tmp_cols))
    cols.sort(key=tmp_cols.index)

    if scr_num_list:

        if isinstance(scr_num_list, list):
            scr_num_list = ','.join(scr_num_list)

        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_scr_indx_quot", **params)
    else:
        warnings.warn("函数[get_security_index_quote]的参数(scr_num_list)为必填项")
        return None


# ================================= 后续开放内容 ================================= #
def get_ins_basc_info(ins_num=None, ins_abbr=None, ins_fn=None, unif_soci_cred_code=None, cols=None, rslt_type=0):
    """
    获取公司基本信息。

    """

    int_param = []
    float_param = ['reg_cptl']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'reg_cptl'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'ins_num', 'ins_fn', 'ins_abbr', 'eng_name', 'eng_abbr',
            'cont_addr', 'main_busi', 'legp_rep_name', 'setp_date', 'reg_addr',
            'reg_cptl', 'reg_crrc', 'eml', 'corp_web', 'cont_tel',
            'fax_num', 'boar_scry_name', 'unif_soci_cred_code', 'ins_savc_stat', 'ins_clas_code'
        ]

    params = {
        "ins_num": ins_num,
        "ins_abbr": ins_abbr,
        "ins_fn": ins_fn,
        "unif_soci_cred_code": unif_soci_cred_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_ins_basc_info", **params)


def get_stk_susp_info(intv_strt_date=None, intv_end_date=None, cols=None, rslt_type=0):
    """
    获取证券停牌信息。也可以根据日期范围查询出在这段时间内持续停牌的证券，例如起始日期、结束日期设置为同一天，可以查询出
    当天停牌的所有证券。

    """

    int_param = ['cont_susp_days']
    float_param = []
    if cols:
        int_param = list({'cont_susp_days'}.intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = ['trad_date', 'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'cont_susp_days']

    params = {
        "intv_strt_date": intv_strt_date,
        "intv_end_date": intv_end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_stk_susp_info", **params)


def get_stk_st_flag(intv_strt_date=None, intv_end_date=None, cols=None, rslt_type=0):
    """
    获取股票交易代码（支持多值输入），选择查询开始日期与结束日期，获取股票在一段时间ST标记信息。

    """

    int_param = ['cont_st_days']
    float_param = []
    if cols:
        int_param = list({'cont_st_days'}.intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'trad_date', 'scr_code', 'scr_num', 'scr_abbr', 'mkt_code',
            'stk_risk_chg_type_code', 'cont_st_days'
        ]

    params = {
        "intv_strt_date": intv_strt_date,
        "intv_end_date": intv_end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_stk_st_flag", **params)


def get_stk_basc_affi(scr_num_list=None, affi_strt_date=None, affi_end_date=None, cols=None, rslt_type=0):
    """
    获取沪深股票公告详细信息，包括公告来源、公告标题、公告链接、公告日期、公告对应代码。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date',
            'end_date', 'affi_titl', 'affi_link', 'ins_num'
        ]

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "affi_strt_date": affi_strt_date,
            "affi_end_date": affi_end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stk_basc_affi", **params)
    else:
        warnings.warn("函数[get_stk_basc_affi]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_stk_sect_info(scr_num_list, cols=None, rslt_type=0):
    """
    获取沪深股票所属板块信息

    """

    int_param = ['sect_code']
    float_param = []
    if cols:
        int_param = list({'sect_code'}.intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = ['scr_num', 'in_date', 'dele_date', 'sect_code', 'sect_name']

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stk_sect_info", **params)
    else:
        warnings.warn("函数[get_stk_sect_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_bsht(scr_num_list, rept_type=None, rept_merg_flag=None, strt_date='19900101', end_date=None,
             date_type='1', cols=None, rslt_type=0):
    """
    1、根据2007年新会计准则制定的合并资产负债表模板，收集了2007年以来沪深上市公司定期报告中各个会计期间的资产负
    债表数据； 2、仅收集合并报表数据，包括期末和期初数据； 3、如果上市公司对外财务报表进行更正，调整，均有采集并对外展示； 4、本表中单位为人民币元； 5、每季更新。

    """

    int_param = []
    float_param = [
        'crrc_cptl', 'bal_clr', 'lbofi', 'trd_finl_ast', 'recv_bill', 'recv_acct', 'pre_pay_fund',
        'recv_prem', 'recv_resr_acct', 'recv_resr_agmt_rsrv', 'recv_intr', 'recv_divd', 'oth_recv_acct',
        'purc_rese_finl_ast', 'invt', 'one_year_not_liqd_ast', 'oth_liqd_ast', 'curr_ast', 'gant_loan_advm',
        'avl_sale_finl_ast', 'hmi_ivsm', 'long_recv_acct', 'long_stor_ivsm', 'ivsm_estt', 'fix_ast',
        'ucst_proj', 'proj_matr', 'fix_ast_disp', 'prod_bilg_matr', 'olga_ast', 'immt_ast', 'dev_pay',
        'gdwl', 'long_prep_pay_fee', 'defr_tax_ast', 'oth_not_liqd_ast', 'not_liqd_ast', 'ast', 'shor_lend',
        'borw_pboc', 'absb_deps_intb_deps', 'borw_cptl', 'trd_finl_liab', 'payb_bill', 'payb_acct',
        'pre_recv_acct', 'sell_repo_st', 'payb_fee', 'payb_empl_saly', 'payb_fax', 'payb_intr', 'payb_divid',
        'oth_payb_acct', 'payb_resr_acct', 'insr_agmt_rsrv', 'agt_trd_scr_fund', 'agt_undr_scr_fund',
        'one_year_not_liqd_liab', 'oth_liqd_liab', 'liqd_liab', 'long_loan', 'payb_bond', 'long_acct_payb',
        'spcl_acct_apyb', 'expe_liab', 'defr_inct_liab', 'other_not_liqd_liab', 'not_liqd_liab', 'liab',
        'paid_capi', 'capi_resf', 'inv_stk', 'spcl_acct_apyb', 'surp_resf', 'norm_risk_prep', 'un_assn_prof',
        'repr_cnvr_diff', 'attr_prn_shah_evol', 'mir_num', 'shah_equi', 'liab_shah_equi', 'cash_pobc_fund',
        'intb_dpsi', 'prcm', 'devd_prcm_ast', 'fin_leas_recv_acct', 'recv_acct_ivsm', 'oth_ast',
        'intb_oth_finl_ins_dpsi', 'devd_finl_liab', 'absd_dpsi', 'oth_liab', 'recv_subg_recv',
        'recv_resr_uexp_duty_rsrv', 'recv_resr_otdl_rsrv', 'recv_resr_life_duty_rsrv',
        'recv_resr_long_helh_rsrv', 'ins_cust_plg_loan', 'term_deps', 'recg_capi_marg', 'alne_acct_ast',
        'pre_recv_prem', 'payb_clam', 'payb_insr_plcy_divd', 'insr_cust_fund_ivsm', 'uexp_duty_rsrv',
        'otdl_rsrv', 'life_insr_duty_rsrv', 'long_helh_insr_duty_rsrv', 'alne_acct_liab', 'cust_cptl_dpsi',
        'cust_pros_dpsi', 'marg', 'trd_seat_pay', 'plg_loan', 'not_liqd_liab_pref_stk',
        'not_liqd_liab_perp_bond', 'shah_equi_pref_stk', 'shah_equi_perp_bond', 'shah_equi_trea_stk',
        'shah_equi_spcl_proj', 'hold_prep_sale_liab', 'esti_fee', 'long_payb_emp_slry', 'defr_incm'
    ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({
            'crrc_cptl', 'bal_clr', 'lbofi', 'trd_finl_ast', 'recv_bill', 'recv_acct', 'pre_pay_fund', 'recv_prem',
            'recv_resr_acct', 'recv_resr_agmt_rsrv', 'recv_intr', 'recv_divd', 'oth_recv_acct', 'purc_rese_finl_ast',
            'invt', 'one_year_not_liqd_ast', 'oth_liqd_ast', 'curr_ast', 'gant_loan_advm', 'avl_sale_finl_ast',
            'hmi_ivsm', 'long_recv_acct', 'long_stor_ivsm', 'ivsm_estt', 'fix_ast', 'ucst_proj', 'proj_matr',
            'fix_ast_disp', 'prod_bilg_matr', 'olga_ast', 'immt_ast', 'dev_pay', 'gdwl', 'long_prep_pay_fee',
            'defr_tax_ast', 'oth_not_liqd_ast', 'not_liqd_ast', 'ast', 'shor_lend', 'borw_pboc', 'absb_deps_intb_deps',
            'borw_cptl', 'trd_finl_liab', 'payb_bill', 'payb_acct', 'pre_recv_acct', 'sell_repo_st', 'payb_fee',
            'payb_empl_saly', 'payb_fax', 'payb_intr', 'payb_divid', 'oth_payb_acct', 'payb_resr_acct',
            'insr_agmt_rsrv', 'agt_trd_scr_fund', 'agt_undr_scr_fund', 'one_year_not_liqd_liab', 'oth_liqd_liab',
            'liqd_liab', 'long_loan', 'payb_bond', 'long_acct_payb', 'spcl_acct_apyb', 'expe_liab', 'defr_inct_liab',
            'other_not_liqd_liab', 'not_liqd_liab', 'liab', 'paid_capi', 'capi_resf', 'inv_stk', 'spcl_acct_apyb',
            'surp_resf', 'norm_risk_prep', 'un_assn_prof', 'repr_cnvr_diff', 'attr_prn_shah_evol', 'mir_num',
            'shah_equi', 'liab_shah_equi', 'cash_pobc_fund', 'intb_dpsi', 'prcm', 'devd_prcm_ast',
            'fin_leas_recv_acct', 'recv_acct_ivsm', 'oth_ast', 'intb_oth_finl_ins_dpsi', 'devd_finl_liab', 'absd_dpsi',
            'oth_liab', 'recv_subg_recv', 'recv_resr_uexp_duty_rsrv', 'recv_resr_otdl_rsrv',
            'recv_resr_life_duty_rsrv', 'recv_resr_long_helh_rsrv', 'ins_cust_plg_loan', 'term_deps', 'recg_capi_marg',
            'alne_acct_ast', 'pre_recv_prem', 'payb_clam', 'payb_insr_plcy_divd', 'insr_cust_fund_ivsm',
            'uexp_duty_rsrv', 'otdl_rsrv', 'life_insr_duty_rsrv', 'long_helh_insr_duty_rsrv', 'alne_acct_liab',
            'cust_cptl_dpsi', 'cust_pros_dpsi', 'marg', 'trd_seat_pay', 'plg_loan', 'not_liqd_liab_pref_stk',
            'not_liqd_liab_perp_bond', 'shah_equi_pref_stk', 'shah_equi_perp_bond', 'shah_equi_trea_stk',
            'shah_equi_spcl_proj', 'hold_prep_sale_liab', 'esti_fee', 'long_payb_emp_slry', 'defr_incm'}.intersection(
            set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'scr_abbr', 'mkt_code', 'rept_type', 'affi_date', 'end_date', 'rept_merg_flag',
            'rept_adj_flag', 'ins_attr_code', 'crrc_cptl', 'bal_clr', 'lbofi', 'trd_finl_ast', 'recv_bill', 'recv_acct',
            'pre_pay_fund', 'recv_prem', 'recv_resr_acct', 'recv_resr_agmt_rsrv', 'recv_intr', 'recv_divd',
            'oth_recv_acct', 'purc_rese_finl_ast', 'invt', 'one_year_not_liqd_ast', 'oth_liqd_ast', 'curr_ast',
            'gant_loan_advm', 'avl_sale_finl_ast', 'hmi_ivsm', 'long_recv_acct', 'long_stor_ivsm', 'ivsm_estt',
            'fix_ast', 'ucst_proj', 'proj_matr', 'fix_ast_disp', 'prod_bilg_matr', 'olga_ast', 'immt_ast', 'dev_pay',
            'gdwl', 'long_prep_pay_fee', 'defr_tax_ast', 'oth_not_liqd_ast', 'not_liqd_ast', 'ast', 'shor_lend',
            'borw_pboc', 'absb_deps_intb_deps', 'borw_cptl', 'trd_finl_liab', 'payb_bill', 'payb_acct', 'pre_recv_acct',
            'sell_repo_st', 'payb_fee', 'payb_empl_saly', 'payb_fax', 'payb_intr', 'payb_divid', 'oth_payb_acct',
            'payb_resr_acct', 'insr_agmt_rsrv', 'agt_trd_scr_fund', 'agt_undr_scr_fund', 'one_year_not_liqd_liab',
            'oth_liqd_liab', 'liqd_liab', 'long_loan', 'payb_bond', 'long_acct_payb', 'spcl_acct_payb', 'expe_liab',
            'defr_inct_liab', 'other_not_liqd_liab', 'not_liqd_liab', 'liab', 'paid_capi', 'capi_resf', 'inv_stk',
            'spcl_acct_rsrv', 'surp_resf', 'norm_risk_prep', 'un_assn_prof', 'repr_cnvr_diff', 'attr_prn_shah_evol',
            'mir_num', 'shah_equi', 'liab_shah_equi', 'cash_pobc_fund', 'intb_dpsi', 'prcm', 'devd_prcm_ast',
            'fin_leas_recv_acct', 'recv_acct_ivsm', 'oth_ast', 'intb_oth_finl_ins_dpsi', 'devd_finl_liab', 'absd_dpsi',
            'oth_liab', 'recv_subg_recv', 'recv_resr_uexp_duty_rsrv', 'recv_resr_otdl_rsrv', 'recv_resr_life_duty_rsrv',
            'recv_resr_long_helh_rsrv', 'ins_cust_plg_loan', 'term_deps', 'recg_capi_marg', 'alne_acct_ast',
            'pre_recv_prem', 'payb_clam', 'payb_insr_plcy_divd', 'insr_cust_fund_ivsm', 'uexp_duty_rsrv', 'otdl_rsrv',
            'life_insr_duty_rsrv', 'long_helh_insr_duty_rsrv', 'alne_acct_liab', 'cust_cptl_dpsi', 'cust_pros_dpsi',
            'marg', 'trd_seat_pay', 'plg_loan', 'not_liqd_liab_pref_stk', 'not_liqd_liab_perp_bond',
            'shah_equi_pref_stk', 'shah_equi_perp_bond', 'shah_equi_trea_stk', 'shah_equi_spcl_proj',
            'hold_prep_sale_liab', 'esti_fee', 'long_payb_emp_slry', 'defr_incm'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "rept_type": rept_type,
            "rept_merg_flag": rept_merg_flag,
            "strt_date": strt_date,
            "end_date": end_date,
            "date_type": date_type,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_bsht", **params)
    else:
        warnings.warn("函数[get_bsht]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_cfst(scr_num_list, rept_type=None, rept_merg_flag=None, strt_date='19900101', end_date=None,
             date_type='1', cols=None, rslt_type=0):
    """
    1、根据2007年新会计准则制定的合并现金流量表模板，收集了2007年以来沪深上市公司定期报告中各个会计期间的现金流
    量表数据； 2、仅收集合并报表数据，包括本期和上期数据； 3、如果上市公司对外财务报表进行更正，调整，均有采集并对外展示； 4、本表中单位为人民币元； 5、每季更新。

    """

    int_param = []
    float_param = [
        'cash_recv_sale', 'cust_dpsi_intb_dpsi_incr', 'pboc_loan_incr', 'oth_fin_brow_amt_incr',
        'cash_recv_prem_in', 'net_cash_resr_busi', 'net_incr_insd_dpst_ivsm', 'net_incr_deal_trd_finl_ast',
        'cash_recv_intr_fee', 'brow_amt_net_incr', 'repo_amt_net_incr', 'tax_retu_recv',
        'oth_cash_recv_oper', 'cash_in_oper', 'cash_pay_purc_merc_serv', 'net_incr_loan_advn_cust',
        'dpst_pboc_intb_net_incr', 'cash_pay_agmt_comp', 'cash_pay_intr_fee', 'inpy_divd_pay',
        'cash_pay_emp', 'cash_pay_tax', 'oth_cash_pay_oper', 'cash_out_oper', 'net_cash_oper',
        'cash_recv_ivsm', 'cash_recv_ivsm_payf', 'cash_recv_deal_ast', 'cash_recv_deal_sub_oth',
        'oth_cash_recv_ivsm', 'cash_in_ivsm', 'cash_pay_purc_ast', 'cash_pay_ivsm', 'plg_loan_net_incr',
        'cash_recv_sub_pay', 'cash_pay_ivsm_oth', 'cash_out_ivsm', 'net_cash_ivsm', 'cash_recv_absb_ivsm',
        'cash_recv_sub_absb_shah', 'loan_recv', 'cash_recv_bond_iss', 'oth_cash_recv_fin', 'cash_in_fin',
        'cash_pay_debt', 'cash_pay_prof_intr', 'sub_pay_prof_intr', 'oth_cash_pay_fin', 'cash_out_fin',
        'net_cash_fin', 'er_chg_efft_cash_eq', 'cash_eq_net_incr', 'cash_eq', 'bgng_cash_eq_bal',
        'end_cash_eq_bal', 'gant_loan_advm_redc', 'dpst_pboc_intb_redc', 'oth_fin_lend_amt_redc',
        'avl_sale_finl_ast_incr', 'net_prof', 'ast_ipoa_prep', 'fix_ipoa_depr', 'imtr_ast_shr',
        'long_prep_fee_shr', 'prep_fee_redc', 'pre_fee_incr', 'fix_immt_oth_ast_loss',
        'fix_ipoa_depr_abnd_loss', 'fv_chg_loss', 'fin_fee', 'ivsm_loss', 'defr_inct_ast_redc',
        'defr_inct_liab_incr', 'inv_redc', 'oper_recv_proj_redc', 'oper_recv_proj_incr', 'oth',
        'debt_tran_capt', 'one_traf_corp_bond', 'fin_leas_fix_ipoa', 'cash_end_bal', 'cash_bgng_bal',
        'cash_eqvl_end_bal', 'cash_eqvl_bgng_bal', 'cash_cash_eqvl_net_incr'
    ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({
            'cash_recv_sale', 'cust_dpsi_intb_dpsi_incr', 'pboc_loan_incr', 'oth_fin_brow_amt_incr',
            'cash_recv_prem_in', 'net_cash_resr_busi', 'net_incr_insd_dpst_ivsm',
            'net_incr_deal_trd_finl_ast', 'cash_recv_intr_fee', 'brow_amt_net_incr',
            'repo_amt_net_incr', 'tax_retu_recv', 'oth_cash_recv_oper', 'cash_in_oper',
            'cash_pay_purc_merc_serv', 'net_incr_loan_advn_cust', 'dpst_pboc_intb_net_incr',
            'cash_pay_agmt_comp', 'cash_pay_intr_fee', 'inpy_divd_pay', 'cash_pay_emp', 'cash_pay_tax',
            'oth_cash_pay_oper', 'cash_out_oper', 'net_cash_oper', 'cash_recv_ivsm',
            'cash_recv_ivsm_payf', 'cash_recv_deal_ast', 'cash_recv_deal_sub_oth', 'oth_cash_recv_ivsm',
            'cash_in_ivsm', 'cash_pay_purc_ast', 'cash_pay_ivsm', 'plg_loan_net_incr',
            'cash_recv_sub_pay', 'cash_pay_ivsm_oth', 'cash_out_ivsm', 'net_cash_ivsm',
            'cash_recv_absb_ivsm', 'cash_recv_sub_absb_shah', 'loan_recv', 'cash_recv_bond_iss',
            'oth_cash_recv_fin', 'cash_in_fin', 'cash_pay_debt', 'cash_pay_prof_intr',
            'sub_pay_prof_intr', 'oth_cash_pay_fin', 'cash_out_fin', 'net_cash_fin',
            'er_chg_efft_cash_eq', 'cash_eq_net_incr', 'cash_eq', 'bgng_cash_eq_bal', 'end_cash_eq_bal',
            'gant_loan_advm_redc', 'dpst_pboc_intb_redc', 'oth_fin_lend_amt_redc',
            'avl_sale_finl_ast_incr', 'net_prof', 'ast_ipoa_prep', 'fix_ipoa_depr', 'imtr_ast_shr',
            'long_prep_fee_shr', 'prep_fee_redc', 'pre_fee_incr', 'fix_immt_oth_ast_loss',
            'fix_ipoa_depr_abnd_loss', 'fv_chg_loss', 'fin_fee', 'ivsm_loss', 'defr_inct_ast_redc',
            'defr_inct_liab_incr', 'inv_redc', 'oper_recv_proj_redc', 'oper_recv_proj_incr', 'oth',
            'debt_tran_capt', 'one_traf_corp_bond', 'fin_leas_fix_ipoa', 'cash_end_bal',
            'cash_bgng_bal', 'cash_eqvl_end_bal', 'cash_eqvl_bgng_bal', 'cash_cash_eqvl_net_incr'}.intersection(
            set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'scr_abbr', 'mkt_code', 'rept_type', 'affi_date', 'end_date', 'rept_merg_flag',
            'rept_adj_flag', 'ins_attr_code', 'cash_recv_sale', 'cust_dpsi_intb_dpsi_incr', 'pboc_loan_incr',
            'oth_fin_brow_amt_incr', 'cash_recv_prem_in', 'net_cash_resr_busi', 'net_incr_insd_dpst_ivsm',
            'net_incr_deal_trd_finl_ast', 'cash_recv_intr_fee', 'brow_amt_net_incr', 'repo_amt_net_incr',
            'tax_retu_recv', 'oth_cash_recv_oper', 'cash_in_oper', 'cash_pay_purc_merc_serv', 'net_incr_loan_advn_cust',
            'dpst_pboc_intb_net_incr', 'cash_pay_agmt_comp', 'cash_pay_intr_fee', 'inpy_divd_pay', 'cash_pay_emp',
            'cash_pay_tax', 'oth_cash_pay_oper', 'cash_out_oper', 'net_cash_oper', 'cash_recv_ivsm',
            'cash_recv_ivsm_payf', 'cash_recv_deal_ast', 'cash_recv_deal_sub_oth', 'oth_cash_recv_ivsm', 'cash_in_ivsm',
            'cash_pay_purc_ast', 'cash_pay_ivsm', 'plg_loan_net_incr', 'cash_recv_sub_pay', 'cash_pay_ivsm_oth',
            'cash_out_ivsm', 'net_cash_ivsm', 'cash_recv_absb_ivsm', 'cash_recv_sub_absb_shah', 'loan_recv',
            'cash_recv_bond_iss', 'oth_cash_recv_fin', 'cash_in_fin', 'cash_pay_debt', 'cash_pay_prof_intr',
            'sub_pay_prof_intr', 'oth_cash_pay_fin', 'cash_out_fin', 'net_cash_fin', 'er_chg_efft_cash_eq',
            'cash_eq_net_incr', 'cash_eq', 'bgng_cash_eq_bal', 'end_cash_eq_bal', 'gant_loan_advm_redc',
            'dpst_pboc_intb_redc', 'oth_fin_lend_amt_redc', 'avl_sale_finl_ast_incr', 'net_prof', 'ast_ipoa_prep',
            'fix_ipoa_depr', 'imtr_ast_shr', 'long_prep_fee_shr', 'prep_fee_redc', 'pre_fee_incr',
            'fix_immt_oth_ast_loss', 'fix_ipoa_depr_abnd_loss', 'fv_chg_loss', 'fin_fee', 'ivsm_loss',
            'defr_inct_ast_redc', 'defr_inct_liab_incr', 'inv_redc', 'oper_recv_proj_redc', 'oper_recv_proj_incr',
            'oth', 'debt_tran_capt', 'one_traf_corp_bond', 'fin_leas_fix_ipoa', 'cash_end_bal', 'cash_bgng_bal',
            'cash_eqvl_end_bal', 'cash_eqvl_bgng_bal', 'cash_cash_eqvl_net_incr',
        ]

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "rept_type": rept_type,
            "rept_merg_flag": rept_merg_flag,
            "strt_date": strt_date,
            "end_date": end_date,
            "date_type": date_type,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_cfst", **params)
    else:
        warnings.warn("函数[get_cfst]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_proft(scr_num_list, rept_type=None, rept_merg_flag=None, strt_date='19900101', end_date=None, date_type='1',
              cols=None, rslt_type=0):
    """
    1、根据2007年新会计准则制定的合并利润表模板，收集了2007年以来沪深上市公司定期报告中各个会计期间的利润表数据
    ； 2、仅收集合并报表数据，包括本期和上期数据； 3、如果上市公司对外财务报表进行更正，调整，均有采集并对外展示； 4、本表中单位为人民币元； 5、每季更新。

    """

    int_param = []
    float_param = [
        'bus_incm', 'inpt_oper_incm', 'intr_incm', 'has_earn_prem', 'chag_cms_incm', 'bus_cost',
        'inpt_oper_cost', 'intr_pay', 'chag_cms_pay', 'surr_amt', 'comp_pay_namt', 'feth_inst_rsrv_namt',
        'inpy_divd_pay', 'resr_fee', 'bus_tax_atta', 'sale_fee', 'mag_fee', 'fin_fee', 'imfs_loss',
        'fair_val_chg', 'ivsm_incm_chg', 'jovs_ivsm_incm_chg', 'exch_incm', 'bus_prof', 'otfb_incm',
        'otfb_pay', 'nofw_ast_deal_loss', 'prof_pamt', 'inct_fee', 'net_prof', 'attr_prn_comr_net_prof',
        'min_shah_incm', 'basc_eps', 'diln_eps', 'oth_comp_eps', 'comp_eps', 'attr_prn_comr_comp_eps',
        'attr_mish_comp_eps', 'intr_net_incm', 'net_chag_cms_incm', 'oth_busi_incm', 'busi_aep',
        'oth_busi_cost', 'insr_busi_incm', 'resr_fee_incm', 'cede_prem', 'feth_uexp_duty_rsrv',
        'spba_comp_pay', 'feth_insr_duty_rsrv', 'spba_insr_duty_rsrv', 'spba_resr_fee',
        'agt_bs_secb_net_incm', 'scr_bs_undb_net_incm', 'bent_cust_asmb_net_incm', 'ast_dsps_payf',
        'oth_payf', 'cont_oper_net_prof', 'end_oper_net_prof', 'ent_cust_asmb_net_incm'
    ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({
            'bus_incm', 'inpt_oper_incm', 'intr_incm', 'has_earn_prem', 'chag_cms_incm', 'bus_cost', 'inpt_oper_cost',
            'intr_pay', 'chag_cms_pay', 'surr_amt', 'comp_pay_namt', 'feth_inst_rsrv_namt', 'inpy_divd_pay',
            'resr_fee', 'bus_tax_atta', 'sale_fee', 'mag_fee', 'fin_fee', 'imfs_loss', 'fair_val_chg', 'ivsm_incm_chg',
            'jovs_ivsm_incm_chg', 'exch_incm', 'bus_prof', 'otfb_incm', 'otfb_pay', 'nofw_ast_deal_loss', 'prof_pamt',
            'inct_fee', 'net_prof', 'attr_prn_comr_net_prof', 'min_shah_incm', 'basc_eps', 'diln_eps', 'oth_comp_eps',
            'comp_eps', 'attr_prn_comr_comp_eps', 'attr_mish_comp_eps', 'intr_net_incm', 'net_chag_cms_incm',
            'oth_busi_incm', 'busi_aep', 'oth_busi_cost', 'insr_busi_incm', 'resr_fee_incm', 'cede_prem',
            'feth_uexp_duty_rsrv', 'spba_comp_pay', 'feth_insr_duty_rsrv', 'spba_insr_duty_rsrv', 'spba_resr_fee',
            'agt_bs_secb_net_incm', 'scr_bs_undb_net_incm', 'bent_cust_asmb_net_incm', 'ast_dsps_payf', 'oth_payf',
            'cont_oper_net_prof', 'end_oper_net_prof', 'ent_cust_asmb_net_incm'}.intersection(
            set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'scr_abbr', 'mkt_code', 'rept_type', 'affi_date', 'end_date', 'rept_merg_flag',
            'rept_adj_flag', 'ins_attr_code', 'bus_incm', 'inpt_oper_incm', 'intr_incm', 'has_earn_prem',
            'chag_cms_incm', 'bus_cost', 'inpt_oper_cost', 'intr_pay', 'chag_cms_pay', 'surr_amt', 'comp_pay_namt',
            'feth_inst_rsrv_namt', 'inpy_divd_pay', 'resr_fee', 'bus_tax_atta', 'sale_fee', 'mag_fee', 'fin_fee',
            'imfs_loss', 'fair_val_chg', 'ivsm_incm_chg', 'jovs_ivsm_incm_chg', 'exch_incm', 'bus_prof', 'otfb_incm',
            'otfb_pay', 'nofw_ast_deal_loss', 'prof_pamt', 'inct_fee', 'net_prof', 'attr_prn_comr_net_prof',
            'min_shah_incm', 'basc_eps', 'diln_eps', 'oth_comp_eps', 'comp_eps', 'attr_prn_comr_comp_eps',
            'attr_mish_comp_eps', 'intr_net_incm', 'net_chag_cms_incm', 'oth_busi_incm', 'busi_aep', 'oth_busi_cost',
            'insr_busi_incm', 'resr_fee_incm', 'cede_prem', 'feth_uexp_duty_rsrv', 'spba_comp_pay',
            'feth_insr_duty_rsrv', 'spba_insr_duty_rsrv', 'spba_resr_fee', 'agt_bs_secb_net_incm',
            'scr_bs_undb_net_incm', 'bent_cust_asmb_net_incm', 'ast_dsps_payf', 'oth_payf', 'cont_oper_net_prof',
            'end_oper_net_prof', 'ent_cust_asmb_net_incm'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "rept_type": rept_type,
            "rept_merg_flag": rept_merg_flag,
            "strt_date": strt_date,
            "end_date": end_date,
            "date_type": date_type,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_proft", **params)
    else:
        warnings.warn("函数[get_proft]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fin_indx(scr_num_list, rept_type=None, strt_date='19900101', end_date=None, date_type='1', cols=None,
                 rslt_type=0):
    """
    根据上市公司披露的财务数据计算的财务指标。

    """

    int_param = []
    float_param = [
        'basc_eps', 'dilu_eps', 'eps_end_capt_dilt', 'eps_ttm', 'bps', 'ps_busi_tot_incm', 'ps_busi_incm',
        'ps_busi_incm_ttm', 'ps_busi_prof', 'ps_btax_prof', 'ps_capi_resf', 'ps_surp_resf', 'ps_resf',
        'ps_un_assn_prof', 'ps_dpsi_payf', 'ps_net_cash_oper', 'ps_net_cash_oper_ttm', 'ps_net_cash',
        'ps_net_cash_ttm', 'ps_corp_cash', 'ps_shah_cash', 'roe_avg', 'roe_wght', 'roe_dilt',
        'roe_dect_dilt', 'roe_dect_wght', 'roe_ttm', 'roa', 'roa_ttm', 'jroa', 'jroa_ttm', 'roic', 'npm',
        'npm_ttm', 'gpm', 'gpm_ttm', 'cost_rate', 'pd_rate', 'pd_rate_ttm', 'net_prof_rate',
        'net_prof_rate_ttm', 'busi_prof_rate', 'busi_prof_rate_ttm', 'btax_prof_rate', 'btax_prof_rate_ttm',
        'bus_cost_rate', 'bus_cost_rate_ttm', 'sale_fee_rate', 'sale_fee_rate_ttm', 'mag_fee_rate',
        'mag_fee_rate_ttm', 'fin_fee_rate', 'fin_fee_rate_ttm', 'imfs_loss_rate', 'imfs_loss_rate_ttm',
        'attr_prn_net_prof', 'dect_pl_net_prof', 'btax_prof', 'btax_depr_prof', 'tot_busi_prof_rate',
        'cost_prof_rate', 'curr_rati', 'qr', 'over_qr', 'debt_equity_rati', 'prn_shah_evol_div_liab_tot',
        'prn_shah_evol_div_ibrg_debt', 'nv_debt_rate', 'nv_div_ibrg_debt', 'nv_div_net_debt',
        'btax_depr_prof_div_liab_tot', 'net_cash_oper_div_liab_tot', 'net_cash_oper_div_ibrg_debt',
        'net_cash_oper_div_curr_debt', 'net_cash_oper_div_net_debt', 'intr_prot_mult', 'liab_oper_cptl_rate',
        'cash_debt_rati', 'basc_eps_yoy_grow', 'dilu_eps_yoy_grow', 'busi_incm_yoy_grow',
        'busi_incm_3year_cmpl_grow_rate', 'busi_prof_yoy_grow', 'prof_pamt_yoy_grow', 'net_prof_yoy_grow',
        'prn_net_prof_yoy_grow', 'prn_net_prof_dect_yoy_grow', 'prn_net_prof_3yr_cmpl_grat',
        'form_5yr_prn_net_prof_avg_incr', 'net_cash_oper_yoy_grow', 'ps_net_cash_oper_yoy_grow',
        'roe_dilt_yoy_grow', 'nv_yoy_grow', 'tot_ast_yoy_grow', 'ps_nv_relt_grow_rate',
        'prn_shah_evol_relt_grow_rate', 'ast_sum_relt_grow_rate', 'cont_grow_rate', 'busi_pd',
        'inv_turn_rate', 'inv_turn_days', 'recv_acct_turn_rate', 'recv_acct_turn_days',
        'payb_acct_turn_rate', 'payb_acct_turn_days', 'curr_ast_turn_rate', 'fix_ast_turn_rate',
        'shah_equi_turn_rate', 'tot_ast_turn_rate', 'cash_recv_sale_div_busi_incm',
        'cash_sale_div_busi_incm_ttm', 'net_cash_oper_div_busi_incm', 'net_cash_oper_div_bus_incm_ttm',
        'net_cash_oper_div_payf_oper', 'net_csh_oper_div_payf_oper_ttm', 'cptl_pay_div_depr',
        'cash_eq_net_incr', 'net_cash_oper', 'cash_recv_sale', 'cash_flow', 'net_prof_cash',
        'busi_incm_cash', 'tot_ast_cash_recc', 'ps_cash_eq', 'ps_divd', 'divd_prot_mult',
        'cash_divd_prot_mult', 'divd_pay_rate', 'dpsi_surp_rate', 'ast_liab_rate', 'curr_ast_div_tot_ast',
        'not_liqd_ast_tot_ast', 'fix_ast_rati', 'immt_ast_rati', 'long_loan_div_tot_ast',
        'payb_bond_div_tot_ast', 'prn_shah_evol_div_all_cptl', 'ibrg_debt_div_all_cptl',
        'liqd_liab_div_liab_tot', 'not_liqd_liab_div_liab_tot', 'shah_equi_rate', 'equi_mult', 'oper_cptl',
        'long_liab_div_shah_equi_tot', 'long_ast_fit_rate', 'payf_oper_div_prof_pamt',
        'payf_oper_div_prof_pamt_ttm', 'jovt_ivsm_payf_div_prof_pamt', 'jovt_ivsm_payf_div_prof_ttm',
        'val_chg_div_prof_pamt', 'val_chg_div_prof_pamt_ttm', 'nopr_net_amt_div_prof_amt',
        'nopr_net_amt_div_prof_pamt_ttm', 'inct_div_prof_pamt', 'dect_pl_net_prof_div_net_prof',
        'equi_mult_dupont', 'prn_shah_net_prof_div_net_prof', 'net_prof_div_busi_tot_incm',
        'net_prof_div_prof_pamt', 'prof_pamt_div_btax_prof', 'btax_prof_div_busi_tot_incm'
    ]
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(
            {'basc_eps', 'dilu_eps', 'eps_end_capt_dilt', 'eps_ttm', 'bps', 'ps_busi_tot_incm', 'ps_busi_incm',
             'ps_busi_incm_ttm', 'ps_busi_prof', 'ps_btax_prof', 'ps_capi_resf', 'ps_surp_resf', 'ps_resf',
             'ps_un_assn_prof', 'ps_dpsi_payf', 'ps_net_cash_oper', 'ps_net_cash_oper_ttm', 'ps_net_cash',
             'ps_net_cash_ttm', 'ps_corp_cash', 'ps_shah_cash', 'roe_avg', 'roe_wght', 'roe_dilt', 'roe_dect_dilt',
             'roe_dect_wght', 'roe_ttm', 'roa', 'roa_ttm', 'jroa', 'jroa_ttm', 'roic', 'npm', 'npm_ttm', 'gpm',
             'gpm_ttm', 'cost_rate', 'pd_rate', 'pd_rate_ttm', 'net_prof_rate', 'net_prof_rate_ttm', 'busi_prof_rate',
             'busi_prof_rate_ttm', 'btax_prof_rate', 'btax_prof_rate_ttm', 'bus_cost_rate', 'bus_cost_rate_ttm',
             'sale_fee_rate', 'sale_fee_rate_ttm', 'mag_fee_rate', 'mag_fee_rate_ttm', 'fin_fee_rate',
             'fin_fee_rate_ttm', 'imfs_loss_rate', 'imfs_loss_rate_ttm', 'attr_prn_net_prof', 'dect_pl_net_prof',
             'btax_prof', 'btax_depr_prof', 'tot_busi_prof_rate', 'cost_prof_rate', 'curr_rati', 'qr', 'over_qr',
             'debt_equity_rati', 'prn_shah_evol_div_liab_tot', 'prn_shah_evol_div_ibrg_debt', 'nv_debt_rate',
             'nv_div_ibrg_debt', 'nv_div_net_debt', 'btax_depr_prof_div_liab_tot', 'net_cash_oper_div_liab_tot',
             'net_cash_oper_div_ibrg_debt', 'net_cash_oper_div_curr_debt', 'net_cash_oper_div_net_debt',
             'intr_prot_mult', 'liab_oper_cptl_rate', 'cash_debt_rati', 'basc_eps_yoy_grow', 'dilu_eps_yoy_grow',
             'busi_incm_yoy_grow', 'busi_incm_3year_cmpl_grow_rate', 'busi_prof_yoy_grow', 'prof_pamt_yoy_grow',
             'net_prof_yoy_grow', 'prn_net_prof_yoy_grow', 'prn_net_prof_dect_yoy_grow', 'prn_net_prof_3yr_cmpl_grat',
             'form_5yr_prn_net_prof_avg_incr', 'net_cash_oper_yoy_grow', 'ps_net_cash_oper_yoy_grow',
             'roe_dilt_yoy_grow', 'nv_yoy_grow', 'tot_ast_yoy_grow', 'ps_nv_relt_grow_rate',
             'prn_shah_evol_relt_grow_rate', 'ast_sum_relt_grow_rate', 'cont_grow_rate', 'busi_pd', 'inv_turn_rate',
             'inv_turn_days', 'recv_acct_turn_rate', 'recv_acct_turn_days', 'payb_acct_turn_rate',
             'payb_acct_turn_days', 'curr_ast_turn_rate', 'fix_ast_turn_rate', 'shah_equi_turn_rate',
             'tot_ast_turn_rate', 'cash_recv_sale_div_busi_incm', 'cash_sale_div_busi_incm_ttm',
             'net_cash_oper_div_busi_incm', 'net_cash_oper_div_bus_incm_ttm', 'net_cash_oper_div_payf_oper',
             'net_csh_oper_div_payf_oper_ttm', 'cptl_pay_div_depr', 'cash_eq_net_incr', 'net_cash_oper',
             'cash_recv_sale', 'cash_flow', 'net_prof_cash', 'busi_incm_cash', 'tot_ast_cash_recc', 'ps_cash_eq',
             'ps_divd', 'divd_prot_mult', 'cash_divd_prot_mult', 'divd_pay_rate', 'dpsi_surp_rate', 'ast_liab_rate',
             'curr_ast_div_tot_ast', 'not_liqd_ast_tot_ast', 'fix_ast_rati', 'immt_ast_rati', 'long_loan_div_tot_ast',
             'payb_bond_div_tot_ast', 'prn_shah_evol_div_all_cptl', 'ibrg_debt_div_all_cptl', 'liqd_liab_div_liab_tot',
             'not_liqd_liab_div_liab_tot', 'shah_equi_rate', 'equi_mult', 'oper_cptl', 'long_liab_div_shah_equi_tot',
             'long_ast_fit_rate', 'payf_oper_div_prof_pamt', 'payf_oper_div_prof_pamt_ttm',
             'jovt_ivsm_payf_div_prof_pamt', 'jovt_ivsm_payf_div_prof_ttm', 'val_chg_div_prof_pamt',
             'val_chg_div_prof_pamt_ttm', 'nopr_net_amt_div_prof_amt', 'nopr_net_amt_div_prof_pamt_ttm',
             'inct_div_prof_pamt', 'dect_pl_net_prof_div_net_prof', 'equi_mult_dupont',
             'prn_shah_net_prof_div_net_prof', 'net_prof_div_busi_tot_incm', 'net_prof_div_prof_pamt',
             'prof_pamt_div_btax_prof', 'btax_prof_div_busi_tot_incm'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_num', 'scr_code', 'scr_abbr', 'mkt_code', 'rept_type', 'affi_date', 'end_date',
            'basc_eps', 'dilu_eps', 'eps_end_capt_dilt', 'eps_ttm', 'bps', 'ps_busi_tot_incm', 'ps_busi_incm',
            'ps_busi_incm_ttm', 'ps_busi_prof', 'ps_btax_prof', 'ps_capi_resf', 'ps_surp_resf', 'ps_resf',
            'ps_un_assn_prof', 'ps_dpsi_payf', 'ps_net_cash_oper', 'ps_net_cash_oper_ttm', 'ps_net_cash',
            'ps_net_cash_ttm', 'ps_corp_cash', 'ps_shah_cash', 'roe_avg', 'roe_wght', 'roe_dilt', 'roe_dect_dilt',
            'roe_dect_wght', 'roe_ttm', 'roa', 'roa_ttm', 'jroa', 'jroa_ttm', 'roic', 'npm', 'npm_ttm', 'gpm',
            'gpm_ttm', 'cost_rate', 'pd_rate', 'pd_rate_ttm', 'net_prof_rate', 'net_prof_rate_ttm', 'busi_prof_rate',
            'busi_prof_rate_ttm', 'btax_prof_rate', 'btax_prof_rate_ttm', 'bus_cost_rate', 'bus_cost_rate_ttm',
            'sale_fee_rate', 'sale_fee_rate_ttm', 'mag_fee_rate', 'mag_fee_rate_ttm', 'fin_fee_rate',
            'fin_fee_rate_ttm', 'imfs_loss_rate', 'imfs_loss_rate_ttm', 'attr_prn_net_prof', 'dect_pl_net_prof',
            'btax_prof', 'btax_depr_prof', 'tot_busi_prof_rate', 'cost_prof_rate', 'curr_rati', 'qr', 'over_qr',
            'debt_equity_rati', 'prn_shah_evol_div_liab_tot', 'prn_shah_evol_div_ibrg_debt', 'nv_debt_rate',
            'nv_div_ibrg_debt', 'nv_div_net_debt', 'btax_depr_prof_div_liab_tot', 'net_cash_oper_div_liab_tot',
            'net_cash_oper_div_ibrg_debt', 'net_cash_oper_div_curr_debt', 'net_cash_oper_div_net_debt',
            'intr_prot_mult', 'liab_oper_cptl_rate', 'cash_debt_rati', 'basc_eps_yoy_grow', 'dilu_eps_yoy_grow',
            'busi_incm_yoy_grow', 'busi_incm_3year_cmpl_grow_rate', 'busi_prof_yoy_grow', 'prof_pamt_yoy_grow',
            'net_prof_yoy_grow', 'prn_net_prof_yoy_grow', 'prn_net_prof_dect_yoy_grow', 'prn_net_prof_3yr_cmpl_grat',
            'form_5yr_prn_net_prof_avg_incr', 'net_cash_oper_yoy_grow', 'ps_net_cash_oper_yoy_grow',
            'roe_dilt_yoy_grow', 'nv_yoy_grow', 'tot_ast_yoy_grow', 'ps_nv_relt_grow_rate',
            'prn_shah_evol_relt_grow_rate', 'ast_sum_relt_grow_rate', 'cont_grow_rate', 'busi_pd', 'inv_turn_rate',
            'inv_turn_days', 'recv_acct_turn_rate', 'recv_acct_turn_days', 'payb_acct_turn_rate', 'payb_acct_turn_days',
            'curr_ast_turn_rate', 'fix_ast_turn_rate', 'shah_equi_turn_rate', 'tot_ast_turn_rate',
            'cash_recv_sale_div_busi_incm', 'cash_sale_div_busi_incm_ttm', 'net_cash_oper_div_busi_incm',
            'net_cash_oper_div_bus_incm_ttm', 'net_cash_oper_div_payf_oper', 'net_csh_oper_div_payf_oper_ttm',
            'cptl_pay_div_depr', 'cash_eq_net_incr', 'net_cash_oper', 'cash_recv_sale', 'cash_flow', 'net_prof_cash',
            'busi_incm_cash', 'tot_ast_cash_recc', 'ps_cash_eq', 'ps_divd', 'divd_prot_mult', 'cash_divd_prot_mult',
            'divd_pay_rate', 'dpsi_surp_rate', 'ast_liab_rate', 'curr_ast_div_tot_ast', 'not_liqd_ast_tot_ast',
            'fix_ast_rati', 'immt_ast_rati', 'long_loan_div_tot_ast', 'payb_bond_div_tot_ast',
            'prn_shah_evol_div_all_cptl', 'ibrg_debt_div_all_cptl', 'liqd_liab_div_liab_tot',
            'not_liqd_liab_div_liab_tot', 'shah_equi_rate', 'equi_mult', 'oper_cptl', 'long_liab_div_shah_equi_tot',
            'long_ast_fit_rate', 'payf_oper_div_prof_pamt', 'payf_oper_div_prof_pamt_ttm',
            'jovt_ivsm_payf_div_prof_pamt', 'jovt_ivsm_payf_div_prof_ttm', 'val_chg_div_prof_pamt',
            'val_chg_div_prof_pamt_ttm', 'nopr_net_amt_div_prof_amt', 'nopr_net_amt_div_prof_pamt_ttm',
            'inct_div_prof_pamt', 'dect_pl_net_prof_div_net_prof', 'equi_mult_dupont', 'prn_shah_net_prof_div_net_prof',
            'net_prof_div_busi_tot_incm', 'net_prof_div_prof_pamt', 'prof_pamt_div_btax_prof',
            'btax_prof_div_busi_tot_incm',
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "rept_type": rept_type,
            "strt_date": strt_date,
            "end_date": end_date,
            "date_type": date_type,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fin_indx", **params)
    else:
        warnings.warn("函数[get_fin_indx]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_stk_plac_info(scr_num_list, affi_strt_date='19900101', affi_end_date=None, strt_equi_reg_date='19900101',
                      end_equi_reg_date=None, cols=None, rslt_type=0):
    """
    获取股票历次配股的基本信息包含每次配股方案的内容、方案进度、历史配股预案公布次数以及最终是否配股成功。

    """

    int_param = ['plac_vol', 'plac_capt_radx']
    float_param = ['ps_plac_num', 'plac_prc']
    if cols:
        int_param = list({'plac_vol', 'plac_capt_radx'}.intersection(set(convert_fields(cols))))
        float_param = list({'ps_plac_num', 'plac_prc'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'excr_date', 'affi_date', 'equi_reg_date', 'ps_plac_num',
            'plac_prc', 'plac_scr_code', 'plac_pay_strt_date', 'plac_pay_end_date', 'plac_list_date', 'plac_vol',
            'plac_capt_radx',
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "affi_strt_date": affi_strt_date,
            "affi_end_date": affi_end_date,
            "strt_equi_reg_date": strt_equi_reg_date,
            "end_equi_reg_date": end_equi_reg_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stk_plac_info", **params)
    else:
        warnings.warn("函数[get_stk_plac_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_stk_divd_info(scr_num_list=None, excr_date=None, affi_strt_date='19900101', affi_end_date=None,
                      reg_strt_date='19900101', reg_end_date=None, bons_type=None, cols=None, rslt_type=0):
    """
    获取股票历次分红(派现、送股、转增股)的基本信息包含历次分红预案的内容、实施进展情况以及历史宣告分红次数。

    """

    int_param = ['bons_type', 'bons_capt_radx']
    float_param = ['ps_divd', 'atax_ps_divd', 'ps_gant_num', 'ps_tran_incr_num', 'ps_divd_fcrr', 'atax_ps_divd_fcrr']
    if cols:
        int_param = list({'bons_type', 'bons_capt_radx'}.intersection(set(convert_fields(cols))))
        float_param = list(
            {'ps_divd', 'atax_ps_divd', 'ps_gant_num',
             'ps_tran_incr_num', 'ps_divd_fcrr', 'atax_ps_divd_fcrr'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date', 'end_date', 'bons_type', 'equi_reg_date',
            'equi_arvd_date', 'excr_date', 'ps_divd', 'atax_ps_divd', 'ps_gant_num', 'ps_tran_incr_num',
            'gant_list_date', 'ps_divd_fcrr', 'atax_ps_divd_fcrr', 'crrc_code', 'cdvd_dist_date', 'bons_capt_radx'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "excr_date": excr_date,
        "affi_strt_date": affi_strt_date,
        "affi_end_date": affi_end_date,
        "reg_strt_date": reg_strt_date,
        "reg_end_date": reg_end_date,
        "bons_type": bons_type,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_stk_divd_info", **params)


def get_stk_addi(scr_num_list=None, rspl_affi_strt_date='19900101', rspl_affi_end_date=None,
                 glmt_rsln_affi_strt_date='19900101', glmt_rsln_affi_end_date=None,
                 addi_type_code=None, cols=None, rslt_type=0):
    """
    获取历次增发方案以及实施信息包括发行价、发行量、发行费用的相关信息。

    """

    int_param = ['list_cir_capt']
    float_param = [
        'iss_prc_topl', 'iss_prc_lowl', 'iss_vol_topl', 'iss_vol_lowl', 'onle_purs_topl', 'olds_ratn_rati',
        'parv', 'iss_prc', 'iss_vol', 'iss_tot_mval', 'iss_fee_gamt', 'coll_cptl_tot_amt',
        'coll_cptl_net_amt'
    ]
    if cols:
        int_param = list({'list_cir_capt'}.intersection(set(convert_fields(cols))))
        float_param = list(
            {'iss_prc_topl', 'iss_prc_lowl', 'iss_vol_topl', 'iss_vol_lowl', 'onle_purs_topl',
             'olds_ratn_rati', 'parv', 'iss_prc', 'iss_vol', 'iss_tot_mval', 'iss_fee_gamt',
             'coll_cptl_tot_amt', 'coll_cptl_net_amt'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'addi_type_code', 'rspl_affi_date', 'glmt_rsln_affi_date',
            'sasac_aprv_affi_date', 'csrc_aprv_affi_date', 'rspl_eff_strt_date', 'rspl_eff_end_date', 'uw_strt_date',
            'uw_end_date', 'main_uw_name', 'vice_main_uw_name', 'iss_prc_topl', 'iss_prc_lowl', 'iss_vol_topl',
            'iss_vol_lowl', 'onle_iss_date', 'onle_purs_code', 'onle_purs_topl', 'olds_ratn_rati', 'olds_ratn_date',
            'olds_ratn_purs_code', 'parv', 'iss_prc', 'iss_vol', 'iss_tot_mval', 'iss_fee_gamt', 'coll_cptl_tot_amt',
            'coll_cptl_net_amt', 'list_cir_capt', 'rstk_list_date', 'equi_reg_date', 'crrc_code', 'affi_date',
            'plan_chg_type_code',
        ]
    params = {
        "scr_num_list": scr_num_list,
        "rspl_affi_strt_date": rspl_affi_strt_date,
        "rspl_affi_end_date": rspl_affi_end_date,
        "glmt_rsln_affi_strt_date": glmt_rsln_affi_strt_date,
        "glmt_rsln_affi_end_date": glmt_rsln_affi_end_date,
        "addi_type_code": addi_type_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_stk_addi", **params)


def get_ins_mngr_info(scr_num_list, affi_strt_date='19900101', affi_end_date=None, cols=None, rslt_type=0):
    """
    获取上市公司历届管理层信息，包括届次，职务，任期起始时间，任期结束时间等（含科创板）。

    """

    int_param = ['aoff_sesn']
    float_param = []
    if cols:
        int_param = list({'aoff_sesn'}.intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "affi_strt_date": affi_strt_date,
            "affi_end_date": affi_end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_ins_mngr_info", **params)
    else:
        warnings.warn("函数[get_ins_mngr_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_ins_mngr_chg(scr_num_list, affi_strt_date='19900101', affi_end_date=None, cols=None, rslt_type=0):
    """
    获取公司高管变更信息，包含变更类型、变更职位及教育背景等信息（含科创板）。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date', 'name', 'birt_date', 'aoff_date', 'leav_date',
            'pos_code', 'pos_type_code', 'aoff_chg_type_code', 'leav_resn', 'ins_fn', 'indv_intr'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "affi_strt_date": affi_strt_date,
            "affi_end_date": affi_end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_ins_mngr_chg", **params)
    else:
        warnings.warn("函数[get_ins_mngr_chg]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_ins_capt_chg(scr_num_list=None, ins_num=None, intv_strt_date=None, intv_end_date=None, cols=None,
                     rslt_type=None):
    """
    获取上市公司股本结构及历次股本变动数据（含科创板）。

    输入参数：
    :param str|list scr_num_list : 证券编码列表，如['000001.XSHE']
    :param str ins_num : 机构编码
    :param str intv_strt_date : 区间开始日期，格式'YYYYMMDD'，参考日期trad_date，默认"19000101"
    :param str intv_end_date : 区间结束日期，格式'YYYYMMDD'，参考日期trad_date，默认"now"
    :param str|list cols : 筛选字段，默认返回所有
    :param int rslt_type : 数据返回结果类型，0-pandas.DataFrame，1-numpy.ndarray，默认0

    输出参数：
    :param str scr_code : 交易代码，如'000001',
    :param str scr_num : 证券编码，如'000001.XSHE',
    :param str scr_abbr : 证券简称,
    :param str mkt_code : 交易市场代码，取值字典项：
NEEQ  全国中小企业股份转让系统
XSHE  深圳证券交易所
XSHG 上海证券交易所
XHKG  香港交易所,
    :param str ins_num : 机构编码,
    :param str trad_date : 交易日,
    :param int tot_capt : 总股本,
    :param int tot_cir_capt : 总流通股本,
    :param int astk_capt : A股本,
    :param int astk_cir_capt : A股流通股本,
    :param int bstk_capt : B股股本,
    :param int bstk_cir_capt : B股流通股,
    :param int hstk_capt : H股股本,
    :param int hstk_cir_capt : H股流通股本,
    :param float tlc_capt : 有限售条件股份合计,
    :param float ntlc_capt : 无限售流通股份合计,
    :param int astk_tlc_capt : A股自由流通股本,
    :param float astk_ntlc_capt : A股自由流通市值,

    返回数据类型：


    代码调用:


    结果输出:

    """

    int_param = ['tot_capt', 'tot_cir_capt', 'astk_capt', 'astk_cir_capt', 'bstk_capt', 'bstk_cir_capt', 'hstk_capt',
                 'hstk_cir_capt', 'astk_tlc_capt']
    float_param = ['tlc_capt', 'ntlc_capt', 'astk_ntlc_capt']
    if cols:
        int_param = list(
            {'tot_capt', 'tot_cir_capt', 'astk_capt', 'astk_cir_capt', 'bstk_capt', 'bstk_cir_capt', 'hstk_capt',
             'hstk_cir_capt', 'astk_tlc_capt'}.intersection(set(convert_fields(cols))))
        float_param = list({'tlc_capt', 'ntlc_capt', 'astk_ntlc_capt'}.intersection(set(convert_fields(cols))))
    params = {
        "scr_num_list": scr_num_list,
        "ins_num": ins_num,
        "intv_strt_date": intv_strt_date,
        "intv_end_date": intv_end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_ins_capt_chg", **params)


def get_ins_top10_shah(scr_num_list=None, strt_date=None, end_date=None, cols=None, rslt_type=0):
    """
    获取公司十大股东信息，包含持股数以及持股比例（含科创板）。

    """

    int_param = ['shah_rank', 'hold_num', 'lmt_sale_stk_vol', 'ustk_vol']
    float_param = ['occp_tscp_rati']
    if cols:
        int_param = list(
            {'shah_rank', 'hold_num', 'lmt_sale_stk_vol', 'ustk_vol'}.intersection(set(convert_fields(cols))))
        float_param = list({'occp_tscp_rati'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'end_date', 'affi_date', 'shah_rank', 'shah_name',
            'hold_num', 'occp_tscp_rati', 'lmt_sale_stk_vol', 'ustk_vol', 'capt_char_desc', 'shah_clas_num',
            'shah_attr_code'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_ins_top10_shah", **params)


def get_ins_top10_cir_shah(scr_num_list=None, strt_date=None, end_date=None, cols=None, rslt_type=0):
    """
    获取公司十大流通股东信息，包含持股数以及持股比例。

    """

    int_param = ['shah_rank', 'ustk_vol']
    float_param = ['occp_tscp_rati']
    if cols:
        int_param = list({'shah_rank', 'ustk_vol'}.intersection(set(convert_fields(cols))))
        float_param = list({'occp_tscp_rati'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'end_date', 'affi_date', 'shah_rank', 'shah_name',
            'ustk_vol', 'occp_tscp_rati'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_ins_top10_cir_shah", **params)


def get_rstk_drrt(scr_num_list=None, strt_drrt_date='19900101', end_drrt_date=None,
                  affi_strt_date='19900101', affi_end_date=None, cols=None, rslt_type=0):
    """
    获取上市公司限售股流通时间、数量与股份性质等信息（含科创板）。

    """

    int_param = ['drrt_stk_src_code']
    float_param = []
    if cols:
        int_param = list({'drrt_stk_src_code'}.intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date', 'drrt_date', 'drrt_stk_src_code'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "strt_drrt_date": strt_drrt_date,
        "end_drrt_date": end_drrt_date,
        "affi_strt_date": affi_strt_date,
        "affi_end_date": affi_end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_rstk_drrt", **params)


def get_rstk_drrt_dtl(scr_num_list=None, strt_cir_date='19900101', end_cir_date=None,
                      affi_strt_date='19900101', affi_end_date=None, cols=None, rslt_type=0):
    """
    获取记录上市公司首次公开发行前股东股份解禁的相关信息（含科创板）。

    """

    int_param = ['cir_stk_vol']
    float_param = []
    if cols:
        int_param = list({'cir_stk_vol'}.intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date', 'shah_onum', 'shah_name', 'cir_strt_date',
            'cir_stk_vol'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "strt_cir_date": strt_cir_date,
        "end_cir_date": end_cir_date,
        "affi_strt_date": affi_strt_date,
        "affi_end_date": affi_end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_rstk_drrt_dtl", **params)


def get_prof_pred(scr_num_list, strt_date='19900101', end_date=None, cols=None, rslt_type=0):
    """
    记录上市公司盈利预测数据。

    """

    int_param = []
    float_param = ['busi_incm', 'busi_cost', 'busi_prof', 'prof_gamt', 'net_prof', 'attr_pcrp_ownr_equi', 'eps', 'bps',
                   'ps_casf']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(
            {'busi_incm', 'busi_cost', 'busi_prof', 'prof_gamt', 'net_prof', 'attr_pcrp_ownr_equi', 'eps', 'bps',
             'ps_casf'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'pred_writ_date', 'pred_writ_ins_num', 'pred_writ_ins_name',
            'pred_ann', 'busi_incm', 'busi_cost', 'busi_prof', 'prof_gamt', 'net_prof', 'attr_pcrp_ownr_equi', 'eps',
            'bps', 'ps_casf'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_prof_pred", **params)
    else:
        warnings.warn("函数[get_prof_pred]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_marg_scr(scr_num_list=None, trad_date=None, rels_ins_name=None, cols=None,
                 rslt_type=0):
    """
    获取东方证券、国泰君安、国信证券、华泰证券、上交所、申万宏源、深交所、银河证券、中信证券所公布的每个交易日的可充抵保
    证金标的证券信息。

    """

    int_param = []
    float_param = ['cnvr_rate']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'cnvr_rate'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'trad_date', 'tect_date', 'invl_date',
            'rels_ins_num', 'rels_ins_name', 'cnvr_rate'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "trad_date": trad_date,
            "rels_ins_name": rels_ins_name,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_marg_scr", **params)
    else:
        warnings.warn("函数[get_marg_scr]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_stk_bloc_rep(scr_num_list, strt_date='19900101', end_date=None, bs_flag=None, cols=None,
                     rslt_type=0):
    """
    获取大宗交易申报信息，包括股票代码、申报日期、申报价格、申报数量等信息。

    """

    int_param = ['rep_onum']
    float_param = ['rep_prc', 'rep_vol']
    if cols:
        int_param = list({'rep_onum'}.intersection(set(convert_fields(cols))))
        float_param = list({'rep_prc', 'rep_vol'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'rep_date', 'rep_onum', 'bs_flag', 'rep_prc', 'rep_vol'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "bs_flag": bs_flag,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stk_bloc_rep", **params)
    else:
        warnings.warn("函数[get_stk_bloc_rep]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_stk_bloc_recd(scr_num_list, strt_date='19900101', end_date=None, cols=None, rslt_type=0):
    """
    获取大宗交易信息，包括股票代码、交易日期、成交价、成交量等。

    """

    int_param = ['trd_sn']
    float_param = ['trd_px', 'mtch_vol', 'mtch_amt', 'trd_tims']
    if cols:
        int_param = list({'trd_sn'}.intersection(set(convert_fields(cols))))
        float_param = list({'trd_px', 'mtch_vol', 'mtch_amt', 'trd_tims'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'trad_date', 'trd_sn', 'trd_px', 'mtch_vol', 'mtch_amt',
            'buyr_busp_name', 'sler_busp_name'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stk_bloc_recd", **params)
    else:
        warnings.warn("函数[get_stk_bloc_recd]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_basc_info(scr_num_list=None, fund_list_stat=None, fund_type=None, oper_mode_code=None,
                       strt_list_date=None, end_list_date=None, cols=None, rslt_type=0):
    """
    获取基金的基本档案信息，包含基金名称、交易代码、分级情况、所属类别、上市信息、投资范围等信息。

    """

    int_param = ['mng_ins_num', 'trus_ins_num']
    float_param = ['cir_shr']
    if cols:
        int_param = list({'mng_ins_num', 'trus_ins_num'}.intersection(set(convert_fields(cols))))
        float_param = list({'cir_shr'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'fund_type', 'oper_mode_code', 'qdii_flag', 'etf_flag',
            'lof_flag', 'list_stat', 'mngr_name', 'setp_date', 'at_pd_date', 'list_date', 'delt_date', 'mng_ins_num',
            'mng_ins_abbr', 'mng_ins_name', 'trus_ins_num', 'trus_ins_abbr', 'trus_ins_name', 'ivsm_scop', 'ivsm_tgt',
            'perf_cont_basi', 'cir_shr'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "fund_list_stat": fund_list_stat,
        "fund_type": fund_type,
        "oper_mode_code": oper_mode_code,
        "strt_list_date": strt_list_date,
        "end_list_date": end_list_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_fund_basc_info", **params)


def get_cifd_fund_basc_info(scr_num_list=None, mkt_code=None, cols=None, rslt_type=0):
    """
    获取分级基金的基本信息，包含母、子基金名称、交易代码、分拆比例等信息。

    """

    int_param = []
    float_param = ['spli_rat']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'spli_rat'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'fund_type', 'subf_scr_num', 'subf_scr_code',
            'subf_scr_abbr', 'subf_fund_type', 'subf_mkt_code', 'trac_indx', 'strt_date', 'end_date', 'spli_rat'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "mkt_code": mkt_code,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_cifd_fund_basc_info", **params)


def get_fund_feer_info(scr_num_list, fund_feer_type_code=None, fund_amt=None, strt_date=None, end_date=None,
                       cols=None, rslt_type=0):
    """
    获取基金费率，如管理费、销售费、申购费、赎回费等。

    """

    int_param = []
    float_param = ['fee_amt_lowl', 'fee_amt_topl', 'hldp_almt_lowl', 'hldp_almt_topl', 'fee_rate']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(
            {'fee_amt_lowl', 'fee_amt_topl', 'hldp_almt_lowl',
             'hldp_almt_topl', 'fee_rate'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'strt_date', 'end_date', 'fund_feer_type_code',
            'chag_mode_code', 'cust_type_code', 'fee_amt_lowl', 'fee_amt_topl', 'shr_lowl', 'shr_topl',
            'hldp_almt_lowl', 'hldp_almt_topl', 'date_grul_code', 'fee_rate', 'fee_unit', 'fee_curr', 'fee_rate_des',
            'feer_clfi'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "fund_feer_type_code": fund_feer_type_code,
            "fund_amt": fund_amt,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fund_feer_info", **params)
    else:
        warnings.warn("函数[get_fund_feer_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_rat_info(scr_num_list, rat_src_code=None, strt_date='19900101', end_date=None,
                      cols=None, rslt_type=0):
    """
    获取晨星和银河基金评级信息。

    """

    int_param = []
    float_param = []
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(set([]).intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'rat_src_ins', 'rat_date', 'intv', 'fund_star_rat'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "rat_src_code": rat_src_code,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fund_rat_info", **params)
    else:
        warnings.warn("函数[get_fund_rat_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_nav_info(scr_num_list, fund_clas_abbr=None, strt_date='19900101', end_date=None,
                      cols=None, rslt_type=0):
    """
    获取获取某只基金的历史净值数据(货币型除外),包括了单位份额净值、累计净值与复权净值。

    """

    int_param = ['fund_clas_num']
    float_param = ['unit_nv', 'aggr_unit_nv', 'aft_rstr_unit_nv']
    if cols:
        int_param = list({'fund_clas_num'}.intersection(set(convert_fields(cols))))
        float_param = list({'unit_nv', 'aggr_unit_nv', 'aft_rstr_unit_nv'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'fund_clas_num', 'fund_clas_abbr', 'nv_date', 'unit_nv',
            'aggr_unit_nv', 'aft_rstr_unit_nv'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "fund_clas_abbr": fund_clas_abbr,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fund_nav_info", **params)
    else:
        warnings.warn("函数[get_fund_nav_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_shr_chg(scr_num_list, fund_rept_type=None, strt_date='19900101', end_date=None,
                     cols=None, rslt_type=0):
    """
    获取基金定期报告中开放式基金份额变动情况。

    """

    int_param = []
    float_param = ['bgng_tot_shr', 'end_tot_shr', 'shr_chg', 'spli_cnvr_shr_chg']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'bgng_tot_shr', 'end_tot_shr', 'shr_chg', 'spli_cnvr_shr_chg'}.intersection(
            set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'rept_type', 'affi_date', 'end_date', 'bgng_tot_shr',
            'end_tot_shr', 'shr_chg', 'spli_cnvr_shr_chg'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "fund_rept_type": fund_rept_type,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fund_shr_chg", **params)
    else:
        warnings.warn("函数[get_fund_shr_chg]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_perf_indx(scr_num_list=None, fund_type=None, strt_date=None, end_date=None, cols=None, rslt_type=None):
    """
    获取获取基金相关业绩指标。

    输入参数：
    :param str|list scr_num_list : 证券代码列表，如['600570.XSHG']，该字段为必填项
    :param str|list fund_type : 基金类型。E-股票基金 B-债券基金 M-货币市场基金 F-基金中基金 H-混合基金 O-其他基金
    :param str strt_date : 开始日期，如：'20190101',参考日期trd_date，默认"19000101"
    :param str end_date : 结束日期，如：'20190101',参考日期trd_date，默认"now"
    :param str|list cols : 筛选字段，默认返回所有
    :param int rslt_type : 数据返回结果类型，0-pandas.DataFrame，1-numpy.ndarray，默认0

    输出参数：
    :param str scr_num : 证券编码，如'600570.XSHG',
    :param str scr_code : 证券代码,
    :param str scr_abbr : 证券简称,
    :param str mkt_code : 交易市场代码,
    :param str fund_type : 基金类型。E-股票基金 B-债券基金 M-货币市场基金 F-基金中基金 H-混合基金 O-其他基金,
    :param str trd_date : 交易日期，'YYYYMMDD',
    :param float rect_one_mth_shap : 近一月夏普比率,
    :param float rect_thre_mth_shap : 近三月夏普比率,
    :param float rect_half_year_shap : 近六月夏普比率,
    :param float rect_one_year_shap : 近一年夏普比率,
    :param float rect_two_year_shap : 近二年夏普比率,
    :param float rect_thre_year_shap : 近三年夏普比率,
    :param float this_year_shap : 今年以来夏普比率,
    :param float sinc_setp_shap : 成立以来夏普比率,
    :param float rect_one_mth_beta : 近一月贝塔比率,
    :param float rect_thre_mth_beta : 近三月贝塔比率,
    :param float rect_half_year_beta : 近六月贝塔比率,
    :param float rect_one_year_beta : 近一年贝塔比率,
    :param float rect_two_year_beta : 近二年贝塔比率,
    :param float rect_thre_year_beta : 近三年贝塔比率,
    :param float this_year_beta : 今年以来贝塔比率,
    :param float sinc_setp_beta : 成立以来贝塔比率,
    :param float rect_one_mth_jesn : 最近一月詹森比率,
    :param float rect_thre_mth_jesn : 最近三月詹森比率,
    :param float rect_half_year_jesn : 最近六月詹森比率,
    :param float rect_one_year_jesn : 最近一年詹森比率,
    :param float rect_two_year_jesn : 最近两年詹森比率,
    :param float rect_thre_year_jesn : 最近三年詹森比率,
    :param float this_year_jesn : 本年詹森比率,
    :param float sinc_setp_jesn : 成立以来詹森比率,

    返回数据类型：


    代码调用:


    结果输出:

    """

    int_param = []
    float_param = ['rect_one_mth_shap', 'rect_thre_mth_shap', 'rect_half_year_shap', 'rect_one_year_shap',
                   'rect_two_year_shap', 'rect_thre_year_shap', 'this_year_shap', 'sinc_setp_shap', 'rect_one_mth_beta',
                   'rect_thre_mth_beta', 'rect_half_year_beta', 'rect_one_year_beta', 'rect_two_year_beta',
                   'rect_thre_year_beta', 'this_year_beta', 'sinc_setp_beta', 'rect_one_mth_jesn', 'rect_thre_mth_jesn',
                   'rect_half_year_jesn', 'rect_one_year_jesn', 'rect_two_year_jesn', 'rect_thre_year_jesn',
                   'this_year_jesn', 'sinc_setp_jesn']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'rect_one_mth_shap', 'rect_thre_mth_shap', 'rect_half_year_shap', 'rect_one_year_shap',
                            'rect_two_year_shap', 'rect_thre_year_shap', 'this_year_shap', 'sinc_setp_shap',
                            'rect_one_mth_beta', 'rect_thre_mth_beta', 'rect_half_year_beta', 'rect_one_year_beta',
                            'rect_two_year_beta', 'rect_thre_year_beta', 'this_year_beta', 'sinc_setp_beta',
                            'rect_one_mth_jesn', 'rect_thre_mth_jesn', 'rect_half_year_jesn', 'rect_one_year_jesn',
                            'rect_two_year_jesn', 'rect_thre_year_jesn', 'this_year_jesn', 'sinc_setp_jesn'}.intersection(set(convert_fields(cols))))
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "fund_type": fund_type,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fund_perf_indx", **params)
    else:
        warnings.warn("函数[get_fund_perf_indx]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_ast_cfg_info(scr_num_list, strt_date='19900101', end_date=None, cols=None, rslt_type=0):
    """
    获取基金定期披露的资产配置情况，包含了资产净值，资产净值中权益类、现金等资产的市值与占比情况。

    """

    int_param = []
    float_param = ['tot_ast', 'nav', 'stk_mval', 'bond_mval', 'cash_ast', 'stk_mval_nv_pct', 'bond_mval_nv_pct',
                   'cash_ast_nv_pct']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(
            {'tot_ast', 'nav', 'stk_mval', 'bond_mval', 'cash_ast', 'stk_mval_nv_pct', 'bond_mval_nv_pct',
             'cash_ast_nv_pct'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date', 'end_date', 'tot_ast', 'nav', 'stk_mval',
            'bond_mval', 'fund_mval', 'oth_mval', 'stk_mval_nv_pct', 'bond_mval_nv_pct', 'fund_mval_nv_pct',
            'oth_mval_nv_pct'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_fund_ast_cfg_info", **params)
    else:
        warnings.warn("函数[get_fund_ast_cfg_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)


def get_fund_hldp_dtl(scr_num_list=None, hldp_scr_code_mkt=None, hldp_scr_type=None, strt_date='19900101', end_date=None,
                      cols=None, rslt_type=0):
    """
    获取基金定期披露的持仓明细，包含所持有的股票、债券、基金的持仓明细数据。

    """

    int_param = []
    float_param = ['hldp_vol', 'hldp_val', 'ast_rati']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list({'hldp_vol', 'hldp_val', 'ast_rati'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'affi_date', 'end_date', 'hldp_scr_code_mkt',
            'hldp_scr_abbr', 'hldp_mkt_code', 'hldp_scr_type', 'hldp_vol', 'hldp_val', 'ast_rati'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "hldp_scr_code_mkt": hldp_scr_code_mkt,
        "hldp_scr_type": hldp_scr_type,
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_fund_hldp_dtl", **params)


def get_crrc_fund_payf_info(scr_num_list=None, strt_date='19900101', end_date=None, cols=None, rslt_type=0):
    """
    获取某只货币型基金的历史收益情况，包含了每万份收益，七日年化收益率等信息。

    """

    int_param = []
    float_param = ['micp_fund_unit_payf', 'sevn_day_aror', 'unit_net_val']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(
            {'micp_fund_unit_payf', 'sevn_day_aror', 'unit_net_val'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'nv_date', 'micp_fund_unit_payf', 'sevn_day_aror',
            'unit_net_val'
        ]
    params = {
        "scr_num_list": scr_num_list,
        "strt_date": strt_date,
        "end_date": end_date,
        "cols": cols,
        "rslt_type": rslt_type,
        "int_param": int_param,
        "float_param": float_param
    }
    return get_data("get_crrc_fund_payf_info", **params)


def get_etf_daly_pr_info(scr_num_list, strt_trd_date='19900101', end_trd_date=None, cols=None, rslt_type=0):
    """
    获取ETF基金交易日的申赎清单基本信息，包括标的指数名称，上一交易日的现金差额、最小申赎单位净值、单位净值，交易日当
    日的预估现金差额、最小申赎单位、现金替代比例上限、是否允许申购赎回、是否公布IOPV等信息。

    """

    int_param = []
    float_param = ['cash_diff', 'min_pr_unit_nv', 'fund_shr_nv', 'min_pr_unit', 'esti_cash', 'cash_repl_rati_topl',
                   'purs_topl', 'redp_topl']
    if cols:
        int_param = list(set([]).intersection(set(convert_fields(cols))))
        float_param = list(
            {'cash_diff', 'min_pr_unit_nv', 'fund_shr_nv', 'min_pr_unit', 'esti_cash', 'cash_repl_rati_topl',
             'purs_topl', 'redp_topl'}.intersection(set(convert_fields(cols))))
    else:
        cols = [
            'scr_code', 'scr_num', 'scr_abbr', 'mkt_code', 'trd_date', 'cash_diff', 'min_pr_unit_nv', 'fund_shr_nv',
            'min_pr_unit', 'esti_cash', 'cash_repl_rati_topl', 'purs_topl', 'redp_topl', 'pbsh_iopv_flag',
            'purs_redp_perm', 'trac_indx_code', 'trac_indx_abbr', 'is_pbsh_iopv', 'is_pbsh_purs', 'is_pbsh_redp'
        ]
    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_trd_date": strt_trd_date,
            "end_trd_date": end_trd_date,
            "cols": cols,
            "rslt_type": rslt_type,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_etf_daly_pr_info", **params)
    else:
        warnings.warn("函数[get_etf_daly_pr_info]的参数(scr_num_list)为必填项")
        if rslt_type == 0:
            return pd.DataFrame()
        else:
            return np.empty(0)

def get_opt_contr_info(opt_num_list=None, underlying_code=None, mkt_code=None, call_put=None, cols=None):
    """

    """

    int_param = ['opt_contr_code', 'contr_mtp']
    float_param = ['strike_px', 'list_px', 'list_day_ceil', 'list_day_floor']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        pass


    params = {
        "opt_num_list": opt_num_list,
        "underlying_code": underlying_code,
        'mkt_code': mkt_code,
        'call_put': call_put,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_opt_contr_info", **params)

def get_opt_underlying(underlying_code=None, mkt_code=None, cols=None):
    """

    """

    int_param = ['contr_mtp']
    float_param = []
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        pass


    params = {
        "underlying_code": underlying_code,
        'mkt_code': mkt_code,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_opt_underlying", **params)

def get_opt_contr_by_date(underlying_code=None, mkt_code=None, trd_date=None, cols=None):
    """

    """

    int_param = ['opt_contr_code', 'contr_mtp']
    float_param = ['strike_px', 'list_px', 'list_day_ceil', 'list_day_floor']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        pass


    params = {
        "underlying_code": underlying_code,
        'mkt_code': mkt_code,
        'trd_date': trd_date,
        "cols": cols,
        "int_param": int_param,
        "float_param": float_param
    }

    return get_data("get_opt_contr_by_date", **params)

def get_stock_px_limit(scr_num_list=None, strt_date=None, end_date=None, cols=None):
    """

    """

    int_param = []
    float_param = ['preclose_px', 'limit_up', 'limit_down']
    if cols:
        int_param = list(set(int_param).intersection(set(convert_fields(cols))))
        float_param = list(set(float_param).intersection(set(convert_fields(cols))))
    else:
        pass

    if scr_num_list:
        params = {
            "scr_num_list": scr_num_list,
            "strt_date": strt_date,
            "end_date": end_date,
            "cols": cols,
            "int_param": int_param,
            "float_param": float_param
        }
        return get_data("get_stock_px_limit", **params)
    else:
        warnings.warn("函数[get_stock_px_limit]的参数(scr_num_list)为必填项")
        return pd.DataFrame()