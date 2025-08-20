# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`img-show` is a Python package that simplifies displaying images using OpenCV. The package automatically handles various image formats (NumPy arrays, PyTorch tensors), coerces images into valid shapes for display, and manages window sizing based on screen dimensions.

### Core Architecture

- **Single module design**: All functionality is contained in `img_show.py`
- **Main functions**:
  - `show_img()`: Display a single image with automatic coercion and sizing
  - `show_imgs()`: Display multiple images simultaneously
  - `coerce_img()`: Convert various image formats to displayable NumPy arrays
  - `close_all()`: Close all open image windows

### Key Implementation Details

- **Image coercion pipeline**: `_coerce_shape()` → dtype conversion → normalization
- **Automatic resizing**: Images larger than screen are automatically resized while maintaining aspect ratio
- **Channel order handling**: Automatically detects and converts between channels-first (PyTorch) and channels-last (NumPy) formats
- **Global window tracking**: Uses `open_window_names` set to track open windows for cleanup

## Common Development Commands

### Build
```bash
make build        # Build source and wheel distributions
python setup.py sdist bdist_wheel
```

### Code Quality
```bash
ruff check        # Lint code (ruff is available in dev requirements)
ruff format       # Format code
mypy img_show.py  # Type checking
```

### Package Management
```bash
make clean        # Clean build artifacts
make upload-test  # Upload to test PyPI
make upload       # Upload to PyPI
```

### Installation
```bash
pip install opencv-python numpy  # Runtime dependencies
pip install -e .[dev]            # Install in development mode with dev tools
```

## Python Version Support

- Minimum: Python 3.8
- Supported: 3.8, 3.9, 3.10, 3.11, 3.12
- Uses legacy typing imports (Union, List, etc.) for 3.8 compatibility

## Dependencies

- **Runtime**: opencv-python, numpy
- **Optional**: torch (for PyTorch tensor support)
- **Development**: twine, ruff, mypy

## Key Files

- `img_show.py`: Single-module implementation
- `setup.cfg`: Package metadata and configuration
- `requirements.txt`: Runtime dependencies
- `requirements_dev.txt`: Development tools
- `Makefile`: Build and upload commands