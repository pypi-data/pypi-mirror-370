from .dice import Dice
from .rng import high, low, RNG


def roll(rng: RNG, *dice_expression: Dice) -> int:
    total = 0
    for dice_term in dice_expression:
        total = dice_term.op(total, sum(roll_each_die(rng, dice_term)))
    return total


def min_roll(*dice_expression: Dice) -> int:
    return roll(low, *dice_expression)


def max_roll(*dice_expression: Dice) -> int:
    return roll(high, *dice_expression)


def roll_each_die(rng: RNG, dice: Dice) -> list[int]:
    if dice.is_mod:
        return [dice.number * dice.sides]
    else:
        return [_roll_die(rng, dice.sides) for _ in range(dice.number)]


def _roll_die(rng: RNG, sides: int) -> int:
    roll = rng(sides)
    assert 1 <= roll <= sides
    return roll
