"""Tests for core Aisert functionality."""
import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel

from aisert import Aisert, AisertConfig, AisertError
from aisert.exception import (
    SchemaValidationError,
    ContainsValidationError,
    TokenValidationError,
    SemanticValidationError
)


class TestModel(BaseModel):
    name: str
    age: int


class TestAisert:
    """Test core Aisert functionality."""

    def test_init_with_content(self):
        """Test Aisert initialization with content."""
        aisert = Aisert("test content")
        assert aisert.content == "test content"
        assert aisert.config is not None

    def test_init_with_config(self):
        """Test Aisert initialization with custom config."""
        config = AisertConfig(
            token_model="gpt-4",
            model_provider="openai"
        )
        aisert = Aisert("test", config)
        assert aisert.config == config

    def test_fluent_interface(self):
        """Test fluent interface returns self."""
        aisert = Aisert("test content")
        result = aisert.assert_contains(["test"], strict=False)
        assert result is aisert

    def test_collect_returns_report(self):
        """Test collect returns AisertReport."""
        aisert = Aisert("test content")
        result = aisert.assert_contains(["test"], strict=False).collect()
        assert hasattr(result, 'status')
        assert hasattr(result, 'rules')
        assert result.status is True

    def test_strict_mode_raises_exception(self):
        """Test strict mode raises exceptions on failure."""
        with pytest.raises(ContainsValidationError):
            Aisert("test").assert_contains(["missing"], strict=True)

    def test_non_strict_mode_collects_errors(self):
        """Test non-strict mode collects errors without raising."""
        result = (
            Aisert("test")
            .assert_contains(["missing"], strict=False)
            .collect()
        )
        assert result.status is False
        assert len(result.rules) == 1
        assert list(result.rules.values())[0]['validator'] == 'ContainsValidator'


class TestSchemaValidation:
    """Test schema validation functionality."""

    def test_valid_schema(self):
        """Test valid schema validation."""
        json_data = '{"name": "John", "age": 30}'
        result = (
            Aisert(json_data)
            .assert_schema(TestModel, strict=False)
            .collect()
        )
        assert result.status is True

    def test_invalid_schema(self):
        """Test invalid schema validation."""
        json_data = '{"name": "John"}'  # missing age
        result = (
            Aisert(json_data)
            .assert_schema(TestModel, strict=False)
            .collect()
        )
        assert result.status is False

    def test_invalid_json(self):
        """Test invalid JSON raises error."""
        with pytest.raises(SchemaValidationError):
            Aisert("invalid json").assert_schema(TestModel, strict=True)

    def test_non_pydantic_schema(self):
        """Test non-Pydantic schema raises error."""
        with pytest.raises(SchemaValidationError):
            Aisert("{}").assert_schema(dict, strict=True)


class TestContainsValidation:
    """Test contains validation functionality."""

    def test_contains_success(self):
        """Test successful contains validation."""
        result = (
            Aisert("Hello world")
            .assert_contains(["Hello", "world"], strict=False)
            .collect()
        )
        assert result.status is True

    def test_contains_failure(self):
        """Test failed contains validation."""
        result = (
            Aisert("Hello world")
            .assert_contains(["missing"], strict=False)
            .collect()
        )
        assert result.status is False

    def test_not_contains_success(self):
        """Test successful not_contains validation."""
        result = (
            Aisert("Hello world")
            .assert_not_contains(["spam"], strict=False)
            .collect()
        )
        assert result.status is True

    def test_not_contains_failure(self):
        """Test failed not_contains validation."""
        result = (
            Aisert("Hello world")
            .assert_not_contains(["Hello"], strict=False)
            .collect()
        )
        assert result.status is False

    def test_contains_invalid_input(self):
        """Test contains with invalid input type."""
        with pytest.raises(ContainsValidationError):
            Aisert("test").assert_contains("not_a_list", strict=True)


class TestTokenValidation:
    """Test token validation functionality."""

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_token_validation_success(self, mock_factory):
        """Test successful token validation."""
        mock_validator = Mock()
        mock_validator.count.return_value = 5
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(token_model="gpt-3.5-turbo", model_provider="openai")
        result = (
            Aisert("short text", config)
            .assert_tokens(10, strict=False)
            .collect()
        )
        assert result.status is True

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_token_validation_failure(self, mock_factory):
        """Test failed token validation."""
        mock_validator = Mock()
        mock_validator.count.return_value = 15
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(token_model="gpt-3.5-turbo", model_provider="openai")
        with pytest.raises(TokenValidationError):
            Aisert("long text", config).assert_tokens(10, strict=True)

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_token_validation_dict_input(self, mock_factory):
        """Test token validation with dict input."""
        mock_validator = Mock()
        mock_validator.count.return_value = 5
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(token_model="gpt-3.5-turbo", model_provider="openai")
        result = (
            Aisert({"key": "value"}, config)
            .assert_tokens(10, strict=False)
            .collect()
        )
        assert result.status is True
        # Verify JSON conversion was called
        mock_validator.count.assert_called_with('{"key": "value"}')


class TestSemanticValidation:
    """Test semantic validation functionality."""

    @patch('aisert.validators.semantic_validator.SemanticValidator.get_instance')
    def test_semantic_validation_success(self, mock_get_instance):
        """Test successful semantic validation."""
        mock_validator = Mock()
        mock_validator.validate.return_value = Mock(status=True, reason="Similar")
        mock_get_instance.return_value = mock_validator
        
        result = (
            Aisert("Hello world")
            .assert_semantic_matches("Hi world", 0.8, strict=False)
            .collect()
        )
        assert result.status is True

    @patch('aisert.validators.semantic_validator.SemanticValidator.get_instance')
    def test_semantic_validation_failure(self, mock_get_instance):
        """Test failed semantic validation."""
        mock_validator = Mock()
        mock_validator.validate.side_effect = SemanticValidationError("Not similar")
        mock_get_instance.return_value = mock_validator
        
        with pytest.raises(SemanticValidationError):
            Aisert("Hello").assert_semantic_matches("Goodbye", 0.8, strict=True)


class TestChainedValidation:
    """Test chained validation scenarios."""

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_multiple_validations_success(self, mock_factory):
        """Test multiple successful validations."""
        mock_validator = Mock()
        mock_validator.count.return_value = 5
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(token_model="gpt-3.5-turbo", model_provider="openai")
        result = (
            Aisert("Hello world", config)
            .assert_contains(["Hello"], strict=False)
            .assert_tokens(10, strict=False)
            .collect()
        )
        assert result.status is True
        assert len(result.rules) == 2
        # Check that results are ordered
        assert 1 in result.rules
        assert 2 in result.rules

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_multiple_validations_mixed_results(self, mock_factory):
        """Test multiple validations with mixed results."""
        mock_validator = Mock()
        mock_validator.count.return_value = 5
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(token_model="gpt-3.5-turbo", model_provider="openai")
        result = (
            Aisert("Hello world", config)
            .assert_contains(["missing"], strict=False)  # Fail
            .assert_tokens(10, strict=False)  # Pass
            .collect()
        )
        assert result.status is False  # Overall failure
        assert len(result.rules) == 2
        assert result.rules[1]['status'] is False  # First validation failed
        assert result.rules[2]['status'] is True   # Second validation passed


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_exception_hierarchy(self):
        """Test exception hierarchy."""
        assert issubclass(SchemaValidationError, AisertError)
        assert issubclass(ContainsValidationError, AisertError)
        assert issubclass(TokenValidationError, AisertError)
        assert issubclass(SemanticValidationError, AisertError)

    def test_validate_helper_method(self):
        """Test _validate helper method error handling."""
        aisert = Aisert("test")
        
        # Test with strict=False should not raise
        aisert._validate(Mock(validate=Mock(side_effect=AisertError("test"))), False)
        
        # Test with strict=True should raise
        with pytest.raises(AisertError):
            aisert._validate(Mock(validate=Mock(side_effect=AisertError("test"))), True)