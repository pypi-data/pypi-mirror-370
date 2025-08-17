# iPhone Framer

Generate App Store-compliant screenshots by adding iPhone frames and promotional text to your app screenshots.

## Installation

```bash
pip install iphone-framer
```

Or use with uvx (no installation required):

```bash
# With custom output filename
uvx iphone-framer screenshot.png -o output.png -t "Amazing App" -s "Experience the future"

# Auto-generate output filename
uvx iphone-framer screenshot.png -t "Amazing App" -s "Experience the future"
```

## Usage

### Basic Usage

```bash
# With custom output filename
iphone-framer screenshot.png -o output.png -t "Revolutionary Design" -s "Experience the future" --device 6.9_inch

# Auto-generate output filename (creates screenshot_appstore.png)
iphone-framer screenshot.png -t "Revolutionary Design" -s "Experience the future" --device 6.9_inch
```

### Gradient Backgrounds

```bash
# Ocean blue gradient
iphone-framer screenshot.png -o output.png -t "Ocean App" --gradient ocean

# Sunset gradient with diagonal direction
iphone-framer screenshot.png -o output.png -t "Sunset Vibes" --gradient sunset --gradient-direction diagonal
```

### Available Options

- `--device`: Choose from `6.9_inch`, `6.5_inch`, `6.1_inch`, `5.5_inch`
- `--gradient`: Use preset gradients: `ocean, sunset, forest, purple, midnight, rose, emerald, autumn, arctic, cosmic`
- `--gradient-direction`: `vertical` or `diagonal`
- `--bg-color`: Custom RGB background color as "R,G,B"

## Features

- 📱 Multiple iPhone sizes (6.9", 6.5", 6.1", 5.5")
- 🎨 Beautiful gradient presets
- 🏝️ Dynamic Island for modern iPhones
- 📐 App Store compliant dimensions
- ✨ Promotional text with shadows
- 🔄 Cross-platform font support

## Device Sizes

- `6.9_inch`: iPhone 14 Pro Max, 15 Pro Max, 16 Pro Max (1290x2796)
- `6.5_inch`: iPhone 14 Plus, 13 Pro Max, 12 Pro Max (1284x2778)
- `6.1_inch`: iPhone 14 Pro, 13 Pro, 12 Pro (1170x2532)
- `5.5_inch`: iPhone 8 Plus, 7 Plus, 6s Plus (1242x2208)

## License

MIT