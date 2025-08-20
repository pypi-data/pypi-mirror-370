from __future__ import annotations

from dataclasses import dataclass

from .interned import interned
from .op import Op


@interned
@dataclass(frozen=True, slots=True)
class Dice:
    number: int
    sides: int
    op: Op = Op.PLUS

    @property
    def is_mod(self) -> bool:
        return 0 == self.number or 0 == self.sides or 1 == self.sides

    def to_plus(self) -> Dice:
        return self.__class__(self.number, self.sides, Op.PLUS)

    def to_minus(self) -> Dice:
        return self.__class__(self.number, self.sides, Op.MINUS)

    def to_times(self) -> Dice:
        return self.__class__(self.number, self.sides, Op.TIMES)

    @classmethod
    def die(cls, sides: int) -> Dice:
        return cls(1, sides)

    @classmethod
    def mod(cls, op: Op, value: int) -> Dice:
        return cls(value, 1, op)

    @classmethod
    def n_dice(cls, number: int, sides: int | Dice) -> Dice:
        sides_value = sides.sides if isinstance(sides, Dice) else sides
        return cls(number, sides_value, Op.PLUS)


d = Dice.die
mod = Dice.mod
nd = Dice.n_dice
