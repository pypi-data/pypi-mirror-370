

from typing import Dict


class DefaultConfig:
    """
    Default configuration for Aserti.i
    This class holds the default settings for the Asert application.
    """

    # Default values for the configuration
    token_encoding: str = None
    token_model: str = "gpt-3.5-turbo"
    model_provider: str = "openai"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"

    @staticmethod
    def to_dict() -> Dict[str, str]:
        """
        Converts the DefaultConfig to a dictionary.
        :return: A dictionary containing the default configuration values.
        """
        return {
            "token_encoding": DefaultConfig.token_encoding,
            "token_model": DefaultConfig.token_model,
            "model_provider": DefaultConfig.model_provider,
            "sentence_transformer_model": DefaultConfig.sentence_transformer_model,
        }