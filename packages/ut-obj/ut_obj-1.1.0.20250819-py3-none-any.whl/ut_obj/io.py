# coding=utf-8
from typing import Any


class Io:

    @staticmethod
    def verify(io: Any) -> None:
        if io is None:
            raise Exception("io is None")
        elif isinstance(io, str):
            if io == '':
                raise Exception("io is empty string")
        elif isinstance(io, bytes):
            if io == b'':
                raise Exception("io is empty byte string")
