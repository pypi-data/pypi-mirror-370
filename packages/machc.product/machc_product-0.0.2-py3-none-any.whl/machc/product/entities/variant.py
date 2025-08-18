from machc.base import EntityId


class VariantId(EntityId):
    """
    The VariantId class extends EntityId to uniquely identify variant entities
    within the MachC project. It leverages the shared UUID-based or key-based
    identification functionality provided by the EntityId class.

    This class ensures consistency and modularity, adhering to Clean Architecture
    principles for scalable and maintainable system design.
    """

    def __init__(self, id=None, key=None):
        """
        Constructs a VariantId instance using either a UUID or a string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        super().__init__(id=id, key=key)


class AbstractVariant(VariantId):
    """
    The AbstractVariant class extends VariantId to represent a product variant
    with additional attributes like SKU, key, display name, description, and image URL.

    This class adheres to Clean Architecture principles, ensuring modularity and
    reusability within the MachC ecosystem.
    """

    def __init__(
        self,
        id=None,
        key=None,
        sku=None,
        display_name=None,
        description=None,
        image_url=None
    ):
        """
        Initializes an AbstractVariant instance with optional attributes.

        Args:
            id (uuid.UUID, optional): The UUID for the variant.
            key (str, optional): A unique key to identify the variant.
            sku (str, optional): Stock Keeping Unit (SKU) for the variant.
            display_name (str, optional): Display name for the variant.
            description (str, optional): Description of the variant.
            image_url (str, optional): URL of the variant's image.
        """
        super().__init__(id=id, key=key)
        self._sku = sku
        self._key = key
        self._display_name = display_name
        self._description = description
        self._image_url = image_url

    # SKU
    @property
    def sku(self):
        return self._sku

    @sku.setter
    def sku(self, value):
        self._sku = value

    # Key
    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    # Display Name
    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    # Description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    # Image URL
    @property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        self._image_url = value