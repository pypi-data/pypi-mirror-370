"""
Defines custom exceptions for the pipeline library.

These exceptions provide specific error information related to failures
during the execution of a BeautifulSoup pipeline, such as a tag not being found
or an assertion failing.
"""
from typing import TypeVar, Generic, Iterable
from bs4.element import PageElement
T = TypeVar("T", bound=PageElement | Iterable[PageElement])

class Error(Exception): 
    """Base class for all exceptions in this library."""
    def __init__(self, msg: str = "") -> None:
        """
        Initializes the Error.

        Args:
            msg: An optional error message describing the issue.
        """
        self.msg: str = msg
        
    def __bool__(self) -> bool: 
        """Errors are considered False in boolean contexts."""
        return False
    
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        return f"{self.__class__.__name__}(msg={self.msg})"
    def __str__(self) -> str: return self.__repr__()
class UnknownElement(Error, Generic[T]):
    """
    Raised when an operation returns an unexpected BeautifulSoup element type.

    For example, raised if a pipeline step expects a `Tag` but receives a
    `NavigableString`.
    """
    def __init__(self, value: T, msg: str = "") -> None:
        """
        Initializes the UnknownElement error.

        Args:
            value: The unexpected element that was found.
            msg: An optional error message.
        """
        self.value: T = value
        super().__init__(msg=msg)
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        return f"{self.__class__.__name__}(msg={self.msg}, value={self.value})"
class ElementNotFound(Error): 
    """Raised when a `find` operation fails to find any matching element."""
    ...
class AssertError(Error): 
    """Raised when a pipeline assertion (`assert_all`, `assert_any`) fails."""
    ...
class IndexOutError(Error): 
    """Raised when attempting to access a sequence with an out-of-bounds index."""
    def __init__(self, index: int, msg: str = "") -> None:
        """
        Initializes the IndexOutError.

        Args:
            index: The index that caused the error.
            msg: An optional error message.
        """
        self.index: int = index
        super().__init__(msg=msg)
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        return f"{self.__class__.__name__}(msg={self.msg}, index={self.index})"

