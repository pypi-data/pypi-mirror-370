#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
String types test - verify variable display for string operations
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


class TestStringTypes:
    """String types test class"""
    
    def test_regular_string(self):
        """Test regular string output"""
        def trigger_exception():
            text = "hello world"
            index = len(text)
            result = text[index]
        
        output = capture_exception_output(trigger_exception)
        
        expected_message = "hello world"
        assert f"text='{expected_message}'" in output
        assert f"index={len(expected_message)}" in output
    
    def test_f_string(self):
        """Test f-string output"""
        def trigger_exception():
            name = "Alice"
            age = 25
            message = f"Hello {name}, you are {age} years old"
            index = len(message)
            result = message[index]
        
        output = capture_exception_output(trigger_exception)
        
        expected_message = "Hello Alice, you are 25 years old"
        assert f"message='{expected_message}'" in output
        assert f"index={len(expected_message)}" in output
    
    def test_multiline_string(self):
        """Test multiline string output"""
        def trigger_exception():
            text = """This is a
multiline string
with several lines"""
            index = len(text)
            result = text[index]
        
        output = capture_exception_output(trigger_exception)
        
        expected_text = "This is a\nmultiline string\nwith several lines"
        assert f"text='{expected_text.encode('unicode_escape').decode()}'" in output
        assert f"index={len(expected_text)}" in output
    
    def test_very_long_string(self):
        """Test very long string output"""
        def trigger_exception():
            long_text = "A" * 1000  # 1000 characters
            index = len(long_text)
            result = long_text[index]
        
        output = capture_exception_output(trigger_exception)
        
        # Check if long string is properly handled (truncated or shown)
        assert "long_text=" in output
        assert f"index={1000}" in output
