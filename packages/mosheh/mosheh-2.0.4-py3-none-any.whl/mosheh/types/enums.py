"""
As a professional alternative to dealing with options (e.g. to choose between roles),
this file provides standard interfaces for the entire operation of the project.

The classes here declared (using any enum type - Enum, StrEnum, IntEnum, ...) are enums
with a really useful function: to standardize the possible types of their own types
(for example, a function strictly assumes only 4 different types, and exactly one of
them).
"""

from enum import StrEnum, auto


class Statement(StrEnum):
    """Enum-like class to enumerate in-code the dealed statements."""

    Import = auto()
    ImportFrom = auto()
    Assign = auto()
    AnnAssign = auto()
    ClassDef = auto()
    FunctionDef = auto()
    AsyncFunctionDef = auto()
    Assert = auto()


class ImportType(StrEnum):
    """Enum-like class to enumerate in-code the import types."""

    Native = auto()
    TrdParty = auto()
    Local = auto()


class FunctionType(StrEnum):
    """Enum-like class to enumerate in-code the function types."""

    Function = auto()
    Method = auto()
    Generator = auto()
    Coroutine = auto()


class FileRole(StrEnum):
    """Enum-like class to enumerate in-code the files investigated."""

    PythonSourceCode = ':material-language-python: Python Source Code'
    PythonStubFile = ':material-language-python: Python Stub File'
