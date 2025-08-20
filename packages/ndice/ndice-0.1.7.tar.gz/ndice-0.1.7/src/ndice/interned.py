from __future__ import annotations

import inspect

from collections import OrderedDict
from typing import Any, TypeVar


T = TypeVar('T')


def interned(cls: type[T]) -> type[T]:
    cache: dict[tuple, T] = {}
    original_new = cls.__new__

    def __new__(cls, *args, **kwargs):
        arguments = _get_arguments(cls, *args, **kwargs)

        key = tuple(arguments.values())
        if key in cache:
            return cache[key]

        instance = original_new(cls)
        for name, value in arguments.items():
            object.__setattr__(instance, name, value)

        cache[key] = instance
        return instance

    cls.__new__ = __new__  # type: ignore[method-assign]
    return cls


def _get_arguments(cls: type, *args, **kwargs) -> OrderedDict[str, Any]:
    init_signature = inspect.signature(cls.__init__)  # type: ignore[misc]
    bound_arguments = init_signature.bind(None, *args, **kwargs)
    bound_arguments.apply_defaults()
    bound_arguments.arguments.pop('self')
    return bound_arguments.arguments
