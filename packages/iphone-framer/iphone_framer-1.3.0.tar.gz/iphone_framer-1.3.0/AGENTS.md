# iPhone Framer - Agent Documentation

## Project Overview

This is a Python tool (v1.2.0) for generating App Store-compliant screenshots by adding iPhone frames and promotional text to existing app screenshots. The main component is `iPhoneFrameGenerator` class in `iphone_framer.py`. The project is published on PyPI and can be installed via `pip install iphone-framer`.

## Current Project Structure

```
iphone-framer/
├── iphone_framer.py          # Main script with iPhoneFrameGenerator class
├── pyproject.toml           # Package configuration (v1.2.0)
├── mise.toml                # Development tasks and tooling
├── README.md                # Public documentation
├── AGENTS.md                # This file - agent context
├── analyze_frame.py         # Analysis utilities
├── detailed_frame_analysis.py # Detailed frame analysis
├── uv.lock                  # Dependency lock file
└── [Various test outputs]   # Generated test images
```

## Development Commands

### Package Management & Publishing

```bash
# Build package
mise run build                # uv build
mise run clean-build         # rm -rf dist/ && uv build

# Publishing (requires UV_PUBLISH_TOKEN)
mise run publish             # Production PyPI
mise run test-publish        # TestPyPI

# Version bumping
mise run bump-patch          # uv version --bump patch
mise run bump-minor          # uv version --bump minor  
mise run bump-major          # uv version --bump major

# Complete release workflow
mise run release             # Clean, build, publish
mise run test-release        # Clean, build, test-publish
```

### Development & Testing

```bash
# Local development (installed mode)
uvx --from . iphone-framer screenshot.png -o output.png -t "Title" -s "Subtitle" --device 6.9_inch

# Direct execution
python3 iphone_framer.py screenshot.png -o output.png -t "Title" -s "Subtitle" --device 6.9_inch

# Quick testing
mise run test               # Basic test with sample screenshot
mise run test2              # Test with ocean gradient
```

### Code Quality

```bash
ruff format *.py           # Format Python files before committing
```

### Installation Methods

```bash
# Production installation
pip install iphone-framer

# Direct usage (no installation)
uvx iphone-framer screenshot.png -t "Amazing App" -s "Experience the future"

# Local development
uvx --from . iphone-framer [args...]
```

## Core Features & Capabilities

### Device Support
- **6.9_inch**: iPhone 14 Pro Max, 15 Pro Max, 16 Pro Max (1290x2796)
- **6.5_inch**: iPhone 14 Plus, 13 Pro Max, 12 Pro Max (1284x2778)  
- **6.1_inch**: iPhone 14 Pro, 13 Pro, 12 Pro (1170x2532)
- **5.5_inch**: iPhone 8 Plus, 7 Plus, 6s Plus (1242x2208)

### Visual Features
- **Dynamic Island**: Automatically added for modern iPhones (6.9", 6.1")
- **Home Indicator**: Added for all devices except 5.5"
- **Realistic Phone Frames**: Metallic appearance with highlights and bezels
- **Rounded Screenshots**: Corner radius of 40px with Dynamic Island cutouts
- **Promotional Text**: Title/subtitle with shadow effects

### Background Options
- **Solid Colors**: Custom RGB via `--bg-color "R,G,B"`
- **Gradient Presets**: 10 built-in presets with vertical/diagonal directions
  - ocean, sunset, forest, purple, midnight, rose, emerald, autumn, arctic, cosmic

### Output Formats
- **PNG**: Default with transparency support
- **JPEG**: High quality (95%) for smaller file sizes
- **App Store Compliance**: RGB mode, proper dimensions

## Architecture

### Core Class: iPhoneFrameGenerator

**Key Methods:**
- `process_screenshot()`: Main processing pipeline (lines 344-449)
- `create_phone_frame()`: Generates realistic iPhone frames (lines 182-268)
- `create_rounded_screenshot()`: Applies corner radius and Dynamic Island (lines 133-164)
- `add_promotional_text()`: Renders title/subtitle with shadows (lines 294-342)
- `create_gradient_background()`: Generates gradient backgrounds (lines 75-131)
- `get_font()`: Cross-platform font loading with fallbacks (lines 270-292)

**Configuration:**
- `app_store_sizes`: Target dimensions for each device (lines 22-27)
- `gradient_presets`: 10 predefined gradient color schemes (lines 62-73)
- `frame_config`: Phone frame appearance settings (lines 44-59)
- `dynamic_island_dimensions`: Modern iPhone cutout specs (lines 36-41)

### Processing Pipeline
1. Load and validate input screenshot
2. Calculate optimal scaling for target device size
3. Resize screenshot maintaining aspect ratio (90% of available space)
4. Apply rounded corners and Dynamic Island cutout
5. Generate background (solid color or gradient)
6. Create realistic phone frame with metallic appearance
7. Composite all elements (background → frame → screenshot)
8. Add promotional text with shadows
9. Convert to RGB and export in target format

### Font System
Cross-platform font loading with prioritized fallbacks:
1. macOS: SF Compact, Helvetica, Arial
2. Linux: Liberation Sans Bold
3. Windows: Arial
4. Final fallback: Default system font

## Dependencies & Environment

**Core Dependencies:**
- **Pillow (>=9.0.0)**: Image processing and manipulation
- **Python**: >=3.8 support (3.8-3.12 tested)

**Development Tools:**
- **uv**: Package management and building
- **mise**: Task runner and environment management  
- **ruff**: Code formatting

## Command Line Interface

**Required Arguments:**
- `screenshot`: Path to input iPhone screenshot
- `-t, --title`: Main promotional text (required)

**Optional Arguments:**
- `-o, --output`: Output path (default: input_filename_appstore.jpg)
- `-s, --subtitle`: Subtitle text
- `-d, --device`: Device size (default: 6.9_inch)
- `--bg-color`: RGB background color as "R,G,B"
- `--gradient`: Gradient preset name
- `--gradient-direction`: vertical|diagonal (default: vertical)
- `--version`: Show version information

## File Naming Conventions

**Auto-generated outputs:** `{input_name}_appstore.{jpg|png}`
**Test outputs:** Various `test-*.png` files for development verification
**Analysis scripts:** `analyze_frame.py`, `detailed_frame_analysis.py` for debugging

## Publishing Workflow

The project is configured for automated publishing to PyPI:
1. Update version in pyproject.toml
2. Run `mise run clean-build` to build package
3. Run `mise run test-publish` to test on TestPyPI
4. Run `mise run publish` for production release
5. Requires `UV_PUBLISH_TOKEN` environment variable

## Development Notes

- Always format code with `ruff format *.py` before committing
- Test with sample screenshot.png included in repository
- Version 1.2.0 includes gradient backgrounds and improved frame rendering
- Cross-platform compatibility tested on macOS, Linux, Windows
- App Store compliance: RGB output, proper dimensions, no alpha channels
