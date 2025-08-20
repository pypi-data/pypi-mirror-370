# coding=utf-8
from collections.abc import Iterator
from typing import Any

TyArr = list[Any]
TnArr = None | TyArr
TyPoA = list[TnArr]
TyTup = tuple[Any, ...]

TnTup = None | TyTup


class PoA:
    """
    Manage Pair of Arrays
    """
    @staticmethod
    def yield_items(
            poa: TyPoA, obj: Any) -> Iterator[TnTup]:
        arr0 = poa[0]
        arr1 = poa[1]
        if arr0 is None:
            yield None
        elif arr1 is None:
            yield None
        else:
            for item0 in arr0:
                for item1 in arr1:
                    yield (item0, item1, obj)
