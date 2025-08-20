from random import randrange, Random
from typing import Callable, TypeAlias


RNG: TypeAlias = Callable[[int], int]


def rng(sides: int) -> int:
    return randrange(sides) + 1


def high(sides: int) -> int:
    return sides


def low(sides: int) -> int:
    return 1


def mid(sides: int) -> int:
    return (sides + 1) // 2


def AscendingRNG(initial_value: int) -> RNG:
    ascending_value = initial_value

    def ascending(sides: int) -> int:
        nonlocal ascending_value
        next_value = (max(ascending_value, 1) - 1) % sides + 1
        ascending_value += 1
        return next_value

    return ascending


def FixedRNG(fixed_value: int) -> RNG:
    return lambda sides: _clamp(1, fixed_value, sides)


def PRNG(seed: int) -> RNG:
    r = Random(seed)
    return lambda sides: r.randrange(sides) + 1


def _clamp(lower: int, value: int, upper: int) -> int:
    return max(lower, min(value, upper))
