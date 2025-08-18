"""Tests for exception hierarchy and handling."""
import pytest

from aisert.exception import (
    AisertError,
    SchemaValidationError,
    ContainsValidationError,
    TokenValidationError,
    SemanticValidationError
)


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_base_exception(self):
        """Test AisertError base exception."""
        error = AisertError("Base error message")
        assert str(error) == "Base error message"
        assert isinstance(error, Exception)

    def test_schema_validation_error_inheritance(self):
        """Test SchemaValidationError inherits from AisertError."""
        error = SchemaValidationError("Schema error")
        assert isinstance(error, AisertError)
        assert isinstance(error, Exception)
        assert str(error) == "Schema error"

    def test_contains_validation_error_inheritance(self):
        """Test ContainsValidationError inherits from AisertError."""
        error = ContainsValidationError("Contains error")
        assert isinstance(error, AisertError)
        assert isinstance(error, Exception)
        assert str(error) == "Contains error"

    def test_token_validation_error_inheritance(self):
        """Test TokenValidationError inherits from AisertError."""
        error = TokenValidationError("Token error")
        assert isinstance(error, AisertError)
        assert isinstance(error, Exception)
        assert str(error) == "Token error"

    def test_semantic_validation_error_inheritance(self):
        """Test SemanticValidationError inherits from AisertError."""
        error = SemanticValidationError("Semantic error")
        assert isinstance(error, AisertError)
        assert isinstance(error, Exception)
        assert str(error) == "Semantic error"

    def test_all_exceptions_catchable_by_base(self):
        """Test all specific exceptions can be caught by base exception."""
        exceptions = [
            SchemaValidationError("Schema"),
            ContainsValidationError("Contains"),
            TokenValidationError("Token"),
            SemanticValidationError("Semantic")
        ]
        
        for exc in exceptions:
            try:
                raise exc
            except AisertError as e:
                assert isinstance(e, AisertError)
            except Exception:
                pytest.fail("Exception should be catchable by AisertError")

    def test_specific_exception_catching(self):
        """Test catching specific exception types."""
        # Test SchemaValidationError
        with pytest.raises(SchemaValidationError):
            raise SchemaValidationError("Schema specific error")
        
        # Test ContainsValidationError
        with pytest.raises(ContainsValidationError):
            raise ContainsValidationError("Contains specific error")
        
        # Test TokenValidationError
        with pytest.raises(TokenValidationError):
            raise TokenValidationError("Token specific error")
        
        # Test SemanticValidationError
        with pytest.raises(SemanticValidationError):
            raise SemanticValidationError("Semantic specific error")

    def test_exception_with_empty_message(self):
        """Test exceptions with empty messages."""
        error = AisertError("")
        assert str(error) == ""
        
        error = SchemaValidationError("")
        assert str(error) == ""

    def test_exception_with_none_message(self):
        """Test exceptions with None message."""
        error = AisertError(None)
        assert str(error) == "None"

    def test_exception_chaining(self):
        """Test exception chaining with from clause."""
        original_error = ValueError("Original error")
        
        try:
            try:
                raise original_error
            except ValueError as e:
                raise TokenValidationError("Token error occurred") from e
        except TokenValidationError as e:
            assert e.__cause__ is original_error
            assert isinstance(e.__cause__, ValueError)

    def test_multiple_exception_types_in_hierarchy(self):
        """Test that we can distinguish between different exception types."""
        def raise_schema_error():
            raise SchemaValidationError("Schema problem")
        
        def raise_token_error():
            raise TokenValidationError("Token problem")
        
        # Test we can catch specific types
        with pytest.raises(SchemaValidationError):
            raise_schema_error()
        
        with pytest.raises(TokenValidationError):
            raise_token_error()
        
        # Test we can catch both with base class
        for error_func in [raise_schema_error, raise_token_error]:
            with pytest.raises(AisertError):
                error_func()


class TestExceptionMessages:
    """Test exception message formatting and content."""

    def test_detailed_error_messages(self):
        """Test exceptions with detailed error messages."""
        detailed_message = "Validation failed: Expected 'name' field but got 'username'"
        error = SchemaValidationError(detailed_message)
        assert str(error) == detailed_message

    def test_formatted_error_messages(self):
        """Test exceptions with formatted error messages."""
        token_count = 150
        limit = 100
        message = f"Token limit exceeded: {token_count} tokens found, limit is {limit}"
        error = TokenValidationError(message)
        assert "150" in str(error)
        assert "100" in str(error)
        assert "exceeded" in str(error)

    def test_multiline_error_messages(self):
        """Test exceptions with multiline error messages."""
        multiline_message = """Validation failed with multiple errors:
        1. Missing required field 'name'
        2. Invalid email format
        3. Age must be positive integer"""
        
        error = SchemaValidationError(multiline_message)
        assert "Missing required field" in str(error)
        assert "Invalid email format" in str(error)
        assert "Age must be positive" in str(error)