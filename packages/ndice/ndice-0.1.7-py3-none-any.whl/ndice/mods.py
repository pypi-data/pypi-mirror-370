from .dice import Dice, mod
from .op import Op


def plus(value: int | Dice) -> Dice:
    return value.to_plus() if isinstance(value, Dice) else mod(Op.PLUS, value)


def minus(value: int | Dice) -> Dice:
    return value.to_minus() if isinstance(value, Dice) else mod(Op.MINUS, value)


def times(value: int | Dice) -> Dice:
    return value.to_times() if isinstance(value, Dice) else mod(Op.TIMES, value)
