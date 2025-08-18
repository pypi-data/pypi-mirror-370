from typing import Optional, List, TypeVar, Generic

from machc.base import EntityId
from .category import CategoryId
from .variant import AbstractVariant


class ProductId(EntityId):
    """
    The ProductId class extends EntityId to uniquely identify product entities
    within the MachC project. It leverages the shared identification logic provided
    by the EntityId class and aligns with the principles of modularity and Clean Architecture.
    """

    def __init__(self, id=None, key=None):
        """
        Constructs a ProductId instance using either a UUID or a string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        super().__init__(id=id, key=key)

# Generic type for variants
V = TypeVar("V", bound=AbstractVariant)

class AbstractProduct(ProductId, Generic[V]):
    """
    The AbstractProduct class represents a generic product entity with associated properties like
    key, name, description, brand, variants, categories, and other attributes.

    This class extends ProductId for unique product identification and uses generics to support
    different types of variants.
    """

    def __init__(
        self,
        key: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
        image: Optional[str] = None,
        brand: Optional[str] = None,
        variants: Optional[List[V]] = None,
        categories: Optional[List[CategoryId]] = None,
    ):
        """
        Initializes an AbstractProduct instance.

        Args:
            key (Optional[str]): A unique key for the product.
            name (Optional[str]): The name of the product.
            description (Optional[str]): The description of the product.
            slug (Optional[str]): A slug for use in URLs.
            image (Optional[str]): A reference to the product's primary image.
            brand (Optional[str]): The brand of the product.
            variants (Optional[List[V]]): A list of product variants.
            categories (Optional[List[CategoryId]]): A list of category IDs associated with the product.
        """
        super().__init__()
        self._key = key
        self._name = name
        self._description = description
        self._slug = slug
        self._image = image
        self._brand = brand
        self._variants = variants or []
        self._categories = categories or []

    # Key
    @property
    def key(self) -> Optional[str]:
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    # Name
    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    # Description
    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    # Slug
    @property
    def slug(self) -> Optional[str]:
        return self._slug

    @slug.setter
    def slug(self, value: str):
        self._slug = value

    # Image
    @property
    def image(self) -> Optional[str]:
        return self._image

    @image.setter
    def image(self, value: str):
        self._image = value

    # Brand
    @property
    def brand(self) -> Optional[str]:
        return self._brand

    @brand.setter
    def brand(self, value: str):
        self._brand = value

    # Variants
    @property
    def variants(self) -> List[V]:
        return self._variants

    @variants.setter
    def variants(self, value: List[V]):
        self._variants = value

    # Categories
    @property
    def categories(self) -> List[CategoryId]:
        return self._categories

    @categories.setter
    def categories(self, value: List[CategoryId]):
        self._categories = value