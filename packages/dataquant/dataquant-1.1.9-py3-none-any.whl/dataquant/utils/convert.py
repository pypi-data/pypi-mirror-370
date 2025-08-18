# -*- coding: utf-8 -*-
import io
from dataquant.utils.parallel import parallel_df
import pandas as pd
from itertools import groupby


def convert_param(_type, param):
    if param is None:
        return _type()              #返回该类型空值

    return param


def convert_fields(field):
    if field is None:
        return []

    if isinstance(field, list):
        return field

    if isinstance(field, str):
        return [field]

    raise ValueError("字段[{}]类型转换失败，支持[None, str, list]类型，实参类型为[{}]".format(field, type(field)))


def sort_merge_df(df_list, sort_cols, ignore_index=True):
    df = None
    if len(df_list) <= 0:
        return df
    if len(df_list) == 1:
        return df_list[0] # 节省10ms左右

    sorted_dfs = sorted(df_list, key=lambda df: '|'.join(df.iloc[0][sort_cols].astype(str)))
    df = pd.concat(sorted_dfs, ignore_index=ignore_index)
    return df


def sort_merge_df_dic(df_dic, ignore_index=True):
    df = None
    if len(df_dic) <= 0:
        return df
    sorted_dfs = list(zip(*sorted(df_dic.items(),key=lambda kv:kv[0])))[1]
    if len(df_dic) == 1:
        return sorted_dfs[0] # 节省10ms左右
    df = pd.concat(sorted_dfs, ignore_index=ignore_index)
    return df


def split_df(df: pd.DataFrame):
    new_str = df.to_csv(sep='|', header=False, index=False)  # 47ms
    df = pd.read_csv(io.StringIO(new_str.replace('"', '')), header=None, sep='|', dtype='float64')  # 38ms
    return df
