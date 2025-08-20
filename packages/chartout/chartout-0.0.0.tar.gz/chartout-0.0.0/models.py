from dataclasses import dataclass, field, asdict
from typing import List, Union, Optional, Dict, Any

# Data Classes
@dataclass
class Texture:
    id: str
    content: Union[str, Any]  # 'Any' can be used for alt.Chart or other types

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Texture instance to a dictionary."""
        return asdict(self)

@dataclass
class StoreItem:
    id: str
    name: Optional[str] = None
    textures: List[Texture] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the StoreItem instance to a dictionary."""
        return asdict(self)

@dataclass
class CartItem(StoreItem):
    quantity: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert the CartItem instance to a dictionary."""
        return asdict(self)

@dataclass
class ActiveItem(StoreItem):
    textures: List[Texture] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ActiveItem instance to a dictionary."""
        return asdict(self)

@dataclass
class ActiveTexture:
    texture: bytes  # Equivalent to Uint8Array in TypeScript

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ActiveTexture instance to a dictionary."""
        return asdict(self)

@dataclass
class InitViz:
    images: Dict[int, bytes] = field(default_factory=dict)

    def to_dict(self) -> Dict[int, bytes]:
        """Convert the InitViz instance to a dictionary."""
        return self.images
