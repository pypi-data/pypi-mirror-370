"""
Exceptions used throughout
"""

from __future__ import annotations

from typing import Any, Callable, Optional


# TODO: move this into an `fgen_runtime` package
class CompiledExtensionNotFoundError(ImportError):
    """
    Raised when a compiled extension can't be imported i.e. found
    """

    def __init__(self, compiled_extension_name: str):
        error_msg = f"Could not find compiled extension {compiled_extension_name!r}"

        super().__init__(error_msg)


class MissingOptionalDependencyError(ImportError):
    """
    Raised when an optional dependency is missing

    For example, plotting dependencies like matplotlib
    """

    def __init__(self, callable_name: str, requirement: str) -> None:
        """
        Initialise the error

        Parameters
        ----------
        callable_name
            The name of the callable that requires the dependency

        requirement
            The name of the requirement
        """
        error_msg = f"`{callable_name}` requires {requirement} to be installed"
        super().__init__(error_msg)


class WrapperError(ValueError):
    """
    Base exception for errors that arise from wrapper functionality
    """


class NotInitialisedError(WrapperError):
    """
    Raised when the wrapper around the Fortran module hasn't been initialised yet
    """

    def __init__(self, instance: Any, method: Optional[Callable[..., Any]] = None):
        if method:
            error_msg = f"{instance} must be initialised before {method} is called"
        else:
            error_msg = f"instance ({instance:r}) is not initialized yet"

        super().__init__(error_msg)


# TODO: change or even remove this when we move to better error handling
class UnallocatedMemoryError(ValueError):
    """
    Raised when we try to access memory that has not yet been allocated

    We can't always catch this error, but this is what we raise when we can.
    """

    def __init__(self, variable_name: str):
        error_msg = (
            f"The memory required to access `{variable_name}` is unallocated. "
            "You must allocate it before trying to access its value. "
            "Unfortunately, we cannot provide more information "
            "about why this memory is not yet allocated."
        )

        super().__init__(error_msg)
