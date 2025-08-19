#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic data types test - verify variable display for different basic data types
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


class TestBasicTypes:
    """Basic data types test class"""
    
    def test_integer(self):
        """Test integer output"""
        def trigger_exception():
            a = 42
            b = 0
            result = a / b
        
        output = capture_exception_output(trigger_exception)
        
        assert "a=42" in output
        assert "b=0" in output

    def test_float(self):
        """Test float output"""
        def trigger_exception():
            a = 42.0
            b = 0.0
            result = a / b

        output = capture_exception_output(trigger_exception)

        assert "a=42.0" in output
        assert "b=0.0" in output
    
    def test_boolean(self):
        """Test boolean output"""
        def trigger_exception():
            a = True
            result = a << -1

        output = capture_exception_output(trigger_exception)

        assert "a=True" in output

    def test_none(self):
        """Test None value output"""
        def trigger_exception():
            a = None
            result = a + 1

        output = capture_exception_output(trigger_exception)

        assert "a=None" in output
