# coding=utf-8
from collections.abc import Callable
from typing import Any

TyAny = Any
TyArr = list[Any]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyTup = tuple[Any, ...]
TyArrTup = TyArr | TyTup

TyDoA = dict[Any, TyArr]
TyAoD = list[TyDic]
TnCallable = None | TyCallable
TyDoAoD = dict[Any, TyAoD]
TnAny = None | Any
TnArr = None | TyArr


class DoA:
    """
    Manage Dictionary of Arrays
    """
    @staticmethod
    def append_by_key(
            doa: TyDoA, key: TyAny, value: TnAny, item: TnAny = None) -> None:
        """
        append the item to the value of the dictionary of Arrays
        for the given key if the item is not contained in the value.
        """
        if item is None:
            item = []
        elif not isinstance(item, (list, tuple)):
            item = [item]
        if key not in doa:
            doa[key] = item
        doa[key].append(value)

    @staticmethod
    def append_unique_by_key(
            doa: TyDoA, key: TyAny, value: TnAny, item: TnAny = None) -> None:
        """assign item to dictionary defined as value
           for the given keys.
        """
        if item is None:
            item = []
        elif not isinstance(item, (list, tuple)):
            item = [item]
        if key not in doa:
            doa[key] = item
        if value not in doa[key]:
            doa[key].append(value)

    @staticmethod
    def sh_union(doa: TyDoA) -> TyArr:
        arr_new = []
        for _key, _arr in doa.items():
            arr_new.extend(_arr)
        return arr_new
