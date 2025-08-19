# coding=utf-8
from collections.abc import Iterator
from typing import Any

from .dod import DoD

TyArr = list[Any]
TyTup3 = tuple[Any, Any, Any]
TyDic = dict[Any, Any]
TyDoA = dict[Any, TyArr]
TyDoDoA = dict[Any, TyDoA]
TyIterTup3 = Iterator[TyTup3]


class DoDoA:
    @staticmethod
    def append(dodoa: TyDoDoA, keys: TyArr, value: Any) -> TyDoDoA:
        key0 = keys[0]
        key1 = keys[1]
        if key0 not in dodoa:
            dodoa[key0] = {}
        if key1 not in dodoa[key0]:
            dodoa[key0][key1] = []
        dodoa[key0][key1].append(value)
        return dodoa

    @staticmethod
    def sh_union(dodoa: TyDoDoA) -> TyArr:
        arr_new = []
        for _key1, _key2, arr in DoD.yield_values(dodoa):
            arr_new.extend(arr)
        return arr_new
