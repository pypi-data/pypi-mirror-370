# Bot Vision Suite Documentation

Welcome to the comprehensive documentation for Bot Vision Suite, a powerful Python package for computer vision-based automation and RPA (Robotic Process Automation).

## Table of Contents

1. [Quick Start](quickstart.md)
2. [Installation Guide](installation.md)
3. [API Reference](api_reference.md)
4. [Configuration Guide](configuration.md)
5. [Advanced Usage](advanced_usage.md)
6. [Examples](examples.md)
7. [Migration Guide](migration.md)
8. [Troubleshooting](troubleshooting.md)
9. [Contributing](contributing.md)

## Overview

Bot Vision Suite is a modular, extensible Python package that provides computer vision capabilities for automation tasks. It allows you to:

- **Find text elements** on screen using OCR (Optical Character Recognition)
- **Click on text elements** automatically
- **Execute complex workflows** with multiple steps
- **Handle errors gracefully** with retry mechanisms
- **Debug visually** with overlay highlights
- **Configure flexibly** for different use cases

## Key Features

### 🔍 Multiple OCR Engines
- **Tesseract**: Industry-standard OCR engine
- **EasyOCR**: Deep learning-based OCR
- **OpenCV**: Computer vision-based text detection
- **Extensible**: Add your own OCR engines

### ⚙️ Flexible Configuration
- Confidence thresholds
- Retry mechanisms
- Debug modes
- Custom Tesseract paths
- Performance tuning

### 🎯 Precise Targeting
- Region-based searching
- Case-sensitive/insensitive matching
- Confidence scoring
- Multi-step workflows

### 🐛 Debugging Support
- Visual overlays
- Detailed logging
- Error reporting
- Debug screenshots

### 📦 Easy Integration
- Pip installable
- Simple API
- Multiple usage patterns
- Comprehensive examples

## Quick Example

```python
from bot_vision import find_text, click_text

# Find text on screen
if find_text("Login"):
    print("Login button found!")
    
# Click a button
if click_text("Submit"):
    print("Submit button clicked!")
```

## Architecture

```
bot-vision-suite/
├── bot_vision/           # Main package
│   ├── core/            # Core functionality
│   │   ├── ocr_engine.py     # OCR engines
│   │   ├── image_processing.py # Image preprocessing
│   │   ├── task_executor.py  # Task execution
│   │   └── overlay.py        # Visual debugging
│   ├── utils/           # Utilities
│   │   ├── config.py        # Configuration
│   │   └── text_filters.py  # Text processing
│   └── exceptions.py    # Custom exceptions
├── tests/               # Test suite
├── examples/            # Usage examples
└── docs/               # Documentation
```

## Getting Started

1. **Install the package**:
   ```bash
   pip install bot-vision-suite
   ```

2. **Try a simple example**:
   ```python
   from bot_vision import find_text
   
   if find_text("Desktop"):
       print("Found Desktop text!")
   ```

3. **Explore the examples**:
   - `examples/basic_example.py` - Simple usage patterns
   - `examples/advanced_workflow.py` - Complex workflows
   - `examples/migration_guide.py` - Migration from old scripts

## Support

- **Documentation**: Full API reference and guides
- **Examples**: Comprehensive example scripts
- **Tests**: Unit and integration tests
- **Issues**: Report bugs and request features

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
