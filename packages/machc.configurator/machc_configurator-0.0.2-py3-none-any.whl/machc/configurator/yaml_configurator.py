from typing import Dict, Any

import yaml

from .file_configurator import AbstractFileConfigurator


class YamlConfigurator(AbstractFileConfigurator):
    """
    The YamlConfigurator class provides methods to load configuration properties
    from YAML files. It supports hierarchical YAML structures and flattens them
    into a single-level dictionary with dot-separated keys for easier access.

    Example:
        Input:
        {
            "parent": {
                "child1": "value1",
                "child2": {
                    "grandchild": "value2"
                }
            }
        }

        Output:
        {
            "parent.child1": "value1",
            "parent.child2.grandchild": "value2"
        }
    """

    def __init__(self, name: str = None):
        """
        Initializes the YamlConfigurator. Optionally loads a properties file.

        Args:
            name (str, optional): The name of the properties file to load. Defaults to None.
        """
        super().__init__(name)

    def load_file(self, props: Dict[str, Any], file_stream) -> Dict[str, Any]:
        source = yaml.safe_load(file_stream)
        if source:
            self.props = self.flatten(source)  # Flatten dictionary
        return self.props

    def flatten(self, source: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
        items = []
        for key, value in source.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                items.extend(self.flatten(value, new_key, sep).items())
            else:
                items.append((new_key, value))
        return dict(items)
