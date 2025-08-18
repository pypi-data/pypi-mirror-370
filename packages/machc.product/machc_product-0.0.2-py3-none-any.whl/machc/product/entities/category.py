from machc.base import EntityId


class CategoryId(EntityId):
    """
    The CategoryId class extends EntityId to uniquely identify category entities
    within the MachC project. It provides the foundational identification functionality
    for categories, utilizing UUID or key-based identification methods.

    This class adheres to Clean Architecture principles to ensure modularity, reusability,
    and separation of concerns.
    """

    def __init__(self, id=None, key=None):
        """
        Constructs a CategoryId instance using either a UUID or a string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        super().__init__(id=id, key=key)