"""Tests for the configuration management system."""

import os
import tempfile
import yaml
import pytest
from pathlib import Path

from pdfimages.utils.config import Configuration, ConfigurationError


@pytest.fixture(scope="function")
def config():
    """Fixture to provide a fresh Configuration instance for each test."""
    # Load configuration from the default config file
    # This ensures tests use the same defaults as the application
    return Configuration()


def test_default_configuration(config):
    """Test that default configuration is loaded correctly."""
    assert config.get("output.directory") == "extracted_images"
    assert config.get("processing.quality") == 90
    assert config.get("logging.level") == "INFO"


def test_merge_with_dict(config):
    """Test merging configuration with a dictionary."""
    custom_config = {
        "output": {
            "directory": "custom_output",
            "format": "jpg"
        },
        "processing": {
            "quality": 80
        }
    }
    
    # Merge our custom values with the config
    config.merge_config(custom_config)
    
    # Check merged values
    assert config.get("output.directory") == "custom_output"
    assert config.get("output.format") == "jpg"
    assert config.get("processing.quality") == 80
    
    # Check that other defaults are preserved
    assert config.get("output.maintain_structure") is True
    assert config.get("processing.deduplicate") is True


def test_load_from_file(config):
    """Test loading configuration from a YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
        yaml_content = """
output:
  directory: file_output
  format: tiff
processing:
  min_width: 200
  min_height: 200
  quality: 90
"""
        temp.write(yaml_content)
        temp_path = temp.name
    
    try:
        config.load_from_file(temp_path)
        
        # Check loaded values
        assert config.get("output.directory") == "file_output"
        assert config.get("output.format") == "tiff"
        assert config.get("processing.min_width") == 200
        assert config.get("processing.min_height") == 200
        
        # Check that other defaults are preserved
        assert config.get("processing.quality") == 90
    finally:
        os.unlink(temp_path)


def test_invalid_yaml_file():
    """Test handling of invalid YAML files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
        temp.write("invalid: yaml: content:")
        temp_path = temp.name
    
    try:
        with pytest.raises(ConfigurationError):
            Configuration(config_file=temp_path)
    finally:
        os.unlink(temp_path)


def test_nonexistent_file():
    """Test handling of nonexistent configuration files."""
    with pytest.raises(ConfigurationError):
        Configuration(config_file="/path/to/nonexistent/config.yaml")


def test_validation(config):
    """Test validation of configuration values."""
    # Test invalid output format
    with pytest.raises(ConfigurationError):
        config.merge_config({"output": {"format": "invalid"}})
        config.validate()
    
    # Reset config for next test
    config = Configuration()
    
    # Test invalid quality value
    with pytest.raises(ConfigurationError):
        config.merge_config({"processing": {"quality": 101}})
        config.validate()
    
    # Reset config for next test
    config = Configuration()
    
    # Test invalid scaling value
    with pytest.raises(ConfigurationError):
        config.merge_config({"processing": {"scaling": 0}})
        config.validate()
    
    # Reset config for next test
    config = Configuration()
    
    # Test invalid similarity threshold
    with pytest.raises(ConfigurationError):
        config.merge_config({"processing": {"similarity_threshold": 1.5}})
        config.validate()
    
    # Reset config for next test
    config = Configuration()
    
    # Test invalid log level
    with pytest.raises(ConfigurationError):
        config.merge_config({"logging": {"level": "INVALID"}})
        config.validate()


def test_get_set_methods(config):
    """Test get and set methods for configuration values."""
    
    # Test get with default
    assert config.get("nonexistent.key", "default") == "default"
    
    # Test default output format is present
    assert config.get("output.format") is not None
    
    # Test set and get
    config.set("output.new_option", "value")
    assert config.get("output.new_option") == "value"
    
    # Test nested set
    config.set("new_section.nested.option", 42)
    assert config.get("new_section.nested.option") == 42


def test_as_dict(config):
    """Test converting configuration to dictionary."""
    config_dict = config.as_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict["output"]["directory"] == "extracted_images"
    assert config_dict["output"]["format"] is not None  # Ensure format is present
    assert config_dict["processing"]["quality"] == 90


def test_get_default_config_path(monkeypatch):
    """Test getting the default configuration path."""
    # Mock home directory
    mock_home = tempfile.mkdtemp()
    monkeypatch.setattr(Path, "home", lambda: Path(mock_home))
    
    # Test when no config files exist
    config_path = Configuration.get_default_config_path()
    assert "default_config.yaml" in str(config_path)
    
    # Create a config in the home directory
    os.makedirs(os.path.join(mock_home, ".pdfimages"), exist_ok=True)
    home_config = os.path.join(mock_home, ".pdfimages", "config.yaml")
    with open(home_config, 'w') as f:
        f.write("# Home config")
    
    # Test that home config is found
    config_path = Configuration.get_default_config_path()
    assert config_path == Path(home_config)
