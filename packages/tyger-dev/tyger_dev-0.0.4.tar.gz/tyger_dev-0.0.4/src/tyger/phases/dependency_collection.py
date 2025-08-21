import ast
from typing import Any, Optional

from tyger.parser import Parser
from tyger.phase import Phase
from tyger.diagnostics.diagnostics import TygerDiagnostic
from tyger.diagnostics.errors import ModuleNotFoundTygerError


def resolve_full_name(module: str, level: int, package_name: str = "") -> str:
    if level > 0:
        # We need to resolve the full name of the module
        if not package_name:
            raise ImportError("attempted relative import with no known parent package")

        package_name_tokens = package_name.split(".")
        package_name_prefix = ".".join(package_name_tokens[:-level])
        module = f"{package_name_prefix}.{module}"
    return module


class DependencyCollectionPhase(Phase):
    def __init__(self, cwd: str = "", file_path: Optional[str] = None):
        self.parser = Parser(cwd)
        self.diagnostics: list[TygerDiagnostic] = []
        self.current_file_path = file_path

    def run(self, source: ast.Module, **kwargs) -> tuple[ast.Module, dict[str, Any]]:
        self.diagnostics = []
        deps = self.collect_dependencies(source.body)
        kwargs["dependencies"] = deps
        kwargs["diagnostics"] = self.diagnostics
        return source, kwargs

    def collect_dependencies(
        self, stmts: list[ast.stmt], package_name=""
    ) -> dict[str, ast.Module]:
        deps: dict[str, ast.Module] = {}
        for st in stmts:
            match st:
                case ast.FunctionDef(_, _, body):
                    func_deps = self.collect_dependencies(body, package_name)
                    deps.update(func_deps)
                case (
                    ast.For(_, _, body, orelse)
                    | ast.While(_, body, orelse)
                    | ast.If(_, body, orelse)
                ):
                    body_deps = self.collect_dependencies(body, package_name)
                    orelse_deps = self.collect_dependencies(orelse, package_name)
                    deps.update(body_deps)
                    deps.update(orelse_deps)
                case ast.ImportFrom(module, names, level):
                    if module is None:
                        module = ""
                    full_module_name = resolve_full_name(module, level, package_name)
                    if full_module_name.startswith(
                        "tyger"
                    ) or full_module_name.startswith("typing"):
                        continue
                    setattr(st, "__full_name__", full_module_name)
                    module_tokens = full_module_name.split(".")
                    for i, token in enumerate(module_tokens):
                        module_name = ".".join(module_tokens[: i + 1])
                        try:
                            module_ast = self.parser.parse_module(module_name)
                            module_deps = self.collect_dependencies(
                                module_ast.body, module_name
                            )
                            deps.update(module_deps)
                            deps[module_name] = module_ast
                        except ModuleNotFoundError:
                            # Only add diagnostic for the top-level module not found
                            # Skip intermediate modules as they might be expected to not exist
                            if i == 0:  # This is the top-level module
                                self.diagnostics.append(
                                    ModuleNotFoundTygerError(
                                        st,
                                        module_name,
                                        self.current_file_path,
                                    )
                                )
                            break  # Stop trying to parse further modules in this chain

                    for name in names:
                        try:
                            submodule_name = f"{full_module_name}.{name.name}"
                            submodule_ast = self.parser.parse_module(submodule_name)
                            submodule_deps = self.collect_dependencies(
                                submodule_ast.body, submodule_name
                            )
                            deps.update(submodule_deps)
                            deps[submodule_name] = submodule_ast
                        except ModuleNotFoundError:
                            # This is expected when the imported name is not a module
                            # but rather a function, class, or variable within the module
                            continue

                case ast.Import(names):
                    for name in names:
                        if name.name.startswith("tyger") or name.name.startswith(
                            "typing"
                        ):
                            continue
                        module_tokens = name.name.split(".")
                        for i in range(len(module_tokens)):
                            module_name = ".".join(module_tokens[: i + 1])
                            try:
                                module_ast = self.parser.parse_module(module_name)
                                module_deps = self.collect_dependencies(
                                    module_ast.body, module_name
                                )
                                deps.update(module_deps)
                                deps[module_name] = module_ast
                            except ModuleNotFoundError:
                                self.diagnostics.append(
                                    ModuleNotFoundTygerError(
                                        st,
                                        module_name,
                                        self.current_file_path,
                                    )
                                )

        return deps
