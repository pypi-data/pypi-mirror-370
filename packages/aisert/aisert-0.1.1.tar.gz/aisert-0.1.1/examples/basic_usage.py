"""
Basic Aisert usage examples for getting started.

Shows:
1. Simple validation with default config
2. Custom configuration
3. Strict vs non-strict modes
4. Basic error handling
"""

import logging
import sys
import os

# Add parent directory to path to import aisert
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import Aisert, AisertConfig
from pydantic import BaseModel

logging.basicConfig(level=logging.WARNING)  # Reduce noise for examples
logger = logging.getLogger("BasicUsageExample")


class UserModel(BaseModel):
    name: str
    email: str
    age: int


def simple_validation_example():
    """
    Simplest possible Aisert usage with default configuration.
    """
    print("\n=== Simple Validation Example ===")
    
    response = "Paris is the capital of France."
    
    # Use default configuration (no setup required)
    result = (
        Aisert(response)
        .assert_contains(["Paris", "France"])
        .collect()
    )
    
    print(f"✅ Validation passed: {result.status}")
    print(f"Details: {result.rules}")


def custom_configuration_example():
    """
    Using custom configuration for specific AI providers.
    """
    print("\n=== Custom Configuration Example ===")
    
    # Custom config for OpenAI with specific model
    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-4",
        sentence_transformer_model="all-MiniLM-L6-v2"  # Faster loading
    )
    
    response = "The weather today is sunny and warm."
    
    result = (
        Aisert(response, config)
        .assert_contains(["weather"])
        .assert_tokens(max_tokens=20)
        .collect()
    )
    
    print(f"Status: {'✅ PASS' if result.status else '❌ FAIL'}")
    for order, validation in result.rules.items():
        print(f"  {order}. {validation['validator']}: {validation['status']}")


def strict_vs_non_strict_modes():
    """
    Demonstrate strict mode (raises exceptions) vs non-strict mode (collects errors).
    """
    print("\n=== Strict vs Non-Strict Modes ===")
    
    response = "Hello world"
    
    print("Non-strict mode (collects all errors):")
    result = (
        Aisert(response)
        .assert_contains(["Hello"], strict=False)  # Will pass
        .assert_contains(["missing"], strict=False)  # Will fail but continue
        .assert_tokens(max_tokens=5, strict=False)  # Will fail but continue
        .collect()
    )
    
    print(f"Overall status: {result.status}")
    for order, validation in result.rules.items():
        status_icon = "✅" if validation['status'] else "❌"
        print(f"  {status_icon} {validation['validator']}: {validation['reason']}")
    
    print("\nStrict mode (stops at first error):")
    try:
        result = (
            Aisert(response)
            .assert_contains(["Hello"])  # Will pass
            .assert_contains(["missing"])  # Will raise exception here
            .collect()
        )
    except Exception as e:
        print(f"❌ Exception raised: {e}")


def schema_validation_example():
    """
    Validate JSON responses against Pydantic models.
    """
    print("\n=== Schema Validation Example ===")
    
    # Valid JSON response
    valid_json = '{"name": "John Doe", "email": "john@example.com", "age": 30}'
    
    result = (
        Aisert(valid_json)
        .assert_schema(UserModel, strict=False)
        .assert_contains(["name", "email"], strict=False)
        .collect()
    )
    
    print(f"Valid JSON: {'✅ PASS' if result.status else '❌ FAIL'}")
    
    # Invalid JSON response
    invalid_json = '{"name": "John Doe", "age": "thirty"}'
    
    result = (
        Aisert(invalid_json)
        .assert_schema(UserModel, strict=False)
        .collect()
    )
    
    print(f"Invalid JSON: {'✅ PASS' if result.status else '❌ FAIL'}")
    if not result.status:
        print(f"  Error: {list(result.rules.values())[0]['reason'][:100]}...")


def content_moderation_example():
    """
    Real-world content moderation use case.
    """
    print("\n=== Content Moderation Example ===")
    
    user_comments = [
        "Great product, really helpful!",
        "This is spam content with inappropriate language",
        "Excellent customer service"
    ]
    
    flagged_terms = ["spam", "inappropriate", "offensive"]
    
    for i, comment in enumerate(user_comments, 1):
        result = (
            Aisert(comment)
            .assert_not_contains(flagged_terms, strict=False)
            .collect()
        )
        
        status = "✅ APPROVED" if result.status else "❌ FLAGGED"
        print(f"Comment {i}: {status}")
        if not result.status:
            print(f"  Reason: {list(result.rules.values())[0]['reason']}")

def error_handling_example():
    """
    Proper error handling patterns.
    """
    print("\n=== Error Handling Example ===")
    
    from aisert.exception import AisertError, ContainsValidationError
    
    response = "Hello world"
    
    # Method 1: Try-catch for strict mode
    try:
        result = (
            Aisert(response)
            .assert_contains(["missing_word"])  # This will fail
            .collect()
        )
    except ContainsValidationError as e:
        print(f"Caught specific error: {e}")
    except AisertError as e:
        print(f"Caught general Aisert error: {e}")
    
    # Method 2: Non-strict mode for graceful handling
    result = (
        Aisert(response)
        .assert_contains(["Hello"], strict=False)  # Pass
        .assert_contains(["missing"], strict=False)  # Fail gracefully
        .collect()
    )
    
    if result.status:
        print("✅ All validations passed")
    else:
        print("❌ Some validations failed:")
        for order, validation in result.rules.items():
            if not validation['status']:
                print(f"  - {validation['validator']}: {validation['reason']}")

if __name__ == "__main__":
    print("🚀 Aisert Basic Usage Examples")
    print("=" * 40)
    
    simple_validation_example()
    custom_configuration_example()
    strict_vs_non_strict_modes()
    schema_validation_example()
    content_moderation_example()
    error_handling_example()
    
    print("\n✨ Basic examples completed! Check out real_world_examples.py for advanced patterns.")
