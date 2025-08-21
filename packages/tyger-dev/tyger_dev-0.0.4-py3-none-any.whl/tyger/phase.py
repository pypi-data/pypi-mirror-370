import ast
from abc import ABC, abstractmethod
from typing import Any


class Phase(ABC):
    @abstractmethod
    def run(self, source: ast.Module, **kwargs) -> tuple[ast.Module, dict[str, Any]]: ...
