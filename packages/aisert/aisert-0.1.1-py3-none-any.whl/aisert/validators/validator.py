import logging

from ..models.result import Result
from ..models.validator_enums import ValidatorEnums


class BaseValidator:
    """
    Abstract base class for all Aisert validators.
    
    Provides common functionality and interface that all validators must implement.
    Each validator performs a specific type of validation (schema, content, tokens, etc.)
    and returns a Result object with the outcome.
    
    Attributes:
        validator_name: Human-readable name of the validator
        logger: Logger instance for debugging and error reporting
    """

    def __init__(self, name: ValidatorEnums):
        """
        Initialize base validator with name and logging.
        
        Args:
            name: ValidatorEnums value identifying this validator type
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validator_name = name.value

    def validate(self, *args, **kwargs) -> Result:
        """
        Perform validation and return result.
        
        Must be implemented by all subclasses to define specific validation logic.
        
        Returns:
            Result object containing validator name, status, and reason
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    def name(self):
        """
        Get the human-readable name of this validator.
        
        Returns:
            String name of the validator (e.g., "ContainsValidator")
        """
        return self.validator_name
