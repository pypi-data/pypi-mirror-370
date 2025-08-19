"""
The core pipeline implementation for chaining BeautifulSoup operations.

This module contains the `Pipeline` and `PipelineSequence` classes, which are
the heart of the library. It also defines the various pipeline elements that
represent individual operations like finding, filtering, and asserting on
BeautifulSoup tags.
"""

from typing import TypeAlias, Callable, Iterable, Any, TypeVar, Generic, Literal, Sequence, overload
from re import Pattern
from bs4.element import Tag, NavigableString, PageElement

from .args import resolve_value, Default, NestedNameArgBase, NestedNameArg, NestedAttrsArgBase, NestedRecursiveArg, NestedRecursiveArgBase, NestedStringArgBase, NestedStringArg, NestedAttrArgBase
from .exceptions import Error, ElementNotFound, UnknownElement, AssertError, IndexOutError
from .types import Strainable

T = TypeVar("T", bound=PageElement)
TAny = TypeVar("TAny")

class PipelineElement: 
    """Abstract base class for an operation on a single Tag."""
    def copy(self) -> "PipelineElement": raise NotImplementedError()
    def _exec(self, value: Tag) -> Tag | Error: raise NotImplementedError()
class PipelineSequenceElement:
    """Abstract base class for an operation on a sequence of Tags."""
    def copy(self) -> "PipelineSequenceElement": raise NotImplementedError()
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag] | Error: raise NotImplementedError()
class Pipeline2SequenceElement:
    """Abstract base class for an operation that converts a Tag to a sequence of Tags."""
    def copy(self) -> "Pipeline2SequenceElement": raise NotImplementedError()
    def _exec(self, value: Tag) -> Sequence[Tag] | Error: raise NotImplementedError()
class Sequence2PipelineElement:
    """Abstract base class for an operation that converts a sequence of Tags to a single Tag."""
    def copy(self) -> "Sequence2PipelineElement": raise NotImplementedError()
    def _exec(self, value: Sequence[Tag]) -> Tag | Error: raise NotImplementedError()
    
class FindTag(PipelineElement):
    """A pipeline step that finds the first matching Tag."""
    def __init__(
        self,
        name: Strainable | None = None,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool | None = None,
        string: Strainable | None = None,
        **kwargs: Strainable | None
    ) -> None:
        """Initializes the FindTag operation with BeautifulSoup find() arguments."""
        self.name = name
        self.attrs = attrs
        self.recursive = recursive if recursive is not None else True
        self.string = string
        self.kwargs = kwargs
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name={self.name}, attrs={self.attrs}, recursive={self.recursive}, string={self.string}, kwargs={self.kwargs})"
    def _exec(self, value: Tag) -> Tag | UnknownElement[PageElement] | ElementNotFound: 
        """Executes the find() operation on the given tag."""
        result = value.find(
            name=self.name,
            attrs=self.attrs,
            recursive=self.recursive,
            string=self.string,
            **self.kwargs
        )
        if result is None: 
            return ElementNotFound(msg=f'tag not found for {self}')
        if not isinstance(result, Tag): 
            return UnknownElement(
                value=result,
                msg=f"its type is not Tag, type: {type(result)}"
            )
        return result
    def copy(self) -> "FindTag":
        """Creates a copy of this operation."""
        return FindTag(
            name = self.name,
            attrs = self.attrs,
            recursive = self.recursive,
            string = self.string,
            **self.kwargs,   
        )
class FindAllTags(Pipeline2SequenceElement):
    """A pipeline step that finds all matching Tags, returning a sequence."""
    def __init__(
        self,
        name: Strainable | None = None,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: Strainable | None = None,
        limit: int | None = None,
        **kwargs: Strainable | None
    ) -> None:
        """Initializes the FindAllTags operation with BeautifulSoup find_all() arguments."""
        self.name = name
        self.attrs = attrs
        self.recursive = recursive
        self.string = string
        self.limit = limit
        self.kwargs = kwargs
    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name={self.name}, attrs={self.attrs}, recursive={self.recursive}, string={self.string}, kwargs={self.kwargs})"
    def _exec(self, value: Tag) -> Sequence[Tag] | UnknownElement[PageElement]: 
        """Executes the find_all() operation on the given tag."""
        results: list[Tag | NavigableString | None] = value.find_all(
            name=self.name,
            attrs=self.attrs,
            recursive=self.recursive,
            string=self.string,
            limit=self.limit,
            **self.kwargs
        )
        for idx, result in enumerate(results):
            if not isinstance(result, Tag): 
                return UnknownElement(
                    value=result,
                    msg=f"its type is not Tag, type: {type(result)} at idx: {idx}"
                )
        return results
    def copy(self) -> "FindAllTags":
        """Creates a copy of this operation."""
        return FindAllTags(
            name = self.name,
            attrs = self.attrs,
            recursive = self.recursive,
            string = self.string,
            limit = self.limit,
            **self.kwargs,   
        )

class PipelineFinal:
    def __init__(self, pipeline: "Pipeline") -> None:
        self.pipeline = pipeline
    def run(self, soup: Tag) -> Tag:
        result = self.pipeline.run(soup)
        if isinstance(result, Error):
            raise result
        return result
    def transform(self, fn: Callable[[Tag], TAny]) -> "PipelineTransformFinal[TAny]":
        return PipelineTransformFinal(self.pipeline, fn)
class PipelineTransformFinal(Generic[TAny]):
    def __init__(self, pipeline: "Pipeline", fn: Callable[[Tag], TAny]) -> None:
        self.pipeline = pipeline
        self.fn = fn
    def run(self, soup: Tag) -> TAny:
        result = self.pipeline.run(soup)
        if isinstance(result, Error):
            raise result
        return self.fn(result)
class PipelineSequenceFinal:
    def __init__(self, pipeline: "PipelineSequence") -> None:
        self.pipeline = pipeline
    def run(self, soup: Tag) -> Sequence[Tag]:
        result = self.pipeline.run(soup)
        if isinstance(result, Error):
            raise result
        return result
    def transform(self, fn: Callable[[Sequence[Tag]], TAny]) -> "PipelineSequenceTransformFinal[TAny]":
        return PipelineSequenceTransformFinal(self.pipeline, fn)
class PipelineSequenceTransformFinal(Generic[TAny]):
    def __init__(self, pipeline: "PipelineSequence", fn: Callable[[Sequence[Tag]], TAny]) -> None:
        self.pipeline = pipeline
        self.fn = fn
    def run(self, soup: Tag) -> TAny:
        result = self.pipeline.run(soup)
        if isinstance(result, Error):
            raise result
        return self.fn(result)
class Pipeline(PipelineElement):
    """
    Builds and executes a chain of commands to find a single BeautifulSoup Tag.

    Each method like `find_tag` or `find_nested_tag` adds a step to the pipeline
    and returns a new Pipeline instance, allowing for method chaining. The
    pipeline is executed by calling the `run()` or `run_and_raise_for_error()`
    methods.
    """
    def __init__(self) -> None:
        """Initializes a new, empty pipeline."""
        self._runs: list[PipelineElement] = []
    def copy(self) -> "Pipeline":
        """
        Creates a shallow copy of the pipeline.

        This allows for branching the pipeline to perform different searches
        from a common base.
        """
        pipeline = Pipeline()
        # pipeline._runs = [_run.copy() for _run in self._runs] # BUG: may raise max-recurrsion error
        pipeline._runs = self._runs.copy()
        return pipeline
    def _exec(self, value: Tag) -> Tag | Error: 
        return self.run(value)
    def run(self, value: Tag) -> Tag | Error:
        """
        Executes the pipeline starting from the given soup or tag.

        Args:
            soup: The BeautifulSoup object or Tag to start the search from.

        Returns:
            The final Tag if found, otherwise an `Error` object.
        """
        result: Tag = value
        for _run in self._runs:
            new_result = _run._exec(result)
            if isinstance(new_result, Error): return new_result
            result = new_result
        return result
    __call__ = run
    def run_and_raise_for_error(self, soup: Tag) -> Tag:
        """
        Executes the pipeline and raises an exception on failure.

        Args:
            soup: The BeautifulSoup object or Tag to start the search from.

        Returns:
            The final Tag if found.

        Raises:
            Error: An exception (e.g., ElementNotFound) if the pipeline fails.
        """
        result = self.run(soup)
        if isinstance(result, Error):
            raise result
        return result
    @property
    def raise_for_error(self) -> PipelineFinal: 
        return PipelineFinal(self.copy())
    @overload
    def join(self, run: "Pipeline") -> "Pipeline": ...
    @overload
    def join(self, run: "PipelineSequence") -> "PipelineSequence": ...
    def join(self, run: "Pipeline | PipelineSequence") -> "Pipeline | PipelineSequence":
        if isinstance(run, PipelineSequence):
            pipelinesequence = PipelineSequence(
                pipeline=self.join(run.pipeline),
                solo_run=run._solo_run.copy()
            )
            pipelinesequence._runs = run._runs.copy()
            if run._final_run is not None:
                raise RuntimeError(f"Something Went Wrong. final_run is {run._final_run}.")
            return pipelinesequence
        pipeline = self.copy()
        pipeline._runs.append(run.copy())
        return pipeline
    @overload
    def find_tag(
        self,
        name: Strainable,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: Strainable | None = None,
        **kwargs: Strainable | None
    ) -> "Pipeline": ...
    @overload
    def find_tag(
        self,
        name: None = None,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: None = None,
        **kwargs: Strainable | None
    ) -> "Pipeline": ...
    def find_tag(
        self,
        name: Strainable | None = None,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: Strainable | None = None,
        **kwargs: Strainable | None,
    ) -> "Pipeline":
        """
        Adds a `find()` operation to the pipeline.

        Args:
            **kwargs: Keyword arguments to be passed to `bs4.Tag.find()`.
                      (e.g., name, attrs, recursive, string).

        Returns:
            A new Pipeline instance with the find operation appended.
        """
        pipeline = self.copy()
        if name is None and string is not None: 
            raise AttributeError('name is None but string is not None, this cannot find Tag but it finds NavigableString')
        pipeline._runs.append(
            FindTag(
                name=name,
                attrs=attrs,
                recursive=recursive,
                string=string,
                **kwargs
            )
        )
        return pipeline
    def find_nested_tag(
        self,
        name: NestedNameArgBase = NestedNameArg(),
        attrs: dict[str, NestedAttrArgBase] | NestedAttrsArgBase = {},
        recursive: NestedRecursiveArgBase = NestedRecursiveArg(),
        string: NestedStringArgBase = NestedStringArg(),
        **kwargs: NestedAttrArgBase,
    ) -> "Pipeline":
        """
        Adds multiple `find_tag` operations to the pipeline to locate a deeply nested tag.

        This method is useful for navigating a known, deeply nested structure
        without chaining multiple `find_tag` calls. The `NestedArg` class is used
        to specify the arguments for each level of the search.

        Args:
            name: A NestedArg defining the tag name for each step.
            attrs: A NestedArg defining the attributes for each step. Can be a single
                   NestedArg for the whole attrs dict, or a dict of NestedArgs.
            recursive: A NestedArg defining the recursive flag for each step.
            string: A NestedArg defining the string content for each step.
            **kwargs: Other `find` arguments (like `class_`) as NestedArgs.

        Returns:
            A new Pipeline instance with the nested find operations appended.
        """
        # Create a copy of the current pipeline to avoid modifying it in place.
        pipeline = self.copy()
        
        # --- Step 1: Determine the maximum depth of the nested search ---
        # This is the number of `find` operations we will need to chain.
        # We start by checking the length of the explicitly defined NestedArgs.
        _deepest: int = max(len(name), len(recursive), len(string))
        # Then, we find the maximum length among any NestedArgs passed in via **kwargs.
        _kwargs_value_max_length: int = max((len(value) for value in kwargs.values()), default=0)
        # The `attrs` argument can be structured in two ways, so it needs special handling.
        new_attrs: Sequence[dict[str, Strainable | None] | Strainable | None]
        
        # --- Step 2: Resolve the `attrs` argument ---
        # Case A: `attrs` is a single NestedArg, e.g., attrs=NestedArg() >> {'class': 'a'} >> {'class': 'b'}
        if not isinstance(attrs, dict):
            _attrs_value_max_length: int = len(attrs)
            # The overall depth is the max of all argument lengths seen so far.
            deepest: int = max(_deepest, _kwargs_value_max_length, _attrs_value_max_length)
            # Resolve the single `attrs` NestedArg to match the deepest length.
            new_attrs = resolve_value(attrs.values, attrs.specal, max_n=deepest, default=lambda _: True)
        # Case B: `attrs` is a dict of NestedArgs, e.g., attrs={'class': NestedArg() >> 'a' >> 'b'}
        else:
            # Find the max length among all NestedArgs inside the `attrs` dictionary.
            _attrs_value_max_length: int = max((len(value) for value in attrs.values()), default=0)
            # The overall depth is the max of all argument lengths.
            deepest: int = max(_deepest, _kwargs_value_max_length, _attrs_value_max_length)
            # First, resolve each individual NestedArg within the dict to the same `deepest` length.
            resolved_attrs = {
                k: resolve_value(v.values, specal=v.specal, max_n=deepest, default=lambda _: True)
                for k, v in attrs.items()
            }
            # Then, "transpose" the dictionary of lists into a list of dictionaries.
            # This creates one `attrs` dictionary for each level of the search.
            # Example: {'class': ['a', 'b']} becomes [{'class': 'a'}, {'class': 'b'}]
            new_attrs = [
                {k: values[i] for k, values in resolved_attrs.items()}
                for i in range(deepest)
            ] 
            
        # --- Step 3: Resolve all other arguments to the final `deepest` length ---
        # Resolve the `kwargs` in the same way as the dictionary-based `attrs`.
        resolved_kwargs = {
            k: resolve_value(v.values, specal=v.specal, max_n=deepest, default=lambda _: True)
            for k, v in kwargs.items()
        }
        # Transpose the kwargs into a list of dictionaries for each search level.
        new_kwargs: list[dict[str, Strainable | None]] = [
            {k: values[i] for k, values in resolved_kwargs.items()}
            for i in range(deepest)
        ]
        
        # Resolve the simple, direct NestedArgs.
        new_name = resolve_value(name.values, specal=name.specal, max_n=deepest, default=None)
        new_recursive = resolve_value(recursive.values, specal=recursive.specal, max_n=deepest, default=True)
        new_string = resolve_value(string.values, specal=string.specal, max_n=deepest, default=None)
        
        # --- Step 4: Build and append the FindTag operations ---
        # Use `zip` to iterate over all the resolved argument lists simultaneously.
        # Each iteration of this loop corresponds to one level of the nested search.
        for _name, _attrs, _recursive, _string, _kwargs in zip(
            new_name, new_attrs, new_recursive, new_string, new_kwargs,
            strict=True # Ensure all lists have the same length, which they should.
        ):
            # Sanity check: `find(string=...)` without a `name` will find NavigableString,
            # but the goal of this library is to work with Tags. Raise an error to prevent this.
            if _name is None and _string is not None:
                raise AttributeError('name is None but string is not None, this cannot find Tag but it finds NavigableString')
            
            # Create a FindTag operation with the resolved arguments for the current level.
            pipeline._runs.append(
                FindTag(
                    name=_name,
                    attrs=_attrs,
                    recursive=_recursive,
                    string=_string,
                    **_kwargs
                )
            )
            
        # Return the newly configured pipeline.
        return pipeline
    
    @overload
    def find_all_tags(
        self,
        name: Strainable,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: Strainable | None = None,
        limit: int | None = None,
        **kwargs: Strainable | None
    ) -> "PipelineSequence": ...
    @overload
    def find_all_tags(
        self,
        name: None = None,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: None = None,
        limit: int | None = None,
        **kwargs: Strainable | None
    ) -> "PipelineSequence": ...
    def find_all_tags(
        self,
        name: Strainable | None = None,
        attrs: dict[str, Strainable | None] | Strainable | None = {},
        recursive: bool = True,
        string: Strainable | None = None,
        limit: int | None = None,
        **kwargs: Strainable | None
    ) -> "PipelineSequence":
        """
        Converts the pipeline to a `PipelineSequence` by finding all matching tags.

        This is a terminal operation for a standard `Pipeline`, as it transitions
        from finding a single item to finding multiple items.

        Args:
            **kwargs: Keyword arguments to be passed to `bs4.Tag.find_all()`.
                      (e.g., name, attrs, recursive, limit).

        Returns:
            A `PipelineSequence` instance initialized with this find_all operation.
        """
        if name is None and string is not None: 
            raise AttributeError('name is None but string is not None, this cannot find Tag but it finds NavigableString')
        return PipelineSequence(
            pipeline=self.copy(), 
            solo_run=FindAllTags(
                name=name,
                attrs=attrs,
                recursive=recursive,
                string=string,
                limit=limit,
                **kwargs
            )
        )
        
class Filter(PipelineSequenceElement):
    """A pipeline step that filters a sequence of tags using a function."""
    def __init__(self, fn: Callable[[Tag], bool | Sequence[Tag] | Tag | Error]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag]: 
        return [v for v in value if self.fn(v)]
    def copy(self) -> "Filter":
        return Filter(fn = self.fn)
class EnumerateFilter(PipelineSequenceElement):
    """A pipeline step that filters a sequence of tags using a function that accepts index and tag."""
    def __init__(self, fn: Callable[[int, Tag], bool | Sequence[Tag] | Tag | Error]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag]: 
        return [v for idx, v in enumerate(value) if self.fn(idx, v)]
    def copy(self) -> "EnumerateFilter":
        return EnumerateFilter(fn = self.fn)
class Map(PipelineSequenceElement):
    """A pipeline step that transforms each tag in a sequence using a function."""
    def __init__(self, fn: Callable[[Tag], Tag]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag]: 
        return [self.fn(v) for v in value]
    def copy(self) -> "Map":
        return Map(fn = self.fn)
class EnumerateMap(PipelineSequenceElement):
    """A pipeline step that transforms each tag using a function that accepts index and tag."""
    def __init__(self, fn: Callable[[int, Tag], Tag]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag]: 
        return [self.fn(idx, v) for idx, v in enumerate(value)]
    def copy(self) -> "EnumerateMap":
        return EnumerateMap(fn = self.fn)
    
class AssertAll(PipelineSequenceElement):
    """A pipeline step that asserts a condition is true for all tags in a sequence using a function."""
    def __init__(self, fn: Callable[[Tag], bool | Sequence[Tag] | Tag | Error]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag] | AssertError: 
        if not all(self.fn(v) for v in value):
            return AssertError(msg=f"Not All values fullfill the fn's requrenment")
        return value
    def copy(self) -> "AssertAll":
        return AssertAll(fn = self.fn)
class AssertEnumerateAll(PipelineSequenceElement):
    """A pipeline step that asserts a condition is true for all tags in a sequence using a function that accepts index and tag."""
    def __init__(self, fn: Callable[[int, Tag], bool | Sequence[Tag] | Tag | Error]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag] | AssertError: 
        if not all(self.fn(idx, v) for idx, v in enumerate(value)):
            return AssertError(msg=f"Not All values fullfill the fn's requrenment")
        return value
    def copy(self) -> "AssertEnumerateAll":
        return AssertEnumerateAll(fn = self.fn)
class AssertAny(PipelineSequenceElement):
    """A pipeline step that asserts a condition is true for any tags in a sequence using a function."""
    def __init__(self, fn: Callable[[Tag], bool | Sequence[Tag] | Tag | Error]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag] | AssertError: 
        if not any(self.fn(v) for v in value):
            return AssertError(msg=f"Any values doesn't fullfill the fn's requrenment")
        return value
    def copy(self) -> "AssertAny":
        return AssertAny(fn = self.fn)
class AssertEnumerateAny(PipelineSequenceElement):
    """A pipeline step that asserts a condition is true for any tags in a sequence using a function that accepts index and tag."""
    def __init__(self, fn: Callable[[int, Tag], bool | Sequence[Tag] | Tag | Error]) -> None:
        self.fn = fn
    def _exec(self, value: Sequence[Tag]) -> Sequence[Tag] | AssertError: 
        if not all(self.fn(idx, v) for idx, v in enumerate(value)):
            return AssertError(msg=f"Any values doesn't fullfill the fn's requrenment")
        return value
    def copy(self) -> "AssertEnumerateAny":
        return AssertEnumerateAny(fn = self.fn)
class ByIndex(Sequence2PipelineElement):
    """A pipeline step that selects a single tag from a sequence by its index."""
    def __init__(self, index: int) -> None:
        self.index = index
    def _exec(self, value: Sequence[Tag]) -> Tag | IndexOutError: 
        if self.index >= 0 and len(value) <= self.index:
            return IndexOutError(index=self.index, msg=f"Unable to get {self.index}ith element.")
        if self.index < 0 and len(value) < (-self.index):
            return IndexOutError(index=self.index, msg=f"Unable to get {self.index}ith element.")
        return value[self.index]
    def copy(self) -> "ByIndex": 
        return ByIndex(index=self.index)
class PipelineSequence(PipelineElement):
    """
    Builds and executes a chain of commands on a sequence of BeautifulSoup Tags.

    This class is created when `find_all_tags` is called on a `Pipeline`. It
    allows for sequence operations like `filter`, `map`, and `assert_all`.
    The chain can be terminated by selecting a single element (e.g., with `.first`
    or `[i]`), which returns a `Pipeline` that can be further chained or executed.
    """
    def __init__(self, pipeline: Pipeline, solo_run: Pipeline2SequenceElement) -> None:
        """Initializes the PipelineSequence."""
        self.pipeline = pipeline
        
        self._solo_run: Pipeline2SequenceElement = solo_run
        self._runs: list[PipelineSequenceElement] = []
        self._final_run: Sequence2PipelineElement | None = None
    def copy(self) -> "PipelineSequence":
        """Creates a shallow copy of the pipeline sequence."""
        pipeline = PipelineSequence(
            pipeline=self.pipeline.copy(),
            solo_run=self._solo_run.copy(),
        )
        # pipeline._runs = [_run.copy() for _run in self._runs] # BUG: may raise max-recurrsion error
        pipeline._runs = self._runs.copy()
        pipeline._final_run = self._final_run.copy() if self._final_run is not None else None
        return pipeline
    def _exec(self, value: Tag) -> Tag | Error:
        """Internal execution method to run the full sequence-to-tag pipeline."""
        if self._final_run is None:
            raise RuntimeError(f"Something Went Wrong. final_run is {self._final_run}.")
        
        result = self._solo_run._exec(value)
        
        if isinstance(result, Error): return result
        
        for _run in self._runs:
            result = _run._exec(result)
            if isinstance(result, Error): return result
        
        return self._final_run._exec(result)
        
    def run(self, value: Tag) -> Sequence[Tag] | Error:
        """
        Executes the pipeline up to the sequence operations.

        Args:
            soup: The BeautifulSoup object or Tag to start the search from.

        Returns:
            The final sequence of Tags, or an `Error` object on failure.
        """
        result = self.pipeline.run(value)
        if not isinstance(result, Tag): return result
        new_result = self._solo_run._exec(result)
        
        if isinstance(new_result, Error): return new_result
        
        for _run in self._runs:
            new_result = _run._exec(new_result)
            if isinstance(new_result, Error): return new_result
            
        return new_result
    __call__ = run
    def run_and_raise_for_error(self, soup: Tag) -> Sequence[Tag]:
        """
        Executes the sequence pipeline and raises an exception on failure.

        Args:
            soup: The BeautifulSoup object or Tag to start the search from.

        Returns:
            The final sequence of Tags.

        Raises:
            Error: An exception if any part of the pipeline fails.
        """
        result = self.run(soup)
        if isinstance(result, Error): raise result
        return result
    @property
    def raise_for_error(self) -> PipelineSequenceFinal: 
        return PipelineSequenceFinal(self.copy())
    
    def filter(self, fn: Callable[[Tag], bool | Sequence[Tag] | Tag | Error]) -> "PipelineSequence": 
        """
        Adds a filter operation to the sequence pipeline.

        Args:
            fn: A function that takes a Tag and returns `True` to keep it.

        Returns:
            A new `PipelineSequence` with the filter step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(Filter(fn=fn))
        return pipeline
    def enumerate_filter(self, fn: Callable[[int, Tag], bool | Sequence[Tag] | Tag | Error]) -> "PipelineSequence": 
        """
        Adds a filter operation to the sequence pipeline.

        Args:
            fn: A function that takes a index, Tag and returns `True` to keep it.

        Returns:
            A new `PipelineSequence` with the filter step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(EnumerateFilter(fn=fn))
        return pipeline
    
    def map(self, fn: Callable[[Tag], Tag]) -> "PipelineSequence": 
        """
        Adds a map/transform operation to the sequence pipeline.

        Args:
            fn: A function that takes a Tag and returns a transformed Tag.

        Returns:
            A new `PipelineSequence` with the map step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(Map(fn=fn))
        return pipeline
    def enumerate_map(self, fn: Callable[[int, Tag], Tag]) -> "PipelineSequence": 
        """
        Adds a map/transform operation to the sequence pipeline.

        Args:
            fn: A function that takes a index, Tag and returns a transformed Tag.

        Returns:
            A new `PipelineSequence` with the map step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(EnumerateMap(fn=fn))
        return pipeline
    
    def assert_all(self, fn: Callable[[Tag], bool | Sequence[Tag] | Tag | Error]) -> "PipelineSequence": 
        """
        Adds an assertion that all tags in the sequence satisfy a condition.

        If the condition is not met, the pipeline will return an `AssertError`.

        Args:
            fn: A function that takes a Tag and returns `True` if the condition is met.

        Returns:
            A new `PipelineSequence` with the assertion step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(AssertAll(fn=fn))
        return pipeline
    def assert_enumerate_all(self, fn: Callable[[int, Tag], bool | Sequence[Tag] | Tag | Error]) -> "PipelineSequence": 
        """
        Adds an assertion that all tags in the sequence satisfy a condition.

        If the condition is not met, the pipeline will return an `AssertError`.

        Args:
            fn: A function that takes a index, Tag and returns `True` if the condition is met.

        Returns:
            A new `PipelineSequence` with the assertion step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(AssertEnumerateAll(fn=fn))
        return pipeline
    
    def assert_any(self, fn: Callable[[Tag], bool | Sequence[Tag] | Tag | Error]) -> "PipelineSequence": 
        """
        Adds an assertion that any tags in the sequence satisfy a condition.

        If the condition is not met, the pipeline will return an `AssertError`.

        Args:
            fn: A function that takes a Tag and returns `True` if the condition is met.

        Returns:
            A new `PipelineSequence` with the assertion step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(AssertAny(fn=fn))
        return pipeline
    def assert_enumerate_any(self, fn: Callable[[int, Tag], bool | Sequence[Tag] | Tag | Error]) -> "PipelineSequence": 
        """
        Adds an assertion that any tags in the sequence satisfy a condition.

        If the condition is not met, the pipeline will return an `AssertError`.

        Args:
            fn: A function that takes a index, Tag and returns `True` if the condition is met.

        Returns:
            A new `PipelineSequence` with the assertion step appended.
        """
        pipeline = self.copy()
        pipeline._runs.append(AssertEnumerateAny(fn=fn))
        return pipeline
    
    @property
    def first(self) -> Pipeline: 
        """
        Selects the first element from the sequence, returning to a `Pipeline`.

        This is an alias for `__getitem__(0)`.
        """
        return self[0]
    @property
    def last(self) -> Pipeline: 
        """
        Selects the last element from the sequence, returning to a `Pipeline`.

        This is an alias for `__getitem__(-1)`.
        """
        return self[-1]
    def __getitem__(self, index: int) -> Pipeline:
        """
        Selects an element by index from the sequence, returning to a `Pipeline`.

        This is a finalizer for the sequence, converting it back to a pipeline
        that will yield a single tag.

        Args:
            index: The integer index of the tag to select.

        Returns:
            A new `Pipeline` that includes the full sequence logic followed by
            the index selection.
        """
        pipeline = self.copy()
        pipeline._final_run = ByIndex(index=index)
        # Append the entire configured sequence operation as a single step to the base pipeline
        pipeline.pipeline._runs.append(pipeline)
        return pipeline.pipeline