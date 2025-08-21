# coding=utf-8
from typing import Any, TypeAlias

import traceback
import polars as pl

from ut_log.log import Log, LogEq

TyPlDf: TypeAlias = pl.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyStmt = str

TyDoA = dict[Any, TyArr]
TyAoD = list[TyDic]

TnAoD = None | TyAoD
TnDoA = None | TyDoA
TnPlDf = None | TyPlDf


class PlDf:
    """
    Manage Polars Dataframe
    """
    @staticmethod
    def filter(df: TyPlDf, stmt: TyStmt) -> TyPlDf:
        try:
            LogEq.debug("stmt", stmt)
            return df.filter(stmt)
        # except pl.ComputeError as e:
        except Exception as e:
            Log.error(f"An ERROR occurred: {e}")
            Log.error(traceback.format_exc())
            return df

    @staticmethod
    def pivot(df: TyPlDf, d_pv: TyDic) -> TyPlDf:
        try:
            return df.pivot(**d_pv)
        except Exception as e:
            print(f"An ERROR occurred: {e}")
            print(traceback.format_exc())
        return df

    @classmethod
    def pivot_filter(cls, df: TyPlDf, d_pv, stmt) -> TyPlDf:
        _df_new: TyPlDf = cls.filter(df, stmt)
        return cls.pivot(_df_new, d_pv)

    @staticmethod
    def to_aod(df: TnPlDf) -> TnAoD:
        if df is None:
            return []
        _df = df.fill_null(None)
        aod: TyAoD = _df.to_dicts()
        return aod

    @staticmethod
    def to_doa(df: TnPlDf) -> TnDoA:
        if df is None:
            return {}
        _df = df.fill_null(None)
        doa: TyDoA = _df.to_dict(as_series=False)
        return doa
