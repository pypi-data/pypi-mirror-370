#!/usr/bin/env python3
"""
iPhone Screenshot Frame Generator for App Store
Creates App Store compliant screenshots by adding phone frames and promotional text
"""

from PIL import Image, ImageDraw, ImageFont
import os
import argparse

__version__ = "1.1.2"


class iPhoneFrameGenerator:
    def __init__(self):
        # App Store screenshot dimensions (6.5" display - iPhone 14 Pro Max, etc.)
        self.app_store_sizes = {
            "6.9_inch": (1290, 2796),  # iPhone 14 Pro Max, 15 Pro Max, 16 Pro Max
            "6.5_inch": (1284, 2778),  # iPhone 14 Plus, 13 Pro Max, 12 Pro Max
            "6.1_inch": (1170, 2532),  # iPhone 14 Pro, 13 Pro, 12 Pro
            "5.5_inch": (1242, 2208),  # iPhone 8 Plus, 7 Plus, 6s Plus
        }

        # iPhone frame dimensions (approximate bezels and rounded corners)
        self.bezel_thickness = (
            40  # This controls the bezel thickness around the screenshot.
        )
        self.text_area_height = 400  # Space for promotional text

        # Dynamic Island dimensions
        self.dynamic_island_dimensions = {
            "width": 350,
            "height": 90,
            "radius": 40,
            "y_offset": 30,
        }

        # Centralized phone frame configuration
        self.frame_config = {
            "corner_radius": 150,
            "body_radius_offset": 15,
            "body_colors": {
                "outer": (58, 58, 60),
                "inner": (28, 28, 30),
                "highlight": (88, 88, 90),
            },
            "highlight_width": 3,
            "home_indicator": {
                "width": 134,
                "height": 5,
                "radius": 3,
                "color": (255, 255, 255),
            },
        }

        # Gradient background presets
        self.gradient_presets = {
            "ocean": [(87, 171, 224), (85, 120, 211), (89, 88, 214)],  # Deep ocean blue
            "sunset": [(255, 94, 77), (255, 154, 0), (255, 206, 84)],  # Warm sunset
            "forest": [(52, 73, 94), (44, 62, 80), (26, 188, 156)],  # Forest green
            "purple": [(106, 90, 205), (147, 39, 143), (234, 162, 215)],  # Purple dream
            "midnight": [(12, 20, 31), (25, 42, 86), (44, 62, 80)],  # Midnight blue
            "rose": [(252, 163, 186), (252, 74, 130), (108, 91, 123)],  # Rose gold
            "emerald": [(52, 152, 219), (26, 188, 156), (46, 204, 113)],  # Emerald sea
            "autumn": [(235, 149, 50), (207, 98, 34), (183, 65, 14)],  # Autumn leaves
            "arctic": [(174, 198, 207), (230, 233, 240), (209, 236, 241)],  # Arctic ice
            "cosmic": [(41, 50, 65), (72, 52, 212), (123, 67, 151)],  # Cosmic space
        }

    def create_gradient_background(
        self, width, height, gradient_colors, direction="vertical"
    ):
        """Create a gradient background"""
        background = Image.new("RGB", (width, height))

        if direction == "vertical":
            # Vertical gradient
            for y in range(height):
                # Calculate position in gradient (0.0 to 1.0)
                position = y / height

                # Find which color segment we're in
                segment_size = 1.0 / (len(gradient_colors) - 1)
                segment = min(int(position / segment_size), len(gradient_colors) - 2)
                local_position = (position - segment * segment_size) / segment_size

                # Interpolate between colors
                color1 = gradient_colors[segment]
                color2 = gradient_colors[segment + 1]

                r = int(color1[0] + local_position * (color2[0] - color1[0]))
                g = int(color1[1] + local_position * (color2[1] - color1[1]))
                b = int(color1[2] + local_position * (color2[2] - color1[2]))

                # Draw horizontal line with this color
                for x in range(width):
                    background.putpixel((x, y), (r, g, b))

        elif direction == "diagonal":
            # Diagonal gradient from top-left to bottom-right
            max_distance = (width**2 + height**2) ** 0.5

            for y in range(height):
                for x in range(width):
                    # Calculate distance from top-left corner
                    distance = (x**2 + y**2) ** 0.5
                    position = distance / max_distance

                    # Find which color segment we're in
                    segment_size = 1.0 / (len(gradient_colors) - 1)
                    segment = min(
                        int(position / segment_size), len(gradient_colors) - 2
                    )
                    local_position = (position - segment * segment_size) / segment_size

                    # Interpolate between colors
                    color1 = gradient_colors[segment]
                    color2 = gradient_colors[segment + 1]

                    r = int(color1[0] + local_position * (color2[0] - color1[0]))
                    g = int(color1[1] + local_position * (color2[1] - color1[1]))
                    b = int(color1[2] + local_position * (color2[2] - color1[2]))

                    background.putpixel((x, y), (r, g, b))

        return background.convert("RGB")

    def create_rounded_screenshot(
        self, screenshot, corner_radius=40, device_size="6.9_inch"
    ):
        """Create a screenshot with rounded corners by compositing onto a black background."""
        width, height = screenshot.size

        # Create a mask for rounded corners
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, width, height], radius=corner_radius, fill=255)

        # Add cutout for Dynamic Island for modern iPhones
        if device_size in ["6.9_inch", "6.1_inch"]:
            island_width = int(
                self.dynamic_island_dimensions["width"] * 0.3
            )  # Scale down for screenshot
            island_height = int(self.dynamic_island_dimensions["height"] * 0.3)
            island_radius = int(self.dynamic_island_dimensions["radius"] * 0.3)
            island_x = (width - island_width) // 2
            island_y = int(self.dynamic_island_dimensions["y_offset"] * 0.3)

            draw.rounded_rectangle(
                [island_x, island_y, island_x + island_width, island_y + island_height],
                radius=island_radius,
                fill=0,  # Punch a hole in the mask
            )

        # Create the final rounded screenshot with black background
        result = Image.new("RGB", (width, height), (0, 0, 0))  # Black background
        result.paste(screenshot, (0, 0), mask)

        return result

    def add_dynamic_island(self, draw, frame_width, device_size="6.9_inch"):
        """Add Dynamic Island for modern iPhones"""
        if device_size in ["6.9_inch", "6.1_inch"]:
            island_width = self.dynamic_island_dimensions["width"]
            island_height = self.dynamic_island_dimensions["height"]
            island_radius = self.dynamic_island_dimensions["radius"]
            island_x = (frame_width - island_width) // 2
            island_y = 25  # Position from the top of the frame

            # Draw Dynamic Island
            draw.rounded_rectangle(
                [island_x, island_y, island_x + island_width, island_y + island_height],
                radius=island_radius,
                fill=(0, 0, 0),
            )

    def create_phone_frame(
        self, width, height, corner_radius=40, device_size="6.9_inch"
    ):
        """Create a realistic iPhone-style frame"""
        # Create frame with padding
        frame_width = width + (self.bezel_thickness * 2)
        frame_height = height + (self.bezel_thickness * 2)

        # Create the frame image with dark background
        frame = Image.new("RGB", (frame_width, frame_height), (25, 25, 35))
        draw = ImageDraw.Draw(frame)

        # Get frame config
        config = self.frame_config
        body_colors = config["body_colors"]

        # Draw the main phone body with gradient-like effect
        body_radius = corner_radius + config["body_radius_offset"]

        # Outer body (metallic frame)
        draw.rounded_rectangle(
            [0, 0, frame_width, frame_height],
            radius=body_radius,
            fill=body_colors["outer"],
        )

        # Add metallic highlight on the edges
        highlight_width = config["highlight_width"]
        draw.rounded_rectangle(
            [
                highlight_width,
                highlight_width,
                frame_width - highlight_width,
                frame_height - highlight_width,
            ],
            radius=body_radius - highlight_width,
            outline=body_colors["highlight"],
            width=2,
        )

        # Inner bezel area (darker)
        bezel_margin = (
            self.bezel_thickness // 4
        )  # Inner bezel is a fraction of the padding
        bezel_area = [
            bezel_margin,
            bezel_margin,
            frame_width - bezel_margin,
            frame_height - bezel_margin,
        ]
        draw.rounded_rectangle(
            bezel_area, radius=body_radius - bezel_margin, fill=body_colors["inner"]
        )

        # Screen cutout area (where the screenshot will be)
        screen_margin = self.bezel_thickness
        screen_area = [
            screen_margin,
            screen_margin,
            frame_width - screen_margin,
            frame_height - screen_margin,
        ]
        draw.rounded_rectangle(screen_area, radius=corner_radius, fill=(0, 0, 0))

        # Add Dynamic Island for modern iPhones
        self.add_dynamic_island(draw, frame_width, device_size)

        # Add home indicator for modern iPhones (bottom)
        if device_size != "5.5_inch":  # No home indicator on older phones
            home_indicator = config["home_indicator"]
            indicator_width = home_indicator["width"]
            indicator_height = home_indicator["height"]
            indicator_x = (frame_width - indicator_width) // 2
            indicator_y = frame_height - self.bezel_thickness - indicator_height - 10

            draw.rounded_rectangle(
                [
                    indicator_x,
                    indicator_y,
                    indicator_x + indicator_width,
                    indicator_y + indicator_height,
                ],
                radius=home_indicator["radius"],
                fill=home_indicator["color"],
            )

        return frame

    def get_font(self, size, font_weight="bold"):
        """Try to get a system font, fallback to default"""
        font_paths = [
            # "/System/Library/Fonts/Palatino.ttc",
            "/System/Library/Fonts/SFCompact.ttf",
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "/System/Library/Fonts/Arial.ttf",  # macOS Arial
        ]

        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except:
                continue

        # Fallback to default font
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

    def add_promotional_text(self, image, title_text, subtitle_text=""):
        """Add promotional text above the phone frame"""
        draw = ImageDraw.Draw(image)
        img_width, img_height = image.size

        # Font sizes
        title_font = self.get_font(84, "bold")
        subtitle_font = self.get_font(50)

        # Title text
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        title_x = (img_width - title_width) // 2
        title_y = 150

        font_color = (255, 255, 255)  # White text
        shadow_color = (200, 200, 200)  # Light gray shadow
        # Draw title with shadow
        shadow_offset = 2
        # bit shadow for title
        draw.text(
            (title_x + shadow_offset, title_y + shadow_offset),
            title_text,
            font=title_font,
            fill=shadow_color,
        )
        draw.text((title_x, title_y), title_text, font=title_font, fill=font_color)

        # Subtitle text (if provided)
        if subtitle_text:
            subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (img_width - subtitle_width) // 2
            subtitle_y = title_y + title_height + 20

            # Draw subtitle with shadow
            draw.text(
                (subtitle_x + shadow_offset, subtitle_y + shadow_offset),
                subtitle_text,
                font=subtitle_font,
                fill=shadow_color,
            )
            draw.text(
                (subtitle_x, subtitle_y),
                subtitle_text,
                font=subtitle_font,
                fill=font_color,
            )

    def process_screenshot(
        self,
        screenshot_path,
        output_path,
        title_text,
        subtitle_text="",
        device_size="6.9_inch",
        background_color=None,
        gradient_preset=None,
        gradient_direction="vertical",
    ):
        """Main function to process the screenshot"""

        # Load the screenshot
        try:
            screenshot = Image.open(screenshot_path)
        except Exception as e:
            raise Exception(f"Error loading screenshot: {e}")

        # Convert to RGB if needed
        if screenshot.mode != "RGB":
            screenshot = screenshot.convert("RGB")

        # Get target dimensions
        target_width, target_height = self.app_store_sizes[device_size]

        # Resize screenshot to fit within the frame area
        frame_area_width = target_width - (self.bezel_thickness * 2)
        frame_area_height = (
            target_height - self.text_area_height - (self.bezel_thickness * 2)
        )

        # Calculate scaling to fit screenshot in frame area
        scale_x = frame_area_width / screenshot.width
        scale_y = frame_area_height / screenshot.height
        scale = min(scale_x, scale_y) * 0.90

        new_width = int(screenshot.width * scale)
        new_height = int(screenshot.height * scale)

        screenshot_resized = screenshot.resize(
            (new_width, new_height), Image.Resampling.LANCZOS
        )

        # Apply rounded corners to the screenshot by creating a masked composite
        corner_radius = 40  # Smaller corner radius for screenshots
        screenshot_rounded = self.create_rounded_screenshot(
            screenshot_resized, corner_radius, device_size
        )

        # Create the final image
        final_width = target_width
        final_height = target_height

        # Create background (gradient or solid color)
        if gradient_preset and gradient_preset in self.gradient_presets:
            gradient_colors = self.gradient_presets[gradient_preset]
            final_image = self.create_gradient_background(
                final_width, final_height, gradient_colors, gradient_direction
            )
        else:
            # Use solid background color
            if background_color is None:
                background_color = (25, 25, 35)  # Dark blue-gray
            final_image = Image.new(
                "RGB", (final_width, final_height), background_color
            )

        # Create phone frame
        phone_frame = self.create_phone_frame(
            new_width, new_height, corner_radius, device_size
        )

        # Calculate positions
        phone_x = (final_width - phone_frame.width) // 2
        phone_y = (
            self.text_area_height
            + (target_height - self.text_area_height - phone_frame.height) // 2
        )

        screenshot_x = phone_x + self.bezel_thickness
        screenshot_y = phone_y + self.bezel_thickness

        # Paste the phone frame
        final_image.paste(phone_frame, (phone_x, phone_y))

        # Paste the rounded screenshot
        final_image.paste(screenshot_rounded, (screenshot_x, screenshot_y))

        # Add promotional text
        self.add_promotional_text(final_image, title_text, subtitle_text)

        # Ensure final image is RGB for App Store compliance (no alpha channels)
        if final_image.mode != "RGB":
            final_rgb = Image.new("RGB", final_image.size, (25, 25, 35))
            final_rgb.paste(final_image, (0, 0))
            final_image = final_rgb

        # Save the image
        if output_path.lower().endswith((".jpg", ".jpeg")):
            final_image.save(output_path, "JPEG", quality=95)
        else:
            final_image.save(output_path, "PNG")

        print(f"App Store screenshot saved to: {output_path}")
        print(f"Dimensions: {final_image.size}")


def main():
    # Create generator instance to access presets
    generator = iPhoneFrameGenerator()

    parser = argparse.ArgumentParser(
        description="Generate App Store screenshots with phone frames"
    )
    parser.add_argument(
        "--version", action="version", version=f"iphone-framer {__version__}"
    )
    parser.add_argument("screenshot", help="Path to the iPhone screenshot")
    parser.add_argument(
        "-o",
        "--output",
        help="Output path for the framed screenshot (default: input_filename_appstore.jpg)",
    )
    parser.add_argument("-t", "--title", required=True, help="Main promotional text")
    parser.add_argument("-s", "--subtitle", default="", help="Subtitle text (optional)")
    parser.add_argument(
        "-d",
        "--device",
        choices=["6.9_inch", "6.5_inch", "6.1_inch", "5.5_inch"],
        default="6.9_inch",
        help="Target device size",
    )
    parser.add_argument(
        "--bg-color", help='Background color as RGB tuple, e.g., "25,25,35"'
    )
    parser.add_argument(
        "--gradient",
        choices=list(generator.gradient_presets.keys()),
        help="Use a gradient background preset",
    )
    parser.add_argument(
        "--gradient-direction",
        choices=["vertical", "diagonal"],
        default="vertical",
        help="Gradient direction (default: vertical)",
    )

    args = parser.parse_args()

    # Generate output filename if not provided
    if not args.output:
        screenshot_path = args.screenshot
        name, ext = os.path.splitext(screenshot_path)
        args.output = f"{name}_appstore.jpg"

    # Parse background color if provided
    background_color = None
    if args.bg_color:
        try:
            rgb_values = [int(x.strip()) for x in args.bg_color.split(",")]
            if len(rgb_values) == 3:
                background_color = tuple(rgb_values)
        except:
            print("Warning: Invalid background color format. Using default.")

    # Process screenshot using the already created generator instance
    try:
        generator.process_screenshot(
            screenshot_path=args.screenshot,
            output_path=args.output,
            title_text=args.title,
            subtitle_text=args.subtitle,
            device_size=args.device,
            background_color=background_color,
            gradient_preset=args.gradient,
            gradient_direction=args.gradient_direction,
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

# Example usage:
# python iphone_framer.py screenshot.png -o app_store_screenshot.png -t "Amazing New Feature" -s "Experience the future of mobile apps"
# python iphone_framer.py screenshot.png -o output.png -t "Revolutionary Design" --device 6.9_inch --bg-color "30,30,50"
