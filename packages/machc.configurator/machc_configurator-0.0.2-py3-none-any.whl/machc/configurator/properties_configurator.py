import configparser
from typing import Dict, Any

from .file_configurator import AbstractFileConfigurator


class PropertiesConfigurator(AbstractFileConfigurator):
    """
    PropertiesConfigurator is a concrete implementation of AbstractFileConfigurator
    that loads configuration properties from `.properties` files. The class uses
    Python's `configparser` to parse the `.properties` file and populate the configuration map.

    Attributes:
        props (dict): Stores configuration properties loaded from `.properties` files.
    """

    def __init__(self, name: str = None):
        """
        Initializes the PropertiesConfigurator. Optionally loads a properties file.

        Args:
            name (str, optional): The name of the properties file to load. Defaults to None.
        """
        super().__init__(name)

    def load_file(self, props: Dict[str, Any], file_stream):
        """
        Loads properties from the given input stream (representing a `.properties` file)
        and populates the provided dictionary.

        Args:
            props (Dict[str, Any]): The dictionary to store the loaded properties.
            file_stream: The input stream of the `.properties` file to load.

        Raises:
            Exception: If there is an error while reading or parsing the file.
        """
        config = configparser.ConfigParser(delimiters="=")  # Ensure '=' is treated as the key-value separator

        try:
            # Read the `.properties` content from stream
            config.read_file(file_stream)

            # Flatten the parsed properties into the props dictionary
            for section in config.sections():
                for key, value in config.items(section):
                    props[f"{section}.{key}"] = value  # Store as "section.key" for standard property keys

            # Additionally add properties in the default ('[DEFAULT]') section
            for key, value in config.defaults().items():
                props[key] = value

        except Exception as e:
            raise Exception(f"Failed to parse properties file: {str(e)}")
