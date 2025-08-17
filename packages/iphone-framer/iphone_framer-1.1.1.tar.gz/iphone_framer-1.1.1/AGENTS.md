## Project Overview

This is a Python tool for generating App Store-compliant screenshots by adding iPhone frames and promotional text to existing app screenshots. The main component is `iPhoneFrameGenerator` class in `iphone_framer.py`.

## Development Commands

### Running with uvx (Recommended)

```bash
uvx --from . iphone-framer screenshot.png -o output.png -t "Title Text" -s "Subtitle Text" --device 6.9_inch
```

### Running Directly

```bash
source .venv/bin/activate.fish  # Activate virtual environment
python3 iphone_framer.py screenshot.png -o output.png -t "Title Text" -s "Subtitle Text" --device 6.9_inch
```

### Testing Command (from mise.toml)

```bash
mise run test
# Equivalent to: python iphone_framer.py screenshot.png -o output.png -t "Revolutionary Design" -s "Experience the future" --device 6.9_inch
```

### Code Formatting

Always run `ruff format` on Python files before committing:

```bash
ruff format *.py
```

### Testing with Sample File

Test the tool using the included screenshot.png:

```bash
uvx --from . iphone-framer screenshot.png -o test-output.png -t "Test Frame" -s "Sample Screenshot"
```

### Gradient Background Presets

Use elegant gradient backgrounds instead of solid colors:

```bash
# Ocean blue gradient
uvx --from . iphone-framer screenshot.png -o output.png -t "Ocean App" --gradient ocean

# Warm sunset gradient with diagonal direction
uvx --from . iphone-framer screenshot.png -o output.png -t "Sunset Vibes" --gradient sunset --gradient-direction diagonal

# Other available gradients: forest, purple, midnight, rose, emerald, autumn, arctic, cosmic
```

Available gradient presets:

- **ocean**: Deep ocean blue tones
- **sunset**: Warm orange/pink sunset colors
- **forest**: Forest green to teal
- **purple**: Purple dream with mystical tones
- **midnight**: Dark midnight blue
- **rose**: Rose gold elegance
- **emerald**: Emerald sea blues/greens
- **autumn**: Autumn leaf colors
- **arctic**: Cool arctic ice tones
- **cosmic**: Cosmic space purples/blues

## Architecture

### Core Components

- **iPhoneFrameGenerator**: Main class handling screenshot processing
  - `create_phone_frame()`: Generates iPhone-style frames with rounded corners
  - `add_promotional_text()`: Adds title/subtitle text with shadows
  - `process_screenshot()`: Main processing pipeline that combines screenshot, frame, and text
  - `get_font()`: Cross-platform font loading with fallbacks

### Key Configuration

- **App Store Sizes**: Supports multiple iPhone screen sizes (6.9", 6.5", 6.1", 5.5")
- **Frame Dimensions**: 60px padding around screenshots, 200px text area height
- **Output Formats**: PNG (with transparency) or JPEG
- **Font System**: Cross-platform font loading (macOS/Linux/Windows paths)

### Processing Pipeline

1. Load and convert screenshot to RGBA
2. Calculate scaling to fit target App Store dimensions
3. Create phone frame with rounded corners and bezels
4. Composite screenshot into frame
5. Add promotional text with shadows
6. Export final image

## Dependencies

- PIL (Pillow): Image processing and manipulation
- argparse: Command-line interface
- os: File system operations

## Device Size Options

- `6.9_inch`: iPhone 14 Pro Max, 15 Pro Max, 16 Pro Max (1290x2796)
- `6.5_inch`: iPhone 14 Plus, 13 Pro Max, 12 Pro Max (1284x2778)
- `6.1_inch`: iPhone 14 Pro, 13 Pro, 12 Pro (1170x2532)
- `5.5_inch`: iPhone 8 Plus, 7 Plus, 6s Plus (1242x2208)
