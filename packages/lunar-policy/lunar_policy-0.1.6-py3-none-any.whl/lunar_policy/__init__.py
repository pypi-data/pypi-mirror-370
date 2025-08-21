import importlib.metadata
from .data import Path, ComponentData
from .check import Check
from .result import Op, CheckStatus, AssertionResult, NoDataError
from .variables import variable, variable_or_default

__version__ = importlib.metadata.version("lunar_policy")

__all__ = [
    # Loading Data
    "Path",
    "ComponentData",

    # Making Assertions
    "Check",

    # Result Types
    "Op",
    "CheckStatus",
    "AssertionResult",

    # Snippet Variables
    "variable",
    "variable_or_default",

    # Exceptions
    "NoDataError"
]
