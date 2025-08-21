import json
from pathlib import Path
from typing import Any, Dict, Tuple, Union


class ConfigLoader:
    """
    Utility class for loading and processing simulation configuration files

    This class provides static methods for handling different configuration formats
    (JSON, YAML) and sources (files, strings, dictionaries). It includes validation
    and format detection capabilities to ensure robust configuration loading

    The loader supports both file-based and string-based configurations, with
    automatic format detection based on content or file extensions
    """

    @staticmethod
    def load(config: Union[str, dict, Path]) -> Tuple[str, str]:
        """
        Load configuration from various sources and return standardized format

        This method handles multiple input types and automatically detects the
        configuration format, returning a tuple of (content, format_type)

        Args:
            config: Configuration source, can be:
                   - dict: Configuration dictionary (converted to JSON)
                   - str: JSON string, YAML string, or file path
                   - Path: Path object pointing to configuration file

        Returns:
            Tuple of (content_string, format_type) where:
            - content_string: String representation of the configuration
            - format_type: Either "json" or "yaml"

        Raises:
            FileNotFoundError: If file path doesn't exist
            ValueError: If string appears to be malformed JSON or unsupported format

        Example:
            >>> content, fmt = ConfigLoader.load({"agents": [], "protocols": {}})
            >>> content, fmt = ConfigLoader.load("config.yaml")
            >>> content, fmt = ConfigLoader.load('{"simulation": {"blocks": 1000}}')
        """
        if isinstance(config, dict):
            return json.dumps(config), "json"

        if isinstance(config, (str, Path)):
            if isinstance(config, str):
                try:
                    json.loads(config)
                    return config, "json"
                except json.JSONDecodeError:
                    if config.strip().startswith("{") or config.strip().startswith("["):
                        raise ValueError("The provided string appears to be JSON but is malformed")

                    if config.strip().startswith("---") or ":" in config.splitlines()[0]:
                        return config, "yaml"

                    path = Path(config)
            else:
                path = config
        else:
            raise ValueError(f"Unsupported configuration type: {type(config)}")

        if not path.exists():
            raise FileNotFoundError(f"Configuration file '{path}' does not exist")

        content = path.read_text()

        if path.suffix.lower() in (".yml", ".yaml"):
            format_type = "yaml"
        elif path.suffix.lower() == ".json":
            format_type = "json"
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        return content, format_type

    @staticmethod
    def merge_configs(base_config: Dict[str, Any], update_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries

        Performs a deep merge where nested dictionaries are merged recursively,
        and non-dictionary values in update_config override those in base_config

        Args:
            base_config: Base configuration dictionary
            update_config: Configuration updates to apply

        Returns:
            New dictionary containing the merged configuration

        Example:
            >>> base = {"simulation": {"blocks": 1000}, "agents": []}
            >>> update = {"simulation": {"timestep": 12}, "protocols": {}}
            >>> merged = ConfigLoader.merge_configs(base, update)
            >>> # Result: {"simulation": {"blocks": 1000, "timestep": 12},
            >>> #          "agents": [], "protocols": {}}
        """
        result = base_config.copy()

        for key, value in update_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader.merge_configs(result[key], value)
            else:
                result[key] = value

        return result
