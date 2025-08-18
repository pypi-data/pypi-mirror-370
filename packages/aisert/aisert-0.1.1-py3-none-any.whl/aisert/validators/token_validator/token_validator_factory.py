from .common_token_validators import AnthropicTokenValidator, GoogleTokenValidator, HuggingFaceTokenValidator, \
    OpenAITokenValidator
from ...exception import TokenValidationError


class TokenValidatorFactory:
    """
    Factory class for creating instances of token validators based on the model provider.
    This class provides a method to get an instance of a specific token validator
    based on the model provider and token model.
    """
    _token_validators = {
        "anthropic": AnthropicTokenValidator,
        "google": GoogleTokenValidator,
        "huggingface": HuggingFaceTokenValidator,
        "openai": OpenAITokenValidator
    }

    @classmethod
    def register_token_validator(cls, model_provider: str, token_validator_class):
        """
        A class method ot register custom token validators
        :param model_provider: provider of the model
        :param token_validator_class: custom token validator class
        """
        cls._token_validators[model_provider] = token_validator_class

    @staticmethod
    def get_instance(model_provider, **kwargs):
        """
        Get an instance of TokenValidatorFactory with the specified token model.
        :param model_provider:
        :return: An instance of TokenValidatorFactory.
        """
        if not model_provider:
            raise TokenValidationError("model_provider must be provided.")

        if model_provider in TokenValidatorFactory._token_validators:
            token_validator_cls = TokenValidatorFactory._token_validators[model_provider]
            return token_validator_cls.get_instance(**kwargs)
        else:
            raise TokenValidationError(f"Unsupported model provider: {model_provider}")