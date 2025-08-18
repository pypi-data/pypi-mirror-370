class AisertError(Exception):
    """Base exception for all Aisert errors."""
    pass


class TokenValidationError(AisertError):
    """Token counting specific errors."""
    pass


class SchemaValidationError(AisertError):
    """Schema validation specific errors."""
    pass


class SemanticValidationError(AisertError):
    """Semantic validation specific errors."""
    pass


class ContainsValidationError(AisertError):
    """Text contain validation errors"""
    pass


class NotContainsValidationError(AisertError):
    """Text not contains validation errors"""
    pass
