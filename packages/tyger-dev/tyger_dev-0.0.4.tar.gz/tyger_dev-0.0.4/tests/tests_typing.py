import ast
import os.path
import unittest

from tyger.diagnostics.errors import (
    ArityMismatchError,
    ModuleNotFoundTygerError,
    NotFoundBinOpTypeError,
)
from tyger.diagnostics.warnings import RedefineVariableWarning, UnsupportedTypeWarning
from tyger.discipline.simple.types import SimpleTypeSystem
from tyger.driver import Driver
from tyger.diagnostics.errors import (
    AttributeNotFoundError,
    TypeMismatchError,
)
from tyger.parser import Parser
from tyger.phases.dependency_collection import DependencyCollectionPhase
from tyger.phases.type_check import TypingPhase


class TestTyping(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        sources = os.path.join(tests_dir, "sources", "static")
        cls.parser = Parser(sources)
        cls.driver = Driver(
            [
                DependencyCollectionPhase(sources, file_path=sources),
                TypingPhase(SimpleTypeSystem()),
            ]
        )

    def assertDoesNotFail(self, callback):
        try:
            callback()
        except Exception as e:
            self.fail(f"Callback failed with exception {e}")

    def typecheck(self, program: ast.Module):
        return self.driver.run_2(program)

    def read_source(self, loc: str) -> ast.Module:
        return self.parser.parse(loc)

    def assertSingleError(self, program: ast.Module, error_type: type):
        _, _, errors = self.typecheck(program)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], error_type)

    def assertMultipleDiagnostics(
        self, program: ast.Module, expected_count: int, error_types: list[type] = None
    ):
        """Assert that a program has exactly the expected number of errors of specified types.

        Args:
            program: AST module to typecheck
            expected_count: Expected number of errors
            error_types: Optional list of expected error types (can have duplicates)

        Returns:
            List of errors found for additional assertions
        """
        _, _, diagnostics = self.typecheck(program)
        for diagnostic in diagnostics:
            print(diagnostic)
        self.assertEqual(
            expected_count,
            len(diagnostics),
            f"Expected {expected_count} diagnostics, got {len(diagnostics)}",
        )  # If error_types is provided, verify error types match and all expected types are present
        if error_types:
            # Track which expected error types we found
            unique_diagnostic_types = set(error_types)
            found_diagnostic_types = set()

            # In a single pass through the errors, check both conditions
            for diagnostic in diagnostics:
                print(diagnostic)
                # Check that this error matches at least one expected type
                diagnostic_matched = False
                for error_type in unique_diagnostic_types:
                    if isinstance(diagnostic, error_type):
                        diagnostic_matched = True
                        found_diagnostic_types.add(error_type)

                self.assertTrue(
                    diagnostic_matched,
                    f"Diagnostic {diagnostic} is not an instance of any expected types {error_types}",
                )

            # Verify all expected error types were found
            missing_types = unique_diagnostic_types - found_diagnostic_types
            self.assertFalse(
                missing_types,
                f"Expected diagnostic type(s) not found: {', '.join(t.__name__ for t in missing_types)}",
            )

        return diagnostics

    def test_assignments_fail(self):
        program = self.read_source("assignments_fail.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_assignments_ok(self):
        program = self.read_source("assignments_ok.py")
        self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_ann_reassign_fail(self):
        program = self.read_source("ann_reassign_fail.py")
        self.assertMultipleDiagnostics(program, 1, [RedefineVariableWarning])

    def test_unann_reassign_fail(self):
        program = self.read_source("unann_reassign_fail.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_assign_error(self):
        program = self.read_source("assign_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_ann_assign_fail_same_type(self):
        program = self.read_source("ann_assign_fail_same_type.py")
        self.assertMultipleDiagnostics(program, 1, [RedefineVariableWarning])

    def test_function(self):
        program = self.read_source("function.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_ho_function(self):
        program = self.read_source("ho_function.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_function_body_error(self):
        program = self.read_source("function_body_error.py")
        self.assertMultipleDiagnostics(program, 1, [NotFoundBinOpTypeError])

    def test_function_body_ok(self):
        program = self.read_source("function_body_ok.py")
        self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_function_return_invalid(self):
        program = self.read_source("function_return_invalid.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_function_return_ok(self):
        program = self.read_source("function_return_ok.py")
        self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_function_return_dyncheck(self):
        program = self.read_source("function_return_dyncheck.py")
        self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_function_conditional(self):
        program = self.read_source("function_conditional.py")
        self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_dict_key_error(self):
        program = self.read_source("dict_key_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_dict_value_error(self):
        program = self.read_source("dict_value_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_complex_tuple_assign_error(self):
        program = self.read_source("complex_tuple_assign_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_list_addition_error(self):
        program = self.read_source("list_addition_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_import_from_error(self):
        program = self.read_source("import_from_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_import_from_error_module(self):
        program = self.read_source("import_from_error_module.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_import_whole_module_error(self):
        program = self.read_source("import_whole_module_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_import_wildcard_error(self):
        program = self.read_source("import_wildcard_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_import_alias_namespace_error(self):
        program = self.read_source("import_alias_namespace_error.py")
        self.assertMultipleDiagnostics(program, 1, [AttributeNotFoundError])

    def test_module_attribute_error(self):
        program = self.read_source("module_attribute_error.py")
        self.assertMultipleDiagnostics(program, 1, [AttributeNotFoundError])

    def test_implicit_import_error(self):
        program = self.read_source("implicit_import_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_ifexpr_tuple_error(self):
        program = self.read_source("ifexpr_tuple_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_function_dom_error(self):
        program = self.read_source("function_dom_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_dict_assign_fail(self):
        program = self.read_source("dict_assign_fail.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_dict_return_error(self):
        program = self.read_source("dict_return_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_dict_access_error(self):
        program = self.read_source("dict_access_error.py")
        self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_assignments_fail_two(self):
        program = self.read_source("assignments_fail_two.py")
        _ = self.assertMultipleDiagnostics(program, 2, [TypeMismatchError])

    def test_mixed_errors(self):
        program = self.read_source("mixed_errors.py")
        _ = self.assertMultipleDiagnostics(
            program, 3, [RedefineVariableWarning, TypeMismatchError]
        )

    def test_multiple_type_errors(self):
        program = self.read_source("multiple_type_errors.py")
        _ = self.assertMultipleDiagnostics(program, 3, [TypeMismatchError])

    def test_four_type_errors(self):
        program = self.read_source("four_type_errors.py")
        _ = self.assertMultipleDiagnostics(
            program,
            4,
            [
                TypeMismatchError,
            ],
        )

    def test_five_type_errors(self):
        program = self.read_source("five_type_errors.py")
        _ = self.assertMultipleDiagnostics(
            program,
            5,
            [
                TypeMismatchError,
            ],
        )

    def test_mixed_errors_four(self):
        program = self.read_source("mixed_errors_four.py")
        _ = self.assertMultipleDiagnostics(
            program, 4, [RedefineVariableWarning, TypeMismatchError]
        )

    def test_function_multiple_errors(self):
        program = self.read_source("function_multiple_errors.py")
        _ = self.assertMultipleDiagnostics(program, 3, [TypeMismatchError])

    def test_mixed_function_errors(self):
        program = self.read_source("mixed_function_errors.py")
        _ = self.assertMultipleDiagnostics(
            program, 4, [RedefineVariableWarning, TypeMismatchError]
        )

    def test_collection_type_errors(self):
        program = self.read_source("collection_type_errors.py")
        _ = self.assertMultipleDiagnostics(
            program, 3, [TypeMismatchError, TypeMismatchError, TypeMismatchError]
        )

    def test_nested_compound_errors(self):
        program = self.read_source("nested_compound_errors.py")
        _ = self.assertMultipleDiagnostics(
            program, 2, [TypeMismatchError, TypeMismatchError]
        )

    def test_complex_return_errors(self):
        program = self.read_source("complex_return_errors.py")
        _ = self.assertMultipleDiagnostics(program, 3, [TypeMismatchError])

    def test_many_mixed_errors(self):
        program = self.read_source("many_mixed_errors.py")
        _ = self.assertMultipleDiagnostics(
            program,
            6,
            [
                RedefineVariableWarning,
                TypeMismatchError,
            ],
        )

    def test_import_attribute_errors(self):
        program = self.read_source("import_attribute_errors.py")
        _ = self.assertMultipleDiagnostics(
            program, 3, [AttributeNotFoundError, TypeMismatchError]
        )

    def test_function_call_errors(self):
        program = self.read_source("function_call_errors.py")
        _ = self.assertMultipleDiagnostics(program, 2, [TypeMismatchError])

    def test_container_operation_errors(self):
        program = self.read_source("container_operation_errors.py")
        _ = self.assertMultipleDiagnostics(program, 3, [TypeMismatchError])

    def test_nested_function_errors(self):
        program = self.read_source("nested_function_errors.py")
        _ = self.assertMultipleDiagnostics(program, 3, [TypeMismatchError])

    def test_combined_error_patterns(self):
        program = self.read_source("combined_error_patterns.py")
        _ = self.assertMultipleDiagnostics(
            program,
            7,
            [
                RedefineVariableWarning,
                TypeMismatchError,
            ],
        )

    def test_function_dom_arity(self):
        program = self.read_source("function_dom_arity.py")
        _ = self.assertMultipleDiagnostics(program, 1, [ArityMismatchError])

    def test_import_non_existing(self):
        program = self.read_source("import_non_existing.py")
        _ = self.assertMultipleDiagnostics(program, 1, [ModuleNotFoundTygerError])

    def test_f_string(self):
        program = self.read_source("f_string.py")
        _ = self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_simple_f_string_with_int(self):
        program = self.read_source("simple_f_string_with_int.py")
        _ = self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_complex_f_string(self):
        program = self.read_source("complex_f_string.py")
        _ = self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_f_string_with_type_error(self):
        program = self.read_source("f_string_with_type_error.py")
        _ = self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_typing_annotations(self):
        program = self.read_source("typing_annotations.py")
        _ = self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_typing_annotations_complex(self):
        program = self.read_source("typing_annotations_complex.py")
        _ = self.assertMultipleDiagnostics(program, 2, [TypeMismatchError])

    def test_typing_annotations_ok(self):
        program = self.read_source("typing_annotations_ok.py")
        _ = self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_typing_tuple_test(self):
        program = self.read_source("typing_tuple_test.py")
        _ = self.assertMultipleDiagnostics(program, 1, [TypeMismatchError])

    def test_typing_advanced_ok(self):
        program = self.read_source("typing_advanced_ok.py")
        _ = self.assertDoesNotFail(lambda: self.typecheck(program))

    def test_union_warning_test(self):
        """Test that Union/Optional emit warnings while other type errors are caught"""
        program = self.read_source("union_warning_test.py")
        _ = self.assertMultipleDiagnostics(
            program, 3, [UnsupportedTypeWarning, TypeMismatchError]
        )

    def test_union_warnings_only(self):
        """Test that Union types emit warnings but don't crash"""
        program = self.read_source("union_warnings_only.py")
        _ = self.assertMultipleDiagnostics(program, 3, [UnsupportedTypeWarning])

    def test_optional_warnings_only(self):
        """Test that Optional types emit warnings but don't crash"""
        program = self.read_source("optional_warnings_only.py")
        _ = self.assertMultipleDiagnostics(program, 5, [UnsupportedTypeWarning])

    def test_union_optional_mixed(self):
        """Test mixed Union/Optional with type errors"""
        program = self.read_source("union_optional_mixed.py")
        _ = self.assertMultipleDiagnostics(
            program, 6, [UnsupportedTypeWarning, TypeMismatchError]
        )
