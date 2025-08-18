from enum import Enum


class ValidatorEnums(Enum):
    """
    Enum class for validator types.
    """
    SCHEMA = "SchemaValidator"
    CONTAINS = "ContainsValidator"
    NOT_CONTAINS = "NotContainsValidator"
    TOKENS = "TokenValidator"
    SEMANTIC = "SemanticValidator"


    @classmethod
    def members(cls):
        """
        Returns a list of all validator types.
        """
        return [member.value for member in cls]