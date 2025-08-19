"""
chainsoup: A fluent pipeline interface for BeautifulSoup.

This package provides a chainable API to build complex queries for parsing
HTML and XML documents with BeautifulSoup in a more readable and
expressive way.

This __init__.py file exposes the primary user-facing classes and enums so
they can be imported directly from the `chainsoup` package.
"""
from .args import SpecalArg, DEFAULT, NestedNameArg, NestedRecursiveArg, NestedAttrArg, NestedAttrsArg, NestedStringArg
from .exceptions import ElementNotFound, UnknownElement, Error
from .pipeline import Pipeline, PipelineElement