# coding=utf-8
from typing import Any
from collections.abc import Callable

from ut_obj.pokv import PoKV

TyArr = list[Any]
TyCall = Callable[..., Any]
TyDic = dict[Any, Any]

TnDic = None | TyDic


class DoEq:
    """ Manage Commandline Arguments
    """
    @staticmethod
    def _set_sh_prof(d_eq: TyDic, sh_prof: TyCall | Any) -> None:
        """ set current pacmod dictionary
        """
        if callable(sh_prof):
            d_eq['sh_prof'] = sh_prof()
        else:
            d_eq['sh_prof'] = sh_prof

    @classmethod
    def verify(cls, d_eq: TyDic, d_parms: TnDic) -> TyDic:
        if d_parms is None:
            return d_eq
        if 'cmd' in d_eq:
            _d_valid_parms = d_parms
            _cmd = d_eq['cmd']
            _valid_commands = list(d_parms.keys())
            if _cmd not in _valid_commands:
                msg = (f"Wrong command: {_cmd}; "
                       f"valid commands are: {_valid_commands}")
                raise Exception(msg)
            _d_valid_parms = d_parms[_cmd]
        else:
            _d_valid_parms = d_parms
        if _d_valid_parms is None:
            return d_eq

        d_eq_new = {}
        for key, value in d_eq.items():
            if key not in _d_valid_parms:
                msg = (f"Wrong parameter: {key}; "
                       f"valid parameters are: {_d_valid_parms}")
                raise Exception(msg)
            d_eq_new[key] = PoKV.sh_value_by_key_type(key, value, _d_valid_parms)
        return d_eq_new
