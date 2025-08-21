from __future__ import annotations
from typing import Optional, Any, Union
import ast
from abc import ABC

from tyger.diagnostics.diagnostics import TygerDiagnostic


class TygerError(TygerDiagnostic, ABC):
    """Base class for all Tyger type checking errors."""

    code: str = "TYG100"
    symbol: str = "generic-error"
    msg: str = "An error occurred during type checking"

    def __init__(self, node: ast.AST, filename: Optional[str] = None) -> None:
        super().__init__(node, filename)
        self.severity = "error"


class CriticalTypeCheckError(TygerError):
    """Error raised when a critical error occurs during type checking that requires stopping execution."""

    code = "TYG101"
    symbol: str = "critical-type-check-error"

    def __init__(
        self,
        node: ast.AST,
        filename: Optional[str] = None,
        reason: str = "A critical type check error occurred",
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            reason: The specific reason for the critical error
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.msg = reason

    def __str__(self) -> str:
        return f"{self.code} at {self.get_location()} - {self.msg}"


class TypeMismatchError(TygerError):
    """Error raised when there is a type mismatch."""

    code = "TYG102"
    symbol = "type-mismatch-error"

    def __init__(
        self,
        node: ast.AST,
        actual_type: Any,
        expected_type: Any,
        filename: Optional[str] = None,
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            actual_type: The type that was provided
            expected_type: The type that was expected
            filename: Optional name of the file where the error occurred
        """
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.msg = f"Expected type {self.expected_type}, got {self.actual_type}"
        super().__init__(node, filename)


class NotFoundBinOpTypeError(TygerError):
    """Error raised when no result type is found for an operation between two types."""

    code = "TYG103"
    symbol = "not-found-bin-op-type-error"

    def __init__(
        self,
        node: ast.AST,
        lty: Union[str, Any],
        rty: Union[str, Any],
        str_op: str,
        filename: Optional[str] = None,
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            lty: The left operand type
            rty: The right operand type
            str_op: The operation string representation
            filename: Optional name of the file where the error occurred
        """
        self.lty = lty
        self.rty = rty
        self.str_op = str_op
        self.msg = f"No result type found for operation '{self.str_op}' with arguments of type {self.lty} and {self.rty}"
        super().__init__(node, filename)


class NotFoundUnOpTypeError(TygerError):
    """Error raised when no result type is found for a unary operation on a type."""

    code = "TYG104"
    symbol = "not-found-un-op-type-error"

    def __init__(
        self,
        node: ast.AST,
        operand_type: Union[str, Any],
        str_op: str,
        filename: Optional[str] = None,
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            operand_type: The operand type
            str_op: The unary operation string representation
            filename: Name of the file where the error occurred
        """
        self.operand_type = operand_type
        self.str_op = str_op
        self.msg = f"No result type found for operation '{self.str_op}' with operand of type {self.operand_type}"
        super().__init__(node, filename)


class AttributeNotFoundError(TygerError):
    """Error raised when an attribute is not found in a type."""

    code = "TYG105"
    symbol: str = "attribute-not-found-error"

    def __init__(
        self,
        node: ast.AST,
        attr: str,
        object_name: str = "",
        filename: Optional[str] = None,
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            attr: The name of the attribute that was not found
            object_name: Optional name of the object being accessed
            filename: Optional name of the file where the error occurred
        """
        self.attr = attr
        self.object_name = object_name
        object_info = f" '{object_name}'" if object_name else ""
        self.msg = f"Attribute '{self.attr}' not found in object{object_info}"
        super().__init__(node, filename)


class NotFoundTypeError(TygerError):
    """Error raised when a referenced type cannot be found."""

    code = "TYG106"
    symbol: str = "not-found-type-error"

    def __init__(
        self, node: ast.AST, type_name: str, filename: Optional[str] = None
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            type_name: The name of the type that was not found
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.type_name = type_name
        self.msg = f"Type '{self.type_name}' not found in the current context"


class ArityMismatchError(TygerError):
    """Error for function calls with incorrect number of arguments."""

    code: str = "TYG107"
    symbol: str = "arity-mismatch-error"

    def __init__(
        self,
        node: ast.AST,
        expected_arity: int,
        actual_arity: int,
        filename: Optional[str] = None,
    ) -> None:
        super().__init__(node, filename)
        self.expected_arity = expected_arity
        self.actual_arity = actual_arity
        self.msg = f"Expected {expected_arity} argument(s), but got {actual_arity}"

class ModuleNotFoundTygerError(TygerError):
    """Error raised when a referenced module cannot be found."""

    code: str = "TYG108"
    symbol: str = "module-not-found-error"

    def __init__(
        self, node: ast.AST, module_name: str, filename: Optional[str] = None
    ) -> None:
        """
        Args:
            node: AST node where the error occurred
            module_name: The name of the module that was not found
            filename: Optional name of the file where the error occurred
        """
        super().__init__(node, filename)
        self.module_name = module_name
        self.msg = f"Module '{self.module_name}' not found"
