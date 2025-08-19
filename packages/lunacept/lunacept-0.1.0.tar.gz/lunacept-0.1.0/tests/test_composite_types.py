#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composite types test - verify variable display for composite data types
"""
import sys
import io
from contextlib import redirect_stdout
import lunacept


def capture_exception_output(exception_func):
    """Capture exception handling output"""
    original_excepthook = sys.excepthook
    captured_output = []
    
    def capturing_excepthook(exc_type, exc_value, exc_traceback):
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            lunacept.core._excepthook(exc_type, exc_value, exc_traceback)
        captured_output.append(output_buffer.getvalue())
    
    sys.excepthook = capturing_excepthook
    
    try:
        exception_func()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        capturing_excepthook(exc_type, exc_value, exc_traceback)
    finally:
        sys.excepthook = original_excepthook
    
    return captured_output[0] if captured_output else ""


class TestCompositeTypes:
    """Composite types test class"""
    
    def test_list(self):
        """Test list output"""
        def trigger_exception():
            items = [1, 2, 3, 4, 5]
            index = len(items)
            result = items[index]
        
        output = capture_exception_output(trigger_exception)
        
        expected_items = [1, 2, 3, 4, 5]
        assert f"items={expected_items}" in output

    def test_dict(self):
        """Test dict output"""
        def trigger_exception():
            data = {"name": "Alice", "age": 30}
            key = "invalid_key"
            result = data[key]
        
        output = capture_exception_output(trigger_exception)
        
        expected_data = {"name": "Alice", "age": 30}
        assert f"data={expected_data}" in output

    def test_set(self):
        """Test set output"""
        def trigger_exception():
            numbers = {1, 2, 3, 4, 5}
            item = 6
            numbers.remove(item)
        
        output = capture_exception_output(trigger_exception)
        
        # Set order is not guaranteed, so check elements existence
        assert "numbers=" in output

    def test_tuple(self):
        """Test tuple output"""
        def trigger_exception():
            coordinates = (10, 20, 30)
            index = len(coordinates)
            result = coordinates[index]
        
        output = capture_exception_output(trigger_exception)
        
        expected_coordinates = (10, 20, 30)
        assert f"coordinates={expected_coordinates}" in output
    
    def test_large_list(self):
        """Test large list output"""
        def trigger_exception():
            big_list = list(range(1000))  # 1000 elements
            index = len(big_list)
            result = big_list[index]
        
        output = capture_exception_output(trigger_exception)
        
        # Check if large list is properly handled
        assert "big_list=" in output
        assert f"index={1000}" in output
    
    def test_large_dict(self):
        """Test large dict output"""
        def trigger_exception():
            big_dict = {f"key_{i}": f"value_{i}" for i in range(500)}  # 500 pairs
            key = "nonexistent_key"
            result = big_dict[key]
        
        output = capture_exception_output(trigger_exception)
        
        # Check if large dict is properly handled
        assert "big_dict=" in output
        assert "key='nonexistent_key'" in output
    
    def test_large_tuple(self):
        """Test large tuple output"""
        def trigger_exception():
            big_tuple = tuple(range(1000))  # 1000 elements
            index = len(big_tuple)
            result = big_tuple[index]
        
        output = capture_exception_output(trigger_exception)
        
        # Check if large tuple is properly handled
        assert "big_tuple=" in output
        assert f"index={1000}" in output
