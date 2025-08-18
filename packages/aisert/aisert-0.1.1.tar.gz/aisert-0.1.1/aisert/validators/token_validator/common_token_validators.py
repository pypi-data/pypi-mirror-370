from functools import cached_property
from typing import Dict, List
from .token_validator_base import TokenValidatorBase
from ...exception import TokenValidationError

import threading


class OpenAITokenValidator(TokenValidatorBase):
    """
    A token counter for OpenAI models.
    """
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, token_model, token_encoding):
        super().__init__(model_provider="openai")
        self.token_model = token_model
        self.token_encoding = token_encoding

    @classmethod
    def get_instance(cls, token_model: str = None, token_encoding: str = None, **kwargs):
        if not token_encoding and not token_model:
            raise TokenValidationError("Either token_encoding or token_model must be provided.")

        key = token_encoding or token_model
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(token_model, token_encoding)
            return cls._instances[key]

    @cached_property
    def encoding_client(self):
        """
        Returns the encoding for the specified encoding name.
        :return: The encoding object.
        """
        import tiktoken

        try:
            if self.token_encoding:
                self.logger.info(f"Using token encoding: {self.token_encoding}")
                try:
                    if self.token_encoding not in tiktoken.list_encodings():
                        raise TokenValidationError(
                            f"Encoding {self.token_encoding} not found in tiktoken."
                        )
                    else:
                        return tiktoken.get_encoding(self.token_encoding)
                except Exception as e:
                    raise TokenValidationError(
                        f"Failed to get encoding for {self.token_encoding}: {e}"
                    )
            return tiktoken.encoding_for_model(self.token_model)
        except Exception as e:
            raise TokenValidationError(
                f"Failed to get tiktoken encoding_for_model: {e}"
            )

    def count(self, text):
        """
        Counts the number of tokens in the provided text.
        :param text: The input text to count tokens from.
        :return: The number of tokens in the text.
        """
        try:
            token_length = len(self.encoding_client.encode(text))
            self.logger.info(f"Token size is {token_length}.")
            return token_length
        except Exception as e:
            raise TokenValidationError(
                f"Failed to count tokens for model {self.token_model}: {e}",
            )


class HuggingFaceTokenValidator(TokenValidatorBase):
    """
    A token counter for Hugging Face models.
    """

    _instances = {}
    _lock = threading.RLock()

    def __init__(self, token_model):
        super().__init__(model_provider="huggingface")
        self.token_model = token_model

    @classmethod
    def get_instance(cls, token_model: str = None, **kwargs):
        """
        Get an instance of HuggingFaceTokenValidator with the specified token model.
        :param token_model: The model to use for token counting.
        :return: An instance of HuggingFaceTokenValidator.
        """
        if not token_model:
            raise TokenValidationError("parameter token_model must be provided.")

        with cls._lock:
            if token_model not in cls._instances:
                cls._instances[token_model] = cls(token_model)
            return cls._instances[token_model]

    @cached_property
    def encoding_client(self):
        """
        Returns the encoding for the specified token model.
        :return: The encoding object.
        """
        from transformers import AutoTokenizer

        try:
            self.logger.info(f"Using token model: {self.token_model}")
            tokenizer = AutoTokenizer.from_pretrained(self.token_model)
            return tokenizer
        except Exception as e:
            raise TokenValidationError(
                f"Failed to get AutoTokenizer: {e}"
            )

    def count(self, text):
        try:
            token_length = len(self.encoding_client.encode(text))
            self.logger.info(f"Token size is {token_length}.")
            return token_length
        except Exception as e:
            raise TokenValidationError(
                f"Failed to load tokenizer for model {self.token_model}: {e}",
            )


class AnthropicTokenValidator(TokenValidatorBase):
    """
    A token counter for Anthropic models.
    """

    _instances = {}
    _lock = threading.RLock()

    def __init__(self, token_model):
        super().__init__(model_provider="anthropic")
        self.token_model = token_model

    @classmethod
    def get_instance(cls, token_model: str = None, **kwargs):
        """
        Get an instance of AnthropicTokenValidator with the specified token model.
        :param token_model: The model to use for token counting.
        :return: An instance of AnthropicTokenValidator.
        """
        if not token_model:
            raise TokenValidationError("token_model must be provided.")

        with cls._lock:
            if token_model not in cls._instances:
                cls._instances[token_model] = cls(token_model)
            return cls._instances[token_model]

    @cached_property
    def encoding_client(self):
        """
        Returns the encoding for the specified token model.
        :return: The encoding object.
        """
        import anthropic

        try:
            return anthropic.Client()
        except Exception as e:
            raise TokenValidationError(
                f"Failed to get anthropic client: {e}"
            )

    def count(self, text):
        """
        Counts the number of tokens in the provided text.
        :param text: The input text to count tokens from.
        :return: The number of tokens in the text.
        """
        try:
            token_length = self.encoding_client.count_tokens(
                model=self.token_model, messages=text
            )
            self.logger.info(f"Token size is {token_length}.")
            return token_length
        except Exception as e:
            raise TokenValidationError(
                f"Failed to count tokens for model {self.token_model}: {e}",
            )


class GoogleTokenValidator(TokenValidatorBase):
    """
    A token counter for Google models.
    """

    _instances = {}
    _lock = threading.RLock()

    def __init__(self, token_model):
        super().__init__(model_provider="google")
        self.token_model = token_model

    @classmethod
    def get_instance(cls, token_model: str = None, **kwargs):
        """
        Get an instance of GoogleTokenValidator with the specified token model.
        :param token_model: The model to use for token counting.
        :return: An instance of GoogleTokenValidator.
        """
        if not token_model:
            raise TokenValidationError("token_model must be provided.")

        with cls._lock:
            if token_model not in cls._instances:
                cls._instances[token_model] = cls(token_model)
            return cls._instances[token_model]

    @cached_property
    def encoding_client(self):
        """
        Returns the encoding for the specified encoding name.
        :return: The encoding object.
        """
        try:
            from google import genai
            return genai.Client()
        except Exception as e:
            raise TokenValidationError(
                f"Failed to get google genai client: {e}"
            )

    def count(self, text):
        """
        Counts the number of tokens in the provided text.
        :param text: The input text to count tokens from.
        :return: The number of tokens in the text.
        """
        try:
            token_length = self.encoding_client.models.count_tokens(
                model=self.token_model,
                contents=text
            ).total_tokens
            self.logger.info(f"Token size is {token_length}.")
            return token_length
        except Exception as e:
            raise TokenValidationError(
                f"Failed to count tokens for model {self.token_model}: {e}",
            )
