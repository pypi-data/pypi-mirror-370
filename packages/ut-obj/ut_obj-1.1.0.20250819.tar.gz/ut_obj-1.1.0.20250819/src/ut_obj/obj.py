# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any
TyArr = list[Any]
TyCallable = Callable[..., Any]
TyTup = tuple[Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyArrTup = TyArr | TyTup
TyIterAny = Iterator[Any]

TnArr = None | TyArr
TnArrTup = None | TyArrTup
TnCallable = None | TyCallable


class Obj:
    """ Manage Object
    """
    @staticmethod
    def shrink_array(obj: Any) -> Any:
        if isinstance(obj, (tuple, list)):
            if len(obj) == 1:
                return obj[0]
        return obj

    # @classmethod
    # def verify_key_type(cls, obj: Any, sw: bool = True, pytype=type(str)) -> bool:
    #     if obj is None:
    #         return sw
    #     for item in obj:
    #         if isinstance(item, dict):
    #             for key in item.keys():
    #                 if not isinstance(key, pytype):
    #                     sw = False
    #                     print(f"key: {key} is not of type: {pytype}")
    #                     print(f"key type of key: {key} is {type(key)}")
    #             for value in item.values():
    #                 if not cls.verify_key_type(value, sw, pytype):
    #                     return False
    #     return sw

    # @classmethod
    # def verify_key_type_str(
    #         cls, obj: any, sw: bool = True):
    #     return cls.verify_key_type(obj, sw, type=(str))

    @staticmethod
    def yield_aod(obj: Any) -> TyIterAny:
        """ show objects as Array of Dictionaries
        """
        if isinstance(obj, (list, tuple)):
            # for _obj in obj:
            #     yield _obj
            yield from obj
        if isinstance(obj, (dict, str)):
            yield obj

    @staticmethod
    def sh_aod_if_arr(obj: Any, fncs=None) -> TyAoD:
        """ show objects as Array of Dictionaries
        """
        aod = []
        if fncs is None:
            for _obj in obj:
                if _obj is None:
                    continue
                if not _obj == {}:
                    continue
                aod.append(obj)
            return aod
        for _obj in obj:
            obj_new = fncs(_obj)
            if obj_new is None:
                continue
            if not obj_new == {}:
                continue
            aod.append(obj_new)
        return aod

    @staticmethod
    def sh_aod_if_dic(obj: Any, fncs: TnCallable = None) -> TyAoD:
        """ show objects as Array of Dictionaries
        """
        aod: TyAoD = []
        if fncs is None:
            obj_new = obj
        else:
            obj_new = fncs(obj)
        if obj_new is not None:
            if isinstance(obj_new, (dict)):
                if obj_new != {}:
                    aod.append(obj_new)
        return aod

    @classmethod
    def sh_aod(cls, obj: Any, fncs: TnCallable = None) -> TyAoD:
        """ show objects as Array of Dictionaries
        """
        aod = []
        if fncs is None:
            if isinstance(obj, (list, tuple)):
                for _obj in obj:
                    aod.append(_obj)
            elif isinstance(obj, (dict, str)):
                aod.append(obj)
            return aod
        if isinstance(obj, (list, tuple)):
            return cls.sh_aod_if_arr(obj, fncs)
        if isinstance(obj, dict):
            return cls.sh_aod_if_dic(obj, fncs)
        return aod

    @staticmethod
    def sh_arr(obj: Any | TyArr) -> TnArr:
        if obj is None:
            return obj
        if isinstance(obj, list):
            return obj
        return [obj]

    @staticmethod
    def to_string(obj: Any, separator: str = '.') -> str:
        if obj is None:
            return ''
        if isinstance(obj, (list, tuple)):
            return separator.join(obj)
        if isinstance(obj, str):
            return obj.strip()
        if isinstance(obj, int):
            return str(obj)
        return ''

    @staticmethod
    def sh_text(obj: Any) -> Any:
        if isinstance(obj, (list, tuple)):
            return ' '.join(obj)
        return obj

    # @classmethod
    # def flatten(cls, obj):
    #     array = []
    #     for element in obj:
    #         if isinstance(element, list):
    #             array.extend(cls.flatten(element))
    #         else:
    #             array.append(element)
    #     return array

    @classmethod
    def extract_values(cls, obj, key, **kwargs):
        arr = kwargs.get('arr', [])
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    cls.extract_values(v, key, arr=arr)
                if k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                cls.extract_values(item, key, arr=arr)
        return arr
