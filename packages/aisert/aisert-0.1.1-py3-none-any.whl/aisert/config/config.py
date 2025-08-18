import logging

from aisert.config.defaults import DefaultConfig


class AisertConfig:
    """
    Configuration settings for Aisert validation operations.
    
    Controls token counting providers, models, and semantic similarity settings.
    Supports multiple AI providers: OpenAI, Anthropic, HuggingFace, Google.
    
    Example:
        config = AisertConfig(
            model_provider="openai",
            token_model="gpt-4",
            sentence_transformer_model="all-MiniLM-L6-v2"
        )
    """
    logger = logging.getLogger("AisertConfig")

    def __init__(
        self,
        model_provider: str,
        token_model: str,
        token_encoding: str = None,
        sentence_transformer_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize configuration with AI provider and model settings.
        
        Args:
            model_provider: AI provider ("openai", "anthropic", "huggingface", "google")
            token_model: Specific model for token counting (e.g., "gpt-4", "claude-3")
            token_encoding: Token encoding method (OpenAI only, e.g., "cl100k_base")
            sentence_transformer_model: Model for semantic similarity (default: "all-MiniLM-L6-v1")
        
        Example:
            config = AisertConfig("openai", "gpt-3.5-turbo", token_encoding="cl100k_base")
        """
        self.mode = "default"
        self.logger = logging.getLogger(self.__class__.__name__)

        self.token_encoding = token_encoding
        self.token_model = token_model
        self.model_provider = model_provider
        self.sentence_transformer_model = sentence_transformer_model

    @staticmethod
    def get_default_config():
        """
        Get default configuration optimized for most common use cases.
        
        Returns:
            AisertConfig with OpenAI gpt-3.5-turbo and all-MiniLM-L6-v2 models
        
        Example:
            config = AisertConfig.get_default_config()
            # Uses: openai provider, gpt-3.5-turbo, all-MiniLM-L6-v2
        """
        default_config = DefaultConfig.to_dict()
        return AisertConfig(**default_config)

    @staticmethod
    def load(file_path: str) -> "AisertConfig":
        """
        Load configuration from a JSON file with fallback to defaults.
        
        Args:
            file_path: Path to JSON configuration file
        
        Returns:
            AisertConfig loaded from file, or default config if file invalid/missing
        
        Example:
            config = AisertConfig.load("my_config.json")
            # Falls back to defaults if file not found or invalid JSON
        """
        import json
        import os

        #Sanitize file path
        file_path = os.path.abspath(file_path)
        try:
            with open(file_path, "r") as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError as e:
                    AisertConfig.logger.error(
                        f"Error decoding JSON from {file_path}: {e}"
                    )
                    AisertConfig.logger.info("Using default configuration.")
                    return AisertConfig.get_default_config()
        except FileNotFoundError:
            AisertConfig.logger.error(f"Configuration file {file_path} not found.")
            AisertConfig.logger.info(f"Using default configuration.")
            return AisertConfig.get_default_config()
        return AisertConfig(**config_data)


    def __repr__(self):
        return (
            f"AisertConfig(token_encoding={self.token_encoding}, "
            f"token_model={self.token_model}, "
            f"model_provider={self.model_provider}, "
            f"sentence_transformer_model={self.sentence_transformer_model})"
        )
