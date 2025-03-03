"""
Configuration management for the pdfimages package.

This module provides functionality to load, validate, and merge configuration
settings from various sources including YAML files and command-line arguments.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass


class Configuration:
    """
    Configuration manager for pdfimages.
    
    Handles loading configuration from files, merging with defaults,
    and validating configuration values.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "output": {
            "directory": "extracted_images",
            "maintain_structure": True,
            "format": "png",
            "naming_pattern": "page_{page:03d}_{index:03d}"
        },
        "processing": {
            "min_width": 100,
            "min_height": 100,
            "max_width": None,
            "max_height": None,
            "quality": 90,
            "scaling": 1.0,
            "dpi": 300,
            "deduplicate": True,
            "similarity_threshold": 0.95
        },
        "filters": {
            "include_types": ["images", "forms", "all"],
            "exclude_types": [],
            "min_size_bytes": 1024,
            "max_size_bytes": None
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "console": True
        }
    }
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize a Configuration object.
        
        Args:
            config_dict: Optional dictionary with configuration values
            config_file: Optional path to a YAML configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file:
            self.load_from_file(config_file)
            
        if config_dict:
            self.merge_config(config_dict)
            
        self.validate()
    
    def load_from_file(self, config_file: Union[str, Path]) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_file: Path to the configuration file
            
        Raises:
            ConfigurationError: If the file cannot be read or parsed
        """
        try:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self.merge_config(file_config)
        except (yaml.YAMLError, OSError) as e:
            raise ConfigurationError(f"Failed to load configuration from {config_file}: {str(e)}")
    
    def merge_config(self, config_dict: Dict[str, Any]) -> None:
        """
        Merge provided configuration with current configuration.
        
        Args:
            config_dict: Dictionary with configuration values to merge
        """
        self._deep_merge(self.config, config_dict)
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source dictionary into target dictionary.
        
        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def validate(self) -> None:
        """
        Validate the configuration values.
        
        Raises:
            ConfigurationError: If any configuration value is invalid
        """
        # Validate output configuration
        if not isinstance(self.config["output"]["directory"], str):
            raise ConfigurationError("Output directory must be a string")
        
        if not isinstance(self.config["output"]["maintain_structure"], bool):
            raise ConfigurationError("maintain_structure must be a boolean")
        
        if self.config["output"]["format"] not in ["png", "jpg", "jpeg", "tiff", "bmp"]:
            raise ConfigurationError("Output format must be one of: png, jpg, jpeg, tiff, bmp")
        
        # Validate processing configuration
        for param in ["min_width", "min_height", "quality"]:
            if (self.config["processing"][param] is not None and 
                not isinstance(self.config["processing"][param], (int, float))):
                raise ConfigurationError(f"{param} must be a number")
        
        for param in ["max_width", "max_height"]:
            if (self.config["processing"][param] is not None and 
                not isinstance(self.config["processing"][param], (int, float))):
                raise ConfigurationError(f"{param} must be a number or None")
        
        if not 0 <= self.config["processing"]["quality"] <= 100:
            raise ConfigurationError("Quality must be between 0 and 100")
        
        if not 0 < self.config["processing"]["scaling"] <= 10:
            raise ConfigurationError("Scaling must be between 0 (exclusive) and 10")
        
        if not isinstance(self.config["processing"]["deduplicate"], bool):
            raise ConfigurationError("deduplicate must be a boolean")
        
        if not 0 <= self.config["processing"]["similarity_threshold"] <= 1:
            raise ConfigurationError("similarity_threshold must be between 0 and 1")
        
        # Validate filters configuration
        if not isinstance(self.config["filters"]["include_types"], list):
            raise ConfigurationError("include_types must be a list")
        
        if not isinstance(self.config["filters"]["exclude_types"], list):
            raise ConfigurationError("exclude_types must be a list")
        
        # Validate logging configuration
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config["logging"]["level"] not in valid_log_levels:
            raise ConfigurationError(f"Log level must be one of: {', '.join(valid_log_levels)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The configuration key (can use dot notation for nested keys)
            default: Default value to return if key is not found
            
        Returns:
            The configuration value or default if not found
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.
        
        Args:
            key: The configuration key (can use dot notation for nested keys)
            value: The value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Return the configuration as a dictionary.
        
        Returns:
            A dictionary with all configuration values
        """
        return self.config.copy()
    
    @classmethod
    def get_default_config_path(cls) -> Path:
        """
        Get the path to the default configuration file.
        
        Returns:
            Path to the default configuration file
        """
        # Look for config in user's home directory
        home_config = Path.home() / ".pdfimages" / "config.yaml"
        if home_config.exists():
            return home_config
            
        # Look for config in current directory
        local_config = Path.cwd() / "pdfimages.yaml"
        if local_config.exists():
            return local_config
            
        # Return the package default config path
        return Path(__file__).parent.parent / "default_config.yaml"
    
    @classmethod
    def load_default(cls) -> 'Configuration':
        """
        Load the default configuration.
        
        Returns:
            A Configuration object with default settings
        """
        try:
            default_path = cls.get_default_config_path()
            if default_path.exists():
                return cls(config_file=default_path)
        except Exception:
            pass
            
        # If no file is found or there's an error, return default config
        return cls()
