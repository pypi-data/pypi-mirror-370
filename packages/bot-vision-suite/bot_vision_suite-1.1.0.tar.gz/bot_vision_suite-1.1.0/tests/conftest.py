"""
Test configuration and fixtures for bot-vision-suite tests.
"""
import pytest
import os
import tempfile
import numpy as np
from PIL import Image
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    # Create a simple white image with black text
    img = Image.new('RGB', (200, 100), color='white')
    # Note: In real tests, you might want to draw actual text
    return np.array(img)


@pytest.fixture
def mock_tesseract():
    """Mock Tesseract for testing without requiring installation."""
    with patch('pytesseract.image_to_string') as mock:
        mock.return_value = "Sample text from image"
        yield mock


@pytest.fixture
def mock_pyautogui():
    """Mock pyautogui for testing without GUI interactions."""
    with patch('pyautogui.screenshot') as mock_screenshot, \
         patch('pyautogui.click') as mock_click, \
         patch('pyautogui.moveTo') as mock_move:
        
        # Create a mock screenshot
        mock_img = Image.new('RGB', (1920, 1080), color='white')
        mock_screenshot.return_value = mock_img
        
        yield {
            'screenshot': mock_screenshot,
            'click': mock_click,
            'moveTo': mock_move
        }


@pytest.fixture
def sample_task():
    """Sample task configuration for testing."""
    return {
        "task_name": "test_task",
        "description": "A test task",
        "steps": [
            {
                "action": "find_text",
                "text": "test_text",
                "region": [0, 0, 100, 100]
            }
        ]
    }


@pytest.fixture
def sample_tasks():
    """Multiple sample tasks for testing."""
    return [
        {
            "task_name": "task1",
            "description": "First test task",
            "steps": [
                {
                    "action": "find_text",
                    "text": "button1",
                    "region": [0, 0, 200, 200]
                }
            ]
        },
        {
            "task_name": "task2",
            "description": "Second test task",
            "steps": [
                {
                    "action": "click_text",
                    "text": "submit",
                    "region": [100, 100, 300, 300]
                }
            ]
        }
    ]
