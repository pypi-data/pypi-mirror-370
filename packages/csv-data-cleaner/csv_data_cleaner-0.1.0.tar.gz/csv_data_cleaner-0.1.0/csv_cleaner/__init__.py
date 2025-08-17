"""
CSV Data Cleaner - Self-contained tool with AI capabilities.

A powerful tool for cleaning CSV data using industry-standard Python libraries
with optional AI-powered intelligent suggestions.
"""

from .feature_gate import detect_package_version, FeatureGate

# Detect package version and initialize feature gate
__version__ = "1.0.0"
__package_version__ = detect_package_version()

# Initialize global feature gate
_feature_gate = FeatureGate(__package_version__)


def get_feature_gate() -> FeatureGate:
    """Get the global feature gate instance.

    Returns:
        FeatureGate instance for the current package version.
    """
    return _feature_gate


def get_package_version() -> str:
    """Get the current package version.

    Returns:
        Package version ("basic" or "pro")
    """
    return __package_version__


__all__ = [
    "__version__",
    "__package_version__",
    "get_feature_gate",
    "get_package_version",
    "FeatureGate",
    "detect_package_version",
]
