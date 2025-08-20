from __future__ import annotations
import sys
import io
from typing import TYPE_CHECKING, Any, TypeVar, Optional, Dict
import uuid
import hashlib
import os
import time

# Conditional imports for type checking
if TYPE_CHECKING:
    if sys.version_info >= (3, 10):
        from typing import TypeGuard
    else:
        from typing_extensions import TypeGuard
    import altair as alt

# Import models
from .models import ActiveItem, Texture, InitViz, CartItem

# Define a new type variable for VizLike
VizLike = TypeVar("VizLike", bound=Any)


# Helper Functions
def get_altair() -> Any:
    """Get altair module (if already imported - else return None)."""
    return sys.modules.get("altair", None)


def is_altair_chart(chart: Any) -> TypeGuard[alt.typing.ChartType]:
    """Check whether `chart` is an Altair Chart without importing altair."""
    return (alt := get_altair()) is not None and alt.typing.is_chart_type(chart)


def chart_to_png(chart: Any) -> bytes:
    """Convert an Altair chart to PNG byte data."""
    if is_altair_chart(chart):
        byte_stream = io.BytesIO()
        chart.save(byte_stream, format="png", scale_factor=2, ppi=300)
        byte_stream.seek(0)
        return byte_stream.getvalue()
    else:
        msg = f"The provided DataViz object is not supported. Got: {type(chart)}"
        raise TypeError(msg)


# Main Functions
def is_viz_like(viz: VizLike) -> TypeGuard[VizLike]:
    """Check whether `viz` is a valid Altair chart."""
    return is_altair_chart(viz)


def viz_to_active_item(init_viz: InitViz) -> ActiveItem:
    """Convert an InitViz item to an ActiveItem."""
    # Assuming the first image in the InitViz is used for the ActiveItem
    first_image_index = next(iter(init_viz.images))
    png_data = init_viz.images[first_image_index]

    return ActiveItem(
        name="Canvas",
        id="canvas_10x10",
        textures=[
            Texture(
                id="canvas_10x10_texture",
                content=png_data
            )
        ]
    )


def viz_to_init_viz(viz: VizLike) -> InitViz:
    """Convert a VizLike item to an InitViz."""
    images = {0: chart_to_png(viz)}
    return InitViz(images=images)


def cart_item_to_active_item(cart_item: Dict[str, Any]) -> ActiveItem:
    """Convert a CartItem to an ActiveItem."""
    return ActiveItem(
        id=cart_item['id'],
        name=cart_item.get('name'),
        textures=cart_item['textures']
    )


def viz_to_cart_item(viz: VizLike) -> CartItem:
    """Convert a VizLike item to a CartItem."""
    # Convert the VizLike object to PNG bytes
    png_data = chart_to_png(viz)
    
    # Create a Texture instance for the CartItem
    texture = Texture(
        id="my_canvas_texture", 
        content=png_data
    )
    
    # Create and return a CartItem instance
    return CartItem(
        id="my_canvas_id", 
        name="VizLike Item",
        textures=[texture],
        quantity=1
    )


def generate_external_id() -> str:
    """Generate a unique external ID for order creation."""
    # Generate a UUID
    unique_id = uuid.uuid4().hex

    # Get machine-specific information (e.g., hostname)
    machine_info = os.uname().nodename

    # Hash the machine information to keep it consistent and anonymized
    machine_hash = hashlib.sha256(machine_info.encode()).hexdigest()

    # Get the current timestamp
    timestamp = int(time.time())

    # Combine all parts to form the external_id
    external_id = f"{unique_id}-{machine_hash[:8]}-{timestamp}"

    return external_id