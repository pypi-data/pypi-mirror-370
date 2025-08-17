"""
Feature gating system for CSV Data Cleaner.

This module provides centralized feature management for free vs premium versions
of the CSV Data Cleaner package.
"""

import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class FeatureGate:
    """Centralized feature gating system for free vs premium versions."""

    # Basic features available in free version
    BASIC_FEATURES = {
        # Core functionality
        "pandas_wrapper": True,
        "pyjanitor_wrapper": True,
        "basic_cleaning": True,
        "file_operations": True,
        "simple_validation": True,
        "basic_visualization": True,
        "data_profiling": True,
        # CLI commands
        "clean": True,
        "validate": True,
        "info": True,
        "config": True,
        "visualize": True,
        "report": True,
    }

    # Premium features available in pro version
    PREMIUM_FEATURES = {
        # Advanced functionality
        "ai_agent": True,
        "llm_providers": True,
        "feature_engine_wrapper": True,
        "dedupe_wrapper": True,
        "missingno_wrapper": True,
        "advanced_visualization": True,
        "batch_processing": True,
        "performance_optimization": True,
        "parallel_processing": True,
        "memory_optimization": True,
        # CLI commands
        "ai-suggest": True,
        "ai-clean": True,
        "ai-analyze": True,
        "ai-configure": True,
        "ai-logs": True,
        "ai-model": True,
        "dedupe": True,
        "performance": True,
    }

    # Operation categories mapping
    OPERATION_CATEGORIES = {
        # Basic operations (available in both versions)
        "remove_duplicates": "basic",
        "fill_missing": "basic",
        "drop_missing": "basic",
        "clean_column_names": "basic",
        "validate_data": "basic",
        "analyze_data": "basic",
        "generate_report": "basic",
        "quality_visualization": "basic",
        "correlation_visualization": "basic",
        "distribution_visualization": "basic",

        # Pro operations (missingno wrapper)
        "missing_matrix": "pro",
        "missing_bar": "pro",
        "missing_heatmap": "pro",
        "missing_dendrogram": "pro",
        "missing_summary": "pro",

        # Pro operations (dedupe wrapper)
        "dedupe": "pro",
        "train_dedupe": "pro",
        "predict_duplicates": "pro",

        # Pro operations (feature-engine wrapper)
        "advanced_imputation": "pro",
        "categorical_encoding": "pro",
        "outlier_detection": "pro",
        "variable_selection": "pro",
        "data_transformation": "pro",
        "missing_indicator": "pro",

        # Pro operations (AI features)
        "ai_suggest": "pro",
        "ai_clean": "pro",
        "ai_analyze": "pro",
        "ai_configure": "pro",

        # Pro operations (performance features)
        "performance_analysis": "pro",
        "batch_processing": "pro",
        "parallel_processing": "pro",
    }

    # Operation descriptions for upgrade messages
    OPERATION_DESCRIPTIONS = {
        # Missingno operations
        "missing_matrix": "Missing Data Matrix Visualization",
        "missing_bar": "Missing Data Bar Chart",
        "missing_heatmap": "Missing Data Heatmap",
        "missing_dendrogram": "Missing Data Dendrogram",
        "missing_summary": "Missing Data Summary",

        # Dedupe operations
        "dedupe": "Advanced Machine Learning Deduplication",
        "train_dedupe": "Deduplication Model Training",
        "predict_duplicates": "Duplicate Prediction",

        # Feature-engine operations
        "advanced_imputation": "Advanced Data Imputation",
        "categorical_encoding": "Categorical Variable Encoding",
        "outlier_detection": "Outlier Detection",
        "variable_selection": "Variable Selection",
        "data_transformation": "Data Transformation",
        "missing_indicator": "Missing Value Indicators",

        # AI operations
        "ai_suggest": "AI-Powered Cleaning Suggestions",
        "ai_clean": "AI-Powered Automatic Cleaning",
        "ai_analyze": "AI-Powered Data Analysis",
        "ai_configure": "AI Configuration Management",

        # Performance operations
        "performance_analysis": "Performance Analysis",
        "batch_processing": "Batch Processing",
        "parallel_processing": "Parallel Processing",
    }

    def __init__(self, version: str = "basic"):
        """Initialize feature gate with specified version.

        Args:
            version: Package version ("basic" or "pro")
        """
        if version not in ["basic", "pro"]:
            raise ValueError(f"Invalid version: {version}. Must be 'basic' or 'pro'")

        self.version = version
        logger.info(f"Feature gate initialized for version: {version}")

    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available in the current version.

        Args:
            feature_name: Name of the feature to check.

        Returns:
            True if the feature is available, False otherwise.
        """
        if self.version == "basic":
            return self.BASIC_FEATURES.get(feature_name, False)
        else:  # pro version
            return True  # Pro version has all features

    def get_available_wrappers(self) -> List[str]:
        """Get list of available wrappers for the current version.

        Returns:
            List of available wrapper names.
        """
        available_wrappers = []

        if self.is_feature_available("pandas_wrapper"):
            available_wrappers.append("pandas")

        if self.is_feature_available("pyjanitor_wrapper"):
            available_wrappers.append("pyjanitor")

        if self.is_feature_available("feature_engine_wrapper"):
            available_wrappers.append("feature_engine")

        if self.is_feature_available("dedupe_wrapper"):
            available_wrappers.append("dedupe")

        if self.is_feature_available("missingno_wrapper"):
            available_wrappers.append("missingno")

        return available_wrappers

    def get_available_commands(self) -> List[str]:
        """Get list of available CLI commands for the current version.

        Returns:
            List of available command names.
        """
        available_commands = []

        # Basic commands
        basic_commands = ["clean", "validate", "info", "operations", "config", "visualize", "report"]

        # Premium commands
        premium_commands = [
            "ai-suggest",
            "ai-clean",
            "ai-analyze",
            "ai-configure",
            "ai-logs",
            "ai-model",
            "dedupe",
            "performance",
        ]

        # Add basic commands
        for cmd in basic_commands:
            if self.is_feature_available(cmd):
                available_commands.append(cmd)

        # Add premium commands
        for cmd in premium_commands:
            if self.is_feature_available(cmd):
                available_commands.append(cmd)

        return available_commands

    def get_operation_category(self, operation: str) -> str:
        """Get the category (basic/pro) for an operation.

        Args:
            operation: Name of the operation.

        Returns:
            Category: "basic" or "pro".
        """
        return self.OPERATION_CATEGORIES.get(operation, "basic")

    def get_operation_upgrade_message(self, operation: str) -> str:
        """Get upgrade message for a Pro operation.

        Args:
            operation: Name of the operation.

        Returns:
            Upgrade message string.
        """
        if self.version == "pro":
            return ""  # No upgrade needed for pro version

        feature_name = self.OPERATION_DESCRIPTIONS.get(operation, operation)

        return (
            f"❌ {feature_name} is a Pro feature!\n"
            f"   Upgrade to CSV Cleaner Pro for advanced data analysis features!\n"
            f"   Visit: https://gumroad.com/csv-cleaner-pro\n"
        )

    def get_upgrade_message(self, feature_name: str) -> str:
        """Get upgrade message for a premium feature.

        Args:
            feature_name: Name of the feature that requires upgrade.

        Returns:
            Upgrade message string.
        """
        if self.version == "pro":
            return ""  # No upgrade needed for pro version

        feature_messages = {
            "ai_agent": "AI-powered intelligent suggestions",
            "ai-suggest": "AI-powered cleaning suggestions",
            "ai-clean": "AI-powered automatic cleaning",
            "ai-analyze": "AI-powered data analysis",
            "dedupe": "Machine learning-based deduplication",
            "feature_engine_wrapper": "Advanced data transformation",
            "missingno_wrapper": "Advanced missing data analysis",
            "performance": "Performance optimization features",
            "batch_processing": "Batch processing capabilities",
            "parallel_processing": "Parallel processing optimization",
        }

        message = feature_messages.get(feature_name, "Advanced features")
        return f"'{message}' requires CSV Cleaner Pro"

    def get_version_info(self) -> Dict[str, any]:
        """Get information about the current version and available features.

        Returns:
            Dictionary with version information.
        """
        return {
            "version": self.version,
            "available_wrappers": self.get_available_wrappers(),
            "available_commands": self.get_available_commands(),
            "basic_features_count": len(self.BASIC_FEATURES),
            "premium_features_count": len(self.PREMIUM_FEATURES),
            "total_available_features": len(self.get_available_commands())
            + len(self.get_available_wrappers()),
        }


def detect_package_version() -> str:
    """Detect package version from environment or package metadata.

    Returns:
        Package version ("basic" or "pro")
    """
    # Priority 1: Environment variable
    env_version = os.getenv("CSV_CLEANER_VERSION")
    if env_version in ["basic", "pro"]:
        logger.info(f"Package version detected from environment: {env_version}")
        return env_version

    # Priority 2: Package metadata
    try:
        import importlib.metadata

        package_name = importlib.metadata.metadata("csv-cleaner")["Name"]
        if "basic" in package_name.lower():
            logger.info("Package version detected from package name: basic")
            return "basic"
        elif package_name.lower() == "csv-cleaner":
            logger.info("Package version detected from package name: pro")
            return "pro"
        else:
            # Default to pro for csv-cleaner package
            logger.info("Package version defaulting to pro for csv-cleaner")
            return "pro"
    except Exception as e:
        logger.debug(f"Could not detect version from package metadata: {e}")

    # Priority 3: Default to basic
    logger.info("Package version defaulting to: basic")
    return "basic"
