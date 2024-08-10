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
    # Create a mask for the rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)

    # Apply the rounded mask to the image
    rounded_image = ImageOps.fit(image, mask.size)
    rounded_image.putalpha(mask)
    return rounded_image
