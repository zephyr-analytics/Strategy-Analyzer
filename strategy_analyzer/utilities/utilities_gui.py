"""
Utilities module for helper methods of GUI.
"""
import os
import sys

from PIL import Image, ImageOps, ImageDraw


def round_corners(image, radius):
    """
    Rounds the corners of an image with the specified radius.
    
    Parameters:
    - image: PIL.Image object to be rounded.
    - radius: The radius of the corners.

    Returns:
    - Image with rounded corners.
    """
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)
    rounded_image = ImageOps.fit(image, mask.size)
    rounded_image.putalpha(mask)
    return rounded_image


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource.
    
    This method works both when running as a standalone script and when bundled with PyInstaller.

    Args:
        relative_path (str): The relative path to the resource file.

    Returns:
        str: The absolute path to the resource.
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
