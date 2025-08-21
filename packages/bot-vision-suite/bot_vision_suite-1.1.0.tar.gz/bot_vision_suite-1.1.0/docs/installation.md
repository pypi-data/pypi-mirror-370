# Installation Guide

This guide covers different ways to install and set up Bot Vision Suite.

## Prerequisites

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM recommended
- **Display**: GUI environment for automation tasks

### Required Dependencies

The package will automatically install these dependencies:

- `opencv-python` (4.5.0+) - Computer vision operations
- `pillow` (8.0.0+) - Image processing
- `numpy` (1.19.0+) - Numerical operations
- `pyautogui` (0.9.50+) - GUI automation
- `pytesseract` (0.3.7+) - Tesseract OCR wrapper

### Optional Dependencies

For enhanced functionality:

- `easyocr` (1.6.0+) - Alternative OCR engine
- `pytest` (6.0.0+) - For running tests
- `tesseract` - OCR engine (system installation)

## Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
pip install bot-vision-suite
```

This is the simplest method and installs the latest stable version.

### Method 2: Development Installation

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/yourusername/bot-vision-suite.git
cd bot-vision-suite

# Install in development mode
pip install -e .
```

### Method 3: From Source

```bash
# Download and extract the source
wget https://github.com/yourusername/bot-vision-suite/archive/main.zip
unzip main.zip
cd bot-vision-suite-main

# Install
pip install .
```

## Platform-Specific Setup

### Windows

1. **Install Python** (if not already installed):
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH"

2. **Install Tesseract** (optional but recommended):
   ```bash
   # Using chocolatey
   choco install tesseract
   
   # Or download from GitHub releases
   # https://github.com/UB-Mannheim/tesseract/wiki
   ```

3. **Install the package**:
   ```bash
   pip install bot-vision-suite
   ```

### macOS

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and Tesseract**:
   ```bash
   brew install python tesseract
   ```

3. **Install the package**:
   ```bash
   pip3 install bot-vision-suite
   ```

### Linux (Ubuntu/Debian)

1. **Update system packages**:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python and dependencies**:
   ```bash
   sudo apt install python3 python3-pip tesseract-ocr
   ```

3. **Install the package**:
   ```bash
   pip3 install bot-vision-suite
   ```

### Linux (CentOS/RHEL/Fedora)

1. **Install Python and dependencies**:
   ```bash
   # CentOS/RHEL
   sudo yum install python3 python3-pip tesseract
   
   # Fedora
   sudo dnf install python3 python3-pip tesseract
   ```

2. **Install the package**:
   ```bash
   pip3 install bot-vision-suite
   ```

## Virtual Environment Setup (Recommended)

Using a virtual environment helps avoid dependency conflicts:

### Using venv

```bash
# Create virtual environment
python -m venv bot-vision-env

# Activate virtual environment
# Windows:
bot-vision-env\Scripts\activate
# macOS/Linux:
source bot-vision-env/bin/activate

# Install the package
pip install bot-vision-suite
```

### Using conda

```bash
# Create conda environment
conda create -n bot-vision python=3.9

# Activate environment
conda activate bot-vision

# Install the package
pip install bot-vision-suite
```

## Verification

### Basic Installation Test

```python
# test_installation.py
try:
    from bot_vision import BotVision, find_text, click_text
    print("✓ Bot Vision Suite imported successfully!")
    
    # Test configuration
    from bot_vision.utils.config import BotVisionConfig
    config = BotVisionConfig()
    print(f"✓ Default configuration loaded: {config}")
    
    # Test bot creation
    bot = BotVision(config=config)
    print("✓ BotVision instance created successfully!")
    
    print("\n🎉 Installation verified successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run this test:
```bash
python test_installation.py
```

### Dependency Check

```python
# check_dependencies.py
import sys

def check_dependency(module_name, min_version=None):
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {module_name}: {version}")
        return True
    except ImportError:
        print(f"❌ {module_name}: Not installed")
        return False

print("Checking dependencies...")
print("=" * 30)

required = [
    'cv2',  # opencv-python
    'PIL',  # pillow  
    'numpy',
    'pyautogui',
    'pytesseract'
]

optional = [
    'easyocr',
    'pytest'
]

print("Required dependencies:")
all_required = all(check_dependency(dep) for dep in required)

print("\nOptional dependencies:")
for dep in optional:
    check_dependency(dep)

if all_required:
    print("\n🎉 All required dependencies are installed!")
else:
    print("\n❌ Some required dependencies are missing!")
```

### Tesseract Check

```python
# check_tesseract.py
from bot_vision.utils.config import detect_tesseract_path
import pytesseract

print("Checking Tesseract installation...")
print("=" * 35)

# Check if Tesseract is in PATH
tesseract_path = detect_tesseract_path()
if tesseract_path:
    print(f"✓ Tesseract found at: {tesseract_path}")
else:
    print("❌ Tesseract not found in PATH")

# Test Tesseract functionality
try:
    from PIL import Image
    import numpy as np
    
    # Create a test image with text
    img = Image.new('RGB', (200, 50), color='white')
    # Note: In real test, you'd draw text on the image
    
    # Test OCR
    result = pytesseract.image_to_string(img)
    print("✓ Tesseract OCR test completed")
except Exception as e:
    print(f"❌ Tesseract test failed: {e}")
```

## Troubleshooting

### Common Issues

1. **"No module named 'bot_vision'"**
   - Make sure you installed the package: `pip install bot-vision-suite`
   - Check if you're in the correct virtual environment

2. **"Tesseract not found"**
   - Install Tesseract system package
   - Set custom path in configuration:
     ```python
     config = BotVisionConfig(tesseract_path='/path/to/tesseract')
     ```

3. **Permission errors on Windows**
   - Run command prompt as administrator
   - Or use `--user` flag: `pip install --user bot-vision-suite`

4. **Import errors with OpenCV**
   - Try installing a different OpenCV variant:
     ```bash
     pip uninstall opencv-python
     pip install opencv-python-headless
     ```

5. **PyAutoGUI security restrictions on macOS**
   - Grant accessibility permissions to Terminal/IDE
   - System Preferences > Security & Privacy > Accessibility

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search existing issues on GitHub
3. Create a new issue with:
   - Your operating system
   - Python version
   - Complete error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. **Read the [Quick Start Guide](quickstart.md)**
2. **Try the [Basic Example](../examples/basic_example.py)**
3. **Explore the [API Reference](api_reference.md)**
4. **Check out [Advanced Usage](advanced_usage.md)**
