"""
Performance benchmarks and optimization examples for Aisert.

Shows:
1. Model loading vs cached performance
2. Batch processing optimization
3. Memory usage patterns
4. Provider performance comparison
5. Lightweight vs full validation trade-offs
"""

import time
import sys
import os
from typing import List
import psutil
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisert import Aisert, AisertConfig


def measure_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def semantic_model_loading_benchmark():
    """
    Benchmark semantic model loading times across different models.
    """
    print("\n=== Semantic Model Loading Benchmark ===")
    
    models = [
        "all-MiniLM-L6-v2",      # Recommended lightweight
        "all-MiniLM-L12-v2",     # Better quality
        "paraphrase-MiniLM-L3-v2",  # Ultra-fast
        "all-distilroberta-v1"   # Balanced
    ]
    
    test_text = "Artificial intelligence is transforming modern technology."
    expected_text = "AI and machine learning advances"
    
    results = []
    
    for model in models:
        print(f"\nTesting {model}:")
        
        config = AisertConfig(
            model_provider="openai",
            token_model="gpt-3.5-turbo",
            sentence_transformer_model=model
        )
        
        # Measure first load (includes model download/loading)
        start_memory = measure_memory_usage()
        start_time = time.time()
        
        try:
            result = (
                Aisert(test_text, config)
                .assert_semantic_matches(expected_text, threshold=0.5, strict=False)
                .collect()
            )
            
            first_load_time = time.time() - start_time
            memory_after_load = measure_memory_usage()
            
            # Measure cached performance
            start_time = time.time()
            
            result = (
                Aisert(test_text, config)
                .assert_semantic_matches(expected_text, threshold=0.5, strict=False)
                .collect()
            )
            
            cached_time = time.time() - start_time
            
            results.append({
                'model': model,
                'first_load': first_load_time,
                'cached': cached_time,
                'memory_mb': memory_after_load - start_memory,
                'speedup': first_load_time / cached_time if cached_time > 0 else 0
            })
            
            print(f"  First load: {first_load_time:.2f}s")
            print(f"  Cached: {cached_time:.3f}s")
            print(f"  Memory: +{memory_after_load - start_memory:.1f}MB")
            print(f"  Speedup: {first_load_time / cached_time:.1f}x")
            
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                'model': model,
                'first_load': float('inf'),
                'cached': float('inf'),
                'memory_mb': 0,
                'speedup': 0
            })
    
    # Summary
    print(f"\n{'Model':<25} {'First Load':<12} {'Cached':<10} {'Memory':<10} {'Speedup':<8}")
    print("-" * 70)
    
    for r in results:
        if r['first_load'] != float('inf'):
            print(f"{r['model']:<25} {r['first_load']:<12.2f} {r['cached']:<10.3f} {r['memory_mb']:<10.1f} {r['speedup']:<8.1f}x")
        else:
            print(f"{r['model']:<25} {'ERROR':<12} {'ERROR':<10} {'ERROR':<10} {'ERROR':<8}")


def batch_processing_benchmark():
    """
    Compare single vs batch processing performance.
    """
    print("\n=== Batch Processing Benchmark ===")
    
    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-3.5-turbo",
        sentence_transformer_model="all-MiniLM-L6-v2"
    )
    
    # Generate test data
    test_responses = [
        f"This is test response number {i} with some content to validate."
        for i in range(1, 51)  # 50 responses
    ]
    
    flagged_terms = ["spam", "inappropriate", "offensive"]
    
    print(f"Processing {len(test_responses)} responses...")
    
    # Method 1: Individual processing
    print("\nMethod 1: Individual Processing")
    start_time = time.time()
    
    individual_results = []
    for response in test_responses:
        result = (
            Aisert(response, config)
            .assert_not_contains(flagged_terms, strict=False)
            .assert_tokens(max_tokens=50, strict=False)
            .collect()
        )
        individual_results.append(result.status)
    
    individual_time = time.time() - start_time
    
    # Method 2: Optimized batch processing
    print("Method 2: Optimized Batch Processing")
    start_time = time.time()
    
    # Pre-warm the validators (load models once)
    warmup = Aisert("warmup", config).assert_tokens(max_tokens=10, strict=False).collect()
    
    batch_results = []
    for response in test_responses:
        # Reuse the same config and cached models
        result = (
            Aisert(response, config)
            .assert_not_contains(flagged_terms, strict=False)
            .assert_tokens(max_tokens=50, strict=False)
            .collect()
        )
        batch_results.append(result.status)
    
    batch_time = time.time() - start_time
    
    print(f"Individual processing: {individual_time:.2f}s ({individual_time/len(test_responses)*1000:.1f}ms per item)")
    print(f"Batch processing: {batch_time:.2f}s ({batch_time/len(test_responses)*1000:.1f}ms per item)")
    print(f"Improvement: {individual_time/batch_time:.1f}x faster")
    
    # Verify results are identical
    assert individual_results == batch_results, "Results should be identical"
    print("✅ Results verified identical")


def provider_performance_comparison():
    """
    Compare performance across different token counting providers.
    """
    print("\n=== Provider Performance Comparison ===")
    
    test_text = "The quick brown fox jumps over the lazy dog. " * 10  # Longer text
    
    providers = [
        ("openai", "gpt-3.5-turbo"),
        ("openai", "gpt-4"),
        # Note: Other providers require API keys and may not be available
    ]
    
    print(f"Testing with text length: {len(test_text)} characters")
    
    for provider, model in providers:
        print(f"\nTesting {provider} - {model}:")
        
        try:
            config = AisertConfig(
                model_provider=provider,
                token_model=model
            )
            
            # Warm up
            Aisert("warmup", config).assert_tokens(max_tokens=100, strict=False).collect()
            
            # Benchmark
            times = []
            for _ in range(5):  # 5 runs for average
                start_time = time.time()
                
                result = (
                    Aisert(test_text, config)
                    .assert_tokens(max_tokens=500, strict=False)
                    .collect()
                )
                
                times.append(time.time() - start_time)
            
            avg_time = sum(times) / len(times)
            
            # Extract token count from result
            token_info = list(result.rules.values())[0]['reason']
            
            print(f"  Average time: {avg_time:.3f}s")
            print(f"  Token info: {token_info}")
            
        except Exception as e:
            print(f"  Error: {e}")


def lightweight_vs_comprehensive_benchmark():
    """
    Compare lightweight validation vs comprehensive validation.
    """
    print("\n=== Lightweight vs Comprehensive Validation ===")
    
    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-3.5-turbo",
        sentence_transformer_model="all-MiniLM-L6-v2"
    )
    
    test_responses = [
        "Great product, very satisfied with the quality!",
        "The service was excellent and fast delivery.",
        "Not happy with this purchase, poor quality.",
        "Amazing customer support, solved my issue quickly.",
        "Would definitely recommend to others!"
    ]
    
    print(f"Testing {len(test_responses)} responses...")
    
    # Lightweight validation (content only)
    print("\nLightweight Validation (content only):")
    start_time = time.time()
    
    for response in test_responses:
        result = (
            Aisert(response, config)
            .assert_not_contains(["spam", "inappropriate"], strict=False)
            .collect()
        )
    
    lightweight_time = time.time() - start_time
    
    # Comprehensive validation (all validators)
    print("Comprehensive Validation (all validators):")
    start_time = time.time()
    
    for response in test_responses:
        result = (
            Aisert(response, config)
            .assert_contains(["the", "and", "with", "to"], strict=False)  # Common words
            .assert_not_contains(["spam", "inappropriate"], strict=False)
            .assert_tokens(max_tokens=100, strict=False)
            .assert_semantic_matches("customer feedback", threshold=0.3, strict=False)
            .collect()
        )
    
    comprehensive_time = time.time() - start_time
    
    print(f"\nLightweight: {lightweight_time:.2f}s ({lightweight_time/len(test_responses)*1000:.1f}ms per item)")
    print(f"Comprehensive: {comprehensive_time:.2f}s ({comprehensive_time/len(test_responses)*1000:.1f}ms per item)")
    print(f"Overhead: {comprehensive_time/lightweight_time:.1f}x slower for full validation")
    
    print("\n💡 Recommendation:")
    print("  - Use lightweight validation for high-volume, real-time scenarios")
    print("  - Use comprehensive validation for quality assurance and testing")


def concurrent_processing_benchmark():
    """
    Test concurrent processing performance.
    """
    print("\n=== Concurrent Processing Benchmark ===")
    
    config = AisertConfig(
        model_provider="openai",
        token_model="gpt-3.5-turbo",
        sentence_transformer_model="all-MiniLM-L6-v2"
    )
    
    test_responses = [f"Test response {i}" for i in range(20)]
    
    def validate_response(response):
        return (
            Aisert(response, config)
            .assert_contains(["Test"], strict=False)
            .assert_tokens(max_tokens=20, strict=False)
            .collect()
        )
    
    # Sequential processing
    print("Sequential processing:")
    start_time = time.time()
    
    sequential_results = [validate_response(response) for response in test_responses]
    
    sequential_time = time.time() - start_time
    
    # Concurrent processing
    print("Concurrent processing:")
    start_time = time.time()
    
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        concurrent_results = list(executor.map(validate_response, test_responses))
    
    concurrent_time = time.time() - start_time
    
    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Concurrent: {concurrent_time:.2f}s")
    print(f"Speedup: {sequential_time/concurrent_time:.1f}x")
    
    # Verify results
    sequential_status = [r.status for r in sequential_results]
    concurrent_status = [r.status for r in concurrent_results]
    assert sequential_status == concurrent_status, "Results should be identical"
    print("✅ Results verified identical")


if __name__ == "__main__":
    print("🚀 Aisert Performance Benchmarks")
    print("=" * 50)
    
    print("⚠️  Note: First run will be slower due to model downloads")
    print("📊 Running benchmarks...")
    
    semantic_model_loading_benchmark()
    batch_processing_benchmark()
    provider_performance_comparison()
    lightweight_vs_comprehensive_benchmark()
    concurrent_processing_benchmark()
    
    print("\n✨ Benchmarks completed!")
    print("\n💡 Key Takeaways:")
    print("  1. Use lightweight models (all-MiniLM-L6-v2) for faster loading")
    print("  2. Cache models by reusing the same config instance")
    print("  3. Choose validation complexity based on your performance requirements")
    print("  4. Consider concurrent processing for batch operations")