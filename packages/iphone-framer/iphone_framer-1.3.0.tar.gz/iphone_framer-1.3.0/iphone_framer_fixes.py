#!/usr/bin/env python3
"""
iPhone Screenshot Frame Generator for App Store - SUGGESTED FIXES
This file contains the key fixes that should be applied to iphone_framer.py
"""

# Fix 1: Efficient gradient generation using numpy-style operations
def create_gradient_background_efficient(self, width, height, gradient_colors, direction="vertical"):
    """Create a gradient background - EFFICIENT VERSION"""
    if len(gradient_colors) < 2:
        raise ValueError("Gradient requires at least 2 colors")
    
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")
    
    background = Image.new("RGB", (width, height))
    pixels = background.load()
    
    if direction == "vertical":
        # Pre-calculate colors for each row
        row_colors = []
        for y in range(height):
            position = y / max(height - 1, 1)  # Prevent division by zero
            
            segment_size = 1.0 / max(len(gradient_colors) - 1, 1)
            segment = min(int(position / segment_size), len(gradient_colors) - 2)
            local_position = (position - segment * segment_size) / max(segment_size, 0.001)
            
            color1 = gradient_colors[segment]
            color2 = gradient_colors[segment + 1]
            
            r = int(color1[0] + local_position * (color2[0] - color1[0]))
            g = int(color1[1] + local_position * (color2[1] - color1[1]))
            b = int(color1[2] + local_position * (color2[2] - color1[2]))
            
            row_colors.append((r, g, b))
        
        # Fill entire rows at once
        for y in range(height):
            color = row_colors[y]
            for x in range(width):
                pixels[x, y] = color
                
    elif direction == "diagonal":
        max_distance = max((width**2 + height**2) ** 0.5, 1)  # Prevent division by zero
        
        for y in range(height):
            for x in range(width):
                distance = (x**2 + y**2) ** 0.5
                position = distance / max_distance
                
                segment_size = 1.0 / max(len(gradient_colors) - 1, 1)
                segment = min(int(position / segment_size), len(gradient_colors) - 2)
                local_position = (position - segment * segment_size) / max(segment_size, 0.001)
                
                color1 = gradient_colors[segment]
                color2 = gradient_colors[segment + 1]
                
                r = int(color1[0] + local_position * (color2[0] - color1[0]))
                g = int(color1[1] + local_position * (color2[1] - color1[1]))
                b = int(color1[2] + local_position * (color2[2] - color1[2]))
                
                pixels[x, y] = (r, g, b)
    
    return background

# Fix 2: Better error handling with specific exceptions
def get_font_improved(self, size, font_weight="bold"):
    """Try to get a system font, fallback to default - IMPROVED ERROR HANDLING"""
    font_paths = [
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]

    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except (OSError, IOError) as e:
            # Log specific font loading errors if needed
            continue
    
    # Fallback to default font
    try:
        return ImageFont.truetype("arial.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()

# Fix 3: Add input validation
def validate_inputs(self, device_size, width=None, height=None):
    """Validate input parameters"""
    if device_size not in self.app_store_sizes:
        raise ValueError(f"Invalid device size: {device_size}. Must be one of: {list(self.app_store_sizes.keys())}")
    
    if width is not None and width <= 0:
        raise ValueError("Width must be positive")
    
    if height is not None and height <= 0:
        raise ValueError("Height must be positive")

# Fix 4: Improved color parsing with better error handling
def parse_background_color(color_string):
    """Parse background color string with proper error handling"""
    if not color_string:
        return None
        
    try:
        rgb_values = [int(x.strip()) for x in color_string.split(",")]
        if len(rgb_values) != 3:
            raise ValueError("RGB color must have exactly 3 values")
        
        for val in rgb_values:
            if not (0 <= val <= 255):
                raise ValueError("RGB values must be between 0 and 255")
        
        return tuple(rgb_values)
    except ValueError as e:
        raise ValueError(f"Invalid background color format: {e}")

# Fix 5: Configurable constants
class iPhoneFrameGeneratorImproved:
    def __init__(self):
        # Configurable constants instead of hardcoded values
        self.config = {
            "bezel_thickness": 40,
            "text_area_height": 400,
            "title_font_size": 84,
            "subtitle_font_size": 50,
            "title_y_position": 150,
            "subtitle_spacing": 20,
            "shadow_offset": 2,
            "screenshot_scale_factor": 0.90,
            "dynamic_island_scale": 0.3,
            "frame_y_offset": 25,
        }
        
        # Rest of initialization...
        
# Fix 6: Better Dynamic Island handling
def add_dynamic_island_improved(self, draw, frame_width, device_size="6.9_inch"):
    """Add Dynamic Island for modern iPhones - IMPROVED VERSION"""
    if device_size not in ["6.9_inch", "6.1_inch"]:
        return
        
    island_config = self.dynamic_island_dimensions
    island_width = island_config["width"]
    island_height = island_config["height"] 
    island_radius = island_config["radius"]
    island_x = (frame_width - island_width) // 2
    island_y = self.config.get("frame_y_offset", 25)
    
    # Validate dimensions
    if island_x < 0 or island_y < 0:
        return  # Skip if island doesn't fit
    
    draw.rounded_rectangle(
        [island_x, island_y, island_x + island_width, island_y + island_height],
        radius=island_radius,
        fill=(0, 0, 0),
    )

# Fix 7: Better exception handling in main processing
def process_screenshot_improved(self, screenshot_path, output_path, title_text, **kwargs):
    """Main function to process the screenshot - IMPROVED VERSION"""
    
    # Validate inputs first
    device_size = kwargs.get('device_size', '6.9_inch')
    self.validate_inputs(device_size)
    
    # Load the screenshot with better error handling
    try:
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot file not found: {screenshot_path}")
            
        screenshot = Image.open(screenshot_path)
    except (FileNotFoundError, IOError, Image.UnidentifiedImageError) as e:
        raise Exception(f"Error loading screenshot: {e}")
    
    # Validate image
    if screenshot.size[0] == 0 or screenshot.size[1] == 0:
        raise ValueError("Screenshot has invalid dimensions")
    
    # Rest of processing with better error handling...