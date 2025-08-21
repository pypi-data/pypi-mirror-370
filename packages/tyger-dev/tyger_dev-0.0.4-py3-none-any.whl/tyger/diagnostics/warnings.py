from abc import ABC
import ast
from typing import Optional

from tyger.diagnostics.diagnostics import TygerDiagnostic
from tyger.diagnostics.errors import TygerError


class TygerWarning(TygerDiagnostic, ABC):
    """Base class for all Tyger warnings."""

    code: str = "TYG900"
    symbol: str = "generic-warning"
    msg: str = "A potential issue was detected during type checking"

    def __init__(self, node: ast.AST, filename: Optional[str] = None) -> None:
        super().__init__(node, filename)
        self.severity = "warning"


class UndefinedVariableWarning(TygerWarning):
    """Warning for undefined variables."""

    code: str = "TYG901"
    symbol: str = "undefined-variable-warning"

    def __init__(
        self,
        node: ast.AST,
        var_name: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        super().__init__(node, filename)
        self.msg = (
            f"Undefined variable '{var_name}'" if var_name else "Undefined variable"
        )


class UnsupportedExprWarning(TygerWarning):
    """Warning for unsupported expressions in the current context."""

    code = "TYG902"
    symbol: str = "unsupported-expr-warning"

    def __init__(
        self,
        node: ast.AST,
        reason: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        error_reason = (
            reason if reason is not None else "Expression not supported in this context"
        )
        super().__init__(node, filename)
        self.msg = error_reason


class RedefineVariableWarning(TygerWarning):
    """Error raised when a variable is redefined."""

    code = "TYG903"
    symbol: str = "redefine-variable-warning"

    def __init__(
        self, node: ast.AST, name: str, filename: Optional[str] = None
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            name: The name of the variable being redefined
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.name = name
        self.msg = f"Variable '{self.name}' already defined"


class UnsupportedTypeWarning(TygerWarning):
    """Warning for unsupported type annotations."""

    code = "TYG904"
    symbol: str = "unsupported-type-warning"

    def __init__(
        self,
        node: ast.AST,
        type_name: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        super().__init__(node, filename)
        self.msg = (
            f"Unsupported type annotation '{type_name}' - treating as unknown type"
            if type_name else "Unsupported type annotation - treating as unknown type"
        )
