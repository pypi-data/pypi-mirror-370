# coding=utf-8
from typing import Any

from datetime import datetime
import re
import orjson
import simplejson

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]

TnInt = None | int
TnFloat = None | float
TnStr = None | str
TnAoA = None | TyAoA
TnArr = None | TyArr
TnDic = None | TyDic
TnDatetime = None | datetime


class Str:
    """ Manage String Class
    """
    @staticmethod
    def sh_date(string: str, fmt: TnStr = None) -> TnDatetime:
        """ show string as date using the format string
        """
        try:
            if fmt is None:
                fmt = "%m/%d/%Y"
            _date: TnDatetime = datetime.strptime(string, fmt)
            return _date
        except Exception:
            return None

    @staticmethod
    def lchop(string: str, prefix: str) -> str:
        """ return substring of string which starts at the
            end of the contained prefix
        """
        if string.startswith(prefix):
            return string[len(prefix):]
        return string

    @staticmethod
    def rchop(string: str, suffix: str) -> str:
        """ return substring of string which ends at the
            beginning of the contained suffix
        """
        if suffix and string.endswith(suffix):
            return string[:-len(suffix)]
        return string

    @staticmethod
    def strip_multiple_chars(string: str, chars: str) -> str:
        """ replace multiple characters in string
        """
        return string.translate(str.maketrans("", "", chars))

    @staticmethod
    def is_odd(string: str) -> bool:
        """ check if string is odd number
        """
        if string.isnumeric():
            if int(string) % 2 == 0:
                return False
            return True
        return False

    @staticmethod
    def is_integer(string: str) -> bool:
        """ check if string is integer
        """
        if string[0] in ('-', '+'):
            return string[1:].isdigit()
        return string.isdigit()

    @staticmethod
    def is_boolean(string: str) -> bool:
        """ check if string is boolean
        """
        if string.strip().lower() in ['true', 'false']:
            return True
        return False

    @staticmethod
    def is_undefined(string: TnStr) -> bool:
        """ check if string is undefined (None or empty)
        """
        if string is None or string == '':
            return True
        return False

    @staticmethod
    def nvl(string: TnStr) -> TnStr:
        """ nvl function similar to SQL NVL function
        """
        if string is None:
            return ''
        return string

    @staticmethod
    def strip_n(string: str) -> str:
        """ Replace new line characters by Blanks and strip Blanks
        """
        return string.replace('\n', ' ').strip()

    @staticmethod
    def remove(string: str, a_to_remove: TyArr) -> str:
        """ remove all character of a list
        """
        for to_remove in a_to_remove:
            string = string.replace(to_remove, '')
        return string

    @staticmethod
    def sh_boolean(string: str) -> bool:
        """ Show string as boolean if string is a boolean
        """
        match string.lower():
            case 'true':
                return True
            case 'false':
                return False
            case _:
                raise ValueError

    @staticmethod
    def sh_float(string: str) -> TnFloat:
        """ Returns Float if string is of Type Float
            otherwise None
        """
        try:
            return float(string)
        except Exception:
            return None

    @staticmethod
    def sh_int(string: str) -> TnInt:
        """ Returns Int if string is of Type Int
            otherwise None
        """
        try:
            return int(string)
        except ValueError:
            return None

    @staticmethod
    def sh_dic(string: str, sw_decimal=False) -> Any:
        """ Returns Dic if string is of Type Json-String
            otherwise None
        """
        try:
            if sw_decimal:
                return simplejson.loads(string, use_decimal=True)
            else:
                return orjson.loads(string)
        except Exception:
            msg = f"Parameter string = {string} could not be loaded with orjson"
            raise Exception(msg)

    @staticmethod
    def sh_arr(string: str) -> Any:
        """ Show valid Array string as Array
        """
        try:
            return orjson.loads(string)
        except Exception:
            msg = f"Parameter string = {string} could not be loaded with orjson"
            raise Exception(msg)

    @staticmethod
    def sh_aoa(string: str) -> Any:
        """ Show valid Array string as Array
        """
        try:
            return orjson.loads(string)
        except Exception:
            msg = f"Parameter string = {string} could not be loaded with orjson"
            raise Exception(msg)

    @staticmethod
    def sh_first_item(string: str) -> Any:
        """ Show first substring of string
        """
        return string.split()[0]

    @classmethod
    def sh_a_int(cls, string: str, sep: str) -> TyArr:
        """ Show first substring of string
        """
        # arr = string.split(sep)
        arr = re.split(sep, string)
        arr_new = []
        for item in arr:
            _item = item.strip()
            if not isinstance(_item, str):
                continue
            if not _item.isdigit():
                continue
            arr_new.append(cls.sh_int(_item))
        return arr_new

    @classmethod
    def sh_a_str(
            cls, string: str, sep: str, a_exclude: TnArr = None) -> Any:
        """ Show first substring of string
        """
        # arr = string.split(sep)
        arr = re.split(sep, string)

        if a_exclude is None:
            _arr = arr
        else:
            _arr = []
            for item in arr:
                _item = item.strip()
                if _item not in a_exclude:
                    _arr.append(_item)

        arr_new = []
        for item in _arr:
            if isinstance(item, str):
                arr_new.append(item.strip())
            elif isinstance(item, int):
                arr_new.append(str(item))
            else:
                arr_new.append(item)

        return arr_new

    @classmethod
    def sh_a_obj(
            cls, string: str, sep: str, a_exclude: TnArr = None) -> Any:
        """
        Show first substring of string
        """
        # arr = string.split(sep)
        arr = re.split(sep, string)

        if a_exclude is None:
            _arr = arr
        else:
            _arr = []
            for item in arr:
                _item = item.strip()
                if _item not in a_exclude:
                    _arr.append(_item)

        arr_new: TyArr = []
        for item in _arr:
            if isinstance(item, str):
                _item = item.strip()
                if _item.isdigit():
                    _item = cls.sh_int(_item)
                    arr_new.append(_item)
                else:
                    arr_new.append(_item)
            else:
                arr_new.append(item)

        return arr_new
