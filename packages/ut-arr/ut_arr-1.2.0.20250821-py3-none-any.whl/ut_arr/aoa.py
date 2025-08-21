# coding=utf-8
from typing import Any

from ut_arr.arr import Arr

TyAny = Any
TyArr = list[Any]
TyAoA = list[TyArr]
TyDic = dict[Any, Any]

TyDoA = dict[Any, TyArr]
TyAoI = list[int]
TyAoD = list[TyDic]

TnAny = None | Any
TnAoA = None | TyAoA


class AoA:
    """ Manage Array of Arrays
    """
    @staticmethod
    def concatinate(aoa: TyAoA) -> TyArr:
        if not aoa:
            return []
        arr_new: TyArr = []
        for _arr in aoa:
            for _item in _arr:
                arr_new.append(_item)
        return arr_new

    @staticmethod
    def nvl(aoa: TnAoA) -> TyAoA:
        """
        nvl function similar to SQL NVL function
        """
        if aoa is None:
            return []
        return aoa

    @staticmethod
    def to_aod(aoa: TyAoA, keys: TyArr) -> TyAoD:
        """
        Migrate Array of Arrays to Array of Dictionaries
        """
        aod: TyAoD = []
        for _arr in aoa:
            dic: TyDic = Arr.to_dic(_arr, keys)
            aod.append(dic)
        return aod

    @staticmethod
    def to_arr_from_2cols(aoa: TyAoA, a_ix: TyAoI) -> TyArr:
        arr: TyArr = []
        ix0: int = a_ix[0]
        ix1: int = a_ix[1]
        for _arr in aoa:
            item0: Any = _arr[ix0]
            item1: Any = _arr[ix1]
            if item0 not in arr:
                arr.append(item0)
            if isinstance(item1, (tuple, list)):
                for _item1 in item1:
                    if _item1 not in arr:
                        arr.append(_item1)
            else:
                if item1 not in arr:
                    arr.append(item1)
        return arr

    # def to_doa_from_2cols(aoa: TyAoA, a_ix: List[Any]):
    @staticmethod
    def to_doa_from_2cols(aoa: TyAoA, a_ix: TyAoI) -> TyDoA:
        doa: TyDoA = {}
        if len(a_ix) < 2:
            return doa
        ix0: int = a_ix[0]
        ix1: int = a_ix[1]
        for arr in aoa:
            item0: TnAny = arr[ix0]
            item1: TnAny = arr[ix1]
            if item0 not in doa:
                doa[item0] = []
            if isinstance(item1, (tuple, list)):
                doa[item0].extend(item1)
            else:
                doa[item0].append(item1)
            doa[item0] = list(set(doa[item0]))
        return doa

    @staticmethod
    def to_dic_from_2cols(aoa: TyAoA, a_ix: TyAoI) -> TyDic:
        dic: TyDic = {}
        if len(a_ix) < 2:
            return dic
        ix0: int = a_ix[0]
        ix1: int = a_ix[1]
        for _arr in aoa:
            item1: TnAny = _arr[ix1]
            if item1 is None:
                continue
            item0 = _arr[ix0]
            dic[item0] = item1
        return dic
