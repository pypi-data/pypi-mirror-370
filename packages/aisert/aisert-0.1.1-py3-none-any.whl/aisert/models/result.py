from collections import defaultdict
from typing import Dict

from ..models.validator_enums import ValidatorEnums


class Result:
    """
    Represents the result of a single validation operation.
    
    Each Result contains:
    - validator: Name of the validator that produced this result
    - status: Boolean indicating if validation passed (True) or failed (False)
    - reason: Human-readable explanation of the validation outcome
    
    Example:
        result = Result("ContainsValidator", True, "Found all required items")
    """

    def __init__(self, validator: str, status: bool, reason: str = ""):
        """
        Create a new validation result.
        
        Args:
            validator: Name of the validator that produced this result
            status: True if validation passed, False if it failed
            reason: Human-readable explanation of why validation passed/failed
        
        Example:
            result = Result("TokenValidator", False, "Token count 150 exceeds limit 100")
        """
        self.validator = validator
        self.status = status
        self.reason = reason

    def to_dict(self) -> Dict[str, str]:
        """
        Convert the Result to a dictionary for serialization or reporting.
        
        Returns:
            Dictionary with 'validator', 'status', and 'reason' keys
        
        Example:
            {"validator": "ContainsValidator", "status": True, "reason": "All items found"}
        """
        return {"validator": self.validator, "status": self.status, "reason": self.reason}


class AisertStatus:
    """
    Tracks validation results in the order they were executed.
    
    Maintains an ordered collection of validation results, allowing:
    - Multiple validations of the same type (e.g., multiple assert_contains calls)
    - Preservation of execution order for debugging and reporting
    - Easy access to all validation outcomes
    
    Attributes:
        validators: Dictionary mapping execution order (int) to Result objects
        _order: Internal counter for tracking execution sequence
    
    Example:
        status = AisertStatus()
        status.update(Result("ContainsValidator", True, "Found items"))
        status.update(Result("TokenValidator", False, "Too many tokens"))
        # status.validators = {1: Result(...), 2: Result(...)}
    """

    def __init__(self):
        """
        Initialize an empty status tracker.
        
        Creates an empty validators dictionary and sets the execution order counter to 1.
        """
        self.validators = {}
        self._order = 1

    def update(self, result: Result):
        """
        Add a new validation result in execution order.
        
        Args:
            result: Result object from a validator containing outcome and details
        
        Example:
            result = Result("SchemaValidator", True, "Schema validation passed")
            status.update(result)
            # Now status.validators[1] contains this result
        """
        self.validators[self._order] = result
        self._order += 1
