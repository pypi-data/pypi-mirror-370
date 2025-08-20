from typing import Any, TypeAlias

import polars as pl

TyPlDf: TypeAlias = pl.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPlDf = dict[Any, TyPlDf]
TyStrArr = str | TyArr

TnArr = None | TyArr
TnDic = None | TyDic
TnInt = None | int
TnDoPlDf = None | TyDoPlDf


class DoPlDf:

    @staticmethod
    def to_doaod(dodf: TnDoPlDf) -> TyDoAoD:
        """Replace NaN values of Polars Dataframe values of given
           Dictionary and convert them to Array of Dictionaries.
        """
        doaod: TyDoAoD = {}
        if dodf is None:
            return doaod
        for _key, _df in dodf.items():
            _df.fill_nan(None)
            _df = _df.with_columns(pl.col(pl.String).replace("n.a.", None))
            doaod[_key] = _df.to_dicts()
        return doaod
