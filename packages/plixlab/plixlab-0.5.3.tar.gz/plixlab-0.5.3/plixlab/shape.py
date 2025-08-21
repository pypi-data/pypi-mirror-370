"""
PlixLab Shape Generation Module

This module provides functionality for generating various geometric shapes
as PNG images using Cairo graphics library. Shapes can be customized with
color, orientation, and size parameters for use in PlixLab presentations.
"""

import cairo
from io import BytesIO
import numpy as np
from typing import Any


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')

    Returns:
        RGB color tuple (e.g., (255, 0, 0))

    Example:
        >>> hex_to_rgb('#FF0000')
        (255, 0, 0)
    """
    hex_color = hex_color.lstrip("#")
    rgb_tuple = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    # Ensure we return exactly 3 integers
    return (rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])


def arrow(
    context: cairo.Context, scale: float, a: float, b: float, c: float, d: float
) -> None:
    """
    Draw an arrow shape on the Cairo context.

    Args:
        context (cairo.Context): Cairo graphics context to draw on
        scale (float): Scaling factor for the shape
        a (float): Length of the arrow body
        b (float): Height of the arrow head
        c (float): Width of the arrow body
        d (float): Width of the arrow head
    """
    # Scale all parameters
    a *= scale
    b *= scale
    c *= scale
    d *= scale

    # Draw arrow shape
    context.move_to(0, c / 2)
    context.line_to(0, c / 2 + b)
    context.line_to(d, 0)
    context.line_to(0, -c / 2 - b)
    context.line_to(0, -c / 2)
    context.line_to(-a, -c / 2)
    context.line_to(-a, c / 2)
    context.line_to(0, c / 2)
    context.close_path()
    context.stroke()


def square(context: cairo.Context, scale: float, a: float, b: float) -> None:
    """
    Draw a rectangular shape on the Cairo context.

    Args:
        context (cairo.Context): Cairo graphics context to draw on
        scale (float): Scaling factor for the shape
        a (float): Width of the rectangle
        b (float): Height of the rectangle (as a fraction of width)
    """
    # Scale all parameters
    a *= scale*0.7
    b *= scale*0.7

    # Draw rectangular shape
    context.move_to(-a / 2, a / 2 - b)
    context.line_to(a / 2, a / 2 - b)
    context.line_to(a / 2, a / 2)
    context.line_to(-a / 2, a / 2)
    context.line_to(-a / 2, a / 2 - b)
    context.close_path()
    context.stroke()


def run(shape_id: str,color, orientation, aspect_ratio) -> bytes:
    """
    Generate a geometric shape as a PNG image.

    Creates vector graphics shapes using Cairo and returns them as PNG bytes
    suitable for embedding in web presentations.

    Args:
        shape_id (str): Identifier for the shape type ('arrow' or 'square')
        color (tuple[float, float, float]): RGB color tuple (0-1 range)
        orientation (float): Rotation angle in degrees.
        aspect_ratio (float): For 'square' shapes, height/width ratio.
          
    Returns:
        bytes: PNG image data as bytes

    """
    scale = 300
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, scale, scale)
    context = cairo.Context(surface)

    # Center the coordinate system
    context.translate(scale / 2, scale / 2)
    context.set_line_width(0.01 * scale)

    # Handle color parameter
    if isinstance(color, str) and color.startswith("#"):
        # Convert hex color to RGB (0-1 range)
        color = np.array(hex_to_rgb(color)) / 255

   
    print(color)
    context.set_source_rgb(*color)

    # Save the current context state before rotation
    context.save()

    # Apply rotation
    orientation_rad = orientation * np.pi / 180
    context.rotate(-orientation_rad)

    # Generate the requested shape
    if shape_id == "arrow":
        arrow(context, scale, 0.5, 0.15, 0.25, 0.2)
    elif shape_id == "square":
        square(context, scale, 1, aspect_ratio)
    else:
        raise ValueError(f"No shape recognized: {shape_id}")

    # Restore context state
    context.restore()

    # Convert surface to PNG bytes
    buf = BytesIO()
    surface.write_to_png(buf)
    buf.seek(0)
    png_data = buf.getvalue()
    buf.close()

    return png_data
