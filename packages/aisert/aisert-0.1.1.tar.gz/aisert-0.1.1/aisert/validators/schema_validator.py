import json
from json import JSONDecodeError
from typing import Any
from pydantic import BaseModel, TypeAdapter, ValidationError

from .validator import BaseValidator
from ..exception import SchemaValidationError
from ..models.result import Result
from ..models.validator_enums import ValidatorEnums


class SchemaValidator(BaseValidator):
    """
    A class to validate content against a schema.
    """

    def __init__(self):
        super().__init__(ValidatorEnums.SCHEMA)

    def validate(self, content: Any, schema: Any):
        """
        Validates if the content matches the schema.

        :param content: The content to validate.
        :param schema: The schema to validate against.
        :return: Result true/false with reason.
        """
        self.logger.debug(f"Validating content against schema: {schema}")
        self.logger.debug(f"content: {content}")
        try:
            if type(content) is str:
                content = json.loads(content)
        except JSONDecodeError as e:
            raise SchemaValidationError(f"Content is not a valid JSON: {e}")

        is_pydantic_model = isinstance(schema, type) and issubclass(schema, BaseModel)
        is_generic_type = hasattr(schema, "__origin__")

        if not (is_pydantic_model or is_generic_type):
            raise SchemaValidationError("Provided schema is not a valid Pydantic model")
        try:
            TypeAdapter(schema).validate_python(content)
            return Result(self.validator_name,True, "")
        except ValidationError as e:
            raise SchemaValidationError(f"{e}")
        except Exception as e:
            raise SchemaValidationError(f"Unexpected error: {e}")
