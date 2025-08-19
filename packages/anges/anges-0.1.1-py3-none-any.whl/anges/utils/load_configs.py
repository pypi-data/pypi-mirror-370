import os
import yaml
from typing import Dict, Any, Union, Optional, Type
from dataclasses import dataclass, field, fields

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass

@dataclass
class Config:
    """Base configuration class that can be extended for specific configurations."""
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create a Config instance from a dictionary."""
        # Filter the dictionary to only include fields defined in the dataclass
        field_names = {f.name for f in fields(cls)}
        filtered_dict = {}
        
        for field_name in field_names:
            if field_name in config_dict:
                field_value = config_dict[field_name]
                field_type = cls.__annotations__.get(field_name, None)
                
                # Check if the field type is a subclass of Config and the value is a dictionary
                if (isinstance(field_value, dict) and field_type and 
                    hasattr(field_type, '__origin__') and field_type.__origin__ is type and 
                    issubclass(field_type.__args__[0], Config)):
                    # Convert the dictionary to a Config instance
                    filtered_dict[field_name] = field_type.__args__[0].from_dict(field_value)
                # Handle the case where the field is directly a Config subclass (not Type[Config])
                elif (isinstance(field_value, dict) and field_type and 
                      isinstance(field_type, type) and issubclass(field_type, Config)):
                    filtered_dict[field_name] = field_type.from_dict(field_value)
                else:
                    filtered_dict[field_name] = field_value
        
        # Create an instance of the class with the filtered dictionary
        return cls(**filtered_dict)

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load a YAML file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary containing the YAML file contents
        
    Raises:
        ConfigurationError: If the YAML file is invalid
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file) or {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Error parsing YAML file {file_path}: {e}")


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries, with values from override taking precedence.
    
    Args:
        base: Base dictionary
        override: Dictionary with values to override
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge(result[key], value)
        else:
            # Override or add the value
            result[key] = value
            
    return result


def load_config(
    default_config_path: str,
    override_config_path: Optional[str] = None,
    config_class: Optional[Type[Config]] = None
) -> Union[Dict[str, Any], Config]:
    """
    Load configuration from YAML files and environment variables.

    Args:
        default_config_path: Path to the default configuration YAML file
        override_config_path: Optional path to an override configuration YAML file
        config_class: Optional Config subclass to convert the configuration to

    Returns:
        Configuration as a dictionary or a Config instance if config_class is provided

    Raises:
        ConfigurationError: If there is an error loading the configuration
    """
    # Load the default configuration
    config = load_yaml_file(default_config_path)

    # Load and merge the override configuration if provided
    if override_config_path:
        override_config = load_yaml_file(override_config_path)
        config = deep_merge(config, override_config)

    # Convert to a Config instance if a class is provided
    if config_class is not None:
        return config_class.from_dict(config)

    return config
