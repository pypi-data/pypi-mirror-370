from typing import Dict, Any, Optional

from machc.base import DynamicEntity
from .abs_product import AbstractVariant, AbstractProduct


class DynamicVariant(AbstractVariant, DynamicEntity):
    """
    The DynamicVariant class extends AbstractVariant and implements the DynamicEntity interface.
    It represents a flexible variant structure with dynamic attributes, allowing additional
    key-value pairs to be stored beyond the standard variant attributes.

    This class adheres to Clean Architecture principles by maintaining modularity and extensibility.
    """

    def __init__(
        self,
        id=None,
        key: Optional[str] = None,
        sku: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes a DynamicVariant instance.

        Args:
            id (uuid.UUID, optional): A unique identifier for the variant.
            key (Optional[str]): A unique key to identify the variant.
            sku (Optional[str]): Stock Keeping Unit (SKU) for the variant.
            display_name (Optional[str]): Display name for the variant.
            description (Optional[str]): Description of the variant.
            image_url (Optional[str]): URL of the variant's image.
            attributes (Optional[Dict[str, Any]]): A dictionary of dynamic key-value attributes.
        """
        super().__init__(id=id, key=key, sku=sku, display_name=display_name, description=description, image_url=image_url)
        self._attributes = attributes or {}

    # Attributes
    @property
    def attributes(self) -> Dict[str, Any]:
        return self._attributes

    @attributes.setter
    def attributes(self, value: Dict[str, Any]):
        self._attributes = value

class DynamicProduct(AbstractProduct[DynamicVariant], DynamicEntity):
    """
    The DynamicProduct class extends AbstractProduct and implements the DynamicEntity interface.
    It represents a flexible product structure with a dynamic set of attributes in addition to
    the base product properties.

    This class adheres to Clean Architecture principles by maintaining modularity and enabling
    dynamic product management.
    """

    def __init__(
        self,
        product_type: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        key: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        image: Optional[str] = None,
        brand: Optional[str] = None,
        variants: Optional[list] = None,
        categories: Optional[list] = None,
    ):
        """
        Initializes a DynamicProduct instance.

        Args:
            product_type (Optional[str]): The type of the product, representing its classification.
            attributes (Optional[Dict[str, Any]]): Dynamic attributes for the product as key-value pairs.
            key (Optional[str]): A unique identifier for the product.
            name (Optional[str]): Name of the product.
            description (Optional[str]): Description of the product.
            slug (Optional[str]): URL-friendly identifier for the product.
            image (Optional[str]): URL to the product's primary image.
            brand (Optional[str]): Brand name of the product.
            variants (Optional[list]): List of product variants (DynamicVariant objects).
            categories (Optional[list]): List of product categories.
        """
        super().__init__(
            key=key,
            name=name,
            description=description,
            slug=slug,
            image=image,
            brand=brand,
            variants=variants,
            categories=categories,
        )
        self._product_type = product_type
        self._attributes = attributes or {}

    # Product Type
    @property
    def product_type(self) -> Optional[str]:
        return self._product_type

    @product_type.setter
    def product_type(self, value: str):
        self._product_type = value

    # Attributes
    @property
    def attributes(self) -> Dict[str, Any]:
        return self._attributes

    @attributes.setter
    def attributes(self, value: Dict[str, Any]):
        self._attributes = value