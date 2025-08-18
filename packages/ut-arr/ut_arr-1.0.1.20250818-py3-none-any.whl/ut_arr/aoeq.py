# coding=utf-8
from typing import Any

from ut_dic.doeq import DoEq

TyArr = list[Any]
TyDic = dict[Any, Any]

TnDic = None | TyDic


class AoEq:
    """ Dictionary of Equates
    """
    @staticmethod
    def _sh_d_eq(a_equ: TyArr) -> TyDic:
        d_eq = {}
        for s_eq in a_equ[1:]:
            a_eq = s_eq.split('=')
            if len(a_eq) == 1:
                d_eq['cmd'] = a_eq[0]
            else:
                d_eq[a_eq[0]] = a_eq[1]
                d_eq[a_eq[0]] = a_eq[1]
        return d_eq

    @classmethod
    def sh_d_eq(cls, a_equ: TyArr, **kwargs) -> TyDic:
        """ show equates dictionary
        """
        _d_parms: TnDic = kwargs.get('d_parms')
        _prof = kwargs.get('sh_prof')
        _d_eq: TyDic = DoEq.verify(cls._sh_d_eq(a_equ), _d_parms)
        DoEq._set_sh_prof(_d_eq, _prof)
        return _d_eq
