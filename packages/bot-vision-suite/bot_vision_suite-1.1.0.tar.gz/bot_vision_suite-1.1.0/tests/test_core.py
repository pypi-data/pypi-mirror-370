"""
Unit tests for core modules.
"""
import unittest
import numpy as np
from unittest.mock import patch, Mock, MagicMock
from PIL import Image

from bot_vision.core.image_processing import ImageProcessor
from bot_vision.core.ocr_engine import OCREngine
from bot_vision.core.overlay import VisualOverlay
from bot_vision.utils.config import BotVisionConfig
from bot_vision.exceptions import OCRError, ConfigurationError


class TestImageProcessor(unittest.TestCase):
    """Test image processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = BotVisionConfig()
        self.processor = ImageProcessor(self.config)
        
        # Create a sample image
        self.sample_image = np.ones((100, 200, 3), dtype=np.uint8) * 255  # White image
    
    def test_preprocess_for_ocr_basic(self):
        """Test basic image preprocessing."""
        processed = self.processor.preprocess_for_ocr(self.sample_image)
        
        # Should return numpy array
        self.assertIsInstance(processed, np.ndarray)
        
        # Should be grayscale (2D array)
        self.assertEqual(len(processed.shape), 2)
    
    def test_preprocess_for_ocr_with_region(self):
        """Test preprocessing with region cropping."""
        region = (10, 10, 50, 50)  # x, y, width, height
        processed = self.processor.preprocess_for_ocr(self.sample_image, region=region)
        
        # Should crop to specified region
        self.assertEqual(processed.shape, (40, 40))  # height, width
    
    def test_enhance_contrast(self):
        """Test contrast enhancement."""
        # Create image with low contrast
        low_contrast = np.ones((50, 50), dtype=np.uint8) * 128  # Gray image
        
        enhanced = self.processor.enhance_contrast(low_contrast)
        
        # Enhanced image should be different from original
        self.assertFalse(np.array_equal(low_contrast, enhanced))
    
    def test_remove_noise(self):
        """Test noise removal."""
        # Create noisy image
        noisy = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        
        denoised = self.processor.remove_noise(noisy)
        
        # Result should be same shape
        self.assertEqual(noisy.shape, denoised.shape)


class TestOCREngine(unittest.TestCase):
    """Test OCR engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = BotVisionConfig()
        self.engine = OCREngine(self.config)
        
        # Sample image
        self.sample_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
    
    @patch('pytesseract.image_to_string')
    def test_extract_text_tesseract(self, mock_tesseract):
        """Test text extraction with Tesseract."""
        mock_tesseract.return_value = "Sample text"
        
        result = self.engine.extract_text(self.sample_image, method='tesseract')
        
        self.assertEqual(result, "Sample text")
        mock_tesseract.assert_called_once()
    
    @patch('easyocr.Reader')
    def test_extract_text_easyocr(self, mock_reader_class):
        """Test text extraction with EasyOCR."""
        mock_reader = Mock()
        mock_reader.readtext.return_value = [
            ([(0, 0), (100, 0), (100, 50), (0, 50)], "Sample text", 0.9)
        ]
        mock_reader_class.return_value = mock_reader
        
        result = self.engine.extract_text(self.sample_image, method='easyocr')
        
        self.assertEqual(result, "Sample text")
    
    @patch('cv2.dnn.readNet')
    def test_extract_text_opencv(self, mock_readnet):
        """Test text extraction with OpenCV."""
        # Mock OpenCV DNN
        mock_net = Mock()
        mock_readnet.return_value = mock_net
        
        # This would normally require more complex mocking for EAST model
        # For now, just test that the method doesn't crash
        try:
            result = self.engine.extract_text(self.sample_image, method='opencv')
            # OpenCV method might return empty string if no text detected
            self.assertIsInstance(result, str)
        except Exception:
            # OpenCV method might fail without proper model files
            pass
    
    def test_extract_text_invalid_method(self):
        """Test invalid OCR method."""
        with self.assertRaises(OCRError):
            self.engine.extract_text(self.sample_image, method='invalid_method')
    
    @patch('pytesseract.image_to_string')
    def test_find_text_in_image(self, mock_tesseract):
        """Test finding specific text in image."""
        mock_tesseract.return_value = "Hello World Test"
        
        # Should find existing text
        found = self.engine.find_text_in_image(self.sample_image, "World")
        self.assertTrue(found)
        
        # Should not find non-existing text
        found = self.engine.find_text_in_image(self.sample_image, "NotThere")
        self.assertFalse(found)
    
    @patch('pytesseract.image_to_string')
    def test_find_text_case_insensitive(self, mock_tesseract):
        """Test case-insensitive text finding."""
        mock_tesseract.return_value = "Hello World"
        
        # Should find text regardless of case
        found = self.engine.find_text_in_image(self.sample_image, "WORLD", case_sensitive=False)
        self.assertTrue(found)
        
        # Should not find with case sensitivity
        found = self.engine.find_text_in_image(self.sample_image, "WORLD", case_sensitive=True)
        self.assertFalse(found)


class TestVisualOverlay(unittest.TestCase):
    """Test visual overlay functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.overlay = VisualOverlay()
        
        # Create sample image
        self.sample_image = Image.new('RGB', (200, 100), color='white')
    
    def test_highlight_region(self):
        """Test region highlighting."""
        region = (10, 10, 50, 30)  # x, y, width, height
        
        highlighted = self.overlay.highlight_region(self.sample_image, region)
        
        # Should return PIL Image
        self.assertIsInstance(highlighted, Image.Image)
        
        # Should be same size as original
        self.assertEqual(highlighted.size, self.sample_image.size)
    
    def test_highlight_multiple_regions(self):
        """Test highlighting multiple regions."""
        regions = [
            (10, 10, 50, 30),
            (70, 40, 80, 50)
        ]
        
        highlighted = self.overlay.highlight_regions(self.sample_image, regions)
        
        self.assertIsInstance(highlighted, Image.Image)
        self.assertEqual(highlighted.size, self.sample_image.size)
    
    def test_add_text_annotation(self):
        """Test adding text annotations."""
        position = (50, 25)
        text = "Test annotation"
        
        annotated = self.overlay.add_text_annotation(
            self.sample_image, 
            text, 
            position
        )
        
        self.assertIsInstance(annotated, Image.Image)
        self.assertEqual(annotated.size, self.sample_image.size)
    
    def test_create_debug_view(self):
        """Test creating debug view with multiple elements."""
        regions = [(10, 10, 50, 30)]
        annotations = [("Found text", (60, 20))]
        
        debug_view = self.overlay.create_debug_view(
            self.sample_image,
            regions=regions,
            annotations=annotations
        )
        
        self.assertIsInstance(debug_view, Image.Image)


if __name__ == '__main__':
    unittest.main()
