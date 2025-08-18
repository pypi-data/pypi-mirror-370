import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any


class IdentifiedObject(ABC):
    """
    The IdentifiedObject interface defines methods for objects that require unique identification
    within the platform. Classes implementing this interface must provide methods for retrieving 
    and assigning identifiers.
    """

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_key(self):
        pass


class EntityId(IdentifiedObject):
    """
    The EntityId class provides unique identification for entities in the platform, adhering to Clean Architecture principles.
    
    It supports identification using either a UUID or a string-based key, ensuring flexibility for diverse use cases. 
    This implementation is designed to be serializable and forms the foundational component for entity identification 
    within the Machanism Core Entities Module.
    
    Key Features:
    - Supports UUID or string-based key for identification.
    - Implements IdentifiedObject interface to standardize entity identification.
    - Designed for easy serialization and persistence.
    """
    
    def __init__(self, id=None, key=None):
        """
        Constructs an EntityId using either a UUID or a custom string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        self._id = id
        self._key = key

    def get_id(self):
        """
        Retrieves the UUID for this EntityId.

        Returns:
            uuid.UUID: The UUID assigned as the unique identifier, or None if not set.
        """
        return self._id

    def set_id(self, id):
        """
        Sets the UUID for this EntityId.

        Args:
            id (uuid.UUID): The UUID to assign as the unique identifier.
        """
        self._id = id

    def get_key(self):
        """
        Retrieves the custom string-based key for this EntityId.

        Returns:
            str: The string key assigned as the identifier, or None if not set.
        """
        return self._key

    def set_key(self, key):
        """
        Sets the custom string-based key for this EntityId.

        Args:
            key (str): The string key to assign as the identifier.
        """
        self._key = key


class DynamicEntity(IdentifiedObject, ABC):
    """
    The DynamicEntity abstract class represents a dynamic, attribute-driven platform entity
    that is uniquely identifiable. It extends the IdentifiedObject interface to provide unique
    identification capabilities, while also supporting runtime-configurable key-value pairs
    (attributes).

    This class acts as a versatile extension, complementing predefined static data entities by
    enabling the addition of flexible attributes on an as-needed basis. It is not meant to replace
    core static properties, but rather to augment them for secondary use cases.

    Attributes:
        None (Attributes are implemented in concrete subclasses)
    """

    @abstractmethod
    def get_attributes(self) -> Dict[str, Any]:
        """
        Retrieves the dynamic attributes of the entity. Attributes are stored as key-value
        pairs in a dictionary, where the key is a string representing the attribute name,
        and the value is a corresponding object.

        Returns:
            Dict[str, Any]: A dictionary containing the entity's custom attributes.
        """
        pass

    @abstractmethod
    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        """
        Sets the dynamic attributes for the entity. Attributes are added as key-value
        pairs in the form of a dictionary.

        Args:
            attributes (Dict[str, Any]): A dictionary of key-value pairs to set as attributes.
        """
        pass