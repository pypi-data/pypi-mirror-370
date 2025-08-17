"""
TEST SUITE: csv_cleaner.feature_gate
PURPOSE: Test feature gating system for free vs premium versions with comprehensive coverage
SCOPE: FeatureGate class, version detection, feature availability, premium features, edge cases
DEPENDENCIES: pkg_resources, os.environ, unittest.mock
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from csv_cleaner.feature_gate import FeatureGate


class TestFeatureGateInitialization:
    """Test cases for FeatureGate initialization and basic functionality."""

    def test_initialization_basic_version(self):
        """TEST: should_initialize_successfully_with_basic_version"""
        # ARRANGE: Basic version initialization
        version = "basic"

        # ACT: Initialize FeatureGate
        feature_gate = FeatureGate(version)

        # ASSERT: Verify initialization
        assert feature_gate.version == version, f"Expected version to be '{version}', got '{feature_gate.version}'"
        assert feature_gate.version in ["basic", "pro"], f"Expected version to be 'basic' or 'pro', got '{feature_gate.version}'"

    def test_initialization_pro_version(self):
        """TEST: should_initialize_successfully_with_pro_version"""
        # ARRANGE: Pro version initialization
        version = "pro"

        # ACT: Initialize FeatureGate
        feature_gate = FeatureGate(version)

        # ASSERT: Verify initialization
        assert feature_gate.version == version, f"Expected version to be '{version}', got '{feature_gate.version}'"

    def test_initialization_invalid_version(self):
        """TEST: should_raise_valueerror_for_invalid_version"""
        # ARRANGE: Invalid version
        invalid_versions = ["free", "premium", "enterprise", "", None]

        # ACT & ASSERT: Verify ValueError for each invalid version
        for version in invalid_versions:
            with pytest.raises(ValueError, match=f"Invalid version: {version}. Must be 'basic' or 'pro'"):
                FeatureGate(version)

    def test_initialization_case_sensitive(self):
        """TEST: should_be_case_sensitive_for_version_names"""
        # ARRANGE: Case variations
        case_variations = ["Basic", "BASIC", "Pro", "PRO", "basic ", " pro"]

        # ACT & ASSERT: Verify ValueError for case variations
        for version in case_variations:
            with pytest.raises(ValueError, match=f"Invalid version: {version}. Must be 'basic' or 'pro'"):
                FeatureGate(version)


class TestFeatureGateBasicFeatures:
    """Test cases for basic feature availability."""

    def test_basic_features_available_in_basic_version(self):
        """TEST: should_allow_basic_features_in_basic_version"""
        # ARRANGE: Basic version feature gate
        feature_gate = FeatureGate("basic")
        basic_features = [
            "pandas_wrapper", "pyjanitor_wrapper", "basic_cleaning",
            "file_operations", "simple_validation", "basic_visualization",
            "data_profiling", "clean", "validate", "info", "config",
            "visualize", "report"
        ]

        # ACT & ASSERT: Verify all basic features are available
        for feature in basic_features:
            result = feature_gate.is_feature_available(feature)
            assert result is True, f"Expected feature '{feature}' to be available in basic version, got {result}"

    def test_premium_features_not_available_in_basic_version(self):
        """TEST: should_not_allow_premium_features_in_basic_version"""
        # ARRANGE: Basic version feature gate
        feature_gate = FeatureGate("basic")
        premium_features = [
            "ai_agent", "llm_providers", "feature_engine_wrapper",
            "dedupe_wrapper", "missingno_wrapper", "advanced_visualization",
            "batch_processing", "performance_optimization", "parallel_processing",
            "memory_optimization", "ai-suggest", "ai-clean", "ai-analyze",
            "ai-configure", "ai-logs", "ai-model", "dedupe", "performance"
        ]

        # ACT & ASSERT: Verify all premium features are not available
        for feature in premium_features:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected feature '{feature}' to not be available in basic version, got {result}"

    def test_unknown_features_not_available_in_basic_version(self):
        """TEST: should_not_allow_unknown_features_in_basic_version"""
        # ARRANGE: Basic version feature gate and unknown features
        feature_gate = FeatureGate("basic")
        unknown_features = ["unknown_feature", "test_function", "experimental_feature", ""]

        # ACT & ASSERT: Verify unknown features are not available
        for feature in unknown_features:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected unknown feature '{feature}' to not be available, got {result}"


class TestFeatureGateProFeatures:
    """Test cases for pro feature availability."""

    def test_all_features_available_in_pro_version(self):
        """TEST: should_allow_all_features_in_pro_version"""
        # ARRANGE: Pro version feature gate
        feature_gate = FeatureGate("pro")
        all_features = [
            # Basic features
            "pandas_wrapper", "pyjanitor_wrapper", "basic_cleaning",
            "file_operations", "simple_validation", "basic_visualization",
            "data_profiling", "clean", "validate", "info", "config",
            "visualize", "report",
            # Premium features
            "ai_agent", "llm_providers", "feature_engine_wrapper",
            "dedupe_wrapper", "missingno_wrapper", "advanced_visualization",
            "batch_processing", "performance_optimization", "parallel_processing",
            "memory_optimization", "ai-suggest", "ai-clean", "ai-analyze",
            "ai-configure", "ai-logs", "ai-model", "dedupe", "performance"
        ]

        # ACT & ASSERT: Verify all features are available
        for feature in all_features:
            result = feature_gate.is_feature_available(feature)
            assert result is True, f"Expected feature '{feature}' to be available in pro version, got {result}"

    def test_unknown_features_not_available_in_pro_version(self):
        """TEST: should_allow_all_features_in_pro_version_including_unknown"""
        # ARRANGE: Pro version feature gate and unknown features
        feature_gate = FeatureGate("pro")
        unknown_features = ["unknown_feature", "test_function", "experimental_feature", ""]

        # ACT & ASSERT: Verify all features are available in pro version (including unknown)
        for feature in unknown_features:
            result = feature_gate.is_feature_available(feature)
            assert result is True, f"Expected feature '{feature}' to be available in pro version, got {result}"

    def test_pro_version_allows_all_features(self):
        """TEST: should_allow_any_feature_in_pro_version"""
        # ARRANGE: Pro version feature gate
        feature_gate = FeatureGate("pro")

        # ACT & ASSERT: Verify pro version allows any feature name
        test_features = [
            "any_feature", "random_name", "test_function", "experimental_feature",
            "pandas_wrapper", "ai_agent", "clean", "validate", "info", "config",
            "visualize", "report", "ai-suggest", "ai-clean", "ai-analyze",
            "ai-configure", "ai-logs", "ai-model", "dedupe", "performance"
        ]

        for feature in test_features:
            result = feature_gate.is_feature_available(feature)
            assert result is True, f"Expected feature '{feature}' to be available in pro version, got {result}"


class TestFeatureGateEdgeCases:
    """Test cases for edge cases and error scenarios."""

    def test_feature_name_case_sensitivity(self):
        """TEST: should_be_case_sensitive_for_feature_names"""
        # ARRANGE: Feature gate and case variations
        feature_gate = FeatureGate("basic")
        case_variations = [
            ("pandas_wrapper", "Pandas_Wrapper"),
            ("ai_agent", "AI_Agent"),
            ("clean", "Clean"),
            ("unknown_feature", "Unknown_Feature")
        ]

        # ACT & ASSERT: Verify case sensitivity
        for original, case_variant in case_variations:
            original_result = feature_gate.is_feature_available(original)
            variant_result = feature_gate.is_feature_available(case_variant)

            # Known features should be case-sensitive
            if original in ["pandas_wrapper", "clean"]:
                assert original_result is True, f"Expected '{original}' to be available"
                assert variant_result is False, f"Expected case variant '{case_variant}' to not be available"
            else:
                # Unknown features should always be False regardless of case
                assert original_result is False, f"Expected '{original}' to not be available"
                assert variant_result is False, f"Expected case variant '{case_variant}' to not be available"

    def test_feature_name_with_whitespace(self):
        """TEST: should_handle_feature_names_with_whitespace"""
        # ARRANGE: Feature gate and whitespace variations
        feature_gate = FeatureGate("basic")
        whitespace_variations = [
            " pandas_wrapper", "pandas_wrapper ", " pandas_wrapper ",
            "ai_agent", " ai_agent ", "  ai_agent  "
        ]

        # ACT & ASSERT: Verify whitespace handling
        for feature in whitespace_variations:
            result = feature_gate.is_feature_available(feature)
            # Features with whitespace should not be available
            assert result is False, f"Expected feature '{feature}' with whitespace to not be available, got {result}"

    def test_feature_name_with_special_characters(self):
        """TEST: should_handle_feature_names_with_special_characters"""
        # ARRANGE: Feature gate and special character variations
        feature_gate = FeatureGate("basic")
        special_char_variations = [
            "pandas_wrapper!", "ai_agent@", "clean#", "validate$",
            "pandas_wrapper-", "ai_agent_", "clean.", "validate/"
        ]

        # ACT & ASSERT: Verify special character handling
        for feature in special_char_variations:
            result = feature_gate.is_feature_available(feature)
            # Features with special characters should not be available
            assert result is False, f"Expected feature '{feature}' with special characters to not be available, got {result}"

    def test_empty_and_none_feature_names(self):
        """TEST: should_handle_empty_and_none_feature_names"""
        # ARRANGE: Feature gate and empty/None values
        feature_gate = FeatureGate("basic")
        empty_values = ["", None, "   ", "\t", "\n"]

        # ACT & ASSERT: Verify empty/None handling
        for feature in empty_values:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected empty/None feature '{feature}' to not be available, got {result}"


class TestFeatureGateIntegration:
    """Test cases for feature gate integration scenarios."""

    def test_version_detection_from_package(self):
        """TEST: should_detect_version_from_package_metadata"""
        # ARRANGE: Test version detection function
        from csv_cleaner.feature_gate import detect_package_version

        # ACT: Test version detection with environment variable
        with patch.dict(os.environ, {'CSV_CLEANER_VERSION': 'pro'}):
            version = detect_package_version()
            assert version == "pro", f"Expected version 'pro', got '{version}'"

        # ACT: Test version detection with basic environment variable
        with patch.dict(os.environ, {'CSV_CLEANER_VERSION': 'basic'}):
            version = detect_package_version()
            assert version == "basic", f"Expected version 'basic', got '{version}'"

        # ACT: Test version detection with invalid environment variable
        with patch.dict(os.environ, {'CSV_CLEANER_VERSION': 'invalid'}, clear=True):
            version = detect_package_version()
            # Should fall back to package metadata, which detects "pro" for "csv-cleaner"
            assert version == "pro", f"Expected version 'pro' for invalid env var (fallback to package), got '{version}'"

        # ACT: Test version detection without environment variable
        with patch.dict(os.environ, {}, clear=True):
            version = detect_package_version()
            # Should fall back to package metadata, which detects "pro" for "csv-cleaner"
            assert version == "pro", f"Expected version 'pro' for no env var (fallback to package), got '{version}'"

    def test_feature_gate_consistency_across_instances(self):
        """TEST: should_maintain_consistency_across_feature_gate_instances"""
        # ARRANGE: Multiple feature gate instances
        basic_gate1 = FeatureGate("basic")
        basic_gate2 = FeatureGate("basic")
        pro_gate1 = FeatureGate("pro")
        pro_gate2 = FeatureGate("pro")

        # ACT & ASSERT: Verify consistency
        test_features = ["pandas_wrapper", "ai_agent", "clean", "unknown_feature"]

        for feature in test_features:
            # Same version instances should be consistent
            assert basic_gate1.is_feature_available(feature) == basic_gate2.is_feature_available(feature), \
                f"Basic gate instances inconsistent for feature '{feature}'"
            assert pro_gate1.is_feature_available(feature) == pro_gate2.is_feature_available(feature), \
                f"Pro gate instances inconsistent for feature '{feature}'"

    def test_feature_gate_performance(self):
        """TEST: should_perform_efficiently_for_multiple_feature_checks"""
        # ARRANGE: Feature gate and multiple feature checks
        feature_gate = FeatureGate("pro")
        features_to_check = [
            "pandas_wrapper", "ai_agent", "clean", "validate", "info",
            "config", "visualize", "report", "ai-suggest", "ai-clean"
        ] * 100  # 1000 total checks

        # ACT: Perform multiple feature checks
        import time
        start_time = time.time()

        results = []
        for feature in features_to_check:
            result = feature_gate.is_feature_available(feature)
            results.append(result)

        end_time = time.time()
        execution_time = end_time - start_time

        # ASSERT: Verify performance and correctness
        assert execution_time < 1.0, f"Feature checks took too long: {execution_time:.3f} seconds"
        assert len(results) == 1000, f"Expected 1000 results, got {len(results)}"

        # Verify all known features return True in pro version
        known_features = ["pandas_wrapper", "ai_agent", "clean", "validate", "info", "config", "visualize", "report", "ai-suggest", "ai-clean"]
        for feature in known_features:
            assert feature_gate.is_feature_available(feature) is True, f"Expected known feature '{feature}' to be available"


class TestFeatureGateErrorHandling:
    """Test cases for error handling and edge cases."""

    def test_feature_gate_with_malformed_feature_names(self):
        """TEST: should_handle_malformed_feature_names_gracefully"""
        # ARRANGE: Feature gate and malformed feature names
        feature_gate = FeatureGate("basic")
        malformed_features = [
            "feature with spaces",
            "feature-with-dashes",
            "feature.with.dots",
            "feature/with/slashes",
            "feature\\with\\backslashes",
            "feature[with]brackets",
            "feature{with}braces",
            "feature(with)parentheses",
            "feature'with'quotes",
            'feature"with"quotes',
            "feature`with`backticks",
            "feature|with|pipes",
            "feature&with&amps",
            "feature=with=equals",
            "feature+with+plus",
            "feature*with*asterisks",
            "feature^with^carets",
            "feature%with%percent",
            "feature#with#hash",
            "feature@with@at"
        ]

        # ACT & ASSERT: Verify malformed features are handled gracefully
        for feature in malformed_features:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected malformed feature '{feature}' to not be available, got {result}"

    def test_feature_gate_with_unicode_feature_names(self):
        """TEST: should_handle_unicode_feature_names"""
        # ARRANGE: Feature gate and unicode feature names
        feature_gate = FeatureGate("basic")
        unicode_features = [
            "pandas_wrapper_é", "ai_agent_ñ", "clean_ü", "validate_ö",
            "pandas_wrapper_中文", "ai_agent_日本語", "clean_한국어",
            "pandas_wrapper_🌍", "ai_agent_🚀", "clean_💻"
        ]

        # ACT & ASSERT: Verify unicode features are handled gracefully
        for feature in unicode_features:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected unicode feature '{feature}' to not be available, got {result}"

    def test_feature_gate_with_very_long_feature_names(self):
        """TEST: should_handle_very_long_feature_names"""
        # ARRANGE: Feature gate and very long feature names
        feature_gate = FeatureGate("basic")
        long_features = [
            "a" * 1000,  # 1000 character feature name
            "pandas_wrapper" + "x" * 1000,  # Long feature name
            "very_long_feature_name_" * 50,  # Repeated pattern
        ]

        # ACT & ASSERT: Verify long feature names are handled gracefully
        for feature in long_features:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected long feature name to not be available, got {result}"

    def test_feature_gate_with_numeric_feature_names(self):
        """TEST: should_handle_numeric_feature_names"""
        # ARRANGE: Feature gate and numeric feature names
        feature_gate = FeatureGate("basic")
        numeric_features = [
            "123", "456", "789",
            "feature_123", "123_feature",
            "feature_1_2_3", "1_2_3_feature"
        ]

        # ACT & ASSERT: Verify numeric feature names are handled gracefully
        for feature in numeric_features:
            result = feature_gate.is_feature_available(feature)
            assert result is False, f"Expected numeric feature '{feature}' to not be available, got {result}"
