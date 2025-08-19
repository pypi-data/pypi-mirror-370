from typing import TypeAlias, Callable, Iterable
from re import Pattern
from bs4.element import Tag

# Type Aliases for BeautifulSoup's filter arguments
SimpleStrainable: TypeAlias = (
    str
    | bool
    | bytes
    | Pattern[str]
    | Callable[[str], bool]
    | Callable[[Tag], bool]
)
Strainable: TypeAlias = SimpleStrainable | Iterable[SimpleStrainable]