# API Reference

Complete reference for all Bot Vision Suite classes, functions, and modules.

## Core API

### Main Functions

#### `execute_tasks(tasks, config=None)`

Execute a list of automation tasks.

**Parameters:**
- `tasks` (list): List of task dictionaries
- `config` (BotVisionConfig, optional): Configuration object

**Returns:**
- `list`: List of task execution results

**Example:**
```python
from bot_vision import execute_tasks

tasks = [{
    "task_name": "find_button",
    "description": "Find submit button",
    "steps": [
        {"action": "find_text", "text": "Submit"}
    ]
}]

results = execute_tasks(tasks)
```

---

#### `find_text(text, region=None, case_sensitive=True, config=None)`

Find text on the screen using OCR.

**Parameters:**
- `text` (str): Text to search for
- `region` (tuple, optional): Search region as (x, y, width, height)
- `case_sensitive` (bool): Whether search is case sensitive (default: True)
- `config` (BotVisionConfig, optional): Configuration object

**Returns:**
- `bool`: True if text is found, False otherwise

**Example:**
```python
from bot_vision import find_text

# Search entire screen
found = find_text("Login")

# Search specific region
found = find_text("Submit", region=(100, 100, 400, 300))

# Case insensitive search
found = find_text("login", case_sensitive=False)
```

---

#### `click_text(text, region=None, case_sensitive=True, config=None)`

Find and click on text element.

**Parameters:**
- `text` (str): Text to search for and click
- `region` (tuple, optional): Search region as (x, y, width, height)
- `case_sensitive` (bool): Whether search is case sensitive (default: True)
- `config` (BotVisionConfig, optional): Configuration object

**Returns:**
- `bool`: True if text was found and clicked, False otherwise

**Example:**
```python
from bot_vision import click_text

# Click button with text "OK"
success = click_text("OK")

# Click in specific region
success = click_text("Submit", region=(200, 300, 600, 500))
```

## Classes

### BotVision

Main class for computer vision automation.

#### `__init__(config=None)`

Initialize BotVision instance.

**Parameters:**
- `config` (BotVisionConfig, optional): Configuration object

**Example:**
```python
from bot_vision import BotVision
from bot_vision.utils.config import BotVisionConfig

config = BotVisionConfig(debug_mode=True)
bot = BotVision(config=config)
```

#### `execute_tasks(tasks)`

Execute automation tasks.

**Parameters:**
- `tasks` (list): List of task dictionaries

**Returns:**
- `list`: List of execution results

#### `find_text_on_screen(text, region=None, **kwargs)`

Find text on screen.

**Parameters:**
- `text` (str): Text to find
- `region` (tuple, optional): Search region
- `**kwargs`: Additional OCR parameters

**Returns:**
- `bool`: True if found

#### `click_text_on_screen(text, region=None, **kwargs)`

Find and click text.

**Parameters:**
- `text` (str): Text to click
- `region` (tuple, optional): Search region
- `**kwargs`: Additional parameters

**Returns:**
- `bool`: True if successful

---

### BotVisionConfig

Configuration class for Bot Vision Suite.

#### `__init__(confidence_threshold=0.8, max_retries=3, retry_delay=1.0, debug_mode=True, tesseract_path=None)`

Initialize configuration.

**Parameters:**
- `confidence_threshold` (float): OCR confidence threshold (0.0-1.0)
- `max_retries` (int): Maximum retry attempts
- `retry_delay` (float): Delay between retries in seconds
- `debug_mode` (bool): Enable debug logging and overlays
- `tesseract_path` (str, optional): Custom Tesseract executable path
- `overlay_color` (str): Overlay color - available: 'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta', 'white', 'black'
- `overlay_duration` (int): Overlay duration in milliseconds (500-5000 recommended)
- `overlay_width` (int): Overlay line width (1-10 recommended)
- `show_overlay` (bool): Enable/disable overlay display
- `overlay_enabled` (bool): Enable/disable overlay system

**Example:**
```python
from bot_vision.utils.config import BotVisionConfig

# Basic configuration
config = BotVisionConfig(
    confidence_threshold=0.9,
    max_retries=5,
    retry_delay=2.0,
    debug_mode=True,
    tesseract_path="/usr/local/bin/tesseract"
)

# Configuration with overlay colors
config = BotVisionConfig({
    "confidence_threshold": 85.0,
    "retry_attempts": 3,
    "overlay_duration": 2000,      # 2 seconds
    "overlay_color": "blue",       # Blue color
    "overlay_width": 6,            # Thick line
    "show_overlay": True,          # Enable overlay
    "ocr_languages": ["eng", "por"],
    "log_level": "DEBUG"
})
```

**Available Overlay Colors:**
- `red` - Classic red (default)
- `blue` - Professional blue  
- `green` - Success green
- `yellow` - Attention yellow
- `purple` - Creative purple
- `orange` - Vibrant orange
- `cyan` - Modern cyan
- `magenta` - Bold magenta
- `white` - Minimalist white
- `black` - Elegant black

#### `from_dict(config_dict)`

Create configuration from dictionary.

**Parameters:**
- `config_dict` (dict): Configuration dictionary

**Returns:**
- `BotVisionConfig`: Configuration instance

**Example:**
```python
config_data = {
    "confidence_threshold": 0.85,
    "debug_mode": False
}
config = BotVisionConfig.from_dict(config_data)
```

#### `from_file(file_path)`

Load configuration from JSON file.

**Parameters:**
- `file_path` (str): Path to JSON configuration file

**Returns:**
- `BotVisionConfig`: Configuration instance

**Example:**
```python
config = BotVisionConfig.from_file("config.json")
```

#### `to_dict()`

Convert configuration to dictionary.

**Returns:**
- `dict`: Configuration as dictionary

#### `validate()`

Validate configuration parameters.

**Raises:**
- `ConfigurationError`: If configuration is invalid

## Core Modules

### OCREngine

OCR engine for text extraction.

#### `__init__(config)`

Initialize OCR engine.

**Parameters:**
- `config` (BotVisionConfig): Configuration object

#### `extract_text(image, method='tesseract', **kwargs)`

Extract text from image.

**Parameters:**
- `image` (numpy.ndarray): Input image
- `method` (str): OCR method ('tesseract', 'easyocr', 'opencv')
- `**kwargs`: Method-specific parameters

**Returns:**
- `str`: Extracted text

#### `find_text_in_image(image, target_text, **kwargs)`

Check if text exists in image.

**Parameters:**
- `image` (numpy.ndarray): Input image
- `target_text` (str): Text to find
- `**kwargs`: Search parameters

**Returns:**
- `bool`: True if text found

---

### ImageProcessor

Image preprocessing for OCR.

#### `__init__(config)`

Initialize image processor.

#### `preprocess_for_ocr(image, region=None)`

Preprocess image for OCR.

**Parameters:**
- `image` (numpy.ndarray): Input image
- `region` (tuple, optional): Crop region

**Returns:**
- `numpy.ndarray`: Processed image

#### `enhance_contrast(image)`

Enhance image contrast.

**Parameters:**
- `image` (numpy.ndarray): Input image

**Returns:**
- `numpy.ndarray`: Enhanced image

#### `remove_noise(image)`

Remove noise from image.

**Parameters:**
- `image` (numpy.ndarray): Input image

**Returns:**
- `numpy.ndarray`: Denoised image

---

### TaskExecutor

Task execution engine.

#### `__init__(config)`

Initialize task executor.

#### `execute_task(task)`

Execute single task.

**Parameters:**
- `task` (dict): Task definition

**Returns:**
- `dict`: Execution result

#### `execute_find_text(step)`

Execute find_text action.

**Parameters:**
- `step` (dict): Step definition

**Returns:**
- `dict`: Step result

#### `execute_click_text(step)`

Execute click_text action.

**Parameters:**
- `step` (dict): Step definition

**Returns:**
- `dict`: Step result

---

### VisualOverlay

Visual debugging overlays.

#### `highlight_region(image, region, color='red', width=2)`

Highlight region on image.

**Parameters:**
- `image` (PIL.Image): Input image
- `region` (tuple): Region to highlight
- `color` (str): Highlight color
- `width` (int): Line width

**Returns:**
- `PIL.Image`: Image with highlight

#### `add_text_annotation(image, text, position, color='red')`

Add text annotation to image.

**Parameters:**
- `image` (PIL.Image): Input image
- `text` (str): Annotation text
- `position` (tuple): Text position
- `color` (str): Text color

**Returns:**
- `PIL.Image`: Annotated image

## Utility Functions

### Text Filters

#### `clean_text(text, remove_special_chars=False, to_lower=False, to_upper=False)`

Clean and normalize text.

**Parameters:**
- `text` (str): Input text
- `remove_special_chars` (bool): Remove special characters
- `to_lower` (bool): Convert to lowercase
- `to_upper` (bool): Convert to uppercase

**Returns:**
- `str`: Cleaned text

#### `filter_text_by_keywords(text_lines, keywords, case_sensitive=True)`

Filter text lines by keywords.

**Parameters:**
- `text_lines` (list): List of text lines
- `keywords` (list): Keywords to filter by
- `case_sensitive` (bool): Case sensitive matching

**Returns:**
- `list`: Filtered text lines

### Configuration Utilities

#### `detect_tesseract_path()`

Detect Tesseract installation path.

**Returns:**
- `str` or `None`: Tesseract path if found

## Exceptions

### BotVisionError

Base exception class for Bot Vision Suite.

### OCRError

Exception raised for OCR-related errors.

### TaskExecutionError

Exception raised for task execution errors.

### ConfigurationError

Exception raised for configuration errors.

### ElementNotFoundError

Exception raised when UI elements are not found.

## Task Format

### Task Structure

```python
task = {
    "task_name": "unique_task_name",
    "description": "Human-readable description",
    "steps": [
        {
            "action": "find_text",  # or "click_text"
            "text": "target_text",
            "region": [x, y, width, height],  # optional
            "case_sensitive": True,  # optional
            "confidence_threshold": 0.8  # optional
        }
    ]
}
```

### Action Types

#### find_text

Find text on screen without clicking.

**Parameters:**
- `text` (str): Text to find
- `region` (list, optional): Search region
- `case_sensitive` (bool, optional): Case sensitivity
- `confidence_threshold` (float, optional): OCR confidence

#### click_text

Find and click text element.

**Parameters:**
- `text` (str): Text to click
- `region` (list, optional): Search region
- `case_sensitive` (bool, optional): Case sensitivity
- `confidence_threshold` (float, optional): OCR confidence

### Result Format

```python
result = {
    "task_name": "task_name",
    "success": True,  # or False
    "execution_time": 1.23,  # seconds
    "steps_completed": 2,
    "total_steps": 2,
    "error": None,  # or error message
    "details": {
        "step_results": [...],
        "screenshots": [...],  # if debug mode
        "ocr_results": [...]
    }
}
```

## Type Hints

```python
from typing import List, Dict, Optional, Tuple, Union

# Task definition type
Task = Dict[str, Union[str, List[Dict]]]

# Region type
Region = Tuple[int, int, int, int]  # x, y, width, height

# Result type
TaskResult = Dict[str, Union[str, bool, float, int, Dict]]
```

## Examples

See the [examples directory](../examples/) for complete working examples:

- `basic_example.py` - Simple usage patterns
- `advanced_workflow.py` - Complex automation workflows
- `migration_guide.py` - Migration from old scripts
