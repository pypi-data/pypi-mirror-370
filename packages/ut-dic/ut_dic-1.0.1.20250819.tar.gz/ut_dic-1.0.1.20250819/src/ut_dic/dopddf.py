from typing import Any, TypeAlias

import numpy as np
import pandas as pd

from .dic import Dic
from ut_dfr.pddf import PdDf

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[Any, TyPdDf]
TyStrArr = str | TyArr

TnArr = None | TyArr
TnDic = None | TyDic
TnInt = None | int
TnDoPdDf = None | TyDoPdDf


class DoPdDf:

    @staticmethod
    def set_ix_drop_key_filter(
            dodf: TyDoPdDf, d_filter: TyDic, relation: str, index: str) -> TyDic:
        """Apply Function "set_ix_drop_col_filter" to all Panda
           Dataframe values of given Dictionary.
        """
        # def set_index_drop_key_filter(
        _a_key: TyArr = Dic.show_sorted_keys(dodf)
        for _key in _a_key:
            _df = dodf[_key]
            _df = PdDf.set_ix_drop_col_filter(_df, d_filter, relation, index)
            dodf[_key] = _df
        return dodf

    @staticmethod
    def to_doaod(dodf: TnDoPdDf) -> TyDoAoD:
        """Replace NaN (not a number) values of Panda Dataframe values of given
           Dictionary and convert them to Array of Dictionaries.
        """
        doaod: TyDoAoD = {}
        if dodf is None:
            return doaod
        for _key, _df in dodf.items():
            _df.replace(to_replace=np.nan, value=None, inplace=True)
            _df.replace(to_replace='n.a.', value=None, inplace=True)
            doaod[_key] = _df.to_dict(orient='records')
        return doaod
