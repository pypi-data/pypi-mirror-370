# import builtins
from collections.abc import Callable, Iterator
from typing import Any

from .doa import DoA
from ut_log.log import Log
from ut_obj.obj import Obj

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAny_Dic = Any | TyDic
TyAoD = list[TyDic]
TyDoA = dict[Any, TyArr]
TyDoAoD = dict[Any, TyAoD]
TyIterAny = Iterator[Any]
TyKey = Any
TyKeys = Any | TyArr
TyStr = str
TyTup = tuple[Any, ...]
TyArrTup = TyArr | TyTup
TyToD = tuple[TyDic, ...]
TyToDD = tuple[TyDic, TyDic]

TnAny = None | Any
TnAny_Dic = None | TyAny_Dic
TnAoD = None | TyAoD
TnArr = None | TyArr
TnArrTup = None | TyArr | TyTup
TnBool = None | bool
TnCallable = None | TyCallable
TnDic = None | TyDic
TnDoA = None | TyDoA
TnKey = None | TyKey
TnKeys = None | TyKeys


class Dic:
    """
    Dictionary Management
    """
    @classmethod
    def add_counter_by_keys(
            cls, dic: TyDic, keys: TyKeys, counter: Any = None) -> None:
        """
        Apply the function "add_counter_with key" to the last key of the
        key list and the dictionary localized by that key.
        """
        # def add_counter_to_values(
        if not isinstance(keys, (list, tuple)):
            cls.add_counter_by_key(dic, keys, counter)
        else:
            _dic: TnDic = cls.locate(dic, keys[:-1])
            cls.add_counter_by_key(_dic, keys[-1], counter)

    @staticmethod
    def add_counter_by_key(
            dic: TnDic, key: TyKey, counter: TyAny) -> None:
        # def cnt(
        """
        Initialize the unintialized counter with 1 and add it to the
        Dictionary value of the key.
        """
        # def add_counter_to_value(
        if not dic:
            return
        if counter is None:
            counter = 1
        if key not in dic:
            dic[key] = 0
        dic[key] = dic[key] + counter

    @classmethod
    def apply_by_keys(
            cls, dic: TyDic, keys: TyArr, fnc: TyCallable, value: TyAny, item: TnAny
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        # def apply(
        #        fnc: TyCallable, doa: TyDic, keys: TyArr, item: TyAny, item0: TnAny
        if item is None:
            item = []
        if keys is None:
            return
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        DoA.append_by_key(cls.locate(dic, keys[:-1]), keys[-1], value, item)
        fnc(dic[keys[:-1]], item)

    @classmethod
    def append_unique_by_keys(
            cls, dic: TyDic, keys: TyArrTup, value: Any, item: TnAny = None
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if dic is None or not keys:
            return
        if value is None:
            value = []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        DoA.append_unique_by_key(cls.locate(dic, keys[:-1]), keys[-1], value, item)

    @classmethod
    def append_by_keys(
            cls, dic: TnDic, keys: TnKeys, value: Any, item: TnAny = None
    ) -> None:
        """
        Apply the function "append with key" to the last key of the key
        list amd the dictionary localized by that key.
        """
        # def append_values(
        # def append(
        if dic is None or not keys:
            return
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        DoA.append_by_key(cls.locate(dic, keys[:-1]), keys[-1], value, item)

    @staticmethod
    def change_keys_with_keyfilter(
            dic: TyDic, keyfilter: TyDic) -> TyDic:
        """
        Change the keys of the dictionary by the values of the keyfilter
        Dictionary with the same keys.
        """
        dic_new: TyDic = {}
        for key, value in dic.items():
            key_new = keyfilter.get(key)
            if key_new is None:
                continue
            dic_new[key_new] = value
        return dic_new

    @staticmethod
    def copy(
            dic_target: TnDic, dic_source: TnDic, keys: TnKeys = None) -> None:
        """
        copy values for keys from source to target dictionary
        """
        # Dictionary is None or empty
        if not dic_target:
            return
        if not dic_source:
            return
        if keys is None:
            keys = list(dic_source.keys())
        for key in keys:
            dic_target[key] = dic_source[key]

    @classmethod
    def extend_by_keys(
            cls, doa: TyDic, keys: TyKeys, value: TyAny) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        # def extend(
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _doa = cls.locate(doa, keys[:-1])

        # last keys element
        key = keys[-1]
        if isinstance(value, str):
            value = [value]
        if key not in _doa:
            _doa[key] = value
        else:
            _doa[key].extend(value)

    @staticmethod
    def extend_by_key(
            dic: TnDoA, key: TnKey, value: TyAny, item: TnAny = None
    ) -> None:
        """
        Add the item with the key as element to the dictionary if the key
        is undefined in the dictionary. Extend the element value with the
        value if it supports the extend function.
        """
        # def extend_value(
        if not dic:
            return
        if not isinstance(value, (list, tuple)):
            value = [value]
        if item is None:
            item = []
        # last element
        if key not in dic:
            dic[key] = item
        if isinstance(dic[key], (list, tuple)):
            dic[key].extend(value)

    @staticmethod
    def filter_by_keys(dic: TyDic, keys: TyKeys) -> TyDic:
        """
        Filter Dictionary by a single key or an Array of Keys
        """
        if isinstance(keys, str):
            keys = [keys]
        dic_new: TyDic = {}
        for key, value in dic.items():
            if key in keys:
                dic_new[key] = value
        return dic_new

    @staticmethod
    def get_by_keys(dic: TnDic, keys: TyKeys, default: Any = None) -> TnAny_Dic:
        # def get
        if dic is None:
            return None
        if not isinstance(keys, (list, tuple)):
            if keys in dic:
                return dic[keys]
            return default
        _dic = dic
        value = None
        for _key in keys:
            value = _dic.get(_key)
            if value is None:
                return None
            if not isinstance(value, dict):
                return value
            _dic = value
        return value

    @staticmethod
    def get(dic: TyDic, key: TyKey, default: Any = None) -> TnAny:
        # def get
        if dic is None:
            return None
        return dic.get(key, default)

    @staticmethod
    def get_value_yn(dic: TyDic, key: str, value_y, value_n) -> Any:
        # def get_yn_value(dic: TyDic, key: str, value_y, value_n) -> Any:
        if key in dic:
            return value_y
        return value_n

    @staticmethod
    def get_as_array(dic: TyDic, key: TyKey) -> TyArr:
        """
        show array of key value found for given key in dictionary
        """
        if not dic or not key:
            return []
        value: None | Any | TyArr = dic.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @classmethod
    def increment_by_keys(
            cls, dic: TnDic, keys: TnKeys, item: Any = 1) -> None:
        # def increment(
        """
        Appply the function "increment_by_key" to the last key of
        the key list and the dictionary localized by that key.
        """
        # def increment_values(
        # def increment_by_keys(
        if not dic or keys is None:
            return
        if not isinstance(keys, list):
            keys = [keys]
        cls.increment_by_key(
                cls.locate(dic, keys[:-1]), keys[-1], item)

    @staticmethod
    def increment_by_key(
            dic: TnDic, key: Any, item: Any = 1) -> None:
        """
        Increment the value of the key if it is defined in the
        Dictionary, otherwise assign the item to the key.
        """
        # def increment_value(
        # def increment_by_key(
        # last element
        if not dic:
            pass
        elif key not in dic:
            dic[key] = item
        else:
            dic[key] += 1

    @staticmethod
    def is_not(dic: TyDic, key: TyStr) -> TyBool:
        """
        Return False if the key is defined in the Dictionary and
        the key value if not empty, othewise returm True.
        """
        if key in dic:
            if dic[key]:
                return False
        return True

    @staticmethod
    def locate(dic: TyDic, keys: TyKeys) -> TyAny:
        """
        Return the value of the key reached by looping thru the
        nested Dictionary with the keys from the key list until
        the value is None or the last key is reached.
        """
        if not dic:
            msg = "The 1. Parameter 'dic' is None or empty"
            raise Exception(msg)
        if not keys:
            msg = "The 2. Parameter 'keys' is None or empty"
            raise Exception(msg)
        _dic: TyAny = dic
        for _key in keys:
            if isinstance(_dic, dict):
                _dic_new = _dic.get(_key)
                if _dic_new is None:
                    raise Exception(
                            f"Key={_key} does not exist in Dictionary={_dic}")
                    raise Exception(msg)
                _dic = _dic_new
            else:
                raise Exception(f"Value={_dic} is not a Dictionary")
        return _dic

    @classmethod
    def locate_before_last(cls, dic: TyDic, keys: TyKeys) -> Any:
        """
        locate the value by keys in a nested dictionary
        """
        # def locate_value_before_last
        return cls.locate(dic, keys[:-1])

    @staticmethod
    def lstrip_keys(dic: TyDic, string: TyStr) -> TyDic:
        """
        Remove the first string found in the Dictionary keys.
        """
        dic_new: TyDic = {}
        for k, v in dic.items():
            k_new = k.replace(string, "", 1)
            dic_new[k_new] = v
        return dic_new

    @staticmethod
    def merge(dic0: TnDic, dic1: TnDic) -> TnDic:
        if dic0 is None:
            if dic1 is None:
                return None
            return {**dic1}
        if dic1 is None:
            return {**dic0}
        return {**dic0, **dic1}

    @classmethod
    def new(cls, keys: TyKeys, value: Any) -> TnDic:
        """ create a new Dictionary from keys and values
        """
        if value is None or keys is None:
            return None
        dic_new: TyDic = {}
        if isinstance(keys, str):
            dic_new[keys] = value
            return dic_new
        cls.set_by_keys(dic_new, keys, value)
        return dic_new

    @staticmethod
    def normalize_values(dic: TyDic) -> TyDic:
        """
        Replace every Dictionary value by the first list element
        of the value if it is a list with only one element.
        """
        # def normalize_value(dic: TyDic) -> TyDic:
        dic_new: TyDic = {}
        for k, v in dic.items():
            # The value is a list with 1 element
            if isinstance(v, list) and len(v) == 1:
                dic_new[k] = v[0]
            else:
                dic_new[k] = v
        return dic_new

    @staticmethod
    def nvl(dic: TnDic) -> TyDic:
        """
        nvl function similar to SQL NVL function
        """
        if dic is None:
            return {}
        return dic

    @classmethod
    def rename_key_by_kwargs(
            cls, dic: TnDic, kwargs: TyDic) -> TnDic:
        """ rename old dictionary key with new dictionary key by kwargs
        """
        # def rename_key(
        # Dictionary is None or empty
        if not dic:
            return dic
        return cls.rename_key(dic, kwargs.get("key_old"), kwargs.get("key_new"))

    @staticmethod
    def rename_key(dic: TyDic, k_old: TyAny, k_new: TyAny) -> TyDic:
        """ rename old dictionary key with new dictionary key
        """
        return {k_new if k == k_old else k: v for k, v in dic.items()}

    @staticmethod
    def replace_string_in_keys(
            dic: TyDic, old: Any, new: Any) -> TyDic:
        # def replace_keys(
        if not dic:
            return dic
        dic_new = {}
        for key, value in dic.items():
            key_ = key.replace(old, new)
            dic_new[key_] = value
        return dic_new

    @staticmethod
    def round_values(
            dic: TyDic, keys: TnKeys, kwargs: TyDic) -> TyDic:
        # def round_value
        round_digits: int = kwargs.get('round_digits', 2)
        if not dic:
            msg = f"Parameter dic = {dic} is undefined"
            raise Exception(msg)
        if not keys:
            return dic
        dic_new: TyDic = {}
        for key, value in dic.items():
            if value is None:
                dic_new[key] = value
            else:
                if key in keys:
                    dic_new[key] = round(value, round_digits)
                else:
                    dic_new[key] = value
        return dic_new

    @classmethod
    def set_kv_not_none(cls, dic: TyDic, key: TnAny, value: TnAny) -> None:
        """
        Set the given Dictionary key to the given value if both are not None.
        """
        if key is None:
            return
        if value is None:
            return
        dic[key] = value

    @classmethod
    def set_by_keys(cls, dic: TyDic, keys: TyKeys, value: Any) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not isinstance(keys, (list, tuple)):
            dic[keys] = value
            return
        _keys: TyKeys = keys[:-1]
        _dic = cls.locate(dic, _keys)
        if not _dic:
            return
        key_last = keys[-1]
        _dic[key_last] = value

    @classmethod
    def set_by_key(cls, dic: TyDic, key: Any, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not key:
            return
        dic[key] = value

    @staticmethod
    def set_by_key_pair(dic: TyDic, src_key: Any, tgt_key: Any) -> None:
        """
        Replace value of source key by value of target key.
        """
        if src_key in dic and tgt_key in dic:
            dic[tgt_key] = dic[src_key]

    @classmethod
    def set_if_none(cls, dic: TyDic, keys: TyKeys, value_last: Any) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of a
        key array and assign the given value to the last key if that key does
        not exist in the dictionary.
        """
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _dic = cls.locate(dic, keys[:-1])
        if not _dic:
            return
        # last element
        key_last = keys[-1]
        if key_last not in _dic:
            _dic[key_last] = value_last

    @staticmethod
    def set_by_div(
            dic: TnDic, key: str, key1: str, key2: str) -> None:
        """
        Replace the source key value by the division of the values of two
        target keys if they are of type float and the divisor is not 0.
        """
        # Dictionary is None or empty
        if not dic:
            return
        if key1 in dic and key2 in dic:
            _val1 = dic[key1]
            _val2 = dic[key2]
            if (isinstance(_val1, (int, float)) and
               isinstance(_val2, (int, float)) and
               _val2 != 0):
                dic[key] = _val1/_val2
            else:
                dic[key] = None
        else:
            dic[key] = None

    # @staticmethod
    # def set_divide(
    #         dic: TnDic, key: Any, key1: Any, key2: Any) -> None:
    #     """ divide value of key1 by value of key2 and
    #         assign this value to the key
    #     """
    #     # Dictionary is None or empty
    #     if not dic:
    #         return
    #     if key1 in dic and key2 in dic:
    #         _val1 = dic[key1]
    #         _val2 = dic[key2]
    #         if (isinstance(_val1, (int, float)) and
    #            isinstance(_val2, (int, float)) and
    #            _val2 != 0):
    #             dic[key] = _val1/_val2
    #         else:
    #             dic[key] = None
    #     else:
    #         dic[key] = None

    @classmethod
    def set_first_tgt_with_src_by_d_src2tgt(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_src2tgt: TyDic):
        """
        Replace value of first dictionary target key found in the source to
        target dictionary by the source value found in the dictionary.
        """
        for key_src, key_tgt in d_src2tgt.items():
            value_src = cls.get(dic_src, key_src)
            if value_src:
                dic_tgt[key_tgt] = value_src
                break

    @classmethod
    def set_first_tgt_with_src_by_d_tgt2src(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_tgt2src: TyDic):
        """
        Replace value of first dictionary target key found in the target to
        source dictionary by the source value found in the dictionary.
        """
        for key_tgt, key_src in d_tgt2src.items():
            value_src = cls.get(dic_src, key_src)
            if value_src:
                dic_tgt[key_tgt] = value_src
                break

    @staticmethod
    def set_format_value(
            dic: TnDic, key: Any, fmt: Any) -> None:
        """
        Replace the dictionary values by the formatted values by the given
        format string
        """
        if not dic:
            return
        if key in dic:
            value = dic[key]
            dic[key] = fmt.format(value)

    @staticmethod
    def set_multiply_with_factor(
            dic: TnDic, key_new: Any, key: Any, factor: Any) -> None:
        """
        Replace the dictionary values by the original value multiplied with the factor
        """
        # Dictionary is None or empty
        if not dic:
            return
        if key not in dic:
            return
        if dic[key] is None:
            dic[key_new] = None
        else:
            dic[key_new] = dic[key] * factor

    @classmethod
    def set_tgt_with_src(
            cls, dic_tgt: TyDic, dic_src: TyDic) -> None:
        """
        Replace source dictionary values by target dictionary values.
        """
        for key_src in dic_src.keys():
            dic_tgt[key_src] = dic_src.get(key_src)

    @classmethod
    def set_tgt_with_src_by_doaod_tgt2src(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_aotgt2src: TyDoAoD):
        """
        Loop through the target to source dictionaries of the values of the
        dictionary of the arrays of target to source dictionaries until the
        return value of the function "set_nonempty_tgt_with_src_by_d_tgt2src"
        is defined.
        """
        for aotgt2src in d_aotgt2src.values():
            for tgt2src in aotgt2src:
                sw_none = cls.set_nonempty_tgt_with_src_by_d_tgt2src(
                       dic_tgt, dic_src, tgt2src)
                if not sw_none:
                    return

    @classmethod
    def set_nonempty_tgt_with_src_by_d_tgt2src(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_tgt2src: TyDoAoD) -> bool:
        """
        Exceute the function "set_tgt_with_src_by_d_tgt2src" if all
        dictionary values for the keys provided by the values of the
        target to source dictionary are defined.
        """
        if any(dic_src.get(_key_src) is None for _key_src in d_tgt2src.values()):
            return True
        # for key_tgt, key_src in d_tgt2src.items():
        #     _value = dic_src.get(key_src)
        #     if _value is None:
        #         return True
        cls.set_tgt_with_src_by_d_tgt2src(dic_tgt, dic_src, d_tgt2src)
        return False

    @staticmethod
    def set_tgt_with_src_by_d_src2tgt(
            dic_tgt: TyDic, dic_src: TyDic, d_src2tgt: TyDic):
        for key_src, key_tgt in d_src2tgt.items():
            dic_tgt[key_tgt] = dic_src.get(key_src)

    @staticmethod
    def set_tgt_with_src_by_d_tgt2src(
            dic_tgt: TyDic, dic_src: TyDic, d_tgt2src: TyDic):
        for key_tgt, key_src in d_tgt2src.items():
            dic_tgt[key_tgt] = dic_src.get(key_src)

    @classmethod
    def sh_bool(cls, dic: TyDic, a_key: TyArrTup, switch: bool = False) -> bool:
        """
        locate the value by keys in a nested dictionary
        """
        value = cls.locate(dic, a_key)
        if value is None:
            return switch
        if isinstance(value, bool):
            return value
        return switch

    @staticmethod
    def sh_dic(dic: TyDic) -> TyDic:
        dic_new = {}
        for key, value in dic.items():
            f_key = frozenset(key.split(','))
            dic_new[f_key] = value
        return dic_new

    @staticmethod
    def sh_d_filter(key: str, value: Any, method: str = 'df') -> TyDic:
        d_filter = {}
        d_filter['key'] = key
        d_filter['value'] = value
        d_filter['method'] = method
        return d_filter

    @staticmethod
    def sh_d_index_d_values(dic: TyDic, d_pivot: TyDic) -> TyToDD:
        a_index: TyArr = d_pivot.get('index', [])
        a_values: TyArr = d_pivot.get('values', [])
        d_index: TyDic = {}
        d_values: TyDic = {}
        if len(a_values) == 1:
            for key, value in dic.items():
                Log.debug(f"len(a_values) == 1 key = {key}")
                Log.debug(f"len(a_values) == 1 value = {value}")
                if key in a_index:
                    d_index[key] = value
                else:
                    key0 = key
                    key1 = a_values[0]
                    Log.debug(f"len(a_values) == 1 key not in a_index key0 = {key0}")
                    Log.debug(f"len(a_values) == 1 key not in a_index key1 = {key1}")
                    if key0 not in d_values:
                        d_values[key0] = {}
                    d_values[key0][key1] = value
        else:
            for key, value in dic.items():
                if key in a_index:
                    d_index[key] = value
                else:
                    a_key = key.split("_")
                    key1 = a_key[0]
                    key0 = a_key[1]
                    if key0 in a_values:
                        if key0 not in d_values:
                            d_values[key0] = {}
                        d_values[key0][key1] = value
                    else:
                        Log.error(f"ERROR key0 = {key0} no in a_values = {a_values}")
            Log.debug(f"len(a_values) != 1 d_values = {d_values}")
        return d_index, d_values

    @staticmethod
    def sh_d_vals_d_cols(dic: TyDic) -> TyToDD:
        d_cols: TyDic = {}
        d_vals: TyDic = {}
        for key, value in dic.items():
            a_key = key.split("_")
            if len(a_key) == 1:
                key0 = a_key[0]
                d_vals[key0] = value
            else:
                key0 = a_key[0]
                key1 = a_key[1]
                if key1 not in d_cols:
                    d_cols[key1] = {}
                d_cols[key1][key0] = value
        return d_vals, d_cols

    @staticmethod
    def sh_prefixed(dic: TyDic, prefix: str) -> TyDic:
        dic_new: TyDic = {}
        for k, v in dic.items():
            dic_new[f"{prefix}_{k}"] = v
        return dic_new

    @staticmethod
    def sh_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        """
        show array of keys found in dictionary
        """
        if not dic or not keys:
            return []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        arr = []
        for key in keys:
            if key in dic:
                arr.append(key)
        return arr

    @staticmethod
    def show_sorted_keys(dic: TnDic) -> TyArr:
        if not dic:
            return []
        a_key: TyArr = list(dic.keys())
        a_key.sort()
        return a_key

    @staticmethod
    def sh_value_by_keys(dic: TyDic, keys: TyKeys, default: Any = None) -> Any:
        """
        show array of key values found for given keys in dictionary
        """
        # def sh_value(dic: TyDic, keys: TyKeys, default: Any = None) -> Any:
        if not dic:
            return dic
        if not keys:
            return dic
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _dic = dic
        value = None
        for key in keys:
            value = _dic.get(key)
            if value is None:
                return default
            if isinstance(value, dict):
                _dic = value
            else:
                if value is None:
                    return default
                return value
        return value

    @staticmethod
    def sh_values_by_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        """ locate the value for keys in a nested dictionary
        """
        # def sh_values
        if not dic or not keys:
            return []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        arr = []
        for key in keys:
            if key in dic:
                arr.append(dic[key])
        return arr

    @staticmethod
    def sh_value2keys(dic: TyDic) -> TyDic:
        dic_new: TyDic = {}
        for key, value in dic.items():
            if value not in dic_new:
                dic_new[value] = []
            if key not in dic_new[value]:
                dic_new[value].extend(key)
        return dic_new

    @staticmethod
    def split_by_key(
            dic: TnDic, key: TnAny) -> TyTup:
        # Dictionary is None or empty
        if not dic or not key:
            return dic, None
        dic_new = {}
        obj_new = None
        for k, v in dic.items():
            if k == key:
                obj_new = v
            else:
                dic_new[k] = v
        return obj_new, dic_new

    @staticmethod
    def split_by_value(
            dic: TyDic, value: Any) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        dic0 = {}
        dic1 = {}
        for k, v in dic.items():
            if v == value:
                dic0[k] = v
            else:
                dic1[k] = v
        return dic0, dic1

    @staticmethod
    def split_by_value_endswith(
            dic: TyDic, value: Any) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        dic0 = {}
        dic1 = {}
        for k, v in dic.items():
            if v.endswith(value):
                dic0[k] = v
            else:
                dic1[k] = v
        return dic0, dic1

    @staticmethod
    def split_by_value_is_int(
            dic: TyDic) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        dic0 = {}
        dic1 = {}
        for k, v in dic.items():
            if v.isdigit():
                dic0[k] = v
            else:
                dic1[k] = v
        return dic0, dic1

    @staticmethod
    def to_aod(
        # def dic2aod(
            dic: TyDic, key_name: Any, value_name: Any) -> TyAoD:
        # Dictionary is None or empty
        if not dic:
            aod = [dic, dic]
        aod = []
        _dic = {}
        for k, v in dic.items():
            _dic[key_name] = k
            _dic[value_name] = v
            aod.append(_dic)
            _dic = {}
        return aod

    @staticmethod
    def yield_values_with_keyfilter(
            dic: TyDic, keyfilter: TyDic) -> TyIterAny:
        for key, value in dic.items():
            if key in keyfilter:
                yield value

    @staticmethod
    def union(
            dic0: TnDic, dic1: TnDic) -> TnDic:
        if dic0 is None:
            return dic1
        if dic1 is None:
            return dic0
        return dic0 | dic1

    class Names:

        @staticmethod
        def sh(d_data: TyDic, key: str = 'value') -> Any:
            try:
                return Obj.extract_values(d_data, key)
            except Exception:
                return []

        @classmethod
        def sh_item0(cls, d_names: TyDic) -> Any:
            names = cls.sh(d_names)
            if not names:
                return None
            return names[0]

        @classmethod
        def sh_item0_if(cls, string: str, d_names: TyDic) -> Any:
            names = cls.sh(d_names)
            if not names:
                return None
            if string in d_names[0]:
                return names[0]
            return None

    class Key:

        @staticmethod
        def change(
                dic: TyDic, source_key: TyDic, target_key: TyDic) -> TyDic:
            if source_key in dic:
                dic[target_key] = dic.pop(source_key)
            return dic

    class Value:

        @staticmethod
        def get(
                dic: TyDic, keys: TyKeys, default: Any = None):
            if keys is None:
                return dic
            if not isinstance(keys, (list, tuple)):
                keys = [keys]
            if len(keys) == 0:
                return dic
            value = dic
            for key in keys:
                if key not in value:
                    return default
                value = value[key]
                if value is None:
                    break
            return value

        @classmethod
        def set(
                cls, dic: TnDic, keys: TnKeys, value: Any) -> None:
            if value is None:
                return
            if dic is None:
                return
            if keys is None:
                return

            if not isinstance(keys, (list, tuple)):
                keys = [keys]

            value_curr = cls.get(dic, keys[:-1])
            if value_curr is None:
                return
            last_key = keys[-1]
            if last_key in value_curr:
                value_curr[last_key] = value

        @staticmethod
        def is_empty_value(
                value: Any) -> bool:
            if value is None:
                return True
            if isinstance(value, str):
                if value == '':
                    return True
            elif isinstance(value, (list, tuple)):
                if value == []:
                    return True
            elif isinstance(value, dict):
                if value == {}:
                    return True
            return False

        @classmethod
        def is_empty(cls, dic: TnDic, keys: TyArrTup) -> bool:
            if dic is None:
                return True
            if not isinstance(keys, (tuple, list)):
                keys = [keys]
            if isinstance(keys, (list, tuple)):
                value = cls.get(dic, keys)
                return cls.is_empty_value(value)
            return False

        @classmethod
        def is_not_empty(
                cls, dic: TnDic, keys: TyArrTup) -> bool:
            return not cls.is_empty(dic, keys)
