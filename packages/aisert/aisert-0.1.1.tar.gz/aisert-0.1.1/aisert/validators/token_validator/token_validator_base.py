import logging


class TokenValidatorBase:
    """
    Abstract base class for token counting implementations across different AI providers.
    
    Provides a common interface for token counting while allowing provider-specific
    implementations (OpenAI, Anthropic, HuggingFace, Google). Each provider has
    different tokenization methods and APIs.
    
    Subclasses must implement:
    - get_instance(): Factory method for singleton pattern
    - count(): Token counting logic for the specific provider
    
    Example:
        class MyTokenValidator(TokenValidatorBase):
            def count(self, text: str) -> int:
                return len(text.split())  # Simple word count
    """

    def __init__(self, model_provider: str = None):
        """
        Initialize base token validator.
        
        Args:
            model_provider: Name of the AI provider ("openai", "anthropic", etc.)
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_provider = model_provider

    def get_model_provider(self) -> str:
        """
        Get the AI provider name for this token validator.
        
        Returns:
            Provider name string (e.g., "openai", "anthropic")
        """
        return self.model_provider

    def _get_encoding(self):
        """
        Get the encoding client for tokenization (provider-specific).
        
        Must be implemented by subclasses to return the appropriate
        tokenizer/encoder for their specific provider.
        
        Returns:
            Provider-specific encoding client
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement the _get_encoding method.")

    @classmethod
    def get_instance(cls, **kwargs):
        """
        Factory method to get validator instance (typically singleton).
        
        Should be implemented by subclasses to return cached instances
        for performance, as tokenizers can be expensive to initialize.
        
        Args:
            **kwargs: Provider-specific configuration parameters
        
        Returns:
            Instance of the token validator
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement the get_instance method.")

    def count(self, text: str) -> int:
        """
        Count tokens in the provided text using provider-specific logic.
        
        Args:
            text: Input text to count tokens for
        
        Returns:
            Number of tokens in the text
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        
        Example:
            validator = OpenAITokenValidator.get_instance(token_model="gpt-4")
            count = validator.count("Hello world")  # Returns token count
        """
        raise NotImplementedError("Subclasses must implement the count method.")
