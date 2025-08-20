"""Custom exception classes and exception handling utilities.

Provides:
- ExceptionInfo class for enhanced error context propagation
- Helper functions for structured exception data extraction
- Chain traversal utilities for exception causes
"""


class ExceptionInfo(Exception):
    """Enhanced exception for propagating error context through stack layers.

    Carries additional structured data and root cause information.

    Attributes
        message: Human-readable error description
        data: Contextual data dictionary related to the error
        cause: Original exception that triggered this one

    """

    def __init__(self, msg: str = None, data: dict = None, cause: BaseException = None):
        """Initialize exception with context details.

        Args:
            msg: Primary error message
            data: Additional context data as key-value pairs
            cause: Original exception that caused this one

        """
        super().__init__(msg)
        self._message = msg or ""
        self._data = data or {}
        if cause:
            self._cause = cause

    @property
    def message(self):
        """Get the primary error message string."""
        return self._message

    @property
    def data(self):
        """Get additional context data as a dictionary."""
        return self._data

    @property
    def cause(self):
        """Get the original causing exception instance."""
        return self._cause

    def __str__(self):
        """Return informal string representation of the exception.

        Shows the exception type and primary message in a human-readable format.

        Returns
            str: Brief error description in format 'ExceptionInfo: {message}'

        """
        return f"ExceptionInfo: {self._message}"

    def __repr__(self):
        """Return unambiguous string representation of the exception.

        Provides detailed technical information including all constructor parameters.

        Returns
            str: Machine-readable representation showing msg, data and cause

        """
        return f"ExceptionInfo(msg={self.message}, data={self.data}, cause={self.cause})"


def ex_message(e, chain: bool = False, chain_separator: str = " --- ") -> str:
    """Extract error message(s) from exception, optionally following cause chain.

    Args:
        e: Exception to process
        chain: Whether to include messages from chained exceptions
        chain_separator: String to join multiple messages with

    Returns:
        Combined error message string. Falls back to str(e) if no message attribute.

    """

    def ex_message_chain(e):
        error_message = ex_message(e)
        next_ex = e.__cause__ or e.__context__
        while next_ex:
            error_message = error_message + chain_separator + ex_message(next_ex)
            next_ex = next_ex.__cause__ or next_ex.__context__
        return error_message

    try:
        return ex_message_chain(e) if chain else e.message
    except AttributeError:
        return str(e)


def ex_data(e) -> dict:
    """Extract structured data dictionary from exception.

    Args:
        e: Exception to inspect

    Returns:
        Context data dictionary. Returns empty dict if no data available.

    """
    try:
        return e.data
    except AttributeError:
        return {}


def ex_cause(e, get_root=False):
    """Get the direct cause or root cause exception from exception chain.

    Args:
        e: Exception to inspect
        get_root: If True, traverses the entire chain to find the root cause
                  If False (default), returns only the direct cause

    Returns:
        Original causing exception or None if not available
    """
    # First try to get the cause from our custom attribute; if not available, use Python's built-in exception chaining
    try:
        cause = e.cause
    except AttributeError:
        cause = e.__cause__ or e.__context__

    # If get_root is True and we found a cause, traverse to find the root
    if get_root and cause is not None:
        next_cause = ex_cause(cause, get_root=True)
        return next_cause if next_cause is not None else cause

    return cause
