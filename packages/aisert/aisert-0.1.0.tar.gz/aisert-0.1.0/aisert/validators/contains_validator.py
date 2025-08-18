from typing import List

from .validator import BaseValidator
from ..exception import ContainsValidationError
from ..models.result import Result
from ..models.validator_enums import ValidatorEnums


class ContainsValidator(BaseValidator):
    """
    Validates if a text contains a specific substring.
    """

    def __init__(self, invert=False):
        super().__init__(ValidatorEnums.CONTAINS)
        self.invert = invert

    def validate(self, content, items: List) -> Result:
        """
        Validate if the content contains the specified substring.
        """
        if not isinstance(items, list):
            raise ContainsValidationError("items must be a list")

        # Capture both missing and found in single pass
        missing, found = [], []
        for item in items:
            (found if item in content else missing).append(item)

        if self.invert:
            # For assert_not_contains: success when nothing is found

            if found:
                raise ContainsValidationError(f"Found flagged items: {found}")
            reason = f"No flagged items found"
        else:
            # For assert_contains: success when nothing is missing
            if missing:
                raise ContainsValidationError(f"Following items not present in the content: {missing}")
            reason = f"Found all items: {found}"
        return Result(self.validator_name,True, reason)
