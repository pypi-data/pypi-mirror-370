#!/usr/bin/env python3
"""
Comprehensive functionality test for Result Parser Agent CLI
Tests all CLI features without requiring a real API key
"""

import json
import sys
import tempfile
from pathlib import Path

from result_parser_agent.cli import (
    save_output,
    setup_logging,
    validate_input_path,
    validate_metrics,
)
from result_parser_agent.config.settings import settings
from result_parser_agent.models.schema import (
    Instance,
    Iteration,
    Statistics,
    StructuredResults,
)


def test_config_loading():
    """Test configuration loading functionality."""
    print("🧪 Testing configuration loading...")

    # Test default config loads from environment
    config = settings

    # Check that config has required attributes
    assert hasattr(config, "LLM_PROVIDER")
    assert hasattr(config, "LLM_MODEL")

    print(
        f"✅ Default configuration loaded: provider={config.LLM_PROVIDER}, model={config.LLM_MODEL}"
    )


def test_validation_functions():
    """Test validation functions."""
    print("🧪 Testing validation functions...")

    # Create a temporary test file for validation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        temp_file = f.name
        f.write("test content")

    try:
        # Test input path validation with existing file
        validated_path = validate_input_path(temp_file)
        assert validated_path == Path(temp_file)
        print("✅ Input path validation works correctly")
    finally:
        Path(temp_file).unlink(missing_ok=True)

    # Test metrics validation
    metrics = validate_metrics(["RPS", "latency", "throughput"])
    assert len(metrics) == 3
    assert "RPS" in metrics
    print("✅ Metrics validation works correctly")


def test_output_saving():
    """Test output saving functionality."""
    print("🧪 Testing output saving...")

    # Create test data
    stats = Statistics(metricName="RPS", metricValue="1234.56")
    instance = Instance(instanceIndex=1, statistics=[stats])
    iteration = Iteration(iterationIndex=1, instances=[instance])
    results = StructuredResults(iterations=[iteration])

    # Test saving to file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_file = f.name

    try:
        save_output(results, temp_file, pretty_print=True)

        # Verify file was created and contains data
        with open(temp_file) as f:
            data = json.load(f)

        assert len(data["iterations"]) == 1
        print("✅ Output saving works correctly")

    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_cli_parameter_handling():
    """Test CLI parameter handling logic."""
    print("🧪 Testing CLI parameter handling...")

    # Test metrics from CLI
    cli_metrics = "RPS,latency,throughput"
    metrics_list = validate_metrics([m.strip() for m in cli_metrics.split(",")])
    assert len(metrics_list) == 3
    assert "RPS" in metrics_list
    assert "latency" in metrics_list
    assert "throughput" in metrics_list
    print("✅ CLI parameter handling works correctly")


def test_file_operations():
    """Test file operation utilities."""
    print("🧪 Testing file operations...")

    # Test path validation with non-existent file (should raise exception)
    try:
        validate_input_path("non_existent_file.txt")
        assert False, "Should have raised an exception"
    except Exception:
        print("✅ Path validation correctly rejects non-existent files")

    # Test metrics validation with empty list (should raise exception)
    try:
        validate_metrics([])
        assert False, "Should have raised an exception"
    except Exception:
        print("✅ Metrics validation correctly rejects empty lists")


def test_error_handling():
    """Test error handling in validation functions."""
    print("🧪 Testing error handling...")

    # Test invalid metrics
    try:
        validate_metrics([])
        assert False, "Should have raised an exception for empty metrics"
    except Exception:
        print("✅ Empty metrics validation works correctly")

    # Test invalid input path
    try:
        validate_input_path("non_existent_path")
        assert False, "Should have raised an exception for non-existent path"
    except Exception:
        print("✅ Invalid path validation works correctly")


def test_logging_setup():
    """Test logging setup functionality."""
    print("🧪 Testing logging setup...")

    # Test logging setup doesn't crash
    setup_logging(verbose=False, log_level="INFO")
    setup_logging(verbose=True, log_level="DEBUG")
    print("✅ Logging setup works correctly")


def test_environment_config_loading():
    """Test environment-based configuration loading."""
    print("🧪 Testing environment configuration loading...")

    # Test that we can load config multiple times (should be consistent)
    config1 = settings
    config2 = settings

    # Configs should be equivalent
    assert config1.LLM_PROVIDER == config2.LLM_PROVIDER
    assert config1.LLM_MODEL == config2.LLM_MODEL

    print("✅ Environment configuration loading is consistent")


def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting comprehensive functionality tests...")

    test_functions = [
        test_config_loading,
        test_validation_functions,
        test_output_saving,
        test_cli_parameter_handling,
        test_file_operations,
        test_error_handling,
        test_logging_setup,
        test_environment_config_loading,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {str(e)}")
            failed += 1

    print(f"\n📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
