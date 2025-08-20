# coding=utf-8
from collections.abc import Iterator
from typing import Any

TyArr = list[Any]
TyTup = tuple[Any, ...]
TyDic = dict[Any, Any]
TyDoDoD = dict[Any, dict[Any, dict[Any, Any]]]
TyIterTup = Iterator[TyTup]


class DoDoD:

    @staticmethod
    def set(dodod: TyDoDoD, keys: TyArr, value: Any) -> TyDoDoD:
        if keys is None:
            return dodod
        if len(keys) != 3:
            return dodod
        key0 = keys[0]
        key1 = keys[1]
        key2 = keys[2]
        if key0 not in dodod:
            dodod[key0] = {}
        if key1 not in dodod[key0]:
            dodod[key0][key1] = {}
        dodod[key0][key1][key2] = value
        return dodod

    @staticmethod
    def yield_values(dodod: TyDoDoD) -> TyIterTup:
        if dodod is None:
            return
        for key0, dod in dodod.items():
            for key1, dic in dod.items():
                for key2, value in dic.items():
                    if isinstance(value, (list, tuple)):
                        yield (key0, key1, key2, *value)
                    else:
                        yield (key0, key1, key2, value)
