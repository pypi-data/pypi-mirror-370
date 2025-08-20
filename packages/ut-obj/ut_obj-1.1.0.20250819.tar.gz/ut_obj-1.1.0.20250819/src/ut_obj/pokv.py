from typing import Any

from .str import Str
from .date import Date


TyDic = dict[Any, Any]
TyStr = str

TnDic = None | TyDic
TnStr = None | TyStr


class PoKV:
    """
    Pair of key, value
    """
    @classmethod
    def sh_value_by_key_type(cls, key: str, value: Any, d_valid_parms: TnDic) -> Any:

        # Log.debug("key", key)
        # Log.debug("value", value)
        if not d_valid_parms:
            return value
        _type: TnStr = d_valid_parms.get(key)
        if not _type:
            return value
        if isinstance(_type, str):
            match _type:
                case 'int':
                    value = int(value)
                case 'bool':
                    value = Str.sh_boolean(value)
                case 'dict':
                    print(f"DoEqu dict value = {value}")
                    value = Str.sh_dic(value)
                    print(f"DoEqu dict value = {value}")
                case 'list':
                    value = Str.sh_arr(value)
                case '%Y-%m-%d':
                    value = Date.sh(value, _type)
                case '_':
                    match _type[0]:
                        case '[', '{':
                            _obj = Str.sh_dic(_type)
                            if value not in _obj:
                                msg = (f"parameter={key} value={value} is invalid; "
                                       f"valid values are={_obj}")
                                raise Exception(msg)

        # Log.debug("value", value)
        return value
