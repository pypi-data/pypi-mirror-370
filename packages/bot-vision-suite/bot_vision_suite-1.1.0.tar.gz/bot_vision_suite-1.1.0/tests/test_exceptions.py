"""
Unit tests for BotVision exceptions.
"""
import unittest
from bot_vision.exceptions import (
    BotVisionError,
    OCRError,
    TaskExecutionError,
    ConfigurationError,
    ElementNotFoundError
)


class TestBotVisionExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_bot_vision_error_inheritance(self):
        """Test that all custom exceptions inherit from BotVisionError."""
        exceptions = [
            OCRError("test"),
            TaskExecutionError("test"),
            ConfigurationError("test"),
            ElementNotFoundError("test")
        ]
        
        for exc in exceptions:
            self.assertIsInstance(exc, BotVisionError)
            self.assertIsInstance(exc, Exception)
    
    def test_exception_messages(self):
        """Test that exception messages are properly stored."""
        message = "Test error message"
        
        exceptions = [
            BotVisionError(message),
            OCRError(message),
            TaskExecutionError(message),
            ConfigurationError(message),
            ElementNotFoundError(message)
        ]
        
        for exc in exceptions:
            self.assertEqual(str(exc), message)
    
    def test_exception_raising(self):
        """Test that exceptions can be raised and caught properly."""
        with self.assertRaises(BotVisionError):
            raise BotVisionError("Test error")
        
        with self.assertRaises(OCRError):
            raise OCRError("OCR failed")
        
        with self.assertRaises(TaskExecutionError):
            raise TaskExecutionError("Task failed")
        
        with self.assertRaises(ConfigurationError):
            raise ConfigurationError("Config invalid")
        
        with self.assertRaises(ElementNotFoundError):
            raise ElementNotFoundError("Element not found")


if __name__ == '__main__':
    unittest.main()
