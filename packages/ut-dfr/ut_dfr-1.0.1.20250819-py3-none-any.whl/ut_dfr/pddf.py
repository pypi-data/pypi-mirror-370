# coding=utf-8
from typing import Any, TypeAlias

import pandas as pd
import datetime as dt

from ut_log.log import Log, LogEq

TyPdDf: TypeAlias = pd.DataFrame

TyAny = Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[Any, TyPdDf]
TyStr = str

TnAny = None | TyAny
TnPdDf = None | TyPdDf


def sh_format_as_int_with_leading_zeros(fmt: TyStr):
    # return lambda x: fmt.format(int(x))
    def fnc(x: int):
        return fmt.format(int(x))
    return fnc


def sh_format_as_date(fmt: TyStr):
    # return lambda x: dt.datetime.strptime(x, fmt).date()
    def fnc(x: str):
        return dt.datetime.strptime(x, fmt).date()
    return fnc


class PdDf:
    """ Manage Panda Dataframe
    """
    msg_dic_01: str = "Key '{K}' not found in Dictionary {D}"
    msg_df_01: str = "Panda dataframe Entry with key='{K}' and Value={V} not found"
    msg_df_02: str = "Panda dataframe Entry with key='{K}' and Value={V} not found"

    @staticmethod
    def sh_stmt(d_filter: TyDic, relation: TyStr) -> TyStr:
        key = d_filter.get('key')
        value = d_filter.get('value')
        match relation:
            case 'neq':
                return f"{key} != '{value}'"
            case 'eq':
                return f"{key} == '{value}'"
            case _:
                return ''

    @classmethod
    def filter_by_query(cls, df: TyPdDf, d_filter: TyDic, relation: TyStr) -> TyPdDf:
        stmt = cls.sh_stmt(d_filter, relation)
        if not stmt:
            return df
        return df.query(stmt)

    @staticmethod
    def filter_by_df(df: TyPdDf, d_filter: TyDic, relation: TyStr) -> TyPdDf:
        key = d_filter.get('key')
        value = d_filter.get('value')
        match relation:
            case 'neq':
                return df[df[key] != value]
            case 'eq':
                return df[df[key] == value]
            case _:
                return df

    @classmethod
    def filter(cls, df: TyPdDf, d_filter: TyDic, relation: TyStr) -> TyPdDf:
        method = d_filter.get('method')
        match method:
            case 'stmt':
                return cls.filter_by_query(df, d_filter, relation)
            case _:
                return cls.filter_by_df(df, d_filter, relation)

    @staticmethod
    def format_leading_zeros(
            df: TyPdDf, a_column_name: TyArr, fmt: TyStr = "{:04d}") -> TyPdDf:
        # def format_with_leading_zeros(
        fnc = sh_format_as_int_with_leading_zeros(fmt)
        for _column_name in a_column_name:
            _df_column_value: Any = df[_column_name].map(fnc)
            df = df.drop(_column_name, axis=1)
            df[_column_name] = _df_column_value
        return df

    @staticmethod
    def format_as_date(
            df: TyPdDf, a_column_name: TyArr, fmt: TyStr = '%Y-%m-%d') -> TyPdDf:
        fnc = sh_format_as_date(fmt)
        for _column_name in a_column_name:
            _df_column_value: Any = df[_column_name].map(fnc)
            df = df.drop(_column_name, axis=1)
            df[_column_name] = _df_column_value
        return df

    @staticmethod
    def pivot_table(df: TyPdDf, d_pv: TyDic) -> TyPdDf:
        return pd.pivot_table(df, **d_pv)

    @classmethod
    def pivot_table_query(cls, df: TyPdDf, d_pv: TyDic, stmt) -> TyPdDf:
        _df_new: TyPdDf = df.query(stmt)
        return cls.pivot_table(_df_new, d_pv)

    @classmethod
    def query_with_key(cls, df: TnPdDf, dic: TyDic, **kwargs) -> TnPdDf:
        if df is None:
            return None
        dic_key: TyAny = kwargs.get('dic_key', '')
        dic_value: TnAny = dic.get(dic_key)
        if not dic_value:
            Log.debug(cls.msg_dic_01.format(K=dic_key, D=dic))
            return None
        d_key2key: TyDic = kwargs.get('d_key2key', {})
        df_key: TnAny = d_key2key.get(dic_key)
        if not df_key:
            return None

        df_new: TnPdDf = df.loc[(df[df_key] == dic_value)]
        if df_new is None:
            Log.debug(cls.msg_df_01.format(V=dic_value, K=df_key))
            return None
        # if df_new.empty:
        if len(df_new.index) == 0:
            Log.error(cls.msg_df_02.format(K=df_key, V=dic_value))
            return None
        return df_new

    @classmethod
    def set_ix_drop_col_filter(
            cls, df: TyPdDf, d_filter: TyDic, relation: TyStr, index: TyStr
    ) -> TyPdDf:
        # def set_index_drop_column_filter(
        df_new = df.reset_index()
        LogEq.debug("BEGIN df_new", df_new)
        df_new_ = cls.filter(df_new, d_filter, relation)
        # drop column (1 is the axis number, 0 for rows and 1 for columns)
        df_new_ = df_new_.drop(d_filter['key'], axis=1)
        df_new_ = df_new_.set_index(index)
        LogEq.debug("END df_new", df_new_)
        return df_new_

    @staticmethod
    def to_aod(df: TnPdDf) -> TyAoD:
        if df is None:
            return []
        aod: TyAoD = df.to_dict(orient='records')
        return aod

    @classmethod
    def to_doaod_by_key(cls, df: TyPdDf, key: TyStr) -> TyDoAoD:
        # def sh_doaod(df: TyPdDf, key: str) -> TyDoAoD:
        doaod: TyDoAoD = {}
        aod: TyAoD = cls.to_aod(df)
        for dic in aod:
            value = dic[key]
            if value not in doaod:
                doaod[value] = []
            del dic[key]
            doaod[value].append(dic)
        return doaod

    @classmethod
    def to_dopddf_by_key(cls, df: TyPdDf, key: TyStr) -> TyDoPdDf:
        # def sh_d_pddf(cls, df: TyPdDf, key: str) -> TyDoPdDf:
        doaod: TyDoAoD = cls.to_doaod_by_key(df, key)
        dopddf = {}
        for key, aod in doaod.items():
            dopddf[key] = pd.DataFrame(aod)
        return dopddf
