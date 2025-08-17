#!/usr/bin/env python3
"""
Analyze frame.png to determine dimensions and corner radius
"""

from PIL import Image
import os


def analyze_frame_image():
    """Analyze the frame.png image to determine corner radius and screen area"""
    frame_path = "frame.png"

    if not os.path.exists(frame_path):
        print(f"Frame image not found at {frame_path}")
        return

    # Load the frame image
    frame = Image.open(frame_path).convert("RGBA")
    width, height = frame.size

    print(f"Frame dimensions: {width} x {height}")

    # Analyze the corner to find the radius
    # Look at the top-left corner and find where the curve starts
    corner_radius = find_corner_radius(frame)
    print(f"Estimated corner radius: {corner_radius} pixels")

    # Find the screen area (the transparent/black area inside the frame)
    screen_bounds = find_screen_area(frame)
    if screen_bounds:
        screen_x, screen_y, screen_w, screen_h = screen_bounds
        print(f"Screen area: {screen_w} x {screen_h} at ({screen_x}, {screen_y})")
        print(f"Screen corner radius (estimated): {corner_radius - 20} pixels")

    return {
        "frame_width": width,
        "frame_height": height,
        "corner_radius": corner_radius,
        "screen_bounds": screen_bounds,
    }


def find_corner_radius(frame):
    """Estimate corner radius by analyzing the top-left corner"""
    width, height = frame.size

    # Convert to grayscale to analyze opacity/transparency
    grayscale = frame.convert("L")

    # Look at the top-left corner
    # Find the point where the corner curve intersects with a 45-degree line
    max_radius = min(width, height) // 4  # reasonable upper bound

    for r in range(1, max_radius):
        # Check point at (r, 0) - should be transparent/black if within corner radius
        # Check point at (0, r) - should be transparent/black if within corner radius
        # Check point at (r, r) - should be opaque/frame if outside corner radius

        try:
            # Get the alpha channel
            alpha_channel = frame.split()[3]  # RGBA alpha channel

            # Check if the corner at distance r is still part of the transparent area
            if r < width and r < height:
                alpha_at_corner = alpha_channel.getpixel((r, r))
                alpha_at_edge_x = alpha_channel.getpixel((r, 0)) if r < width else 0
                alpha_at_edge_y = alpha_channel.getpixel((0, r)) if r < height else 0

                # If we find a point where the corner is opaque but edges are transparent,
                # that's approximately our corner radius
                if alpha_at_corner > 128 and (
                    alpha_at_edge_x < 128 or alpha_at_edge_y < 128
                ):
                    return r

        except IndexError:
            break

    # Fallback: analyze by looking for the curve visually
    # This is a more sophisticated approach
    return estimate_radius_by_curve_analysis(frame)


def estimate_radius_by_curve_analysis(frame):
    """Estimate radius by analyzing the actual curve shape"""
    alpha_channel = frame.split()[3]
    width, height = frame.size

    # Look at the top-left corner and find where transparency ends
    for y in range(min(200, height)):  # Check first 200 pixels
        for x in range(min(200, width)):
            alpha = alpha_channel.getpixel((x, y))
            if alpha > 128:  # Found opaque pixel
                # This gives us a rough idea of the corner radius
                distance_from_corner = (x**2 + y**2) ** 0.5
                if distance_from_corner > 10:  # Ignore very small distances
                    return int(distance_from_corner * 0.7)  # Approximate factor

    return 50  # Default fallback


def find_screen_area(frame):
    """Find the screen area (transparent/dark area) within the frame"""
    alpha_channel = frame.split()[3]
    width, height = frame.size

    # Find bounds of the transparent area (screen)
    min_x, min_y = width, height
    max_x, max_y = 0, 0

    found_transparent = False

    for y in range(height):
        for x in range(width):
            alpha = alpha_channel.getpixel((x, y))
            if alpha < 128:  # Transparent or semi-transparent
                found_transparent = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if found_transparent:
        screen_width = max_x - min_x + 1
        screen_height = max_y - min_y + 1
        return (min_x, min_y, screen_width, screen_height)

    return None


if __name__ == "__main__":
    result = analyze_frame_image()

    if result:
        print("\n=== Analysis Results ===")
        print(f"Frame: {result['frame_width']} x {result['frame_height']}")
        print(f"Corner radius: {result['corner_radius']} pixels")
        if result["screen_bounds"]:
            x, y, w, h = result["screen_bounds"]
            print(f"Screen area: {w} x {h} at offset ({x}, {y})")
            print(
                f"Recommended screenshot corner radius: {max(25, result['corner_radius'] - 15)} pixels"
            )
