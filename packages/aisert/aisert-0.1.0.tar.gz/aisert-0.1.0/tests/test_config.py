"""Tests for AisertConfig functionality."""
import pytest
import tempfile
import json
import os

from aisert import AisertConfig
from aisert.config.defaults import DefaultConfig


class TestAisertConfig:
    """Test AisertConfig functionality."""

    def test_init_with_parameters(self):
        """Test config initialization with parameters."""
        config = AisertConfig(
            token_model="gpt-4",
            model_provider="openai",
            token_encoding="cl100k_base",
            sentence_transformer_model="all-MiniLM-L6-v2"
        )
        assert config.token_model == "gpt-4"
        assert config.model_provider == "openai"
        assert config.token_encoding == "cl100k_base"
        assert config.sentence_transformer_model == "all-MiniLM-L6-v2"

    def test_get_default_config(self):
        """Test getting default configuration."""
        config = AisertConfig.get_default_config()
        assert config.token_model == "gpt-3.5-turbo"
        assert config.model_provider == "openai"
        assert config.sentence_transformer_model == "all-MiniLM-L6-v2"

    def test_load_from_valid_file(self):
        """Test loading config from valid JSON file."""
        config_data = {
            "token_model": "gpt-4",
            "model_provider": "anthropic",
            "token_encoding": None,
            "sentence_transformer_model": "all-MiniLM-L6-v2"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = AisertConfig.load(temp_path)
            assert config.token_model == "gpt-4"
            assert config.model_provider == "anthropic"
        finally:
            os.unlink(temp_path)

    def test_load_from_nonexistent_file(self):
        """Test loading config from nonexistent file returns default."""
        config = AisertConfig.load("nonexistent.json")
        assert config.token_model == "gpt-3.5-turbo"  # Default value

    def test_load_from_invalid_json(self):
        """Test loading config from invalid JSON returns default."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            config = AisertConfig.load(temp_path)
            assert config.token_model == "gpt-3.5-turbo"  # Default value
        finally:
            os.unlink(temp_path)

    def test_repr(self):
        """Test string representation of config."""
        config = AisertConfig(
            token_model="gpt-4",
            model_provider="openai"
        )
        repr_str = repr(config)
        assert "gpt-4" in repr_str
        assert "openai" in repr_str


class TestDefaultConfig:
    """Test DefaultConfig functionality."""

    def test_to_dict(self):
        """Test converting default config to dictionary."""
        config_dict = DefaultConfig.to_dict()
        assert isinstance(config_dict, dict)
        assert "token_model" in config_dict
        assert "model_provider" in config_dict
        assert config_dict["token_model"] == "gpt-3.5-turbo"
        assert config_dict["model_provider"] == "openai"

    def test_default_values(self):
        """Test default configuration values."""
        assert DefaultConfig.token_model == "gpt-3.5-turbo"
        assert DefaultConfig.model_provider == "openai"
        assert DefaultConfig.sentence_transformer_model == "all-MiniLM-L6-v2"
        assert DefaultConfig.token_encoding is None