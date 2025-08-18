"""Token validation module for counting and validating token limits in text content."""
import json

from .token_validator_factory import TokenValidatorFactory
from ...exception import TokenValidationError
from ..validator import BaseValidator
from ...models.result import Result
from ...models.validator_enums import ValidatorEnums


class TokenValidator(BaseValidator):
    """
    Validates the number of tokens in a given text.
    """

    def __init__(self, model_provider: str = None):
        super().__init__(ValidatorEnums.TOKENS)
        self.model_provider = model_provider

    def validate(self, text,
                 token_limit: int = 100,
                 token_model: str = None,
                 token_encoding: str = None
                 ):
        """
        Validates the number of tokens in the text.
        
        :param token_limit: max allowed token limit
        :param text: text to be counted as tokens
        :param token_model: The model to use for token counting.
        :param token_encoding: The encoding to use for token counting.
        :return: The number of tokens in the text.
        """
        try:
            token_validator = TokenValidatorFactory.get_instance(
                model_provider=self.model_provider,
                token_model=token_model,
                token_encoding=token_encoding
            )
            if not isinstance(text, str):
                text = json.dumps(text)

            token_count = token_validator.count(text)
            self.logger.debug(f"Token count: {token_count}")

            if token_count > token_limit:
                raise TokenValidationError(
                    f"Token limit exceeded: {token_count} tokens found, limit is {token_limit}")
            return Result(self.validator_name, True, f"Token count {token_count} is within limit {token_limit}")

        except TokenValidationError:
            raise
        except Exception as e:
            raise TokenValidationError(f"Unexpected error: {e}") from e
