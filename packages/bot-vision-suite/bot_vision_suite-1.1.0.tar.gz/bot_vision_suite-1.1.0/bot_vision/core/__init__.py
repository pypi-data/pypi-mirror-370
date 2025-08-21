"""
Bot Vision Suite - Core Modules

Este módulo contém as classes e funções principais do Bot Vision Suite.
"""

from .image_processing import (
    ImageProcessor,
    preprocess_image_for_ocr,
    get_available_methods
)

from .ocr_engine import (
    OCREngine,
    OCRResult,
    find_text_with_multiple_preprocessing,
    extract_text_from_image
)

from .overlay import (
    VisualOverlay,
    show_overlay,
    show_overlay_blocking,
    show_multiple_overlays
)

from .task_executor import (
    TaskExecutor,
    TaskResult,
    execute_tasks,
    click_images
)

from .relative_image import (
    RelativeImageDetector
)

from .keyboard_commands import (
    KeyboardCommander
)

__all__ = [
    # Image processing
    "ImageProcessor",
    "preprocess_image_for_ocr", 
    "get_available_methods",
    # OCR
    "OCREngine",
    "OCRResult",
    "find_text_with_multiple_preprocessing",
    "extract_text_from_image",
    # Overlay
    "VisualOverlay",
    "show_overlay",
    "show_overlay_blocking", 
    "show_multiple_overlays",
    # Task executor
    "TaskExecutor",
    "TaskResult",
    "execute_tasks",
    "click_images",
    # Relative image detection (NEW!)
    "RelativeImageDetector",
    # Keyboard commands (NEW!)
    "KeyboardCommander"
]
