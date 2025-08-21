from enum import Enum

class YesOrNo(str, Enum):
    YES = "Y"
    NO = "N"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val = value.upper()
            if val in cls.__members__:
                return cls(val)
        return None

class Colors(str, Enum):
    BLUE = "blue"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val = value.upper()
            if val in cls.__members__:
                return cls(val)
        return None
