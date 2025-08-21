import unittest
import ast
import io
import sys
import os
import types as builtin_types
from tyger.discipline.simple.ToAST import SimpleASTElaborator
from tyger.discipline.simple.types import SimpleTypeSystem
from tyger.discipline.simple.evidence import RuntimeException
from tyger.driver import Driver
from tyger.diagnostics.errors import TypeMismatchError
from tyger.parser import Parser
from contextlib import redirect_stdout

from tyger.phases.dependency_collection import DependencyCollectionPhase
from tyger.phases.elaboration import ElaborationPhase
from tyger.phases.type_check import TypingPhase


class TestResult:
    def __init__(self, scope, output, errors):
        self.scope = scope
        self.output = output
        self.errors = errors

    def __getitem__(self, item):
        return self.scope[item]


class TestRuntime(unittest.TestCase):

    def setUp(self):
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        sources = os.path.join(tests_dir, "sources", "runtime")
        self.driver = Driver(
            [
                DependencyCollectionPhase(sources, file_path=sources),
                TypingPhase(SimpleTypeSystem()),
                ElaborationPhase(SimpleASTElaborator()),
            ]
        )
        self.parser = Parser(sources)

    def execute(self, program: ast.Module):
        scope = globals()

        with redirect_stdout(io.StringIO()) as f:
            target_module, deps_asts, errors = self.driver.run_2(program)
            deps = {
                name: compile(ast.fix_missing_locations(code_ast), "<tyger>", "exec")
                for name, code_ast in deps_asts.items()
            }
            # We initialize the dependencies
            # We first add them to sys.modules
            for dep in deps:
                sys.modules[dep] = builtin_types.ModuleType(dep)

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
                scope,
            )

        return TestResult(scope, f.getvalue(), errors)

    def read_source(self, loc: str) -> ast.Module:
        return self.parser.parse(loc)

    ## TESTS
    def test_assignments_transitivity_fail(self):
        program = self.read_source("assignment_transitivity_fail.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_assignments_transitivity_ok(self):
        program = self.read_source("assignments_transitivity_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["y"].value, 1)

    def test_function(self):
        program = self.read_source("function.py")
        self.execute(program)

    def test_hofunction_ok(self):
        program = self.read_source("hofunction_ok.py")
        self.assertEqual(True, self.execute(program)["x"])

    def test_hofunction_invalid_return(self):
        program = self.read_source("hofunction_invalid_return.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_addition_ok(self):
        program = self.read_source("addition_ok.py")
        scope = self.execute(program)
        self.assertEqual(10, scope["x"])
        self.assertEqual(20, scope["y"])

    def test_function_returns_pass(self):
        program = self.read_source("function_returns_pass.py")
        self.assertEqual(None, self.execute(program)["x"])

    def test_function_return_dyncheck(self):
        program = self.read_source("function_return_dyncheck.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_function_return_ok(self):
        program = self.read_source("function_return_ok.py")
        self.assertEqual(2, self.execute(program)["y"])

    def test_function_conditional(self):
        program = self.read_source("function_conditional.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_boolean_not_dyn1(self):
        program = self.read_source("boolean_not_dyn1.py")
        self.assertEqual(False, self.execute(program)["y"])

    def test_boolean_not_dyn2(self):
        program = self.read_source("boolean_not_dyn2.py")
        self.assertEqual(False, self.execute(program)["y"])

    def test_boolean_not_dyn3(self):
        program = self.read_source("boolean_not_dyn3.py")
        self.assertEqual(True, self.execute(program)["y"])

    def test_function_conditional_false(self):
        program = self.read_source("function_conditional_false.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_multiple_assign(self):
        program = self.read_source("multiple_assign.py")
        self.assertEqual(1, self.execute(program)["x"])

    def test_multiple_assign_function(self):
        program = self.read_source("multiple_assign_function.py")
        self.assertEqual(1, self.execute(program)["x"])

    def test_lambda_untyped(self):
        program = self.read_source("lambda_untyped.py")
        self.assertEqual(3, self.execute(program)["x"])

    def test_lambda_typed_ok(self):
        program = self.read_source("lambda_typed_ok.py")
        self.assertEqual(3, self.execute(program)["x"])

    def test_lambda_typed_error(self):
        program = self.read_source("lambda_typed_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program)["x"])

    def test_lambda_ann_assign(self):
        program = self.read_source("lambda_ann_assign.py")
        self.assertRaises(TypeException, lambda: self.execute(program)["x"])

    def test_lambda_modular_not_forgetful(self):
        program = self.read_source("lambda_modular_not_forgetful.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_while_simple(self):
        program = self.read_source("while_simple.py")
        self.assertEqual(11, self.execute(program)["x"])

    def test_while(self):
        program = self.read_source("while.py")
        self.assertEqual(11, self.execute(program)["x"])

    def test_transitivity_tuples_ok(self):
        program = self.read_source("transitivity_tuples_ok.py")
        self.assertEqual((1, 2), self.execute(program)["t2"])

    def test_transitivity_tuples_error(self):
        program = self.read_source("transitivity_tuples_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_list_ascription(self):
        program = self.read_source("list_ascription.py")
        self.assertEqual([1, 2, 3], self.execute(program)["l"])

    def test_transitivity_list_ok(self):
        program = self.read_source("transitivity_list_ok.py")
        self.assertEqual([1, 2], self.execute(program)["t2"])

    def test_transitivity_list_error(self):
        program = self.read_source("transitivity_list_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_list_access_ok(self):
        program = self.read_source("list_access_ok.py")
        self.assertEqual(4, self.execute(program)["y"])

    def test_list_ascribed_unk(self):
        program = self.read_source("list_ascribed_unk.py")
        self.assertEqual(1, self.execute(program)["x"])

    def test_list_access_slice(self):
        program = self.read_source("list_access_slice.py")
        self.assertEqual([2, True], self.execute(program)["y"])

    def test_list_access_error(self):
        program = self.read_source("list_access_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_list_comp_ok(self):
        program = self.read_source("list_comp_ok.py")
        self.assertEqual([(1, 0)], self.execute(program)["l"])

    def test_list_comp_error(self):
        program = self.read_source("list_comp_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_list_bool_ops(self):
        program = self.read_source("list_bool_ops.py")
        scope = self.execute(program)
        self.assertEqual([1, 2], scope["x"])
        self.assertEqual([1, 2], scope["y"])
        self.assertEqual(False, scope["z"])

    def test_list_if_comprehension(self):
        program = self.read_source("list_if_comprehension.py")
        self.assertEqual([6], self.execute(program)["x"])

    def test_for(self):
        program = self.read_source("for.py")
        self.assertEqual(10, self.execute(program)["x"])

    def test_nested_for(self):
        program = self.read_source("nested_for.py")
        self.assertEqual(54, self.execute(program)["z"])

    def test_plus_one(self):
        program = self.read_source("plus_one.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_weird_scope(self):
        program = self.read_source("weird_scope.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_unknown_application(self):
        program = self.read_source("unknown_application.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_unknown_application_many_args(self):
        program = self.read_source("unknown_application_many_args.py")
        self.assertEqual(4, self.execute(program)["x"])

    def test_unknown_application_many_args_transitive(self):
        program = self.read_source("unknown_application_many_args_transitive.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_function_flexible_number_arguments_transitive(self):
        program = self.read_source("function_flexible_number_arguments_transitive.py")
        self.assertEqual(4, self.execute(program)["x"])

    def test_lambda_flexible_number_arguments(self):
        program = self.read_source("lambda_flexible_number_arguments.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_tuple_assign_with_previous_typing_information_static_error(self):
        program = self.read_source(
            "tuple_assign_with_previous_typing_information_static_error.py"
        )
        self.assertRaises(TypeException, lambda: self.execute(program))

    def test_tuple_assign_with_previous_typing_information_runtime_error(self):
        program = self.read_source(
            "tuple_assign_with_previous_typing_information_runtime_error.py"
        )
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_def_local_vars_overriding_global(self):
        program = self.read_source("def_local_vars_overriding_global.py")
        self.assertRaises(TypeException, lambda: self.execute(program))

    def test_assign_greedy(self):
        program = self.read_source("assign_greedy.py")
        self.assertRaises(TypeException, lambda: self.execute(program))

    def test_application_lambda(self):
        program = self.read_source("application_lambda.py")
        self.assertEqual(2, self.execute(program)["x"])

    def test_print_func(self):
        program = self.read_source("print_func.py")
        self.execute(program)
        self.assertEqual(1, 1)

    def test_if_expr_ok(self):
        program = self.read_source("if_expr_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["z"], 4)

    def test_if_expr_ok2(self):
        program = self.read_source("if_expr_ok2.py")
        scope = self.execute(program)
        self.assertEqual(scope["res"], "holahola")
        self.assertEqual(scope["x"], "hola")

    def test_if_expr_error(self):
        program = self.read_source("if_expr_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_if_expr_rt_error1(self):
        program = self.read_source("if_expr_rt_error1.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_dict_ok(self):
        program = self.read_source("dict_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["a"]["a"], 1)
        self.assertEqual(scope["a"]["d"], 4)

    def test_dict_access_ok(self):
        program = self.read_source("dict_access_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["x"], 2)

    def test_mult_assign_to_list(self):
        program = self.read_source("mult_assign_to_list.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_complex_tuple_assign_ok(self):
        program = self.read_source("complex_tuple_assign_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["x"], 1)
        self.assertEqual(scope["z"], 3)
        self.assertEqual(scope["y"], "hola")
        self.assertEqual(scope["a"], True)

    def test_complex_tuple_assign_error(self):
        program = self.read_source("complex_tuple_assign_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_assign_tuple_from_call_ok(self):
        program = self.read_source("assign_tuple_from_call_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["x"], 4)
        self.assertEqual(scope["y"], 5)

    def test_assign_tuple_from_call_error(self):
        program = self.read_source("assign_tuple_from_call_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_dict_index_error(self):
        program = self.read_source("dict_index_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_complex_list_assign_error(self):
        program = self.read_source("complex_list_assign_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_dict_assign_tuple_ok(self):
        program = self.read_source("dict_assign_tuple_ok.py")
        scope = self.execute(program)
        print(scope["d"])
        self.assertEqual(scope["x"], 1)
        expected_d = {1: "a", 2: "b", 3: "hola", 4: "chao"}
        self.assertEqual(scope["d"], expected_d)

    def test_assign_with_effect(self):
        program = self.read_source("assign_call_with_effect.py")
        scope = self.execute(program)
        self.assertEqual(scope.output, "1\n")
        self.assertEqual(scope["x"], 1)
        self.assertEqual(scope["y"], 1)

    def test_print(self):
        program = self.read_source("print.py")
        scope = self.execute(program)
        self.assertEqual(scope.output, "1 2 3\n")

    def test_import_from_ok(self):
        program = self.read_source("import_from_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["x"], 3)
        self.assertEqual(scope["y"], 4)

    def test_import_from_error(self):
        program = self.read_source("import_from_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_import_from_error2(self):
        program = self.read_source("import_from_error2.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_import_from_whole_module_ok(self):
        program = self.read_source("import_from_whole_module_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["x"], 4)

    def test_import_from_whole_module_error(self):
        program = self.read_source("import_from_whole_module_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_import_from_implicit_relative_ok(self):
        program = self.read_source("import_from_implicit_relative_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["z"], 4)

    def test_import_from_dependencies_ok(self):
        program = self.read_source("import_from_dependencies_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["z"], 4)

    def test_import_from_wildcard_ok(self):
        program = self.read_source("import_from_wildcard_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["x"], 1)
        self.assertEqual(scope["z"], 2)

    def test_import_from_wildcard_error(self):
        program = self.read_source("wildcard_import_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_import_ok(self):
        program = self.read_source("import_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["y"], 4)
        self.assertEqual(scope["z"], 5)

    def test_import_ok2(self):
        program = self.read_source("import_ok2.py")
        scope = self.execute(program)
        self.assertEqual(scope["z"], 8)
        self.assertEqual(scope["a"], 4)

    def test_import_error(self):
        program = self.read_source("import_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_import_error2(self):
        program = self.read_source("import_error2.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_module_namespace_ok(self):
        program = self.read_source("module_namespace_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["a"], 1)
        self.assertEqual(scope["b"], 2)

    def test_namespace_error(self):
        program = self.read_source("namespace_error.py")
        self.assertRaises(AttributeError, lambda: self.execute(program))

    def test_import_order(self):
        program = self.read_source("import_order.py")
        result = self.execute(program)
        self.assertEqual(result.output, "ABC")

    def test_ann_import_ok(self):
        program = self.read_source("ann_import_ok.py")
        result = self.execute(program)
        self.assertEqual(result["y"], 1)

    def test_dict_cast_error(self):
        program = self.read_source("dict_cast_error.py")
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_dict_cast_ok(self):
        program = self.read_source("dict_cast_ok.py")
        scope = self.execute(program)
        self.assertEqual(scope["d"]["x"], 3)

    def test_list_comprehension_tuple_ok(self):
        program = self.read_source("list_comprehension_tuple_ok.py")
        result = self.execute(program)
        self.assertEqual(result["x"], 14)
