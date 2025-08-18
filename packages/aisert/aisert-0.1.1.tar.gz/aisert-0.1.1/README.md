# Aisert 🚀

> Assert-style validation library for AI outputs - ensure your LLMs behave exactly as expected

✨ Validate AI responses with confidence!  
🔗 Fluent, chainable API for comprehensive AI output validation  
🎯 From token counts to semantic similarity - production-ready validation

> ⚠️ **Alpha Release** - Currently in alpha. Feedbacks welcome!

## Who Is This For? 👥

**AI/ML Engineers** - Just like you use `assert` statements in unit tests, use Aisert to validate LLM outputs in production  
**QA Engineers** - Automated testing for AI responses, similar to how Selenium tests web UIs  
**DevOps Teams** - Monitor AI model performance and catch regressions, like APM tools for traditional apps  
**Product Teams** - Ensure AI features meet quality standards before reaching users

## Features

- **Fluent Interface**: Chain multiple validations with a beautiful, readable API
- **Multiple Validators**: Schema, content, token count, and semantic similarity validation
- **Flexible Modes**: Strict mode (raises exceptions) or non-strict mode (collects results)
- **Thread-Safe**: Production-ready with proper concurrency handling and model caching
- **Multi-Provider Support**: OpenAI, Anthropic, HuggingFace, and Google token counting
- **Extensible**: Custom token validators via TokenValidatorBase inheritance

## Prerequisites & Setup

### System Requirements
- Python >= 3.9
- 1GB+ RAM (for semantic models)
- 500MB+ disk space (model downloads)

### API Keys (for token counting)
```bash
# Set environment variables for your providers
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Installation

```bash
pip install aisert
```

## Quick Start

```python
from aisert import Aisert, AisertConfig

# Configure for your AI model
config = AisertConfig(
    token_model="gpt-3.5-turbo",
    model_provider="openai"
)

# Validate AI response with fluent interface
result = (
    Aisert(content="Paris is the capital of France.", config=config)
    .assert_contains(["Paris", "France"])
    .assert_tokens(max_tokens=50)
    .assert_semantic_matches("France's capital", threshold=0.8)
    .collect()
)

print(f"Validation passed: {result.status}")
print(f"Details: {result.rules}")
```

## Validation Types

### Content Validation
```python
# Check if response contains specific items
Aisert(content).assert_contains(["keyword1", "keyword2"])

# Check if response doesn't contain items
Aisert(content).assert_not_contains(["spam", "inappropriate"])
```

### Token Count Validation
```python
# Ensure response is within token limits (requires API call)
Aisert(content, config).assert_tokens(max_tokens=100)
```

### Schema Validation
```python
# Validate with Pydantic model
from pydantic import BaseModel

class UserModel(BaseModel):
    name: str
    age: int

Aisert(json_content).assert_schema(UserModel)
```

### Semantic Similarity
```python
# Check semantic similarity (first run loads model, then fast)
# Loading time varies by model - use lightweight models for speed
Aisert(content).assert_semantic_matches(
    expected="Information about artificial intelligence",
    threshold=0.75
)
```

## Validation Patterns

### Content Moderation (Instant)
```python
# Fast validation - no model loading required
result = Aisert(content).assert_not_contains(["spam", "inappropriate"]).collect()
```

### API Response Validation (Comprehensive)
```python
# Full validation with all validators
result = (
    Aisert(content, config)
    .assert_contains(["required_info"])
    .assert_tokens(max_tokens=100)
    .assert_semantic_matches("expected meaning", 0.8)
    .collect()
)
```

### Performance-Optimized (Selective)
```python
# Use only needed validators for optimal performance
result = (
    Aisert(content, config)
    .assert_not_contains(["inappropriate"])
    .assert_tokens(max_tokens=200)
    .collect()
)
```

## Validation Modes

### Strict Mode (Default)
Raises exceptions immediately when validation fails:

```python
try:
    Aisert(content).assert_contains(["required_term"])
except AisertError as e:
    print(f"Validation failed: {e}")
```

### Non-Strict Mode
Collects all validation results without raising exceptions:

```python
result = (
    Aisert(content)
    .assert_contains(["term1"], strict=False)
    .assert_tokens(100, strict=False)
    .collect()
)

if not result.status:
    print("Some validations failed:", result.rules)
```

## Configuration

```python
from aisert import AisertConfig

config = AisertConfig(
    token_model="gpt-4",           # Model for token counting
    model_provider="openai",       # Provider: "openai", "anthropic", "huggingface", "google"
    token_encoding=None,           # Custom encoding (OpenAI only)
    sentence_transformer_model="all-MiniLM-L6-v2"  # Semantic similarity model
)
```

## Real-World Examples

### API Response Validation
```python
def validate_chatbot_response(response_text):
    return (
        Aisert(response_text, config)
        .assert_not_contains(["inappropriate", "harmful"])
        .assert_tokens(max_tokens=500)
        .assert_semantic_matches("helpful customer service", 0.7)
        .collect()
    )
```

### Content Moderation
```python
def moderate_content(user_content):
    moderation_result = (
        Aisert(user_content)
        .assert_not_contains(["spam", "offensive"], strict=False)
        .assert_tokens(max_tokens=1000, strict=False)
        .collect()
    )
    
    return moderation_result.status
```

### Batch Processing
```python
def validate_multiple_responses(responses):
    results = []
    for response in responses:
        result = (
            Aisert(response, config)
            .assert_contains(["required_info"], strict=False)
            .assert_tokens(200, strict=False)
            .collect()
        )
        results.append(result)
    return results
```

## Exception Handling

Aisert provides specific exceptions for different validation types:

```python
from aisert import AisertError
from aisert.exception import (
    SchemaValidationError,    # Schema validation failures
    ContainsValidationError,  # Content validation failures
    TokenValidationError,     # Token count validation failures
    SemanticValidationError   # Semantic similarity failures
)

try:
    Aisert(content).assert_schema(UserModel)
except SchemaValidationError as e:
    print(f"Schema validation failed: {e}")
except AisertError as e:
    print(f"General validation error: {e}")
```

## Performance Notes 📝

- **First Run**: Semantic validation slower initially (model loading time varies by model) ⏳
- **Subsequent**: All validations fast (<100ms) ⚡
- **Selective Usage**: Use only needed validators for optimal performance 🎯
- **Model Caching**: Models cached after first load for 10x+ speedup 🚀
- **Thread Safety**: All validators use singleton pattern with proper locking 🔒
- **Default Config**: Uses OpenAI gpt-3.5-turbo and all-MiniLM-L6-v2 by default ⚙️

## Troubleshooting 🔧

### Common Issues

**Model Loading Timeout**
```python
# Use lightweight model for faster loading
config = AisertConfig(
    sentence_transformer_model="paraphrase-MiniLM-L3-v2"  # Ultra-fast
)
```

**API Key Errors**
```bash
# Ensure environment variables are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

**Memory Issues**
- Semantic models use 100-500MB RAM
- Use lightweight models on resource-constrained systems
- Consider content-only validation for high-volume scenarios

**Dependency Conflicts**
```bash
# Install in clean environment
python -m venv aisert-env
source aisert-env/bin/activate  # or aisert-env\Scripts\activate on Windows
pip install aisert
```

## Current Limitations ⚠️

- **Schema Validation**: Only supports Pydantic models and TypeAdapter, not raw JSON schemas
- **Semantic Models**: Limited to sentence-transformers compatible models

## Supported Providers 🌐

- **OpenAI**: tiktoken-based encoding with model-specific tokenizers
- **Anthropic**: Native anthropic client token counting
- **HuggingFace**: AutoTokenizer from transformers library
- **Google**: genai client integration (experimental)
- **Custom**: Extend TokenValidatorBase for additional providers

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [Homepage](https://github.com/haipad/aisert)
- [Issues](https://github.com/haipad/aisert/issues)