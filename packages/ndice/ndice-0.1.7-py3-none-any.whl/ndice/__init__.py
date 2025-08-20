"""Sides - A dice rolling library for games."""

from .constants import d2, d3, d4, d6, d8, d10, d12, d20, d100
from .constants import four_d6, three_d6, two_d6
from .dice import d, Dice, mod, nd
from .find_version import find_version
from .mods import plus, minus, times
from .op import Op
from .rng import AscendingRNG, FixedRNG, high, low, mid, PRNG, RNG, rng
from .roll import max_roll, min_roll, roll, roll_each_die


__version__ = find_version()
__author__ = 'Don McCaughey'
__email__ = 'don@donm.cc'
