# coding=utf-8
from collections.abc import Callable, Iterator, Iterable
from typing import Any, Literal

import os

from ut_log.log import LogEq

TyArr = list[Any]
TyCallable = Callable[..., Any]
TyIterable = Iterable
TyDic = dict[Any, Any]
TyNum = int | float
TyStr = str
TyTup = tuple[Any, ...]
TyArrTup = TyArr | TyTup
TyAoD = list[TyDic]
TyArrStr = TyArr | str
TyTupArr = TyTup | TyArr

TnAny = None | Any
TnArr = None | TyArr
TnBool = None | bool
TnInt = None | int
TnStr = None | str
TnTup = None | TyTup
TnArrStr = None | TyArr | str
TnArrTup = None | TyArr | TyTup
TnDic = None | TyDic
TnAoD = None | TyAoD


class Arr:
    """ Manage Array
    """
    @staticmethod
    def append(arr: TnArr, item: TnAny) -> None:
        if not arr:
            return
        if not item:
            return
        arr.append(item)

    @staticmethod
    def append_unique(arr: TyArr, item: TnAny) -> None:
        if not arr:
            return
        if not item:
            return
        if item not in arr:
            arr.append(item)

    # @staticmethod
    # def apply_function(arr: TyTupArr, function: TyCall, **kwargs) -> TyTupArr:
    #     if not arr:
    #         return arr
    #     arr_new: TyArr = []
    #     for item in arr:
    #         _item = function(item, **kwargs)
    #         if _item is None:
    #             continue
    #         arr_new.append(_item)
    #     return arr_new

    @staticmethod
    def apply_function(arr: TyTupArr, function: TyCallable, **kwargs) -> TyTupArr:
        if not arr:
            return arr
        arr_new: TyArr = []
        for item in arr:
            _item = function(item, **kwargs)
            # if _item is None:
            #     continue
            arr_new.append(_item)
        return arr_new

    @staticmethod
    def apply_replace(arr: TyTupArr, source: TyStr, target: TyStr) -> TyTupArr:
        if not arr:
            return arr
        arr_new: TyArr = []
        for item in arr:
            if isinstance(item, str):
                item = item.replace(source, target)
            arr_new.append(item)
        return arr_new

    @staticmethod
    def apply_str(arr: TyTupArr) -> TyTupArr:
        if not arr:
            return arr
        arr_new: TyArr = []
        for item in arr:
            if item is None:
                arr_new.append(item)
            else:
                arr_new.append(str(item))
        return arr_new

    @staticmethod
    def encode(arr: TnArr) -> TnStr:
        if arr is None:
            return None
        arr_joined: str = ' '.join(arr)
        if arr_joined == '':
            return None
        return f"{arr_joined} ".replace(' ', '%20')

    @staticmethod
    def extend(arr0: TnArr, arr1: TnArr) -> TnArr:
        # def merge(arr0: TyArr, arr1: TyArr) -> TyArr:
        if arr0 is None:
            if arr1 is None:
                return None
            return arr1
        if arr1 is None:
            return arr0
        arr0.extend(arr1)
        return arr0

    @staticmethod
    def ex_intersection(arr0: TyArr, arr1: TyArr) -> TyArr:
        if not arr0:
            return arr0
        if not arr1:
            return arr1
        return list(set(arr0).intersection(set(arr1)))

    # @staticmethod
    # def extend(arr0: TnArr, arr1: TnArr) -> TnArr:
    #     if not arr0:
    #         return
    #     if not arr1:
    #         return
    #     arr0.extend(arr1)
    #     return arr0

    @staticmethod
    def get_key_value(
            arr: TyArr, ix: int = 0, default: str = '', value: str = 'Title'
    ) -> TnStr:
        if not arr:
            return None
        if ix >= len(arr):
            return default
        _value_ix = arr[ix].replace('\n', ' ').strip()
        if _value_ix == value:
            ix_next = ix + 1
            new_value: TnStr = arr[ix_next].replace('\n', ' ').strip()
        else:
            new_value = default
        LogEq.debug("arr", arr)
        LogEq.debug("value", value)
        LogEq.debug("_value_ix", _value_ix)
        LogEq.debug("new_value", new_value)
        return new_value

    @staticmethod
    def get_text(arr: TyArr, ix: int = 0, default: str = '') -> TnStr:
        if not arr:
            return None
        if ix >= len(arr):
            return default
        _s: TnStr = arr[ix].replace('\n', ' ').strip()
        return _s

    @staticmethod
    def get_text_split(
            arr: TyArr,
            ix0: int = 0,
            default: str = '',
            ix1: int = 0,
            separator: str = 'see less') -> TnStr:
        if not arr:
            return None
        if ix0 >= len(arr):
            return default
        _s: TnStr = arr[ix0].replace('\n', ' ').strip().split(separator)[ix1].strip()
        return _s

    @staticmethod
    def get_item(
            arr: TnArr, ix: TnInt = None, default: TnStr = None) -> TnAny:
        if ix is None:
            return None
        if not arr:
            return None
        if ix < 0 or ix >= len(arr):
            return default
        return arr[ix]

    @staticmethod
    def intersection(arr0: TyArr, arr1: TyArr) -> TyArr:
        if not arr0:
            return arr1
        if not arr1:
            return arr1
        return [item for item in arr0 if item in arr1]

    @staticmethod
    def is_empty(arr: TnArr) -> Literal[True, False]:
        if arr is None:
            return True
        if isinstance(arr, (list, tuple)):
            if arr == []:
                return True
        return False

    @classmethod
    def is_not_empty(
            cls, arr: TnArr) -> Literal[True, False]:
        return not cls.is_empty(arr)

    # def join_filter_none(
    @staticmethod
    def join_not_none(
            arr: Iterable[str | None], separator: str = ' ') -> TnStr:
        return separator.join(filter(None, arr))

    @staticmethod
    def length(arr: TnArr) -> TyNum:
        if not arr:
            return 0
        return len(arr)

    @staticmethod
    def makedirs(dirs: TnArr, **kwargs) -> None:
        if not dirs:
            return
        for dir in dirs:
            os.makedirs(dir, **kwargs)

    @staticmethod
    def sh_dic_from_keys_values(keys: TyArr, values: TyArr) -> TyDic:
        if not keys:
            return {}
        if not values:
            return {}
        return dict(zip(keys, values, strict=False))

    @staticmethod
    def sh_dic_zip(keys: Iterable[Any], values: Iterable[Any]) -> TyDic:
        if not keys:
            return {}
        if not values:
            return {}
        return dict(zip(keys, values, strict=False))

    @staticmethod
    def sh_item(arr: TnArr, ii: int) -> TnAny:
        if not arr:
            return None
        return arr[ii]

    @staticmethod
    def sh_item_lower(arr: TnArr, ii: int) -> TnAny:
        if arr is None:
            return arr
        if arr == []:
            return None
        return arr[ii].lower()

    @staticmethod
    def sh_item_if(
          string: TnStr, arr: TnArr, ii: int) -> TnAny:
        if arr is None:
            return arr
        if arr == []:
            return None
        item: Any = arr[ii]
        if string in item:
            return item
        return None

    @classmethod
    def sh_item0(cls, arr: TyArr) -> Any:
        if arr == []:
            return None
        return cls.sh_item(arr, 0)

    @classmethod
    def sh_item0_if(cls, string: str, arr: TyArr) -> Any:
        return cls.sh_item_if(string, arr, 0)

    @staticmethod
    def sh_items_str(arr: TnArr, start: int, end: int) -> TnStr:
        if arr is None:
            return arr
        if arr == []:
            return None
        return ' '.join(arr[start:end])

    @staticmethod
    def to_dic(arr: TyArr, keys: TyArr) -> TyDic:
        dic = {}
        # for ii in range(len(arr)):
        #     dic[keys[ii]] = arr[ii]
        for ii, item in enumerate(arr):
            dic[keys[ii]] = item
        return dic

    @staticmethod
    def sh_subarray(arr: TyArr, from_: int, to_: int) -> TyArr:
        if not arr:
            return arr
        if from_ >= to_:
            return arr
        from_new: int = max(0, from_)
        len_arr = len(arr)
        if to_ < len_arr:
            to_new: int = to_ + 1
        else:
            to_new = len_arr
        return arr[from_new:to_new]

    @staticmethod
    def sh_items_in_dic(arr: TnArr, dic: TnDic) -> TyArr:
        # def sh_values(arr: TnArr, dic: TnDic) -> TyArr:
        arr_new: TyArr = []
        if not arr:
            return arr_new
        if not dic:
            return arr_new
        for _key in arr:
            if _key in dic:
                arr_new.append(dic[_key])
        return arr_new

    @staticmethod
    def union(arr1: TnArr, arr2: TnArr) -> TnArr:
        if arr1 is None:
            return arr2
        if arr2 is None:
            return arr1
        return arr1 + [item for item in arr2 if item not in arr1]

    @staticmethod
    def yield_items(arr: TyArr, obj: Any) -> Iterator[TnTup]:
        if arr is None:
            yield None
        for _item in arr:
            yield (_item, obj)
