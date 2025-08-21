"""
Integration tests for the BotVision package.
"""
import unittest
from unittest.mock import patch, Mock, MagicMock
import numpy as np
from PIL import Image

from bot_visions0 import BotVision, execute_tasks, find_text, click_text
from bot_vision.utils.config import BotVisionConfig
from bot_vision.exceptions import TaskExecutionError, ElementNotFoundError


class TestBotVisionIntegration(unittest.TestCase):
    """Integration tests for the main BotVision class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = BotVisionConfig(debug_mode=True)
        self.bot = BotVision(config=self.config)
        
        # Sample tasks
        self.sample_tasks = [
            {
                "task_name": "find_login",
                "description": "Find login button",
                "steps": [
                    {
                        "action": "find_text",
                        "text": "Login",
                        "region": [0, 0, 200, 100]
                    }
                ]
            },
            {
                "task_name": "click_submit",
                "description": "Click submit button",
                "steps": [
                    {
                        "action": "click_text",
                        "text": "Submit",
                        "region": [100, 50, 300, 150]
                    }
                ]
            }
        ]
    
    @patch('pyautogui.screenshot')
    @patch('pytesseract.image_to_string')
    def test_execute_single_task(self, mock_tesseract, mock_screenshot):
        """Test executing a single task."""
        # Mock screenshot
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        
        # Mock OCR result
        mock_tesseract.return_value = "Login Button Submit"
        
        # Execute single task
        results = self.bot.execute_tasks([self.sample_tasks[0]])
        
        # Should return results
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        
        # Check result structure
        result = results[0]
        self.assertIn('task_name', result)
        self.assertIn('success', result)
        self.assertEqual(result['task_name'], 'find_login')
    
    @patch('pyautogui.screenshot')
    @patch('pyautogui.click')
    @patch('pytesseract.image_to_string')
    def test_execute_multiple_tasks(self, mock_tesseract, mock_click, mock_screenshot):
        """Test executing multiple tasks."""
        # Mock screenshot
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        
        # Mock OCR result
        mock_tesseract.return_value = "Login Button Submit Button"
        
        # Execute multiple tasks
        results = self.bot.execute_tasks(self.sample_tasks)
        
        # Should return results for all tasks
        self.assertEqual(len(results), 2)
        
        # Check that click was called for the click_text action
        mock_click.assert_called()
    
    @patch('pyautogui.screenshot')
    @patch('pytesseract.image_to_string')
    def test_task_execution_failure(self, mock_tesseract, mock_screenshot):
        """Test task execution when text is not found."""
        # Mock screenshot
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        
        # Mock OCR result that doesn't contain target text
        mock_tesseract.return_value = "Some other text"
        
        # Task looking for non-existent text
        failing_task = {
            "task_name": "find_missing",
            "description": "Find missing text",
            "steps": [
                {
                    "action": "find_text",
                    "text": "NotFound",
                    "region": [0, 0, 200, 100]
                }
            ]
        }
        
        results = self.bot.execute_tasks([failing_task])
        
        # Should return failure result
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_invalid_task_structure(self):
        """Test handling of invalid task structure."""
        invalid_task = {
            "task_name": "invalid",
            # Missing required fields
        }
        
        with self.assertRaises(TaskExecutionError):
            self.bot.execute_tasks([invalid_task])
    

    @patch('pyautogui.screenshot')
    @patch('pyautogui.click')
    @patch('pytesseract.image_to_string')
    @patch('bot_vision.core.overlay.VisualOverlay.show_overlay')
    def test_click_text_with_overlay_parameter(self, mock_show_overlay, mock_tesseract, mock_click, mock_screenshot):
        """Test click_text with show_overlay parameter."""
        # Mock screenshot and OCR
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        mock_tesseract.return_value = "Click Me Button"
        
        bot = BotVision()
        
        # Test with show_overlay=True (default behavior)
        success = bot.click_text("Click Me", show_overlay=True)
        self.assertTrue(success)
        mock_click.assert_called()
        mock_show_overlay.assert_called()  # Overlay should be shown
        
        # Reset mocks
        mock_show_overlay.reset_mock()
        mock_click.reset_mock()
        
        # Test with show_overlay=False
        success = bot.click_text("Click Me", show_overlay=False)
        self.assertTrue(success)
        mock_click.assert_called()
        mock_show_overlay.assert_not_called()  # Overlay should NOT be shown
    
    @patch('pyautogui.screenshot')
    @patch('pyautogui.click')
    @patch('cv2.matchTemplate')
    @patch('bot_vision.core.overlay.VisualOverlay.show_overlay')
    def test_click_image_with_overlay_parameter(self, mock_show_overlay, mock_match_template, mock_click, mock_screenshot):
        """Test click_image with show_overlay parameter."""
        # Mock screenshot
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        
        # Mock template matching to return a good match
        mock_result = np.array([[0.95]])  # High confidence match
        mock_match_template.return_value = mock_result
        
        bot = BotVision()
        
        # Test with show_overlay=True (default)
        with patch('cv2.imread'), patch('os.path.exists', return_value=True):
            success = bot.click_image("test.png", show_overlay=True)
            self.assertTrue(success)
            mock_click.assert_called()
            mock_show_overlay.assert_called()  # Overlay should be shown
        
        # Reset mocks
        mock_show_overlay.reset_mock()
        mock_click.reset_mock()
        
        # Test with show_overlay=False
        with patch('cv2.imread'), patch('os.path.exists', return_value=True):
            success = bot.click_image("test.png", show_overlay=False)
            self.assertTrue(success)
            mock_click.assert_called()
            mock_show_overlay.assert_not_called()  # Overlay should NOT be shown
    
    @patch('pyautogui.click')
    @patch('bot_vision.core.overlay.VisualOverlay.show_overlay')
    def test_click_at_with_overlay_parameter(self, mock_show_overlay, mock_click):
        """Test click_at with show_overlay parameter."""
        bot = BotVision()
        
        # Test with show_overlay=True (default)
        success = bot.click_at(100, 200, show_overlay=True)
        self.assertTrue(success)
        mock_click.assert_called_with(100, 200)
        mock_show_overlay.assert_called()  # Overlay should be shown
        
        # Reset mocks
        mock_show_overlay.reset_mock()
        mock_click.reset_mock()
        
        # Test with show_overlay=False
        success = bot.click_at(100, 200, show_overlay=False)
        self.assertTrue(success)
        mock_click.assert_called_with(100, 200)
        mock_show_overlay.assert_not_called()  # Overlay should NOT be shown
    
    @patch('pyautogui.screenshot')
    @patch('pyautogui.click')
    @patch('pytesseract.image_to_string')
    @patch('bot_vision.core.overlay.VisualOverlay.show_overlay')
    def test_standalone_click_functions_with_overlay(self, mock_show_overlay, mock_tesseract, mock_click, mock_screenshot):
        """Test standalone click functions with show_overlay parameter."""
        # Mock screenshot and OCR
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        mock_tesseract.return_value = "Click Me Button"
        
        # Test standalone click_text with show_overlay=False
        success = click_text("Click Me", show_overlay=False)
        self.assertTrue(success)
        mock_click.assert_called()
        mock_show_overlay.assert_not_called()  # Overlay should NOT be shown

    @patch('pyautogui.screenshot')
    @patch('pytesseract.image_to_string')
    def test_execute_tasks_function(self, mock_tesseract, mock_screenshot):
        """Test the execute_tasks convenience function."""
        # Mock screenshot and OCR
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        mock_tesseract.return_value = "Test Text"
        
        tasks = [{
            "task_name": "test",
            "description": "Test task",
            "steps": [{"action": "find_text", "text": "Test"}]
        }]
        
        results = execute_tasks(tasks)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
    
    @patch('pyautogui.screenshot')
    @patch('pytesseract.image_to_string')
    def test_find_text_function(self, mock_tesseract, mock_screenshot):
        """Test the find_text convenience function."""
        # Mock screenshot and OCR
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        mock_tesseract.return_value = "Hello World Test"
        
        # Should find existing text
        found = find_text("World")
        self.assertTrue(found)
        
        # Should not find non-existing text
        found = find_text("NotThere")
        self.assertFalse(found)
    
    @patch('pyautogui.screenshot')
    @patch('pyautogui.click')
    @patch('pytesseract.image_to_string')
    def test_click_text_function(self, mock_tesseract, mock_click, mock_screenshot):
        """Test the click_text convenience function."""
        # Mock screenshot and OCR
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        mock_tesseract.return_value = "Click Me Button"
        
        # Should successfully click existing text
        success = click_text("Click Me")
        self.assertTrue(success)
        mock_click.assert_called()
        
        # Should fail to click non-existing text
        mock_tesseract.return_value = "Other text"
        success = click_text("NotThere")
        self.assertFalse(success)
    
    @patch('pyautogui.screenshot')
    @patch('pytesseract.image_to_string')
    def test_find_text_with_region(self, mock_tesseract, mock_screenshot):
        """Test find_text with region parameter."""
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        mock_tesseract.return_value = "Target Text"
        
        region = [0, 0, 200, 100]
        found = find_text("Target", region=region)
        self.assertTrue(found)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in various scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bot = BotVision()
    
    def test_configuration_error_handling(self):
        """Test handling of configuration errors."""
        # Invalid configuration should raise error
        with self.assertRaises(Exception):
            BotVision(config={'invalid': 'config'})
    
    @patch('pyautogui.screenshot')
    def test_screenshot_error_handling(self, mock_screenshot):
        """Test handling of screenshot errors."""
        # Mock screenshot failure
        mock_screenshot.side_effect = Exception("Screenshot failed")
        
        with self.assertRaises(TaskExecutionError):
            find_text("test")
    
    @patch('pyautogui.screenshot')
    @patch('pytesseract.image_to_string')
    def test_ocr_error_handling(self, mock_tesseract, mock_screenshot):
        """Test handling of OCR errors."""
        mock_img = Image.new('RGB', (400, 200), color='white')
        mock_screenshot.return_value = mock_img
        
        # Mock OCR failure
        mock_tesseract.side_effect = Exception("OCR failed")
        
        # Should handle OCR errors gracefully
        found = find_text("test")
        self.assertFalse(found)


if __name__ == '__main__':
    unittest.main()
