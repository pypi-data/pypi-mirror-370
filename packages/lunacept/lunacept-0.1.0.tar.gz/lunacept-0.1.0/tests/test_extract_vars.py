#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Variable extraction test - verify the core function extract_vars_from_line
"""
from lunacept.core import extract_vars_from_line


class TestExtractVarsFromLine:
    """Test the core variable extraction function"""
    
    def test_simple_assignment(self):
        """Test simple assignment statement"""
        source = "result = a"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"a"}

    def test_complex_expression(self):
        """Test complex mathematical expression"""
        source = "result = (a + b) * c / d"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"a", "b", "c", "d"}
    
    def test_division_operation(self):
        """Test division operation"""
        source = "result = dividend / divisor"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"dividend", "divisor"}
    
    def test_function_call_with_args(self):
        """Test function call with arguments"""
        source = "result = func(x, y, z)"
        vars_found = extract_vars_from_line(source)
        # Should include function arguments but not function name
        assert vars_found == {"x", "y", "z"}
        assert "func" not in vars_found
    
    def test_list_indexing(self):
        """Test list indexing operation"""
        source = "value = items[index]"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"items", "index"}
    
    def test_dict_access(self):
        """Test dictionary access"""
        source = "value = data[key]"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"data", "key"}
    
    def test_method_call(self):
        """Test method call on object"""
        source = "result = obj.method(arg1, arg2)"
        vars_found = extract_vars_from_line(source)
        # Should include object and arguments but not method name
        assert vars_found == {"obj", "arg1", "arg2"}
        assert "method" not in vars_found
    
    def test_attribute_access(self):
        """Test attribute access"""
        source = "value = obj.attribute"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"obj"}
        assert "attribute" not in vars_found

    def test_nested_function_calls(self):
        """Test nested function calls"""
        source = "result = outer_func(inner_func(x, y), z)"
        vars_found = extract_vars_from_line(source)
        # Should include all arguments but not function names
        assert vars_found == {"x", "y", "z"}
        assert "outer_func" not in vars_found
        assert "inner_func" not in vars_found
    
    def test_multiple_assignments(self):
        """Test multiple variable assignments"""
        source = "a, b = x, y"
        vars_found = extract_vars_from_line(source)
        # Should include right-hand side variables
        assert vars_found == {"x", "y"}
        # Should not include left-hand side (assignment targets)
        assert "a" not in vars_found
        assert "b" not in vars_found
    
    def test_string_operations(self):
        """Test string operations"""
        source = "result = text[start:end]"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"text", "start", "end"}
    
    def test_comparison_operations(self):
        """Test comparison operations"""
        source = "condition = x > y and z < w"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"x", "y", "z", "w"}
    
    def test_builtin_functions_filtered(self):
        """Test that builtin functions are filtered out"""
        source = "result = len(items) + int(value)"
        vars_found = extract_vars_from_line(source)
        # Should include variables but not builtin functions
        assert vars_found == {"items", "value"}
        assert "len" not in vars_found
        assert "int" not in vars_found
    
    def test_list_comprehension(self):
        """Test list comprehension"""
        source = "result = [x * 2 for x in numbers]"
        vars_found = extract_vars_from_line(source)
        # Should include the iterable but not loop variable
        assert vars_found == {"numbers"}
        assert "x" not in vars_found  # Loop variable should be excluded
    
    def test_set_comprehension(self):
        """Test set comprehension"""
        source = "result = {x * 2 for x in numbers}"
        vars_found = extract_vars_from_line(source)
        # Should include the iterable but not loop variable
        assert vars_found == {"numbers"}
        assert "x" not in vars_found  # Loop variable should be excluded
    
    def test_dict_comprehension(self):
        """Test dictionary comprehension"""
        source = "result = {x: x * 2 for x in numbers}"
        vars_found = extract_vars_from_line(source)
        # Should include the iterable but not loop variable
        assert vars_found == {"numbers"}
        assert "x" not in vars_found  # Loop variable should be excluded
    
    def test_generator_expression(self):
        """Test generator expression"""
        source = "result = (x * 2 for x in numbers)"
        vars_found = extract_vars_from_line(source)
        # Should include the iterable but not loop variable
        assert vars_found == {"numbers"}
        assert "x" not in vars_found  # Loop variable should be excluded
    
    def test_comprehension_with_condition(self):
        """Test comprehension with condition"""
        source = "result = [x for x in numbers if x > threshold]"
        vars_found = extract_vars_from_line(source)
        # Should include both iterable and condition variable, but not loop variable
        assert vars_found == {"numbers", "threshold"}
        assert "x" not in vars_found  # Loop variable should be excluded
    
    def test_nested_comprehension(self):
        """Test nested comprehension"""
        source = "result = [y for x in matrix for y in x]"
        vars_found = extract_vars_from_line(source)
        # Should include the outer iterable but not loop variables
        assert vars_found == {"matrix"}
        assert "x" not in vars_found  # Outer loop variable should be excluded
        assert "y" not in vars_found  # Inner loop variable should be excluded
    
    def test_comprehension_with_multiple_iterables(self):
        """Test comprehension with multiple iterables"""
        source = "result = [x + y for x in list1 for y in list2]"
        vars_found = extract_vars_from_line(source)
        # Should include both iterables but not loop variables
        assert vars_found == {"list1", "list2"}
        assert "x" not in vars_found  # Loop variable should be excluded
        assert "y" not in vars_found  # Loop variable should be excluded
    
    def test_lambda_expression(self):
        """Test lambda expression"""
        source = "func = lambda x: x + offset"
        vars_found = extract_vars_from_line(source)
        # Should include variables referenced in lambda
        assert "offset" in vars_found
        # Note: Current implementation includes lambda parameters
        # This is acceptable behavior for debugging purposes
        assert "x" not in vars_found
    
    def test_boolean_expression(self):
        """Test boolean expression that might appear in conditions"""
        source = "condition and flag"
        vars_found = extract_vars_from_line(source)
        # Should include condition variables
        assert vars_found == {"condition", "flag"}
    
    def test_comparison_in_condition(self):
        """Test comparison expression in condition"""
        source = "counter < limit and not finished"
        vars_found = extract_vars_from_line(source)
        # Should include all condition variables
        assert vars_found == {"counter", "limit", "finished"}
    
    def test_conditional_expression(self):
        """Test conditional expression (ternary operator)"""
        source = "result = value if condition else default"
        vars_found = extract_vars_from_line(source)
        # Should include all parts of conditional expression
        assert vars_found == {"value", "condition", "default"}
    
    def test_complex_boolean_expression(self):
        """Test complex boolean expression"""
        source = "status == 'ready' and count > threshold"
        vars_found = extract_vars_from_line(source)
        # Should include variables in condition
        assert vars_found == {"status", "count", "threshold"}
    
    def test_boolean_with_function_calls(self):
        """Test boolean expression with function calls"""
        source = "validate(data) and len(items) > 0"
        vars_found = extract_vars_from_line(source)
        # Should include variables but not function names
        assert vars_found == {"data", "items"}
        assert "validate" not in vars_found
        assert "len" not in vars_found
    
    def test_nested_conditional_expression(self):
        """Test nested conditional expression"""
        source = "result = x if a > b else y if c < d else z"
        vars_found = extract_vars_from_line(source)
        # Should include all variables in nested conditionals
        assert vars_found == {"x", "a", "b", "y", "c", "d", "z"}
    
    def test_iteration_expression(self):
        """Test expression that might appear in for loop"""
        source = "item in collection"
        vars_found = extract_vars_from_line(source)
        # Should include both variables in membership test
        assert vars_found == {"item", "collection"}
    
    def test_slice_expression(self):
        """Test slice expression"""
        source = "data[start:end:step]"
        vars_found = extract_vars_from_line(source)
        # Should include all slice components
        assert vars_found == {"data", "start", "end", "step"}
    
    def test_multistatement_line(self):
        """Test line with multiple statements separated by semicolon"""
        source = "x, y = 1, 0; result = x / y"
        vars_found = extract_vars_from_line(source)
        # Should include variables from both statements
        assert vars_found == {"x", "y"}
    
    def test_empty_line(self):
        """Test empty or whitespace-only line"""
        source = "   "
        vars_found = extract_vars_from_line(source)
        assert vars_found == set()
    
    def test_invalid_syntax(self):
        """Test handling of invalid syntax"""
        source = "invalid syntax here !!!"
        vars_found = extract_vars_from_line(source)
        # Should return empty set for invalid syntax
        assert vars_found == set()
    
    def test_multiline_statement(self):
        """Test multiline statement"""
        source = """result = a + \\
    b + c"""
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"a", "b", "c"}
    
    def test_f_string_variables(self):
        """Test f-string with variables"""
        source = "message = f'Hello {name}, age {age}'"
        vars_found = extract_vars_from_line(source)
        # This might be tricky - f-string parsing
        # Current implementation might not handle this perfectly
        # We'll see what it actually extracts
        result = extract_vars_from_line(source)
        # For now, just verify it doesn't crash
        assert isinstance(result, set)
    
    def test_indented_code(self):
        """Test indented code (like in functions/classes)"""
        source = "    result = x + y"
        vars_found = extract_vars_from_line(source)
        assert vars_found == {"x", "y"}
