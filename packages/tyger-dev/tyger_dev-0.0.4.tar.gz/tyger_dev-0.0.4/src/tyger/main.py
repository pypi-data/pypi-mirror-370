import argparse
import ast
import glob
import json
import os
import sys
import types
from typing import Any, Dict, List, Optional

from tyger.discipline.sectypes.ToAST import SecurityASTElaborator
from tyger.discipline.sectypes.types import SecurityTypeSystem
from tyger.discipline.simple.ToAST import SimpleASTElaborator
from tyger.discipline.simple.types import SimpleTypeSystem
from tyger.driver import Driver
from tyger.parser import Parser
from tyger.phases.dependency_collection import DependencyCollectionPhase
from tyger.phases.elaboration import ElaborationPhase
from tyger.phases.type_check import TypingPhase

# Constants
DISCIPLINE_SIMPLE = "simple"
DISCIPLINE_SECURITY = "security"
VALID_DISCIPLINES = [DISCIPLINE_SIMPLE, DISCIPLINE_SECURITY]


def setup_cli_parser() -> argparse.ArgumentParser:
    """
    Set up and configure the command-line interface parser.
    """
    cli_parser = argparse.ArgumentParser(description="Tyger: a simple typechecker")

    # Create a mutually exclusive group for file input sources
    input_group = cli_parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "file_paths",
        nargs="*",  # Changed from '+' to '*' to allow empty list when using stdin
        help="one or more target file paths (glob patterns supported within quotes)",
    )

    input_group.add_argument(
        "--stdin",
        nargs=1,
        metavar="SOURCE_FILE",
        help="Read code from standard input, with SOURCE_FILE specifying the file path for import resolution",
    )

    cli_parser.add_argument(
        "-d",
        "--discipline",
        default=DISCIPLINE_SIMPLE,
        choices=VALID_DISCIPLINES,
        help=f"Type discipline to use. Available options: {', '.join(VALID_DISCIPLINES)}",
    )

    cli_parser.add_argument(
        "--elaborate",
        action="store_true",
        help="Elaborate target source and dependencies for gradual typing",
    )

    cli_parser.add_argument(
        "--json",
        action="store_true",
        help="Export diagnostics in JSON format to stdout",
    )

    return cli_parser


def process_single_file(
    file_path: str,
    discipline: str,
    phases: List,
    elaborate: bool,
    json_output: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Process a single file and return any diagnostics.
    """
    file_dir, file_name = os.path.split(file_path)
    file_parser = Parser(file_dir)
    file_ast = file_parser.parse(file_name)
    full_file_path = os.path.abspath(file_path)

    driver = Driver(phases)
    target_module, deps_asts, diagnostics = driver.run_2(file_ast)

    if diagnostics and json_output:
        diagnostic_data = []
        for diagnostic in diagnostics:
            diagnostic_info: dict[str, str | int | None] = {
                "type": diagnostic.__class__.__name__,
                "message": str(diagnostic),
            }

            # Try to extract additional information if available
            if hasattr(diagnostic, "lineno"):
                diagnostic_info["lineno"] = diagnostic.lineno
            if hasattr(diagnostic, "end_lineno"):
                diagnostic_info["end_lineno"] = diagnostic.end_lineno
            if hasattr(diagnostic, "col_offset"):
                diagnostic_info["col_offset"] = diagnostic.col_offset
            if hasattr(diagnostic, "end_col_offset"):
                diagnostic_info["end_col_offset"] = diagnostic.end_col_offset

            if hasattr(diagnostic, "filename"):
                diagnostic_info["filename"] = diagnostic.filename
            else:
                # Add the filename if not already present
                diagnostic_info["filename"] = full_file_path

            if hasattr(diagnostic, "severity"):
                diagnostic_info["severity"] = diagnostic.severity

            if hasattr(diagnostic, "symbol"):
                diagnostic_info["symbol"] = diagnostic.symbol

            if hasattr(diagnostic, "code"):
                diagnostic_info["message-id"] = diagnostic.code

            diagnostic_data.append(diagnostic_info)

        output = {
            "diagnostics": diagnostic_data,
            "file_name": file_name,
            "file_path": full_file_path,
            "discipline": discipline,
            "elaborate": elaborate,
        }
        # TODO: Include elaboration diagnostics in the output
        return output

    if elaborate:
        _execute_elaborated_code(target_module, deps_asts)

    return None


def process_from_stdin(
    discipline: str,
    phases: List,
    elaborate: bool,
    json_output: bool = False,
    file_dir: Optional[str] = None,
    source_file_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Process code from standard input and return any diagnostics.
    """
    code = sys.stdin.read()
    file_parser = Parser(file_dir) if file_dir else Parser()
    file_ast = file_parser.parse_string(code)

    # Use the actual source file path for better error reporting if provided
    filename = os.path.abspath(source_file_path) if source_file_path else "<stdin>"
    setattr(file_ast, "filename", filename)

    driver = Driver(phases)
    target_module, deps_asts, diagnostics = driver.run_2(file_ast)

    if diagnostics and json_output:
        diagnostic_data = []
        for diagnostic in diagnostics:
            diagnostic_info: dict[str, str | int | None] = {
                "type": diagnostic.__class__.__name__,
                "message": str(diagnostic),
            }

            # Try to extract additional information if available
            if hasattr(diagnostic, "lineno"):
                diagnostic_info["lineno"] = diagnostic.lineno
            if hasattr(diagnostic, "end_lineno"):
                diagnostic_info["end_lineno"] = diagnostic.end_lineno
            if hasattr(diagnostic, "col_offset"):
                diagnostic_info["col_offset"] = diagnostic.col_offset
            if hasattr(diagnostic, "end_col_offset"):
                diagnostic_info["end_col_offset"] = diagnostic.end_col_offset

            if hasattr(diagnostic, "filename"):
                diagnostic_info["filename"] = diagnostic.filename
            else:
                diagnostic_info["filename"] = filename

            if hasattr(diagnostic, "severity"):
                diagnostic_info["severity"] = diagnostic.severity

            if hasattr(diagnostic, "symbol"):
                diagnostic_info["symbol"] = diagnostic.symbol

            if hasattr(diagnostic, "code"):
                diagnostic_info["message-id"] = diagnostic.code

            diagnostic_data.append(diagnostic_info)

        # Determine the file name for output
        file_name = os.path.basename(filename) if filename != "<stdin>" else "<stdin>"

        output = {
            "diagnostics": diagnostic_data,
            "file_name": file_name,
            "file_path": filename,
            "discipline": discipline,
            "elaborate": elaborate,
        }
        return output

    if elaborate:
        _execute_elaborated_code(target_module, deps_asts)

    return None


def _execute_elaborated_code(
    target_module: ast.Module, deps_asts: Dict[str, ast.Module]
) -> None:
    """
    Execute elaborated code and initialize dependencies.
    """
    deps = {
        name: compile(ast.fix_missing_locations(code_ast), "<tyger>", "exec")
        for name, code_ast in deps_asts.items()
    }

    # We initialize the dependencies
    # We first add them to sys.modules
    for dep in deps:
        sys.modules[dep] = types.ModuleType(dep)

    # Then we add submodules to module namespace where necessary
    for dep in deps:
        name_tokens = dep.split(".")
        for i in range(len(name_tokens) - 1):
            to_update_name = ".".join(name_tokens[: i + 1])
            to_update_module = sys.modules[to_update_name]
            to_add_name = name_tokens[i + 1]
            to_add_module = sys.modules[f"{to_update_name}.{to_add_name}"]
            if not hasattr(to_update_module, to_add_name):
                setattr(to_update_module, to_add_name, to_add_module)

    exec(
        compile(ast.fix_missing_locations(target_module), "<ast>", "exec"),
        globals(),
    )


def expand_file_patterns(patterns: List[str]) -> List[str]:
    """
    Expand glob patterns to individual file paths.
    """
    files = []
    for pattern in patterns:
        if any(c in pattern for c in "*?[]"):
            # This looks like a glob pattern
            matched = glob.glob(pattern, recursive=True)
            if matched:
                files.extend(matched)
            else:
                print(f"Warning: No files matched pattern '{pattern}'")
        else:
            # Treat as a direct file path
            files.append(pattern)
    return files


def get_type_system(discipline: str):
    """
    Get the appropriate type system based on the specified discipline.

    Raises:
        ValueError: If an unsupported discipline is specified
    """
    if discipline == DISCIPLINE_SIMPLE:
        return SimpleTypeSystem()
    elif discipline == DISCIPLINE_SECURITY:
        return SecurityTypeSystem()
    else:
        raise ValueError(f"Unsupported discipline: {discipline}")


def get_elaborator(discipline: str):
    """
    Get the appropriate AST elaborator based on the specified discipline.

    Raises:
        ValueError: If an unsupported discipline is specified
    """
    if discipline == DISCIPLINE_SIMPLE:
        return SimpleASTElaborator()
    elif discipline == DISCIPLINE_SECURITY:
        return SecurityASTElaborator()
    else:
        raise ValueError(f"Unsupported discipline: {discipline}")


def main() -> int:
    """
    Main entry point for the Tyger type checker.
    """
    cli_parser = setup_cli_parser()
    cli_args = cli_parser.parse_args()

    # Get the appropriate type system
    discipline = cli_args.discipline
    type_system = get_type_system(discipline)

    all_results = []
    matching_files = []  # Initialize to empty list for stdin mode
    if cli_args.stdin:
        # Get the file path provided with --stdin
        source_file_path = cli_args.stdin[0]
        file_dir = os.path.dirname(os.path.abspath(source_file_path))

        # Create a dedicated dependency collection phase with the directory of the source file
        dependency_phase = DependencyCollectionPhase(file_dir, file_path=source_file_path)
        phases = _setup_phases(
            discipline,
            type_system,
            cli_args.elaborate,
            source_file_path,
            dependency_phase,
        )

        result = process_from_stdin(
            discipline,
            phases,
            cli_args.elaborate,
            cli_args.json,
            file_dir,
            source_file_path,
        )
        if result is not None:
            all_results.append(result)
    else:
        # Process files
        matching_files = expand_file_patterns(cli_args.file_paths)

        if not matching_files:
            print("No files matched the provided patterns/paths")
            return 1

        # Determine the common directory for all files
        file_dir = _determine_common_directory(matching_files)

        # Create the dependency collection phase that will be shared
        dependency_phase = DependencyCollectionPhase(file_dir, file_path=file_dir)

        for file_path in matching_files:
            # For each file, create a fresh set of phases with the file-specific path
            abs_file_path = os.path.abspath(file_path)
            phases = _setup_phases(
                discipline,
                type_system,
                cli_args.elaborate,
                abs_file_path,
                dependency_phase,
            )

            result = process_single_file(
                file_path, discipline, phases, cli_args.elaborate, cli_args.json
            )
            if result is not None:
                all_results.append(result)

    # Handle JSON output
    if cli_args.json:
        _output_json_results(
            all_results,
            cli_args.stdin,
            matching_files,
            discipline,
            cli_args.elaborate,
        )
        return 1 if all_results else 0

    return 0 if not all_results else 1


def _determine_common_directory(files: List[str]) -> str:
    """
    Determine the common directory for a list of files.
    """
    if len(files) == 1:
        return os.path.dirname(files[0])

    # For multiple files, find the common directory prefix
    common_dir = os.path.commonpath(files)
    if os.path.isfile(common_dir):
        return os.path.dirname(common_dir)
    else:
        return common_dir


def _setup_phases(
    discipline: str, type_system, elaborate: bool, file_path: str, dependency_phase=None
) -> List:
    """
    Set up processing phases based on configuration.
    """
    # Create phases
    phases = []

    # Add dependency collection phase
    if dependency_phase is None:
        file_dir = (
            os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
        )
        phases.append(DependencyCollectionPhase(file_dir, file_path=file_path))
    else:
        phases.append(dependency_phase)

    # Add typing phase
    typing_phase = TypingPhase(type_system, file_path=file_path)
    phases.append(typing_phase)

    # Add elaboration phase if requested
    if elaborate:
        ast_elaborator = get_elaborator(discipline)
        phases.append(ElaborationPhase(ast_elaborator))

    return phases


def _output_json_results(
    results: List[Dict],
    is_stdin: bool,
    matching_files: List[str],
    discipline: str,
    elaborate: bool,
) -> None:
    """
    Output JSON-formatted results.
    """
    combined_output = {
        "results": results,
        "total_files": 1 if is_stdin else len(matching_files),
        "files_with_diagnostics": len(results),
        "discipline": discipline,
        "elaborate": elaborate,
        "input_source": "stdin" if is_stdin else "files",
    }
    print(json.dumps(combined_output, indent=4))


if __name__ == "__main__":
    main()
