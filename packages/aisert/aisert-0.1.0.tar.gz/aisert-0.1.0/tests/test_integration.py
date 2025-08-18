"""Integration tests for Aisert functionality."""
import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel

from aisert import Aisert, AisertConfig


class UserModel(BaseModel):
    name: str
    email: str
    age: int


class TestIntegration:
    """Integration tests for real-world scenarios."""

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_api_response_validation(self, mock_factory):
        """Test complete API response validation workflow."""
        mock_validator = Mock()
        mock_validator.count.return_value = 25
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(
            token_model="gpt-3.5-turbo",
            model_provider="openai"
        )
        
        json_response = '{"name": "John Doe", "email": "john@example.com", "age": 30}'
        
        result = (
            Aisert(json_response, config)
            .assert_schema(UserModel, strict=False)
            .assert_contains(["name", "email"], strict=False)
            .assert_tokens(100, strict=False)
            .collect()
        )
        
        assert result.status is True
        assert len(result.rules) == 3
        assert all(rule['status'] for rule in result.rules.values())

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_content_moderation_workflow(self, mock_factory):
        """Test content moderation workflow."""
        mock_validator = Mock()
        mock_validator.count.return_value = 15
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(
            token_model="gpt-3.5-turbo",
            model_provider="openai"
        )
        
        content = "This is a helpful response about cooking recipes."
        
        result = (
            Aisert(content, config)
            .assert_not_contains(["violence", "hate", "spam"], strict=False)
            .assert_tokens(50, strict=False)
            .collect()
        )
        
        assert result.status is True
        assert len(result.rules) == 2

    @patch('aisert.validators.semantic_validator.SemanticValidator.get_instance')
    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_educational_content_validation(self, mock_token_factory, mock_semantic):
        """Test educational content validation workflow."""
        # Mock token validator
        mock_token_validator = Mock()
        mock_token_validator.count.return_value = 20
        mock_token_factory.return_value = mock_token_validator
        
        # Mock semantic validator
        mock_semantic_validator = Mock()
        mock_semantic_validator.validate.return_value = Mock(status=True, reason="Similar")
        mock_semantic.return_value = mock_semantic_validator
        
        config = AisertConfig(
            token_model="gpt-3.5-turbo",
            model_provider="openai"
        )
        
        content = "Python is a programming language created by Guido van Rossum."
        
        result = (
            Aisert(content, config)
            .assert_contains(["Python", "programming"], strict=False)
            .assert_tokens(100, strict=False)
            .assert_semantic_matches("Python programming language explanation", 0.7, strict=False)
            .collect()
        )
        
        assert result.status is True
        assert len(result.rules) == 3

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_mixed_validation_results(self, mock_factory):
        """Test workflow with mixed validation results."""
        mock_validator = Mock()
        mock_validator.count.return_value = 5
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(
            token_model="gpt-3.5-turbo",
            model_provider="openai"
        )
        
        content = "Hello world"
        
        result = (
            Aisert(content, config)
            .assert_contains(["Hello"], strict=False)  # Pass
            .assert_contains(["missing"], strict=False)  # Fail
            .assert_tokens(10, strict=False)  # Pass
            .collect()
        )
        
        assert result.status is False  # Overall failure due to one failed validation
        assert len(result.rules) == 3
        
        # Check individual results - they are now ordered by execution
        rules = result.rules
        assert rules[1]['status'] is True   # First contains check passed
        assert rules[2]['status'] is False  # Second contains check failed
        assert rules[3]['status'] is True   # Token validation passed

    def test_batch_processing_simulation(self):
        """Test batch processing of multiple responses."""
        responses = [
            "Valid response with good content",
            "Another valid response",
            "Response with spam content"
        ]
        
        results = []
        for response in responses:
            result = (
                Aisert(response)
                .assert_contains(["response"], strict=False)
                .assert_not_contains(["spam"], strict=False)
                .collect()
            )
            results.append(result)
        
        # First two should pass, third should fail
        assert results[0].status is True
        assert results[1].status is True
        assert results[2].status is False

    @patch('aisert.validators.token_validator.token_validator_factory.TokenValidatorFactory.get_instance')
    def test_json_list_validation(self, mock_factory):
        """Test validation of JSON list data."""
        mock_validator = Mock()
        mock_validator.count.return_value = 50
        mock_factory.return_value = mock_validator
        
        config = AisertConfig(
            token_model="gpt-3.5-turbo",
            model_provider="openai"
        )
        
        json_list = [
            {"name": "John", "email": "john@example.com", "age": 30},
            {"name": "Jane", "email": "jane@example.com", "age": 25}
        ]
        
        result = (
            Aisert(json_list, config)
            .assert_tokens(100, strict=False)
            .collect()
        )
        
        assert result.status is True
        # Verify JSON conversion happened
        mock_validator.count.assert_called_once()

    def test_error_recovery_in_chain(self):
        """Test error recovery in validation chain."""
        # This tests that one validation failure doesn't break the chain
        result = (
            Aisert("test content")
            .assert_contains(["missing"], strict=False)  # This will fail
            .assert_contains(["test"], strict=False)     # This will pass
            .collect()
        )

        assert result.status is False  # Overall failure
        assert len(result.rules) == 2
        assert result.rules[1]['status'] is False  # First validation failed
        assert result.rules[2]['status'] is True   # Second validation passed
        
    def test_configuration_inheritance(self):
        """Test that configuration is properly inherited through chain."""
        config = AisertConfig(
            token_model="gpt-4",
            model_provider="openai"
        )
        
        aisert = Aisert("test content", config)
        assert aisert.config.token_model == "gpt-4"
        assert aisert.config.model_provider == "openai"
        
        # Configuration should persist through chain
        chained = aisert.assert_contains(["test"], strict=False)
        assert chained.config.token_model == "gpt-4"