"""
Unit tests for utility modules.
"""
import unittest
import tempfile
import os
from unittest.mock import patch, Mock
from bot_vision.utils.text_filters import clean_text, filter_text_by_keywords
from bot_vision.utils.config import BotVisionConfig, detect_tesseract_path
from bot_vision.exceptions import ConfigurationError


class TestTextFilters(unittest.TestCase):
    """Test text filtering utilities."""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning functionality."""
        # Test whitespace cleanup
        self.assertEqual(clean_text("  hello  world  "), "hello world")
        
        # Test newline handling
        self.assertEqual(clean_text("hello\nworld\r\ntest"), "hello world test")
        
        # Test tab handling
        self.assertEqual(clean_text("hello\tworld"), "hello world")
        
        # Test multiple spaces
        self.assertEqual(clean_text("hello    world"), "hello world")
    
    def test_clean_text_special_chars(self):
        """Test cleaning of special characters."""
        # Test with special characters
        text = "hello@#$%world!@#"
        result = clean_text(text, remove_special_chars=True)
        self.assertEqual(result, "helloworld")
        
        # Test preserving alphanumeric and spaces
        text = "hello123 world456"
        result = clean_text(text, remove_special_chars=True)
        self.assertEqual(result, "hello123 world456")
    
    def test_clean_text_case_handling(self):
        """Test case conversion."""
        text = "Hello World"
        
        # Test lowercase
        result = clean_text(text, to_lower=True)
        self.assertEqual(result, "hello world")
        
        # Test uppercase
        result = clean_text(text, to_upper=True)
        self.assertEqual(result, "HELLO WORLD")
    
    def test_filter_text_by_keywords(self):
        """Test keyword filtering."""
        text_lines = ["Login", "Username", "Password", "Submit", "Cancel"]
        
        # Test single keyword
        keywords = ["login"]
        result = filter_text_by_keywords(text_lines, keywords)
        self.assertEqual(result, ["Login"])
        
        # Test multiple keywords
        keywords = ["username", "password"]
        result = filter_text_by_keywords(text_lines, keywords)
        self.assertEqual(result, ["Username", "Password"])
        
        # Test case insensitive
        keywords = ["LOGIN", "SUBMIT"]
        result = filter_text_by_keywords(text_lines, keywords, case_sensitive=False)
        self.assertEqual(result, ["Login", "Submit"])
        
        # Test case sensitive
        keywords = ["LOGIN"]
        result = filter_text_by_keywords(text_lines, keywords, case_sensitive=True)
        self.assertEqual(result, [])


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = BotVisionConfig()
        
        # Test default values
        self.assertEqual(config.confidence_threshold, 0.8)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_delay, 1.0)
        self.assertTrue(config.debug_mode)
        self.assertIsNone(config.tesseract_path)
    
    def test_config_from_dict(self):
        """Test configuration from dictionary."""
        config_dict = {
            'confidence_threshold': 0.9,
            'max_retries': 5,
            'retry_delay': 2.0,
            'debug_mode': False,
            'tesseract_path': '/usr/bin/tesseract'
        }
        
        config = BotVisionConfig.from_dict(config_dict)
        
        self.assertEqual(config.confidence_threshold, 0.9)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.retry_delay, 2.0)
        self.assertFalse(config.debug_mode)
        self.assertEqual(config.tesseract_path, '/usr/bin/tesseract')
    
    def test_config_from_file(self):
        """Test configuration from JSON file."""
        config_data = {
            'confidence_threshold': 0.7,
            'max_retries': 2,
            'debug_mode': True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            config = BotVisionConfig.from_file(temp_file)
            self.assertEqual(config.confidence_threshold, 0.7)
            self.assertEqual(config.max_retries, 2)
            self.assertTrue(config.debug_mode)
        finally:
            os.unlink(temp_file)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid confidence threshold
        with self.assertRaises(ConfigurationError):
            BotVisionConfig(confidence_threshold=1.5)
        
        with self.assertRaises(ConfigurationError):
            BotVisionConfig(confidence_threshold=-0.1)
        
        # Test invalid max_retries
        with self.assertRaises(ConfigurationError):
            BotVisionConfig(max_retries=-1)
        
        # Test invalid retry_delay
        with self.assertRaises(ConfigurationError):
            BotVisionConfig(retry_delay=-1.0)
    
    @patch('shutil.which')
    def test_detect_tesseract_path(self, mock_which):
        """Test Tesseract path detection."""
        # Test successful detection
        mock_which.return_value = '/usr/bin/tesseract'
        path = detect_tesseract_path()
        self.assertEqual(path, '/usr/bin/tesseract')
        
        # Test failed detection
        mock_which.return_value = None
        path = detect_tesseract_path()
        self.assertIsNone(path)


if __name__ == '__main__':
    unittest.main()
