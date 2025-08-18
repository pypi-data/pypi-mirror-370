from typing import List

from .validator import BaseValidator
from ..exception import NotContainsValidationError
from ..models.validator_enums import ValidatorEnums
from ..models.result import Result


class NotContainsValidator(BaseValidator):
    """
    Validates that content does NOT contain any of the specified flagged items.
    
    Used for content moderation, spam detection, and ensuring unwanted terms
    are absent from AI responses. Fails validation if any flagged items are found.
    
    Example:
        validator = NotContainsValidator()
        result = validator.validate("Clean content", ["spam", "inappropriate"])
        # Returns success since no flagged items found
    """

    def __init__(self):
        """
        Initialize the NotContainsValidator.
        
        Sets up the validator with the NOT_CONTAINS identifier for clear
        reporting and differentiation from regular ContainsValidator.
        """
        super().__init__(ValidatorEnums.NOT_CONTAINS)

    def validate(self, content, items: List) -> Result:
        """
        Validate that content does not contain any of the flagged items.
        
        Args:
            content: Text content to check for absence of flagged items.
            items: List of strings that must NOT be present in the content.
        
        Returns:
            Result object with success status and explanation
        
        Raises:
            NotContainsValidationError: If any flagged items are found or if items is not a list
        
        Example:
            validator.validate("Hello world", ["spam", "bad"])  # Success
            validator.validate("This is spam", ["spam"])  # Raises exception
        """
        if not isinstance(items, list):
            raise NotContainsValidationError("items must be a list")

        found = [item for item in items if item in content]
        if found:
            raise NotContainsValidationError(f"Found flagged items: {found}")

        return Result(self.validator_name, True, "No flagged items found")
