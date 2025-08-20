# coding=utf-8
from collections.abc import Iterator
from typing import Any

TyArr = list[Any]
TyDic = dict[Any, Any]
TyDoD = dict[Any, TyDic]
TyIterTup3 = Iterator[tuple[Any, Any, Any]]

TnAny = None | Any
TnDic = None | TyDic
TnArrStr = None | TyArr | str
TnDoD = None | TyDoD


class DoD:
    """ Manage Dictionary of Dictionaries
    """
    @staticmethod
    def nvl(dod: TnDoD) -> TnDoD:
        """ nvl function similar to SQL NVL function
        """
        if dod is None:
            dod = {}
        return dod

    @classmethod
    def replace_keys(cls, dod: TyDoD, keys: TyDic) -> TyDic:
        """
        Recurse through the Dictionary while building a new one with
        new keys and old values; the old keys are translated to new
        ones by the keys Dictionary.
        """
        _dic = {}
        for key, value in dod.items():
            key_new = keys.get(key, key)
            if isinstance(value, dict):
                _dic[key_new] = cls.replace_keys(value, keys)
            else:
                _dic[key_new] = dod[key]
        return _dic

    @staticmethod
    def yield_values(dod: TyDoD) -> TyIterTup3:
        for key0, dic in dod.items():
            for key1, value in dic.items():
                yield (key0, key1, value)
