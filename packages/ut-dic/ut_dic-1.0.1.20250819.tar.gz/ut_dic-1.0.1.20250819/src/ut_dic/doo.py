# coding=utf-8

from typing import Any
TyDic = dict[Any, Any]


class DoO:
    """ Manage Dictionary of Objects
    """
    @classmethod
    def replace_keys(cls, dic_old: TyDic, d_key: TyDic) -> TyDic:
        """
        Replace the keys of the given Dictionary by the values found in
        the given Keys Dictionary if the values are not Dictionaries;
        otherwise the function is called again with these values.
        """
        dic_new: TyDic = {}
        for key in dic_old.keys():
            if key in d_key:
                key_new = d_key[key]
            else:
                key_new = key
            if isinstance(dic_old[key], dict):
                dic_new[key_new] = cls.replace_keys(dic_old[key], d_key)
            elif isinstance(dic_old[key], (list, tuple)):
                aodic_old = dic_old[key]
                aodic_new = []
                for item in aodic_old:
                    if isinstance(item, dict):
                        item_new = cls.replace_keys(item, d_key)
                        aodic_new.append(item_new)
                dic_new[key_new] = aodic_new
                # dic_new[key_new] = AoD.replace_keys(dic_old[key], d_key)
            else:
                dic_new[key_new] = dic_old[key]
        return dic_new
