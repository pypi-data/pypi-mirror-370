# coding=utf-8

from typing import Any
TyBytes = bytes
TyDoS = dict[Any, str]
TnDoS = None | TyDoS


class Byte:
    """ Manage Byte Class
    """
    @staticmethod
    def replace_by_dic(bytes_: TyBytes, **kwargs) -> str:
        dic: TnDoS = kwargs.get('dic_replace')
        if not dic:
            return bytes_.decode('utf-8')
        string = bytes_.decode('utf-8')
        for k, v in dic.items():
            string = string.replace(k, v)
        return string
