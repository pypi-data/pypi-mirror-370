from typing import Optional

from ..identifier.entity import EntityId

class AddressId(EntityId):
    """
    The AddressId class extends EntityId to uniquely identify address entities
    within the platform. It serves as the foundational identifier for the Address class,
    ensuring consistency and reliability in managing address-related records across the
    Machc project.

    This class inherits the flexibility of EntityId, enabling identification through either
    a UUID or a string-based key, and aligns with Clean Architecture principles to ensure
    modularity and separation of concerns.
    """

    def __init__(self, id=None, key=None):
        """
        Constructs an AddressId instance using either a UUID or a string-based key.

        Args:
            id (uuid.UUID, optional): The UUID to assign as the unique identifier.
            key (str, optional): The string-based key for custom identification.
        """
        super().__init__(id=id, key=key)

class Address(AddressId):
    """
    The Address class represents a detailed contact address entity and extends AddressId
    to provide unique identification for address instances.

    It includes additional address-related fields like recipient names, phone numbers,
    street addresses, city, postal code, country, and more.

    This class is typically used as part of the machc_core entities module and is
    designed for structured and reusable address management in various scenarios.
    """

    def __init__(
        self,
        address_name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        address1: Optional[str] = None,
        address2: Optional[str] = None,
        city: Optional[str] = None,
        postal_code: Optional[str] = None,
        state_address: Optional[str] = None,
        country: Optional[str] = None,
    ):
        """
        Initializes an Address instance with optional attributes for detailed address information.

        Args:
            address_name (Optional[str]): A custom name for the address (e.g., "Home").
            first_name (Optional[str]): The first name of the person associated with the address.
            last_name (Optional[str]): The last name of the person associated with the address.
            phone_number (Optional[str]): The phone number associated with the address.
            address1 (Optional[str]): The primary street address.
            address2 (Optional[str]): The secondary street address (e.g., apartment or suite).
            city (Optional[str]): The city associated with the address.
            postal_code (Optional[str]): The postal or ZIP code of the address.
            state_address (Optional[str]): The state or region of the address.
            country (Optional[str]): The country of the address.
        """
        super().__init__()
        self._address_name = address_name
        self._first_name = first_name
        self._last_name = last_name
        self._phone_number = phone_number
        self._address1 = address1
        self._address2 = address2
        self._city = city
        self._postal_code = postal_code
        self._state_address = state_address
        self._country = country

    # Getters and Setters
    def get_address_name(self) -> Optional[str]:
        return self._address_name

    def set_address_name(self, address_name: str):
        self._address_name = address_name

    def get_first_name(self) -> Optional[str]:
        return self._first_name

    def set_first_name(self, first_name: str):
        self._first_name = first_name

    def get_last_name(self) -> Optional[str]:
        return self._last_name

    def set_last_name(self, last_name: str):
        self._last_name = last_name

    def get_phone_number(self) -> Optional[str]:
        return self._phone_number

    def set_phone_number(self, phone_number: str):
        self._phone_number = phone_number

    def get_address1(self) -> Optional[str]:
        return self._address1

    def set_address1(self, address1: str):
        self._address1 = address1

    def get_address2(self) -> Optional[str]:
        return self._address2

    def set_address2(self, address2: str):
        self._address2 = address2

    def get_city(self) -> Optional[str]:
        return self._city

    def set_city(self, city: str):
        self._city = city

    def get_postal_code(self) -> Optional[str]:
        return self._postal_code

    def set_postal_code(self, postal_code: str):
        self._postal_code = postal_code

    def get_state_address(self) -> Optional[str]:
        return self._state_address

    def set_state_address(self, state_address: str):
        self._state_address = state_address

    def get_country(self) -> Optional[str]:
        return self._country

    def set_country(self, country: str):
        self._country = country