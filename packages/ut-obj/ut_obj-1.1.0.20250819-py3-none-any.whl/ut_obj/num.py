TyNum = int | float
TnInt = None | int
TnNum = None | TyNum


class Num:
    """ Manage Number Class
    """
    @staticmethod
    def divide(num1: TnNum, num2: TnNum, digits: TnInt = None) -> TnNum:
        if not num1:
            return num2
        if not num2:
            return num1
        if isinstance(num1, (int, float)):
            if isinstance(num2, (int, float)):
                if num2 != 0:
                    if num1 != 0:
                        if not digits:
                            return num1/num2
                        return round(num1/num2, digits)
                    return num2
                return num1
            return num1
        if isinstance(num2, (int, float)):
            return num2
        return None

    @staticmethod
    def multiply(num1: TnNum, num2: TnNum, digits: TnInt = None) -> TnNum:
        if not num1 or not num2:
            return None
        if isinstance(num1, (int, float)):
            if isinstance(num2, (int, float)):
                if not digits:
                    return num1*num2
                return round(num1*num2, digits)
            return None
        return None
