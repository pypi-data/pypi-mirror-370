import os
from abc import ABC


class Configurator(ABC):
    """
    The Configurator abstract base class provides an interface for retrieving
    configuration properties (String, int, boolean, long, etc.) from a configurable source.
    It abstracts configuration management by defining methods to fetch property values
    and retrieving implementation details.

    Attributes:
        name (str): The name of the configurator instance.
    """

    def __init__(self, name=None):
        """
        Initializes an AbstractConfigurator instance.

        Args:
            name (str, optional): The name of the configurator instance. Defaults to None.
        """
        self._name = name

    def get(self, prop_name: str) -> str:
        """
        Retrieves a property value by its name. The property is fetched in the following order:
        1. From system properties (environment variables directly matching `prop_name`).
        2. From environment variables (with `.` replaced by `_`).

        Args:
            prop_name (str): The name of the property to retrieve.

        Returns:
            str: The property value if found, otherwise None.
        """
        property_value = os.getenv(prop_name)  # Check system properties (environment variables)
        if property_value is None:
            # Environment variable fallback (replace dots in prop_name with underscores)
            env_name = prop_name.replace('.', '_')
            property_value = os.getenv(env_name)
        return property_value

    def get_int(self, prop_name: str) -> int:
        """
        Retrieves the value of the specified property as an integer.

        Args:
            prop_name (str): The name of the property to retrieve.

        Returns:
            int: The integer value of the property.

        Raises:
            ValueError: If the property cannot be parsed as an integer.
        """
        value = self.get(prop_name)
        if value is None:
            raise ValueError(f"Property '{prop_name}' is missing or invalid.")
        return int(value)

    def get_boolean(self, prop_name: str) -> bool:
        """
        Retrieves the value of the specified property as a boolean.

        Args:
            prop_name (str): The name of the property to retrieve.

        Returns:
            bool: The boolean value of the property (defaults to False if not set or invalid).
        """
        value = self.get(prop_name)
        return bool(value and value.lower() in ["true", "yes", "1"])

    def get_long(self, prop_name: str) -> int:
        """
        Retrieves the value of the specified property as a long integer.

        Args:
            prop_name (str): The name of the property to retrieve.

        Returns:
            int: The long integer value of the property.

        Raises:
            ValueError: If the property cannot be parsed as a long.
        """
        value = self.get(prop_name)
        if value is None:
            raise ValueError(f"Property '{prop_name}' is missing or invalid.")
        return int(value)

    def get_name(self) -> str:
        """
        Retrieves the name of the configurator instance.

        Returns:
            str: The name of the configurator instance.
        """
        return self._name

    def set_name(self, name: str):
        """
        Sets the name of the configurator instance.

        Args:
            name (str): The name to set.
        """
        self._name = name