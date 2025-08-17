"""
CLI commands for CSV Data Cleaner.
"""

import click
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import json
import inquirer
from typing import Dict, List, Optional, Any
import click
import os
import sys
from pathlib import Path

from ..core.cleaner import CSVCleaner
from ..core.config import Config, ConfigurationManager
from ..core.file_operations import FileOperations
from ..core.visualization_manager import VisualizationManager
from .decorators import cli_command_with_cleaner

# Try to import AI components, but make them optional
try:
    from ..core.ai_agent import AIAgent
    from ..core.llm_providers import LLMProviderManager

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIAgent = None
    LLMProviderManager = None

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Setup logging configuration.

    Args:
        verbose: Enable verbose logging.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def parse_operations(operations_str: str) -> List[str]:
    """Parse operations string into list.

    Args:
        operations_str: Comma-separated operations string.

    Returns:
        List of operation names.
    """
    if not operations_str:
        return []

    return [op.strip() for op in operations_str.split(",") if op.strip()]


def display_summary(summary: Dict[str, Any]) -> None:
    """Display cleaning summary in a user-friendly format.

    Args:
        summary: Cleaning operation summary.
    """
    click.echo("\n" + "=" * 50)
    click.echo("📊 CLEANING SUMMARY")
    click.echo("=" * 50)

    click.echo(f"✅ Success: {summary.get('success', False)}")
    click.echo(
        f"📁 Input file: {summary.get('input_rows', 0)} rows, {summary.get('input_columns', 0)} columns"
    )
    click.echo(
        f"📄 Output file: {summary.get('output_rows', 0)} rows, {summary.get('output_columns', 0)} columns"
    )
    click.echo(f"🗑️  Rows removed: {summary.get('rows_removed', 0)}")
    click.echo(f"🗑️  Columns removed: {summary.get('columns_removed', 0)}")
    click.echo(f"⚡ Total time: {summary.get('total_execution_time', 0):.2f} seconds")

    if summary.get("backup_created"):
        click.echo(f"💾 Backup created: {summary.get('backup_path', 'Unknown')}")

    operations = summary.get("operations_performed", [])
    if operations:
        click.echo(f"🔧 Operations performed: {', '.join(operations)}")

    click.echo("=" * 50)


def load_configuration(config_file: Optional[str]) -> Optional[Config]:
    """Load configuration from file or use default.

    Args:
        config_file: Path to configuration file.

    Returns:
        Configuration object or None if not specified.
    """
    if config_file:
        config_manager = ConfigurationManager(config_file)
        return config_manager.load_config()
    return None


def initialize_cleaner(config: Optional[Config]) -> CSVCleaner:
    """Initialize CSV cleaner with configuration.

    Args:
        config: Configuration object.

    Returns:
        Initialized CSVCleaner instance.
    """
    return CSVCleaner(config)


def validate_input_file(input_file: str) -> bool:
    """Validate that input file exists.

    Args:
        input_file: Path to input file.

    Returns:
        True if file exists, False otherwise.
    """
    if not Path(input_file).exists():
        click.echo(f"❌ Error: Input file not found: {input_file}")
        return False
    return True


def handle_dry_run(
    cleaner: CSVCleaner, input_file: str, operations_list: Optional[List[str]]
) -> None:
    """Handle dry run mode - show estimates without modifying files.

    Args:
        cleaner: CSVCleaner instance.
        input_file: Path to input file.
        operations_list: List of operations to estimate.
    """
    click.echo("🔍 DRY RUN MODE - No files will be modified")
    df = cleaner.file_operations.read_csv(input_file)
    estimated_time = cleaner.estimate_processing_time(
        df, operations_list or cleaner.config.default_operations
    )
    click.echo(f"📊 Estimated processing time: {estimated_time:.2f} seconds")
    click.echo(f"📈 Estimated memory usage: {cleaner.config.max_memory_gb:.1f} GB")


def update_cleaner_config(
    cleaner: CSVCleaner,
    chunk_size: Optional[int],
    max_memory: Optional[float],
    parallel: bool,
) -> None:
    """Update cleaner configuration with CLI parameters.

    Args:
        cleaner: CSVCleaner instance.
        chunk_size: Chunk size for processing.
        max_memory: Maximum memory usage in GB.
        parallel: Whether to enable parallel processing.
    """
    if chunk_size:
        cleaner.config.chunk_size = chunk_size
    if max_memory:
        cleaner.config.max_memory_gb = max_memory
    if not parallel:
        cleaner.config.enable_parallel_processing = False


def handle_error(error: Exception, verbose: bool) -> None:
    """Handle and display errors consistently.

    Args:
        error: Exception that occurred.
        verbose: Whether to show detailed error information.
    """
    click.echo(f"❌ Error: {str(error)}")
    if verbose:
        logger.exception("Detailed error information:")
    raise click.Abort()


def ai_logs_command(days: int, config_file: Optional[str], verbose: bool) -> None:
    """View AI interaction logs and usage summary.

    Args:
        days: Number of days to include in summary.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        # Check if AI logging is enabled
        if not config.ai_logging_enabled:
            click.echo(
                "❌ AI logging is disabled. Enable it in configuration to view logs."
            )
            return

        # Initialize AI logging manager
        from ..core.ai_logging import AILoggingManager

        ai_logging_manager = AILoggingManager(config)

        # Get AI logs summary
        summary = ai_logging_manager.get_ai_logs_summary(days)

        click.echo("\n" + "=" * 60)
        click.echo("📝 AI INTERACTION LOGS SUMMARY")
        click.echo("=" * 60)

        click.echo(f"📊 Period: Last {days} days")
        click.echo(f"📁 Log File: {ai_logging_manager.log_file_path}")
        click.echo(f"📈 Total Interactions: {summary['total_interactions']}")
        click.echo(f"💰 Total Cost: ${summary['total_cost_usd']:.4f}")
        click.echo(f"🔢 Total Tokens Used: {summary['total_tokens_used']:,}")
        click.echo(f"✅ Success Rate: {summary['success_rate']:.1%}")
        click.echo(
            f"⏱️  Average Response Time: {summary['average_response_time']:.2f}s"
        )

        if summary["providers_used"]:
            click.echo("\n🤖 Providers Used:")
            for provider, count in summary["providers_used"].items():
                click.echo(f"   • {provider}: {count} interactions")

        if summary["operation_types"]:
            click.echo("\n🔧 Operation Types:")
            for op_type, count in summary["operation_types"].items():
                click.echo(f"   • {op_type}: {count} interactions")

        if "error" in summary:
            click.echo(f"\n❌ Error: {summary['error']}")

        click.echo("=" * 60)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        if verbose:
            logger.exception("Detailed error information:")
        raise click.Abort()


def show_operations_info(operations_list: Optional[List[str]]) -> None:
    """Show information about operations to be performed.

    Args:
        operations_list: List of operations to perform.
    """
    if operations_list:
        click.echo(f"🔧 Operations to perform: {', '.join(operations_list)}")
    else:
        click.echo("🔧 Using default operations")


def perform_cleaning_with_progress(
    cleaner: CSVCleaner,
    input_file: str,
    output_file: str,
    operations_list: Optional[List[str]],
) -> Dict[str, Any]:
    """Perform cleaning with progress bar.

    Args:
        cleaner: CSVCleaner instance.
        input_file: Path to input file.
        output_file: Path to output file.
        operations_list: List of operations to perform.

    Returns:
        Cleaning summary dictionary.
    """
    with click.progressbar(length=1, label="Cleaning CSV file") as bar:
        summary = cleaner.clean_file(input_file, output_file, operations_list)
        bar.update(1)
    return summary


@cli_command_with_cleaner
def clean_command(
    input_file: str,
    output_file: str,
    operations: Optional[str],
    config_file: Optional[str],
    interactive: bool,
    verbose: bool,
    chunk_size: Optional[int] = None,
    parallel: bool = True,
    max_memory: Optional[float] = None,
    dry_run: bool = False,
    config: Optional[Config] = None,
    cleaner: Optional[CSVCleaner] = None,
) -> None:
    """Clean a CSV file using specified operations.

    Args:
        input_file: Path to input CSV file.
        output_file: Path to output CSV file.
        operations: Comma-separated list of operations.
        config_file: Path to configuration file.
        interactive: Enable interactive mode.
        verbose: Enable verbose logging.
        config: Configuration object (injected by decorator).
        cleaner: CSVCleaner instance (injected by decorator).
    """
    # Parse operations
    operations_list = parse_operations(operations) if operations else None

    # Update configuration with CLI parameters
    update_cleaner_config(cleaner, chunk_size, max_memory, parallel)

    # Dry run mode
    if dry_run:
        handle_dry_run(cleaner, input_file, operations_list)
        return

    # Validate input file
    if not validate_input_file(input_file):
        return

    # Interactive mode
    if interactive:
        interactive_mode(cleaner, input_file, output_file, operations_list)
        return

    # Show operation info
    show_operations_info(operations_list)

    # Perform cleaning
    summary = perform_cleaning_with_progress(
        cleaner, input_file, output_file, operations_list
    )

    # Display results
    display_summary(summary)

    click.echo(f"✅ Successfully cleaned {input_file} -> {output_file}")


@cli_command_with_cleaner
def validate_command(
    input_file: str,
    schema_file: Optional[str],
    output: Optional[str],
    config_file: Optional[str],
    verbose: bool,
    config: Optional[Config] = None,
    cleaner: Optional[CSVCleaner] = None,
) -> None:
    """Validate CSV data using advanced validation.

    Args:
        input_file: Path to CSV file to validate.
        schema_file: Path to validation schema file.
        output: Output path for validation report.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
        config: Configuration object (injected by decorator).
        cleaner: CSVCleaner instance (injected by decorator).
    """
    # Read the data
    df = cleaner.file_operations.read_csv(input_file)

    click.echo(f"🔍 Validating data: {input_file}")

    # Perform validation
    validation_results = cleaner.validate_data(df, schema_file)

    # Display results
    click.echo("\n" + "=" * 50)
    click.echo("📊 VALIDATION RESULTS")
    click.echo("=" * 50)

    quality_score = validation_results["quality_score"]
    click.echo(f"✅ Overall Quality Score: {quality_score.overall:.2%}")
    click.echo(f"📊 Completeness: {quality_score.completeness:.2%}")
    click.echo(f"🎯 Accuracy: {quality_score.accuracy:.2%}")
    click.echo(f"🔄 Consistency: {quality_score.consistency:.2%}")
    click.echo(f"✅ Validity: {quality_score.validity:.2%}")

    # Show duplicate penalty if applicable
    if hasattr(quality_score, 'details') and 'duplicate_penalty' in quality_score.details:
        duplicate_penalty = quality_score.details['duplicate_penalty']
        if duplicate_penalty > 0:
            click.echo(f"🔄 Duplicate Penalty: {duplicate_penalty:.2%}")

    click.echo(
        f"\n📋 Validation Rules: {len(validation_results['validation_results'])}"
    )
    passed_rules = sum(
        1 for r in validation_results["validation_results"] if r.passed
    )
    click.echo(f"✅ Passed Rules: {passed_rules}")
    click.echo(
        f"❌ Failed Rules: {len(validation_results['validation_results']) - passed_rules}"
    )
    click.echo(f"🚨 Total Errors: {validation_results['total_errors']}")

    # Show detailed issues
    failed_results = [r for r in validation_results["validation_results"] if not r.passed]
    if failed_results:
        click.echo("\n🔍 DETAILED ISSUES:")
        click.echo("-" * 30)
        for result in failed_results:
            click.echo(f"❌ {result.rule_id}: {', '.join(result.errors)}")
            if result.affected_rows:
                click.echo(f"   Affected rows: {len(result.affected_rows)}")
                if len(result.affected_rows) <= 10:  # Show row numbers if not too many
                    click.echo(f"   Row indices: {result.affected_rows}")
            click.echo()

    # Save validation report if output specified
    if output:
        report_content = cleaner.validator.generate_validation_report()
        with open(output, "w") as f:
            f.write(report_content)
        click.echo(f"\n📄 Validation report saved to: {output}")


@cli_command_with_cleaner
def analyze_command(
    input_file: str,
    output: Optional[str],
    config_file: Optional[str],
    verbose: bool,
    config: Optional[Config] = None,
    cleaner: Optional[CSVCleaner] = None,
) -> None:
    """Analyze CSV data and generate smart validation rules.

    Args:
        input_file: Path to CSV file to analyze.
        output: Output path for analysis report.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
        config: Configuration object (injected by decorator).
        cleaner: CSVCleaner instance (injected by decorator).
    """
    # Read the data
    df = cleaner.file_operations.read_csv(input_file)

    click.echo(f"🔍 Analyzing data: {input_file}")

    # Generate smart validation rules
    smart_rules = cleaner.validator.generate_smart_validation_rules(df)

    # Display analysis results
    click.echo("\n" + "=" * 50)
    click.echo("📊 DATA ANALYSIS RESULTS")
    click.echo("=" * 50)

    click.echo(f"📋 Generated {len(smart_rules)} smart validation rules")
    click.echo()

    if smart_rules:
        click.echo("🔍 SUGGESTED VALIDATION RULES:")
        click.echo("-" * 30)
        for rule in smart_rules:
            click.echo(f"✅ {rule.rule_id}: {rule.description}")
        click.echo()

    # Show data statistics
    click.echo("📈 DATA STATISTICS:")
    click.echo("-" * 20)
    click.echo(f"Rows: {len(df)}")
    click.echo(f"Columns: {len(df.columns)}")
    click.echo(f"Missing values: {df.isna().sum().sum()}")
    click.echo(f"Duplicate rows: {df.duplicated().sum()}")

    # Column-wise statistics
    click.echo("\n📊 COLUMN ANALYSIS:")
    click.echo("-" * 20)
    for column in df.columns:
        null_count = df[column].isna().sum()
        unique_count = df[column].nunique()
        click.echo(f"{column}:")
        click.echo(f"  - Null values: {null_count} ({null_count/len(df)*100:.1f}%)")
        click.echo(f"  - Unique values: {unique_count} ({unique_count/len(df)*100:.1f}%)")
        click.echo()

    # Save analysis report if output specified
    if output:
        report_content = f"""Data Analysis Report for {input_file}

Generated {len(smart_rules)} smart validation rules:

"""
        for rule in smart_rules:
            report_content += f"- {rule.rule_id}: {rule.description}\n"

        report_content += f"""

Data Statistics:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Missing values: {df.isna().sum().sum()}
- Duplicate rows: {df.duplicated().sum()}

Column Analysis:
"""
        for column in df.columns:
            null_count = df[column].isna().sum()
            unique_count = df[column].nunique()
            report_content += f"- {column}: {null_count} nulls ({null_count/len(df)*100:.1f}%), {unique_count} unique ({unique_count/len(df)*100:.1f}%)\n"

        with open(output, "w") as f:
            f.write(report_content)
        click.echo(f"\n📄 Analysis report saved to: {output}")


@cli_command_with_cleaner
def dedupe_command(
    input_file: str,
    output_file: str,
    threshold: float,
    interactive: bool,
    training_file: Optional[str],
    config_file: Optional[str],
    verbose: bool,
    config: Optional[Config] = None,
    cleaner: Optional[CSVCleaner] = None,
) -> None:
    """Perform ML-based deduplication on CSV data.

    Args:
        input_file: Path to input CSV file.
        output_file: Path to output CSV file.
        threshold: Deduplication threshold (0.0-1.0).
        interactive: Enable interactive training.
        training_file: Path to training data file.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
        config: Configuration object (injected by decorator).
        cleaner: CSVCleaner instance (injected by decorator).
    """
    # Read the data
    df = cleaner.file_operations.read_csv(input_file)

    click.echo(f"🔍 Starting ML-based deduplication: {input_file}")

    # Configure dedupe parameters
    if training_file:
        cleaner.config.dedupe_training_file = training_file
    cleaner.config.dedupe_threshold = threshold

    # Perform deduplication
    deduplicated_df = cleaner.library_manager.execute_operation(
        "dedupe", df, threshold=threshold, interactive=interactive, training_file=training_file
    )

    # Save results
    cleaner.file_operations.write_csv(deduplicated_df, output_file)

    click.echo(f"✅ Deduplication completed: {output_file}")
    click.echo(f"📊 Original rows: {len(df)}")
    click.echo(f"📊 Deduplicated rows: {len(deduplicated_df)}")
    click.echo(f"🗑️  Duplicates removed: {len(df) - len(deduplicated_df)}")


def performance_command(
    input_file: str,
    operations: Optional[str],
    config_file: Optional[str],
    verbose: bool,
) -> None:
    """Analyze performance characteristics of data cleaning operations.

    Args:
        input_file: Path to CSV file to analyze.
        operations: Comma-separated list of operations to test.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config = None
        if config_file:
            config_manager = ConfigurationManager(config_file)
            config = config_manager.load_config()

        # Initialize cleaner
        cleaner = CSVCleaner(config)

        # Read the data
        df = cleaner.file_operations.read_csv(input_file)

        # Parse operations
        operations_list = (
            parse_operations(operations)
            if operations
            else cleaner.config.default_operations
        )

        click.echo(f"⚡ Performance Analysis: {input_file}")

        # Get performance summary
        performance_summary = cleaner.get_performance_summary()

        click.echo("\n" + "=" * 50)
        click.echo("📊 PERFORMANCE SUMMARY")
        click.echo("=" * 50)

        # System information
        system_info = performance_summary["parallel_processor"]
        click.echo(f"🖥️  CPU Cores: {system_info['cpu_count']}")
        click.echo(f"🔧 Max Workers: {system_info['max_workers']}")
        click.echo(f"📦 Chunk Size: {system_info['chunk_size']}")

        # Configuration
        config_info = performance_summary["config"]
        click.echo(f"💾 Max Memory: {config_info['max_memory_gb']:.1f} GB")
        click.echo(
            f"🔀 Chunked Processing: {'✅' if config_info['enable_chunked_processing'] else '❌'}"
        )
        click.echo(
            f"⚡ Parallel Processing: {'✅' if config_info['enable_parallel_processing'] else '❌'}"
        )

        # Performance metrics
        perf_metrics = performance_summary["performance_manager"]
        if "message" not in perf_metrics:
            click.echo("\n📈 Performance Metrics:")
            click.echo(f"   Total Operations: {perf_metrics['total_operations']}")
            click.echo(
                f"   Total Duration: {perf_metrics['total_duration_seconds']:.2f}s"
            )
            click.echo(
                f"   Total Rows Processed: {perf_metrics['total_rows_processed']}"
            )
            click.echo(
                f"   Average Rows/Second: {perf_metrics['average_rows_per_second']:.0f}"
            )
            click.echo(f"   Peak Memory Usage: {perf_metrics['peak_memory_mb']:.1f} MB")

        # Estimate processing time
        estimated_time = cleaner.estimate_processing_time(df, operations_list)
        click.echo(
            f"\n⏱️  Estimated Time for {len(operations_list)} operations: {estimated_time:.2f}s"
        )

    except Exception as e:
        handle_error(e, verbose)


def info_command() -> None:
    """Show information about CSV Data Cleaner."""
    click.echo("🔧 CSV Data Cleaner Information")
    click.echo("=" * 50)

    try:
        # Detect package version and create appropriate configuration
        from ..feature_gate import detect_package_version
        version = detect_package_version()

        # Create configuration with detected version
        config = Config()
        config.package_version = version

        # Initialize cleaner with version-aware configuration
        cleaner = CSVCleaner(config)

        # Get wrapper information
        wrapper_info = cleaner.library_manager.get_wrapper_info()

        click.echo("📦 Available wrappers:")
        for name, info in wrapper_info.items():
            click.echo(f"   - {name}: {info['class']}")
            if info["supported_operations"]:
                click.echo(
                    f"     Operations: {', '.join(info['supported_operations'][:5])}"
                )
                if len(info["supported_operations"]) > 5:
                    click.echo(
                        f"     ... and {len(info['supported_operations']) - 5} more"
                    )

        # Get performance summary
        performance = cleaner.get_performance_summary()
        performance_manager_summary = performance.get("performance_manager", {})

        if performance_manager_summary and performance_manager_summary.get("total_operations", 0) > 0:
            click.echo("\n📊 Performance Summary:")
            click.echo(f"   - Total operations: {performance_manager_summary['total_operations']}")
            click.echo(f"   - Total duration: {performance_manager_summary['total_duration_seconds']:.2f}s")
            click.echo(f"   - Total rows processed: {performance_manager_summary['total_rows_processed']:,}")
            click.echo(f"   - Average memory usage: {performance_manager_summary['average_memory_mb']:.1f}MB")
        elif performance_manager_summary and "message" in performance_manager_summary:
            click.echo(f"\n📊 Performance Summary: {performance_manager_summary['message']}")
        else:
            click.echo("\n📊 Performance Summary: No performance data available")

        click.echo("=" * 50)

    except Exception as e:
        click.echo(f"⚠️  Could not load complete information: {e}")


def operations_command() -> None:
    """Show all available operations for CSV Data Cleaner."""
    click.echo("🔧 CSV Data Cleaner - All Available Operations")
    click.echo("=" * 60)

    try:
        # Detect package version and create appropriate configuration
        from ..feature_gate import detect_package_version
        version = detect_package_version()

        # Create configuration with detected version
        config = Config()
        config.package_version = version

        # Initialize cleaner with version-aware configuration
        cleaner = CSVCleaner(config)

        # Get wrapper information
        wrapper_info = cleaner.library_manager.get_wrapper_info()

        total_operations = 0
        for name, info in wrapper_info.items():
            operations = info.get("supported_operations", [])
            total_operations += len(operations)

            click.echo(f"\n📦 {name.upper()} WRAPPER")
            click.echo("-" * 40)
            click.echo(f"Class: {info['class']}")

            if operations:
                click.echo(f"Operations ({len(operations)}):")
                for i, op in enumerate(operations, 1):
                    click.echo(f"  {i:2d}. {op}")
            else:
                click.echo("Operations: None available")

        click.echo("\n" + "=" * 60)
        click.echo(f"📊 Total Operations Available: {total_operations}")
        click.echo("=" * 60)

        click.echo("\n💡 Usage Examples:")
        click.echo("  csv-cleaner clean input.csv output.csv --operations 'remove_duplicates,clean_names'")
        click.echo("  csv-cleaner clean input.csv output.csv --operations 'fill_missing,convert_types'")
        click.echo("  csv-cleaner clean input.csv output.csv --interactive")

    except Exception as e:
        click.echo(f"⚠️  Could not load operations information: {e}")


def config_command(
    action: str,
    key: Optional[str],
    value: Optional[str],
    config_file: Optional[str],
    verbose: bool,
) -> None:
    """Manage CSV Data Cleaner configuration.

    Args:
        action: Configuration action (show, set, get, init).
        key: Configuration key for set/get actions.
        value: Configuration value for set action.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        config_manager = ConfigurationManager(config_file)

        if action == "show":
            config = config_manager.load_config()
            click.echo("📋 Current Configuration:")
            click.echo("=" * 50)

            # Display configuration in a readable format
            config_dict = {
                "Default Operations": config.default_operations,
                "Backup Enabled": config.backup_enabled,
                "Chunk Size": config.chunk_size,
                "Max Memory Usage": f"{config.max_memory_usage / (1024**3):.1f} GB",
                "Log Level": config.log_level,
                "Output Format": config.output_format,
            }

            for key, val in config_dict.items():
                click.echo(f"{key}: {val}")

            click.echo("=" * 50)

        elif action == "set":
            if not key or not value:
                click.echo("❌ Error: Both key and value are required for 'set' action")
                return

            config = config_manager.load_config()

            # Handle different value types
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)

            # Update configuration
            if hasattr(config, key):
                setattr(config, key, value)
                config_manager.save_config(config)
                click.echo(f"✅ Set {key} = {value}")
            else:
                click.echo(f"❌ Error: Unknown configuration key: {key}")

        elif action == "get":
            if not key:
                click.echo("❌ Error: Key is required for 'get' action")
                return

            config = config_manager.load_config()
            if hasattr(config, key):
                value = getattr(config, key)
                click.echo(f"{key}: {value}")
            else:
                click.echo(f"❌ Error: Unknown configuration key: {key}")

        elif action == "init":
            # Create default configuration
            config = Config()
            config_manager.save_config(config)
            click.echo(
                f"✅ Initialized default configuration at: {config_manager.config_path}"
            )

        else:
            click.echo(f"❌ Error: Unknown action: {action}")
            click.echo("Available actions: show, set, get, init")

    except Exception as e:
        handle_error(e, verbose)


def interactive_mode(
    cleaner: CSVCleaner,
    input_file: str,
    output_file: str,
    operations: Optional[List[str]],
    verbose: bool = False,
) -> None:
    """Run Firebase CLI-style interactive mode for CSV cleaning.

    Args:
        cleaner: CSVCleaner instance.
        input_file: Path to input file.
        output_file: Path to output file.
        operations: Initial operations list.
        verbose: Enable verbose logging.
    """
    click.echo("🎯 Interactive Mode")
    click.echo("=" * 50)

    try:
        # Show file information
        file_ops = FileOperations()
        validation_result = file_ops.validate_file(input_file)

        if not validation_result["is_csv"]:
            click.echo(f"❌ Error: {input_file} is not a valid CSV file")
            return

        click.echo(
            f"📁 Input file: {validation_result['estimated_rows']:,} rows, "
            f"{validation_result['estimated_columns']} columns"
        )

        # Get available operations with descriptions
        available_ops = cleaner.get_supported_operations()
        operation_choices = _get_operation_choices(available_ops)

        # Show operation selection interface
        click.echo(f"\n🔧 Select operations to perform:")
        click.echo("   Use ↑↓ arrows to navigate, SPACEBAR to toggle, ENTER to confirm")
        click.echo("   " + "─" * 60)

        # Use inquirer for interactive selection
        questions = [
            inquirer.Checkbox(
                'selected_operations',
                message="Choose operations (spacebar to toggle):",
                choices=operation_choices,
                default=operations if operations else []
            )
        ]

        try:
            answers = inquirer.prompt(questions)
            if not answers or not answers['selected_operations']:
                click.echo("❌ No operations selected. Operation cancelled.")
                return

            # Extract operation values from selected dictionaries
            selected_operations = [op['value'] for op in answers['selected_operations']]

        except Exception as e:
            # Fallback to basic prompt if inquirer fails
            click.echo("⚠️  Advanced interactive mode not available, using basic prompt")
            operations_str = click.prompt(
                "Enter operations (comma-separated) or press Enter for defaults",
                default="",
            )
            selected_operations = parse_operations(operations_str) if operations_str else None
            if not selected_operations:
                click.echo("❌ No operations selected. Operation cancelled.")
                return

        # Show selected operations summary
        click.echo(f"\n📋 Selected operations: {', '.join(selected_operations)}")

        # Confirm before proceeding
        confirm_questions = [
            inquirer.Confirm(
                'proceed',
                message=f"Proceed with cleaning {input_file} → {output_file}?",
                default=True
            )
        ]

        try:
            confirm_answers = inquirer.prompt(confirm_questions)
            if not confirm_answers or not confirm_answers['proceed']:
                click.echo("❌ Operation cancelled")
                return
        except Exception as e:
            # Fallback to basic confirm if inquirer fails
            try:
                if not click.confirm(f"Proceed with cleaning {input_file} -> {output_file}?"):
                    click.echo("❌ Operation cancelled")
                    return
            except Exception as confirm_error:
                # If confirmation fails, assume user wants to proceed
                click.echo("⚠️  Confirmation failed, proceeding with cleaning...")

        # Execute cleaning with progress bar
        with click.progressbar(length=1, label="Cleaning CSV file") as bar:
            summary = cleaner.clean_file(input_file, output_file, selected_operations)
            bar.update(1)

        display_summary(summary)
        click.echo(f"✅ Successfully cleaned {input_file} -> {output_file}")

    except Exception as e:
        handle_error(e, verbose)


def _get_operation_choices(available_ops: List[str]) -> List[Dict[str, str]]:
    """Convert available operations to inquirer choices with descriptions.

    Args:
        available_ops: List of available operation names.

    Returns:
        List of choice dictionaries for inquirer.
    """
    # Operation descriptions for better UX
    operation_descriptions = {
        # Basic cleaning operations
        "remove_duplicates": "Remove duplicate rows from the dataset",
        "drop_missing": "Remove rows with missing values",
        "fill_missing": "Fill missing values with appropriate defaults",
        "clean_text": "Clean and standardize text data",
        "normalize_whitespace": "Normalize whitespace in text fields",
        "remove_special_chars": "Remove special characters from text",

        # Data validation
        "validate_data": "Validate data against defined schemas",
        "check_data_types": "Verify and correct data types",

        # Advanced operations
        "outlier_detection": "Detect and handle outliers in numerical data",
        "variable_selection": "Select relevant variables for analysis",
        "data_transformation": "Apply data transformations",

        # Missing data visualization
        "missing_matrix": "Generate missing data matrix visualization",
        "missing_bar": "Generate missing data bar chart",
        "missing_heatmap": "Generate missing data heatmap",
        "missing_dendrogram": "Generate missing data dendrogram",

        # Feature engineering
        "drop_constant": "Remove constant features",
        "drop_correlated": "Remove highly correlated features",
        "drop_duplicate_features": "Remove duplicate features",

        # ML-based operations
        "dedupe": "ML-based deduplication using fuzzy matching",
    }

    choices = []
    for op in available_ops:
        description = operation_descriptions.get(op, f"Apply {op} operation")
        choices.append({
            'name': f"{op} - {description}",
            'value': op
        })

    return choices


def visualize_command(
    input_file: str,
    viz_type: str,
    output: Optional[str],
    config_file: Optional[str],
    verbose: bool,
) -> None:
    """Generate data visualizations.

    Args:
        input_file: Path to CSV file to visualize.
        viz_type: Type of visualization to generate.
        output: Output path for visualization.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config = None
        if config_file:
            config_manager = ConfigurationManager(config_file)
            config = config_manager.load_config()

        # Initialize cleaner and visualization manager
        cleaner = CSVCleaner(config)
        viz_manager = VisualizationManager()

        # Read the data
        df = cleaner.file_operations.read_csv(input_file)

        click.echo(f"📊 Generating {viz_type} visualization for: {input_file}")

        if viz_type in ["matrix", "bar", "heatmap", "dendrogram"]:
            # Use MissingnoWrapper for missing data visualizations
            if viz_type == "matrix":
                result = cleaner.library_manager.execute_operation(
                    "missing_matrix", df, save_path=output
                )
            elif viz_type == "bar":
                result = cleaner.library_manager.execute_operation(
                    "missing_bar", df, save_path=output
                )
            elif viz_type == "heatmap":
                result = cleaner.library_manager.execute_operation(
                    "missing_heatmap", df, save_path=output
                )
            elif viz_type == "dendrogram":
                result = cleaner.library_manager.execute_operation(
                    "missing_dendrogram", df, save_path=output
                )
        else:
            # Use VisualizationManager for other visualizations
            if viz_type == "quality":
                output_path = viz_manager.create_data_quality_heatmap(df, output)
            elif viz_type == "correlation":
                output_path = viz_manager.create_correlation_matrix(df, output)
            elif viz_type == "distribution":
                output_path = viz_manager.create_distribution_plots(
                    df, save_path=output
                )
            else:
                raise ValueError(f"Unknown visualization type: {viz_type}")

        click.echo(
            f"✅ Visualization saved to: {output_path if 'output_path' in locals() else output}"
        )

    except Exception as e:
        handle_error(e, verbose)


def report_command(
    input_file: str,
    output: Optional[str],
    format: str,
    config_file: Optional[str],
    verbose: bool,
) -> None:
    """Generate comprehensive data quality reports.

    Args:
        input_file: Path to CSV file to analyze.
        output: Output path for report.
        format: Report format (html or json).
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config = None
        if config_file:
            config_manager = ConfigurationManager(config_file)
            config = config_manager.load_config()

        # Initialize cleaner and visualization manager
        cleaner = CSVCleaner(config)
        viz_manager = VisualizationManager()

        # Read the data
        df = cleaner.file_operations.read_csv(input_file)

        click.echo(f"📋 Generating {format.upper()} report for: {input_file}")

        if format == "html":
            output_path = viz_manager.create_summary_report(df, output)
        elif format == "json":
            import json

            if output is None:
                output = "data_report.json"

            # Generate summary statistics
            summary_stats = viz_manager._generate_summary_statistics(df)

            with open(output, "w") as f:
                json.dump(summary_stats, f, indent=2, default=str)

            output_path = output
        else:
            raise ValueError(f"Unknown report format: {format}")

        click.echo(f"✅ Report saved to: {output_path}")

    except Exception as e:
        handle_error(e, verbose)


def ai_suggest_command(
    input_file: str,
    config_file: Optional[str],
    verbose: bool,
    max_suggestions: int = 5,
    include_analysis: bool = True,
) -> None:
    """Get AI-powered cleaning suggestions for a CSV file.

    Args:
        input_file: Path to CSV file to analyze.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
        max_suggestions: Maximum number of suggestions to show.
        include_analysis: Include data analysis in output.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        if config_file:
            config_manager = ConfigurationManager(config_file)
            config = config_manager.load_config()
        else:
            # Load default configuration if no config file specified
            config_manager = ConfigurationManager()
            config = config_manager.load_config()

        # Check if AI is available
        if not AI_AVAILABLE:
            click.echo(
                "❌ AI components are not available. Please install AI dependencies."
            )
            return

        if not config or not config.ai_enabled:
            click.echo(
                "❌ AI is disabled in configuration. Enable AI to use this feature."
            )
            return

        # Initialize cleaner
        cleaner = CSVCleaner(config)

        # Read the data
        df = cleaner.file_operations.read_csv(input_file)

        click.echo(f"🤖 Analyzing {input_file} for AI-powered cleaning suggestions...")

        # Get AI suggestions
        suggestions = cleaner.library_manager.get_ai_suggestions(df)

        if not suggestions:
            click.echo("❌ No AI suggestions available for this dataset.")
            return

        # Display suggestions
        click.echo("\n" + "=" * 60)
        click.echo("🤖 AI CLEANING SUGGESTIONS")
        click.echo("=" * 60)

        for i, suggestion in enumerate(suggestions[:max_suggestions], 1):
            click.echo(f"\n📋 Suggestion {i}:")
            click.echo(f"   🔧 Operation: {suggestion['operation']}")
            click.echo(f"   📚 Library: {suggestion['library']}")
            click.echo(f"   🎯 Confidence: {suggestion['confidence']:.1%}")
            click.echo(f"   💡 Reasoning: {suggestion['reasoning']}")
            click.echo(f"   📊 Impact: {suggestion['estimated_impact']}")

            if suggestion["parameters"]:
                click.echo(f"   ⚙️  Parameters: {suggestion['parameters']}")

        # Include data analysis if requested
        if include_analysis:
            analysis = cleaner.library_manager.get_ai_analysis(df)
            if analysis and analysis.get("ai_enabled"):
                profile = analysis["data_profile"]
                click.echo("\n📊 DATA ANALYSIS:")
                click.echo(f"   📈 Rows: {profile['row_count']:,}")
                click.echo(f"   📊 Columns: {profile['column_count']}")
                click.echo(f"   ❓ Missing data: {profile['missing_percentage']:.1f}%")
                click.echo(
                    f"   🔄 Duplicate rows: {profile['duplicate_percentage']:.1f}%"
                )
                # Display memory usage with appropriate precision
                memory_mb = profile["memory_usage_mb"]
                if memory_mb < 0.01:
                    click.echo(f"   💾 Memory usage: {memory_mb:.4f} MB")
                else:
                    click.echo(f"   💾 Memory usage: {memory_mb:.2f} MB")
                click.echo(f"   ⭐ Quality score: {profile['quality_score']:.1%}")

        click.echo("\n" + "=" * 60)

    except Exception as e:
        handle_error(e, verbose)


def ai_analyze_command(
    input_file: str,
    config_file: Optional[str],
    verbose: bool,
    output: Optional[str] = None,
) -> None:
    """Get AI-powered data analysis for a CSV file.

    Args:
        input_file: Path to CSV file to analyze.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
        output: Output file for analysis results (JSON format).
    """
    setup_logging(verbose)

    try:
        # Load configuration
        if config_file:
            config_manager = ConfigurationManager(config_file)
            config = config_manager.load_config()
        else:
            # Load default configuration if no config file specified
            config_manager = ConfigurationManager()
            config = config_manager.load_config()

        # Check if AI is available
        if not AI_AVAILABLE:
            click.echo(
                "❌ AI components are not available. Please install AI dependencies."
            )
            return

        if not config or not config.ai_enabled:
            click.echo(
                "❌ AI is disabled in configuration. Enable AI to use this feature."
            )
            return

        # Initialize cleaner
        cleaner = CSVCleaner(config)

        # Read the data
        df = cleaner.file_operations.read_csv(input_file)

        click.echo(f"🔍 Performing AI-powered analysis of {input_file}...")

        # Get AI analysis
        analysis = cleaner.library_manager.get_ai_analysis(df)

        if not analysis or not analysis.get("ai_enabled"):
            click.echo("❌ AI analysis not available for this dataset.")
            return

        # Display analysis results
        profile = analysis["data_profile"]
        learning = analysis.get("learning_summary", {})

        click.echo("\n" + "=" * 60)
        click.echo("🔍 AI DATA ANALYSIS")
        click.echo("=" * 60)

        click.echo("\n📊 DATASET PROFILE:")
        click.echo(f"   📈 Rows: {profile['row_count']:,}")
        click.echo(f"   📊 Columns: {profile['column_count']}")
        click.echo(f"   ❓ Missing data: {profile['missing_percentage']:.1f}%")
        click.echo(f"   🔄 Duplicate rows: {profile['duplicate_percentage']:.1f}%")
        # Display memory usage with appropriate precision
        memory_mb = profile["memory_usage_mb"]
        if memory_mb < 0.01:
            click.echo(f"   💾 Memory usage: {memory_mb:.4f} MB")
        else:
            click.echo(f"   💾 Memory usage: {memory_mb:.2f} MB")
        click.echo(f"   ⭐ Quality score: {profile['quality_score']:.1%}")

        click.echo("\n📋 DATA TYPES:")
        click.echo(f"   📝 Text columns: {profile['has_text_columns']}")
        click.echo(f"   🔢 Numeric columns: {profile['has_numeric_columns']}")
        click.echo(f"   📅 Date columns: {profile['has_date_columns']}")
        click.echo(f"   🏷️  Categorical columns: {profile['has_categorical_columns']}")

        if learning and learning.get("total_feedback", 0) > 0:
            click.echo("\n🧠 AI LEARNING SUMMARY:")
            click.echo(f"   📊 Total feedback: {learning['total_feedback']}")
            click.echo(f"   ✅ Success rate: {learning['success_rate']:.1%}")

            if learning.get("most_successful_operations"):
                click.echo("   🏆 Most successful operations:")
                for op, count in learning["most_successful_operations"][:3]:
                    click.echo(f"      • {op}: {count} times")

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(analysis, f, indent=2, default=str)
            click.echo(f"\n💾 Analysis saved to: {output}")

        click.echo("\n" + "=" * 60)

    except Exception as e:
        handle_error(e, verbose)


def ai_configure_command(
    action: str,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    config_file: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Configure AI settings and API keys.

    Args:
        action: Configuration action (show, set, remove, validate).
        provider: AI provider name (openai, anthropic, local).
        api_key: API key for the provider.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        if action == "show":
            click.echo("\n" + "=" * 50)
            click.echo("🤖 AI CONFIGURATION")
            click.echo("=" * 50)

            click.echo(f"✅ AI Enabled: {config.ai_enabled}")
            click.echo(f"🎯 Default Provider: {config.default_llm_provider}")
            click.echo(f"💰 Cost Limit: ${config.ai_cost_limit}")
            click.echo(f"🧠 Learning Enabled: {config.ai_learning_enabled}")
            click.echo(f"💬 Explanations Enabled: {config.ai_explanation_enabled}")
            click.echo(f"🤖 Auto Suggest: {config.ai_auto_suggest}")

            # Add AI logging information
            click.echo("\n📝 AI LOGGING:")
            click.echo(f"   ✅ Enabled: {config.ai_logging_enabled}")
            click.echo(
                f"   📁 Log File: {config.ai_log_file or '~/.csv-cleaner/logs/ai_interactions.log'}"
            )
            click.echo(f"   🔒 Mask Sensitive Data: {config.ai_log_mask_sensitive_data}")
            click.echo(f"   📅 Retention Days: {config.ai_log_retention_days}")

            if config.ai_api_keys:
                click.echo("\n🔑 Configured Providers:")
                for provider_name, key in config.ai_api_keys.items():
                    masked_key = key[:8] + "..." if len(key) > 8 else "***"
                    click.echo(f"   • {provider_name}: {masked_key}")
            else:
                click.echo("\n❌ No API keys configured")

        elif action == "set":
            if not provider or not api_key:
                click.echo("❌ Provider and API key are required for 'set' action")
                return

            config_manager.set_ai_api_key(provider, api_key)
            click.echo(f"✅ API key set for {provider}")

        elif action == "remove":
            if not provider:
                click.echo("❌ Provider is required for 'remove' action")
                return

            config_manager.remove_ai_api_key(provider)
            click.echo(f"✅ API key removed for {provider}")

        elif action == "validate":
            validation = config_manager.validate_ai_config()

            click.echo("\n" + "=" * 50)
            click.echo("🔍 AI CONFIGURATION VALIDATION")
            click.echo("=" * 50)

            click.echo(f"✅ AI Enabled: {validation['ai_enabled']}")

            if validation["providers_available"]:
                click.echo(
                    f"✅ Available Providers: {', '.join(validation['providers_available'])}"
                )
            else:
                click.echo("❌ No providers available")

            if validation["api_keys_configured"]:
                click.echo(
                    f"🔑 API Keys: {', '.join(validation['api_keys_configured'])}"
                )
            else:
                click.echo("❌ No API keys configured")

            if validation["issues"]:
                click.echo("\n❌ Issues:")
                for issue in validation["issues"]:
                    click.echo(f"   • {issue}")

            if validation["warnings"]:
                click.echo("\n⚠️  Warnings:")
                for warning in validation["warnings"]:
                    click.echo(f"   • {warning}")

        else:
            click.echo(f"❌ Unknown action: {action}")

    except Exception as e:
        handle_error(e, verbose)


def ai_model_command(
    action: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    config_file: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Configure AI models for providers.

    Args:
        action: Configuration action (show, set).
        provider: Provider name (openai, anthropic, local).
        model: Model name to set.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config_manager = ConfigurationManager(config_file)
        config = config_manager.load_config()

        if action == "show":
            click.echo("\n" + "=" * 50)
            click.echo("🤖 AI MODEL CONFIGURATION")
            click.echo("=" * 50)

            click.echo(f"🔧 OpenAI Model: {config.ai_openai_model}")
            click.echo(f"🔧 Anthropic Model: {config.ai_anthropic_model}")
            click.echo(f"🔧 Local Model: {config.ai_local_model}")

            # Show available models
            click.echo("\n📋 Available Models:")
            click.echo("   OpenAI: gpt-4o-mini, gpt-4o, gpt-3.5-turbo, gpt-4")
            click.echo(
                "   Anthropic: claude-3-5-sonnet-20241022, claude-3-haiku-20240307"
            )
            click.echo("   Local: llama3.1:8b, llama3.1:70b, llama2")

        elif action == "set":
            if not provider or not model:
                click.echo("❌ Provider and model are required for 'set' action")
                return

            # Validate provider
            if provider not in ["openai", "anthropic", "local"]:
                click.echo("❌ Invalid provider. Must be: openai, anthropic, local")
                return

            # Set model based on provider
            if provider == "openai":
                config.ai_openai_model = model
            elif provider == "anthropic":
                config.ai_anthropic_model = model
            elif provider == "local":
                config.ai_local_model = model

            # Save configuration
            config_manager.save_config(config)
            click.echo(f"✅ Model set for {provider}: {model}")

        else:
            click.echo(f"❌ Unknown action: {action}")

    except Exception as e:
        handle_error(e, verbose)


def ai_clean_command(
    input_file: str,
    output_file: str,
    config_file: Optional[str],
    verbose: bool,
    auto_confirm: bool = False,
    dry_run: bool = False,
    max_suggestions: int = 5,
) -> None:
    """AI-powered automatic cleaning of CSV data.

    Args:
        input_file: Path to input CSV file.
        output_file: Path to output CSV file.
        config_file: Path to configuration file.
        verbose: Enable verbose logging.
        auto_confirm: Automatically confirm all AI suggestions.
        dry_run: Show execution plan without modifying files.
        max_suggestions: Maximum number of suggestions to consider.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config = load_configuration(config_file)

        # If no config file specified, create default config with AI enabled check
        if not config:
            from ..core.config import Config
            config = Config()
            # Check if AI is available and enabled in environment
            if AI_AVAILABLE:
                config.ai_enabled = True

        # Initialize cleaner
        cleaner = initialize_cleaner(config)

        # Validate input file
        if not validate_input_file(input_file):
            return

        # Check if AI is available
        if not AI_AVAILABLE:
            click.echo(
                "❌ AI components are not available. Please install AI dependencies."
            )
            return

        # Check AI configuration more thoroughly
        ai_enabled = False
        if config:
            ai_enabled = getattr(config, 'ai_enabled', False)

        if not ai_enabled:
            click.echo(
                "❌ AI is disabled in configuration. Enable AI to use this feature."
            )
            click.echo("💡 Use 'csv-cleaner ai-configure show' to check AI settings")
            return

        click.echo(f"🤖 Starting AI-powered cleaning of {input_file}...")

        # Read the data
        df = cleaner.file_operations.read_csv(input_file)
        click.echo(f"📊 Loaded {len(df):,} rows and {len(df.columns)} columns")

        # Get AI suggestions
        click.echo("🧠 Analyzing data and generating AI suggestions...")
        suggestions = cleaner.library_manager.get_ai_suggestions(df)

        if not suggestions:
            click.echo("❌ No AI suggestions available for this dataset.")
            return

        # Convert to CleaningSuggestion objects
        from ..core.ai_agent import CleaningSuggestion

        cleaning_suggestions = []
        for suggestion_dict in suggestions[:max_suggestions]:
            try:
                suggestion = CleaningSuggestion(
                    operation=suggestion_dict["operation"],
                    library=suggestion_dict["library"],
                    parameters=suggestion_dict["parameters"],
                    confidence=suggestion_dict["confidence"],
                    reasoning=suggestion_dict["reasoning"],
                    estimated_impact=suggestion_dict["estimated_impact"],
                    priority=suggestion_dict.get("priority", 1),
                )
                cleaning_suggestions.append(suggestion)
            except Exception as e:
                logger.warning(f"Invalid suggestion skipped: {e}")
                continue

        if not cleaning_suggestions:
            click.echo("❌ No valid AI suggestions found.")
            return

        # Get execution plan
        execution_plan = cleaner.library_manager.ai_agent.get_execution_plan(
            cleaning_suggestions
        )

        # Display execution plan
        click.echo("\n" + "=" * 60)
        click.echo("🤖 AI EXECUTION PLAN")
        click.echo("=" * 60)
        click.echo(f"📋 Total suggestions: {execution_plan['total_suggestions']}")
        click.echo(f"✅ Valid suggestions: {execution_plan['valid_suggestions']}")
        click.echo(f"🎯 High confidence: {execution_plan['confidence_summary']['high']}")
        click.echo(
            f"⚠️  Medium confidence: {execution_plan['confidence_summary']['medium']}"
        )
        click.echo(f"❓ Low confidence: {execution_plan['confidence_summary']['low']}")

        click.echo("\n📝 Execution Order:")
        for step in execution_plan["execution_order"]:
            confidence_emoji = (
                "🟢"
                if step["confidence_level"] == "High"
                else "🟡"
                if step["confidence_level"] == "Medium"
                else "🔴"
            )
            click.echo(
                f"   {step['step']}. {confidence_emoji} {step['operation']} ({step['library']}) - {step['confidence_level']} confidence"
            )
            click.echo(f"      💡 {step['reasoning']}")
            click.echo(f"      📊 {step['estimated_impact']}")

        # Dry run mode
        if dry_run:
            click.echo("\n🔍 DRY RUN MODE - No files will be modified")
            click.echo("✅ Execution plan generated successfully")
            return

        # User confirmation (unless auto_confirm)
        if not auto_confirm:
            click.echo(
                f"\n❓ Do you want to execute these {len(execution_plan['execution_order'])} operations?"
            )
            if not click.confirm("Continue with AI-powered cleaning?"):
                click.echo("❌ Operation cancelled by user")
                return

        # Execute AI suggestions
        click.echo("\n🚀 Executing AI suggestions...")
        with click.progressbar(
            length=len(execution_plan["execution_order"]),
            label="Executing AI operations",
        ) as bar:
            (
                result_df,
                execution_summary,
            ) = cleaner.library_manager.ai_agent.execute_suggestions(
                df, cleaning_suggestions, cleaner.library_manager, auto_confirm
            )
            bar.update(len(execution_plan["execution_order"]))

        # Display execution results
        click.echo("\n" + "=" * 60)
        click.echo("🤖 AI EXECUTION RESULTS")
        click.echo("=" * 60)

        if execution_summary["success"]:
            click.echo(
                f"✅ Successfully executed {execution_summary['executed_count']} operations"
            )

            # Show executed operations
            click.echo("\n📋 Executed Operations:")
            for op in execution_summary["executed_operations"]:
                click.echo(
                    f"   ✅ {op['operation']} ({op['library']}) - {op['confidence']:.1%} confidence"
                )

            # Save results
            cleaner.file_operations.write_csv(result_df, output_file)
            click.echo(f"\n💾 Results saved to: {output_file}")

            # Show data changes
            original_rows, original_cols = df.shape
            result_rows, result_cols = result_df.shape
            click.echo("\n📊 Data Changes:")
            click.echo(
                f"   📈 Rows: {original_rows:,} → {result_rows:,} ({result_rows - original_rows:+d})"
            )
            click.echo(
                f"   📊 Columns: {original_cols} → {result_cols} ({result_cols - original_cols:+d})"
            )

        else:
            click.echo("❌ Execution completed with errors")
            click.echo(
                f"✅ Successfully executed: {execution_summary['executed_count']} operations"
            )
            click.echo(f"❌ Failed operations: {len(execution_summary['errors'])}")

            # Show errors
            if execution_summary["errors"]:
                click.echo("\n❌ Errors:")
                for error in execution_summary["errors"]:
                    click.echo(f"   • {error['operation']}: {error['error']}")

            # Save partial results if any operations succeeded
            if execution_summary["executed_count"] > 0:
                cleaner.file_operations.write_csv(result_df, output_file)
                click.echo(f"\n💾 Partial results saved to: {output_file}")

        click.echo("\n" + "=" * 60)

    except Exception as e:
        handle_error(e, verbose)
