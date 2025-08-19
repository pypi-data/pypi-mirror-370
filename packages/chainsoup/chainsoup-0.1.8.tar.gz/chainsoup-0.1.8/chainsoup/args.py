"""
Defines specialized argument classes for building complex pipeline queries.

This module provides the `NestedArg` class, which allows for the construction
of arguments for deeply nested searches in a fluent and expressive way. It
also defines the `SpecalArg` enum used to control the behavior of nested
argument resolution.
"""

from typing import Any, Generic, TypeVar, overload, Literal, Sequence
from enum import Enum
from .types import Strainable

class SpecalArg(Enum):
    """
    Defines special behaviors for resolving `NestedArg` values.

    When a nested search has multiple levels, the arguments for each level
    (like 'name' or 'recursive') may not all be specified to the same depth.
    This enum controls how the shorter argument lists are padded to match the
    deepest list.
    """
    EXPANDLAST = "EXPANDLAST"
    """Repeats the last provided value for any remaining levels."""
    FILLDEFAULT = "FILLDEFAULT"
    """Fills any remaining levels with `DEFAULT, like lambda _: True`."""
    FILLNONE = "FILLNONE"
    """Fills any remaining levels with `None`."""
    FILLFALSE = "FILLFALSE"
    """Fills any remaining levels with `False`."""
    FILLTRUE = "FILLTRUE"
    """Fills any remaining levels with `True`."""

class Default: ...
DEFAULT = Default()

V = TypeVar("V")
class NestedArgBase(Generic[V]):
    """
    Base class for a nested argument container.

    This class holds a list of values and a special resolution strategy
    that are used to construct arguments for each step in a nested pipeline search.
    """
    def __init__(self) -> None: 
        """Initializes the NestedArgBase."""
        self.values: list[V] = []
        self.specal: SpecalArg = SpecalArg.FILLDEFAULT
    def copy(self) -> "NestedArgBase[V]":
        result = NestedArgBase()
        result.values = self.values.copy()
        result.specal = self.specal
        return result
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        s = ' > '.join(map(str, self.values))
        if self.specal is not None:
            s += ' > ' + str(self.specal)
        return f"{self.__class__.__name__}({s})" 
    def __len__(self) -> int:
        """Returns the number of values currently in the argument list."""
        return self.values.__len__()
def resolve_value(values: Sequence[V | Default], 
                  specal: SpecalArg, 
                  max_n: int = -1, 
                  default: V | None = None) -> Sequence[V] | Sequence[V | None] | Sequence[V | bool] | Sequence[V | None | bool]:
    """
    Resolves a list of values to a specific length based on a special behavior.

    This function is used internally by the pipeline to ensure all argument lists
    for a nested search have the same length.

    Args:
        values: The list of values to resolve.
        specal: The special resolution strategy to apply if padding is needed.
        max_n: The target length for the list. If negative, the original list
               is returned.

    Returns:
        The resolved list of values, padded or truncated to `max_n`.

    Raises:
        ValueError: If `specal` is `EXPANDLAST` and `values` is empty.
    """
    resolved_values: list[V | None] = [default if isinstance(value, Default) else value for value in values]
    if max_n < 0: return resolved_values
    if len(resolved_values) == max_n: return resolved_values
    if len(resolved_values) > max_n: return resolved_values[:max_n]
    left: int = max_n - len(resolved_values)
    if specal == SpecalArg.EXPANDLAST:
        if len(resolved_values) == 0: 
            raise ValueError(f"{specal} can't use at first place")
        last = resolved_values[-1]
        return resolved_values + [last]*left
    if specal == SpecalArg.FILLDEFAULT:
        return resolved_values + [default]*left
    if specal == SpecalArg.FILLTRUE:
        return resolved_values + [True]*left
    if specal == SpecalArg.FILLFALSE:
        return resolved_values + [False]*left
    return resolved_values + [None]*left
    
class BaseNestedStrainableArgBase(NestedArgBase[Strainable | None]): ...
class BaseNestedStrainableArg(BaseNestedStrainableArgBase): 
    def copy(self) -> "BaseNestedStrainableArg":
        result = BaseNestedStrainableArg()
        result.values = self.values.copy()
        result.specal = self.specal
        return result
    @overload
    def add(self, value: SpecalArg) -> BaseNestedStrainableArgBase: ...
    @overload
    def add(self, value: Strainable | None) -> "BaseNestedStrainableArg": ...
    def add(self, value: Strainable | None | SpecalArg) -> "BaseNestedStrainableArg | BaseNestedStrainableArgBase":
        result = self.copy()
        if isinstance(value, SpecalArg):
            result.specal = value
            return result
        result.values.append(value)
        return result
    then = add
    __rshift__ = add
NestedNameArgBase = BaseNestedStrainableArgBase
NestedNameArg = BaseNestedStrainableArg
NestedStringArgBase = BaseNestedStrainableArgBase
NestedStringArg = BaseNestedStrainableArg

K = TypeVar('K', dict[str, Strainable | None] | Strainable | None, Strainable | Default | None)
class BaseNestedAttrsArgBase(NestedArgBase[K]): ...
class BaseNestedAttrsArg(BaseNestedAttrsArgBase[K]): 
    def copy(self) -> "BaseNestedAttrsArg[K]":
        result = BaseNestedAttrsArg()
        result.values = self.values.copy()
        result.specal = self.specal
        return result
    @overload
    def add(self, value: SpecalArg) -> BaseNestedAttrsArgBase[K]: ...
    @overload
    def add(self, value: K) -> "BaseNestedAttrsArg[K]": ...
    def add(self, value: K | SpecalArg) -> "BaseNestedAttrsArg[K] | BaseNestedAttrsArgBase[K]":
        result = self.copy()
        if isinstance(value, SpecalArg):
            result.specal = value
            return result
        result.values.append(value)
        return result
    then = add
    __rshift__ = add

NestedAttrArgBase = BaseNestedAttrsArgBase[Strainable | Default | None]
NestedAttrArg = BaseNestedAttrsArg[Strainable | Default | None]
NestedAttrsArgBase = BaseNestedAttrsArgBase[dict[str, Strainable | None] | Strainable | None]
NestedAttrsArg = BaseNestedAttrsArg[dict[str, Strainable | None] | Strainable | None]

class NestedRecursiveArgBase(NestedArgBase[bool | Default]): ...
class NestedRecursiveArg(NestedRecursiveArgBase): 
    def copy(self) -> "NestedRecursiveArg":
        result = NestedRecursiveArg()
        result.values = self.values.copy()
        result.specal = self.specal
        return result
    @overload
    def add(self, value: SpecalArg) -> NestedRecursiveArgBase: ...
    @overload
    def add(self, value: bool | Default) -> "NestedRecursiveArg": ...
    def add(self, value: bool | Default | SpecalArg) -> "NestedRecursiveArg | NestedRecursiveArgBase":
        result = self.copy()
        if isinstance(value, SpecalArg):
            result.specal = value
            return result
        result.values.append(value)
        return result
    then = add
    __rshift__ = add
# string: NestedArgBase[Strainable | None] = NestedArg(),
# **kwargs: NestedArgBase[Strainable | Default | None],
