from typing import Any, Dict, Union, List
import io
from PIL import Image, ImageDraw

# Import from other modules
from .store import customizables
from .support import is_viz_like, chart_to_png

# Helper Functions
def process_image_for_source_size(img, source_size, user_modifications=None):
    """Resize image to fit within source_size while maintaining aspect ratio and alignment."""
    orig_width, orig_height = img.size
    aspect_ratio = orig_width / orig_height

    # Determine new dimensions to fit within source_size while maintaining aspect ratio
    if source_size["width"] / aspect_ratio <= source_size["height"]:
        fit_width = source_size["width"]
        fit_height = int(fit_width / aspect_ratio)
    else:
        fit_height = source_size["height"]
        fit_width = int(fit_height * aspect_ratio)

    # Resize the image to fit within the source size
    resized_img = img.resize((fit_width, fit_height))

    # Apply scale modification if provided
    scale = user_modifications.get("scale", 1.0) if user_modifications else 1.0
    scaled_width = int(fit_width * scale)
    scaled_height = int(fit_height * scale)

    # Resize the image based on the scale
    scaled_img = resized_img.resize((scaled_width, scaled_height))

    # Create a new canvas for the source size
    source_canvas = Image.new(
        "RGB", (source_size["width"], source_size["height"]), (255, 255, 255)
    )

    # Determine alignment
    alignment = user_modifications.get(
        "alignment",
        source_size.get("alignment", {"horizontal": "center", "vertical": "middle"}),
    )
    dx = user_modifications.get("dx", 0)
    dy = user_modifications.get("dy", 0)

    if alignment["horizontal"] == "left":
        x_pos = 0 + dx
    elif alignment["horizontal"] == "right":
        x_pos = source_size["width"] - scaled_width + dx
    else:  # center
        x_pos = (source_size["width"] - scaled_width) // 2 + dx

    if alignment["vertical"] == "top":
        y_pos = 0 + dy
    elif alignment["vertical"] == "bottom":
        y_pos = source_size["height"] - scaled_height + dy
    else:  # middle
        y_pos = (source_size["height"] - scaled_height) // 2 + dy

    # Paste the scaled image onto the source canvas, clipping if necessary
    source_canvas.paste(scaled_img, (x_pos, y_pos))
    return source_canvas, {
        "scaled_width": scaled_width,
        "scaled_height": scaled_height,
        "x_pos": x_pos,
        "y_pos": y_pos,
    }

def position_image_on_canvas(resized_img, canvas_position, user_modifications):
    """Position the resized image on the canvas using user modifications."""
    # Create a tile canvas
    tile_canvas = Image.new(
        "RGB", (canvas_position["width"], canvas_position["height"]), (255, 255, 255)
    )

    final_img = resized_img.resize(
        (canvas_position["width"], canvas_position["height"])
    )

    tile_canvas.paste(final_img, (0, 0))

    return tile_canvas

# Main Functions
def create_tiled_image(variant):
    """Create a tiled image from a variant."""
    # Create a blank canvas
    canvas_size = variant["canvas_size"]
    canvas = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))

    for texture in variant["textures"]:
        if texture["type"] == "image":
            try:
                # Check if content is a byte stream
                if isinstance(texture["content"], bytes):
                    img = Image.open(io.BytesIO(texture["content"]))
                else:
                    # Assume content is a file path
                    img = Image.open(texture["content"])

                # Ensure the image is loaded
                img.load()
            except Exception as e:
                print(f"Error loading image for texture ID {texture['id']}: {e}")
                continue

            # Process image for source size
            resized_img = process_image_for_source_size(img, texture["source_size"])

            # Apply user modifications and position on canvas
            user_modifications = texture.get("user_modifications", {})
            tile_canvas = position_image_on_canvas(
                resized_img, texture["canvas_position"], user_modifications
            )

            # Calculate position on the main canvas
            x = texture["canvas_position"]["x"]
            y = texture["canvas_position"]["y"]

            # Paste the processed image onto the main canvas
            canvas.paste(tile_canvas, (x, y))

        elif texture["type"] == "color":
            # Create a colored rectangle
            color = texture["content"]
            x = texture["canvas_position"]["x"]
            y = texture["canvas_position"]["y"]
            width = texture["canvas_position"]["width"]
            height = texture["canvas_position"]["height"]
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([x, y, x + width, y + height], fill=color)

    # Flip the image
    canvas = canvas.transpose(Image.FLIP_TOP_BOTTOM)
    # Save or display the image
    output = io.BytesIO()
    canvas.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()

def variant_to_texture(id_variant: str, textures: List[Dict[str, Any]]) -> bytes:
    """Create texture data image using the given variant ID and textures."""
    # Retrieve product configurations from the API
    products_json = customizables(debug=True)
    my_variant = next(
        (v for v in products_json["variants"] if v["id"] == id_variant), None
    )

    if not my_variant:
        raise ValueError(f"Variant with ID {id_variant} not found in variants.")

    # Update the variant's textures with the provided textures
    for texture in textures:
        for variant_texture in my_variant["textures"]:
            if variant_texture["id"] == texture["id"]:
                if variant_texture["type"] == "image" and is_viz_like(
                    texture["content"]
                ):
                    # Convert chart to PNG if content is a chart
                    variant_texture["content"] = chart_to_png(texture["content"])
                else:
                    # Directly assign content for non-chart textures
                    variant_texture["content"] = texture["content"]
                # Update other properties if needed
                variant_texture["user_modifications"] = texture.get(
                    "user_modifications", variant_texture.get("user_modifications", {})
                )

    # Create the tiled image using the updated variant
    texture_data = create_tiled_image(my_variant)
    return texture_data
