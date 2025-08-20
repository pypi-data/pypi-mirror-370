from datetime import datetime
from datetime import date

TyDate = date
TnDate = None | TyDate
TnStr = None | str


class Date:

    @staticmethod
    def sh(datestring: TnStr, fmt: str) -> TnDate:
        if not datestring:
            return None
        return datetime.strptime(datestring, fmt).date()
