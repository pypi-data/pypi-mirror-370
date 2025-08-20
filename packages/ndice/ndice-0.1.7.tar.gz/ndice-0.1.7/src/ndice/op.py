from enum import Enum
from functools import total_ordering
from typing import Self, Callable


type BinaryFunction = Callable[[int, int], int]


@total_ordering
class Op(Enum):
    PLUS = '+', int.__add__
    MINUS = '-', int.__sub__
    TIMES = 'x', int.__mul__

    def __init__(self, symbol: str, f: BinaryFunction):
        self.symbol = symbol
        self.f = f

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}.{self.name}>'

    def __str__(self) -> str:
        return self.symbol

    def __lt__(self, other: Self) -> bool:
        assert isinstance(other, Op)
        return self.symbol < other.symbol

    def __call__(self, a: int, b: int) -> int:
        return self.f(a, b)
