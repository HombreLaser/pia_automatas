from enum import Enum
from dataclasses import dataclass


class TokenType(Enum):
    NAME_FIELD = 0
    NAME = 1
    START = 2
    READ = 3
    PRINT = 4
    EQUALS = 5
    ID = 6
    NUMBER = 7
    EXPR = 8
    END = 9
    SUM = 10
    SUBSTRACTION = 11
    MULTIPLY = 12
    DIVIDE = 13
    POWER = 14
    LEF_PARENS = 15
    RIGHT_PARENS = 16

@dataclass
class Token:
    type: TokenType
    value: any = None

    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value is not None else "")
