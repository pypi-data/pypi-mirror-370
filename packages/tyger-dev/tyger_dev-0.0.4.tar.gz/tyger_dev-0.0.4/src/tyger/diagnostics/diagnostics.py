import ast
from abc import ABC
from typing import Optional


class TygerDiagnostic(Exception, ABC):
    """Base class for all Tyger diagnostics"""

    code: str = "TYG000"
    symbol: str = "generic-diagnostic"
    msg: str = "A diagnostic was reported during type checking"

    def __init__(self, node: ast.AST, filename: Optional[str] = None) -> None:
        super().__init__(self.msg)  # Initialize Exception with the error message
        self.node = node
        self.filename = filename
        self.lineno: Optional[int] = getattr(node, "lineno", None)
        self.end_lineno: Optional[int] = getattr(node, "end_lineno", None)
        self.col_offset: Optional[int] = getattr(node, "col_offset", None)
        self.end_col_offset: Optional[int] = getattr(node, "end_col_offset", None)
        self.severity: Optional[str] = None

    def get_location(self) -> str:
        """Get formatted location string for diagnostic reporting.

        Returns:
            String representation of diagnostic location (file:line:col)
        """
        # Handle cases where lineno or col_offset might be None
        line = self.lineno if self.lineno is not None else "?"
        col = self.col_offset if self.col_offset is not None else "?"

        return f"{self.filename}:{line}:{col}" if self.filename else f"{line}:{col}"

    def __str__(self) -> str:
        """String representation of the diagnostic.
        This will be the message shown when the diagnostic is published
        """
        return f"{self.msg}"
