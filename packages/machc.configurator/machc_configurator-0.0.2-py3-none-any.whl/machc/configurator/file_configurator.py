from abc import abstractmethod

from machc.configurator import Configurator


class AbstractFileConfigurator(Configurator):
    """
    AbstractFileConfigurator provides functionality to load configuration properties
    from external file resources. It extends the base configurator functionality and
    uses a dictionary to store key-value pairs of loaded configurations. Subclasses
    must define the specific logic for parsing and loading the configuration files.

    Attributes:
        props (dict): Stores configuration properties loaded from external files.
        name (str): Name of the configurator instance.
    """

    def __init__(self, name=None):
        """
        Initializes the AbstractFileConfigurator instance. Optionally loads configuration
        properties from the specified file.

        Args:
            name (str, optional): The name of the configuration file to load.
        """
        self._name = name
        self.props = {}  # Dictionary to store key-value pairs of configurations.

        if name:
            self.load(name)

    def set_configuration(self, name: str):
        """
        Sets the configuration by loading properties from the specified file name.

        Args:
            name (str): The name of the configuration file to load.
        """
        self.load(name)

    def set_configurations(self, *names: str):
        """
        Sets multiple configurations by loading properties from all specified file names.

        Args:
            names (str): The names of the configuration files to load.
        """
        for name in names:
            self.load(name)

    def get(self, prop_name: str) -> str:
        """
        Retrieves a property value by its name. This method first searches for the property
        in environment variables, then in the loaded configuration dictionary.

        Args:
            prop_name (str): The name of the property to retrieve.

        Returns:
            str: The value of the property if found, otherwise None.
        """
        # Check for property in environment variables
        property_value = super().get(prop_name)

        # Fallback to loaded configurations
        if property_value is None:
            property_value = self.props.get(prop_name)

        return str(property_value) if property_value is not None else None

    def load(self, name: str):
        """
        Loads configuration properties from the specified file.

        Args:
            name (str): The name of the configuration file to load.

        Raises:
            FileNotFoundError: If the specified configuration file is not found.
            IOError: If the file cannot be read.
        """
        try:
            # Attempt to open the file as a resource
            with open(name, 'r') as file:
                self.load_file(self.props, file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{name}' not found.")
        except Exception as e:
            raise IOError(f"Failed to load configuration file '{name}': {str(e)}")

    @abstractmethod
    def load_file(self, props: dict, file_stream) -> None:
        """
        Abstract method to implement custom logic for loading configuration files.
        Subclasses must define how the input file is parsed and properties are stored.

        Args:
            props (dict): The dictionary to store the loaded properties.
            file_stream: The input stream of the configuration file.

        Raises:
            Exception: If any error occurs during the load process.
        """
        raise NotImplementedError("Subclasses must implement `load_file`.")
