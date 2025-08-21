import ast
import os


class Parser:
    def __init__(self, cwd: str = os.getcwd()):
        self.cwd = cwd

    def parse(self, path: str) -> ast.Module:
        src = self.read_source(path) if path else ""
        module = ast.parse(src)

        # Add filename attribute to help with error reporting
        abs_path = os.path.abspath(self.build_file_path(path)) if path else None
        setattr(module, "filename", abs_path)
        return module

    def read_source(self, rel_path: str) -> str:
        abs_path = self.build_file_path(rel_path)
        with open(abs_path, "r") as file:
            return file.read()

    def parse_string(self, program: str) -> ast.Module:
        # TODO: If this line fails, there's a syntax error in the program.
        # We should catch that and raise a SyntaxError with the appropriate message.
        module = ast.parse(program)
        setattr(module, "filename", None)
        return module

    def build_file_path(self, rel_path: str) -> str:
        return os.path.join(self.cwd, rel_path)

    def parse_module(self, module_name: str) -> ast.Module:
        module_prefix = module_name.replace(".", os.sep)
        full_module_prefix = self.build_file_path(module_prefix)
        # module_path = None
        if os.path.isdir(full_module_prefix):
            file_path = os.path.join(full_module_prefix, "__init__.py")
            if os.path.isfile(file_path):
                module_path = os.path.join(module_prefix, "__init__.py")
            else:
                module_path = None
        elif os.path.isfile(f"{full_module_prefix}.py"):
            module_path = f"{module_prefix}.py"
        else:
            raise ModuleNotFoundError(f"No module named {module_name}")

        if module_path is None:
            raise ModuleNotFoundError(f"No module named {module_name}")

        module_ast = self.parse(module_path)
        return module_ast
