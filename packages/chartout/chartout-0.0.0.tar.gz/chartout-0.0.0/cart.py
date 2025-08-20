from dataclasses import dataclass, asdict
from typing import Optional, List
from .models import CartItem
from .support import viz_to_cart_item, VizLike


@dataclass
class Cart:
    """A class to represent a shopping cart containing CartItems.

    Attributes:
        items (List[CartItem]): A list of items in the cart, which can be
        CartItem instances.
    """

    items: List[CartItem]

    def __init__(self, items: Optional[List[CartItem]] = None):
        """Initialize the Cart with an optional list of items.

        Args:
            items (Optional[List[CartItem]]): A list of dictionaries conforming to
            CartItem to initialize the cart with.
        """
        self.items: List[CartItem] = []
        if items is not None:
            self.add(items)

    def add(self, item: CartItem | List[CartItem] | VizLike) -> None:
        """Add a CartItem, a list of CartItems, or a VizLike to the cart.

        Args:
            item (CartItem | List[CartItem] | VizLike): A CartItem, a list of CartItems, or a VizLike to be added to the cart.

        Raises:
            ValueError: If an item in the list is not a valid CartItem or VizLike.
        """
        if isinstance(item, VizLike):
            # Convert VizLike to CartItem
            item = viz_to_cart_item(item)
            self.items.append(item)
        elif isinstance(item, list):
            for i in item:
                if isinstance(i, dict):
                    i = CartItem(**i)
                self.items.append(i)
        else:
            if isinstance(item, dict):
                item = CartItem(**item)
            self.items.append(item)

    def remove(self, *, index: int) -> None:
        """Remove a CartItem from the cart by its index.

        Args:
            index (int): The index of the item to be removed from the cart.

        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index >= len(self.items):
            raise IndexError("Index out of range.")
        del self.items[index]

    def __repr__(self) -> str:
        """Return a string representation of the Cart.

        Returns:
            str: A string representation of the Cart, including item IDs, names, quantities, and texture information.
        """
        if not self.items:
            return "Cart(empty)"
        
        items_repr = "\n".join(
            f"  - ID: {item.id}\n"
            f"    Name: {item.name or 'Unnamed'}\n"
            f"    Quantity: {item.quantity}\n"
            f"    Textures: [{', '.join(texture.id for texture in item.textures)}]"
            for item in self.items
        )
        return f"Cart:\n{items_repr}"

    def to_dict(self):
        return asdict(self)
