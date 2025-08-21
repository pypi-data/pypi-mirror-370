# coding=utf-8
from typing import Any

TyAoO = list[Any]


class AoO:
    """ Manage Array of Objects
    """
    @staticmethod
    def to_unique(aoo: TyAoO) -> TyAoO:
        """ Removes duplicates from Array of Objects
        """
        aoo_new: TyAoO = []
        for _obj in aoo:
            if _obj not in aoo_new and _obj is not None:
                aoo_new.append(_obj)
        return aoo_new
