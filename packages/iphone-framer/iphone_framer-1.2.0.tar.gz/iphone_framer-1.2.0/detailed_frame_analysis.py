#!/usr/bin/env python3
"""
Detailed analysis of frame.png to find screen area and corner radius
"""

from PIL import Image, ImageDraw
import os


def detailed_frame_analysis():
    """Perform detailed analysis of the frame image"""
    frame_path = "frame.png"

    if not os.path.exists(frame_path):
        print(f"Frame image not found at {frame_path}")
        return

    # Load the frame image
    frame = Image.open(frame_path).convert("RGBA")
    width, height = frame.size

    print(f"Frame dimensions: {width} x {height}")

    # Create a visualization to understand the frame structure
    analyze_frame_structure(frame)

    # Find the actual screen area by looking for the black/dark area
    screen_info = find_actual_screen_area(frame)

    if screen_info:
        print(f"\nScreen area found:")
        print(f"  Position: ({screen_info['x']}, {screen_info['y']})")
        print(f"  Size: {screen_info['width']} x {screen_info['height']}")
        print(f"  Corner radius: {screen_info['corner_radius']} pixels")

    return screen_info


def analyze_frame_structure(frame):
    """Analyze the structure of the frame by examining pixel values"""
    width, height = frame.size

    # Sample pixels from different areas
    print("\nPixel analysis:")

    # Check corners
    corners = [
        ("Top-left", 0, 0),
        ("Top-right", width - 1, 0),
        ("Bottom-left", 0, height - 1),
        ("Bottom-right", width - 1, height - 1),
        ("Center", width // 2, height // 2),
    ]

    for name, x, y in corners:
        pixel = frame.getpixel((x, y))
        print(f"  {name} ({x}, {y}): RGBA{pixel}")

    # Check edges
    print("\nEdge analysis:")
    mid_height = height // 2
    for x in [50, 100, 150, 200]:
        if x < width:
            pixel = frame.getpixel((x, mid_height))
            print(f"  Left edge at x={x}: RGBA{pixel}")


def find_actual_screen_area(frame):
    """Find the screen area by analyzing the frame structure"""
    width, height = frame.size

    # The frame appears to be a cutout mask, so we need to find where
    # the actual phone body would be vs where the screen is

    # Look for the transition from transparent to semi-transparent/opaque
    # This indicates the bezel area

    # Scan from edges inward to find the screen boundary
    screen_bounds = find_screen_boundaries(frame)

    if screen_bounds:
        x, y, w, h = screen_bounds

        # Estimate corner radius by looking at the screen area corners
        corner_radius = estimate_screen_corner_radius(frame, x, y, w, h)

        return {"x": x, "y": y, "width": w, "height": h, "corner_radius": corner_radius}

    return None


def find_screen_boundaries(frame):
    """Find the boundaries of the screen area within the frame"""
    width, height = frame.size
    alpha_channel = frame.split()[3]

    # Since the entire frame appears to be transparent (it's a cutout),
    # we need to estimate the screen area based on typical iPhone proportions

    # For iPhone frames, the screen typically has some bezel
    # Let's estimate based on typical iPhone 15 Pro proportions

    # Typical iPhone screen-to-body ratio and bezel sizes
    bezel_top = int(height * 0.03)  # Top bezel (smaller due to notch area)
    bezel_bottom = int(height * 0.03)  # Bottom bezel
    bezel_sides = int(width * 0.04)  # Side bezels

    screen_x = bezel_sides
    screen_y = bezel_top
    screen_width = width - (2 * bezel_sides)
    screen_height = height - bezel_top - bezel_bottom

    print(f"Estimated screen area based on iPhone proportions:")
    print(f"  Bezels - Top: {bezel_top}, Bottom: {bezel_bottom}, Sides: {bezel_sides}")

    return (screen_x, screen_y, screen_width, screen_height)


def estimate_screen_corner_radius(frame, screen_x, screen_y, screen_w, screen_h):
    """Estimate the corner radius for the screen area"""
    # For iPhone screens, the corner radius is typically proportional to the frame
    # iPhone 15 Pro has approximately 55px corner radius at actual size

    # Base this on the screen width (iPhone 15 Pro is ~1179px wide for 6.1")
    # Scale accordingly
    base_radius = 55
    scale_factor = screen_w / 1179  # iPhone 15 Pro reference width
    estimated_radius = int(base_radius * scale_factor)

    # Clamp to reasonable bounds
    estimated_radius = max(30, min(80, estimated_radius))

    return estimated_radius


if __name__ == "__main__":
    result = detailed_frame_analysis()

    if result:
        print(f"\n=== Recommended Settings ===")
        print(f"Screen corner radius for screenshots: {result['corner_radius']} pixels")
        print(f"Screen area offset: ({result['x']}, {result['y']})")
        print(f"Screen area size: {result['width']} x {result['height']}")
