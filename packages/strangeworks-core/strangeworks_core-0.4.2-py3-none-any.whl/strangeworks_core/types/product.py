"""product.py."""
from typing import Dict, Optional

from pydantic import AliasChoices, BaseModel, Field


class Product(BaseModel):
    """Represents a Platform Product object.

    Parameters
    ----------
    slug: str
        User-friendly identifier.
    product_id: Optional[str]
        Internal identifier.
    name: Optional[str]
        Product name.
    """

    slug: str
    product_id: Optional[str] = Field(
        default=None, alias=AliasChoices("id", "product_id")
    )
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "Product":
        """Create a Product object from Dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Product.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        d : Dict[str, Any]
            Product represented as a dictionary.
        """
        return cls(**d)
