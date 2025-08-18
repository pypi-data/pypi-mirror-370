"""
Real-world Aisert examples demonstrating production use cases.

Shows:
1. Content moderation pipeline
2. API response validation
3. Educational content verification
4. Performance optimization with caching
5. Different tokenization models
6. Single vs multiple validator patterns
"""

import logging
import time
import sys
import os
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import Aisert, AisertConfig
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RealWorldExamples")


# Pydantic model for schema validation
class APIResponse(BaseModel):
    status: str
    data: Dict
    message: str


def content_moderation_pipeline():
    """
    Real-world content moderation for user-generated content.
    Shows single validator usage and performance optimization.
    """
    print("\n=== Content Moderation Pipeline ===")

    # Lightweight config for fast moderation
    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-3.5-turbo",
        sentence_transformer_model="all-MiniLM-L6-v2"  # Fast loading
    )

    user_comments = [
        "Great product! Really helpful for my work.",
        "This spam content contains inappropriate material and violence.",
        "Love the new features, very intuitive interface.",
        "Terrible service, complete garbage and waste of money.",
        "Excellent customer support, solved my issue quickly."
    ]

    # Flagged terms for moderation
    flagged_terms = ["spam", "inappropriate", "violence", "garbage", "terrible"]

    print("Moderating user comments...")
    start_time = time.time()

    moderation_results = []
    for i, comment in enumerate(user_comments, 1):
        # Single validator - content moderation only
        result = (
            Aisert(comment, config)
            .assert_not_contains(flagged_terms, strict=False)
            .collect()
        )

        status = "✅ APPROVED" if result.status else "❌ FLAGGED"
        print(f"Comment {i}: {status}")
        moderation_results.append(result.status)

    end_time = time.time()
    print(f"Processed {len(user_comments)} comments in {end_time - start_time:.2f}s")
    print(f"Approval rate: {sum(moderation_results) / len(moderation_results) * 100:.1f}%")


def api_response_validation():
    """
    Validate API responses with multiple validators.
    Shows schema + content + token validation.
    """
    print("\n=== API Response Validation ===")

    # Production config with token limits
    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-4",  # More accurate token counting
        sentence_transformer_model="all-MiniLM-L12-v2"
    )

    # Mock API responses
    api_responses = [
        {
            "response": '{"status": "success", "data": {"user_id": 123, "name": "John"}, "message": "User created successfully"}',
            "expected_content": ["success", "user_id", "created"]
        },
        {
            "response": '{"status": "error", "data": {}, "message": "Invalid input parameters provided"}',
            "expected_content": ["error", "message"]
        }
    ]

    print("Validating API responses...")

    for i, api_data in enumerate(api_responses, 1):
        print(f"\nValidating Response {i}:")

        # Multiple validators - comprehensive validation
        result = (
            Aisert(api_data["response"], config)
            .assert_schema(APIResponse, strict=False)  # Schema validation
            .assert_contains(api_data["expected_content"], strict=False)  # Content validation
            .assert_tokens(max_tokens=100, strict=False)  # Token limit
            .collect()
        )

        print(f"Overall Status: {'✅ VALID' if result.status else '❌ INVALID'}")

        # Detailed breakdown
        for order, validation in result.rules.items():
            status_icon = "✅" if validation['status'] else "❌"
            print(f"  {status_icon} {validation['validator']}: {validation['reason']}")


def caching_performance_demo():
    """
    Demonstrate caching performance benefits on repeated use.
    Shows 10x+ speedup with model reuse.
    """
    print("\n=== Caching Performance Demo ===")

    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-3.5-turbo",
        sentence_transformer_model="all-MiniLM-L6-v2"  # Fast model
    )

    test_content = "Python is a programming language for data science and web development."

    print("First run (model loading):")
    start_time = time.time()

    result = (
        Aisert(test_content, config)
        .assert_semantic_matches("programming language", threshold=0.6, strict=False)
        .collect()
    )

    first_run_time = time.time() - start_time

    print("Second run (cached models):")
    start_time = time.time()

    result = (
        Aisert(test_content, config)
        .assert_semantic_matches("software development", threshold=0.6, strict=False)
        .collect()
    )

    second_run_time = time.time() - start_time

    print(f"First run: {first_run_time:.2f}s (includes model loading)")
    print(f"Second run: {second_run_time:.3f}s (cached models)")
    print(f"Speedup: {first_run_time / second_run_time:.1f}x faster")


def different_tokenization_models():
    """
    Compare token counting across different models.
    Shows model-specific configurations.
    """
    print("\n=== Different Tokenization Models ===")

    test_text = "AI and machine learning are transforming technology."

    models = [
        ("openai", "gpt-3.5-turbo"),
        ("openai", "gpt-4"),
    ]

    print(f"Text: '{test_text}'")
    print("Token counts by model:")

    for provider, model in models:
        try:
            config = AisertConfig(provider, model)
            result = (
                Aisert(test_text, config)
                .assert_tokens(max_tokens=50, strict=False)
                .collect()
            )

            reason = list(result.rules.values())[0]['reason']
            print(f"  {model}: {reason}")

        except Exception as e:
            print(f"  {model}: Error - {e}")


def single_vs_multiple_validators():
    """
    Compare single validator vs multiple validator approaches.
    Shows when to use each pattern.
    """
    print("\n=== Single vs Multiple Validator Patterns ===")

    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-3.5-turbo",
        sentence_transformer_model="all-MiniLM-L6-v2"
    )

    response_text = "Thank you for your feedback! We'll improve our service quality."

    print("Single Validator Pattern (Quick Check):")
    start_time = time.time()

    # Just content moderation
    result = (
        Aisert(response_text, config)
        .assert_not_contains(["spam", "inappropriate", "offensive"], strict=False)
        .collect()
    )

    single_time = time.time() - start_time
    print(f"Result: {'✅ PASS' if result.status else '❌ FAIL'} ({single_time:.3f}s)")

    print("\nMultiple Validator Pattern (Comprehensive Check):")
    start_time = time.time()

    # Full validation suite
    result = (
        Aisert(response_text, config)
        .assert_contains(["thank", "feedback"], strict=False)  # Positive indicators
        .assert_not_contains(["spam", "inappropriate"], strict=False)  # Content moderation
        .assert_tokens(max_tokens=50, strict=False)  # Length check
        .assert_semantic_matches("customer service response", threshold=0.5, strict=False)  # Context check
        .collect()
    )

    multiple_time = time.time() - start_time
    print(f"Result: {'✅ PASS' if result.status else '❌ FAIL'} ({multiple_time:.3f}s)")

    print(f"\nPerformance: Single {single_time:.3f}s vs Multiple {multiple_time:.3f}s")
    print(f"Trade-off: {multiple_time / single_time:.1f}x slower for comprehensive validation")

    result = (
        Aisert(response_text, config)
        .assert_contains(["thank", "feedback"], strict=False)  # Positive indicators
        .assert_not_contains(["spam", "inappropriate"], strict=False)  # Content moderation
        .assert_tokens(max_tokens=50, strict=False)  # Length check
        .assert_semantic_matches("customer service response", threshold=0.5, strict=False)  # Context check
        .collect()
    )

    multiple_time = time.time() - start_time
    print(f"Result: {'✅ PASS' if result.status else '❌ FAIL'} ({multiple_time:.3f}s)")

    # Detailed breakdown
    print("\nValidation Breakdown:")
    for order, validation in result.rules.items():
        status_icon = "✅" if validation['status'] else "❌"
        print(f"  {order}. {status_icon} {validation['validator']}")

    print(f"\nPerformance: Single validator {single_time:.3f}s vs Multiple validators {multiple_time:.3f}s")


if __name__ == "__main__":
    print("🚀 Aisert Real-World Examples")
    print("=" * 50)

    content_moderation_pipeline()
    api_response_validation()
    caching_performance_demo()
    different_tokenization_models()
    single_vs_multiple_validators()

    print("\n✨ Examples completed!")
    print("💡 Key takeaways:")
    print("  - Use single validators for fast, focused checks")
    print("  - Use multiple validators for comprehensive validation")
    print("  - Model caching provides 10x+ speedup on repeated use")
    print("  - Choose lightweight models for faster loading")
