"""
ltcodecs.exceptions
-------------------

This module contains custom exceptions for ltcodecs
"""


class EncodingFailed(Exception):
    """
    Raised when encoding fails
    """

    def __init__(self, message: str = "Encoding failed") -> None:
        self.message = message
        super().__init__(self.message)
