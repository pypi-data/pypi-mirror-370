#!/usr/bin/env python3
"""
Main CLI entry point for CSV Data Cleaner.
"""

import click
from .commands import (
    clean_command,
    validate_command,
    analyze_command,
    info_command,
    operations_command,
    config_command,
    visualize_command,
    report_command,
    dedupe_command,
    performance_command,
    ai_suggest_command,
    ai_analyze_command,
    ai_configure_command,
    ai_logs_command,
    ai_model_command,
    ai_clean_command,
)
from ..feature_gate import detect_package_version, FeatureGate


def get_available_commands(version: str = "basic") -> list:
    """Get list of available commands for the given version.

    Args:
        version: Package version ("basic" or "pro")

    Returns:
        List of available command functions.
    """
    feature_gate = FeatureGate(version)
    available_commands = feature_gate.get_available_commands()

    command_mapping = {
        "clean": clean,
        "validate": validate,
        "analyze": analyze,
        "info": info,
        "operations": operations,
        "config": config,
        "visualize": visualize,
        "report": report,
        "dedupe": dedupe,
        "performance": performance,
        "ai-suggest": ai_suggest,
        "ai-analyze": ai_analyze,
        "ai-configure": ai_configure,
        "ai-logs": ai_logs,
        "ai-model": ai_model,
        "ai-clean": ai_clean,
    }

    return [
        command_mapping[cmd] for cmd in available_commands if cmd in command_mapping
    ]


def show_upgrade_prompt(feature_name: str):
    """Show upgrade prompt for premium features.

    Args:
        feature_name: Name of the feature that requires upgrade.
    """
    feature_gate = FeatureGate(detect_package_version())
    message = feature_gate.get_upgrade_message(feature_name)

    if message:
        click.echo(f"\n💡 {message}")
        click.echo("   Upgrade to CSV Cleaner Pro for advanced data analysis features!")
        click.echo("   Visit: https://gumroad.com/csv-cleaner-pro\n")


@click.group()
@click.version_option(version="1.0.0", prog_name="CSV Data Cleaner")
def cli():
    """CSV Data Cleaner - Self-contained tool with AI capabilities.

    A powerful tool for cleaning CSV data using industry-standard Python libraries
    with optional AI-powered intelligent suggestions.
    """
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--operations", "-ops", help="Comma-separated list of operations to perform"
)
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--chunk-size", type=int, help="Chunk size for processing large files")
@click.option(
    "--parallel/--no-parallel", default=True, help="Enable/disable parallel processing"
)
@click.option("--max-memory", type=float, help="Maximum memory usage in GB")
@click.option(
    "--dry-run", is_flag=True, help="Preview operations without modifying files"
)
def clean(
    input_file,
    output_file,
    operations,
    config,
    interactive,
    verbose,
    chunk_size,
    parallel,
    max_memory,
    dry_run,
):
    """Clean a CSV file using specified operations.

    INPUT_FILE: Path to the input CSV file
    OUTPUT_FILE: Path to the output CSV file

    Examples:
        csv-cleaner clean data.csv cleaned.csv
        csv-cleaner clean data.csv cleaned.csv --operations "remove_duplicates,clean_names"
        csv-cleaner clean data.csv cleaned.csv --interactive

    Note: Use 'csv-cleaner operations' to see all available operations.
    """
    clean_command(
        input_file,
        output_file,
        operations,
        config,
        interactive,
        verbose,
        chunk_size,
        parallel,
        max_memory,
        dry_run,
    )


@cli.command()
@click.argument("input_file", type=click.Path())
@click.option(
    "--schema", "-s", type=click.Path(), help="Path to validation schema file"
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output path for validation report"
)
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def validate(input_file, schema, output, config, verbose):
    """Validate a CSV file and show information.

    INPUT_FILE: Path to the CSV file to validate

    Examples:
        csv-cleaner validate data.csv
        csv-cleaner validate data.csv --verbose
    """
    validate_command(input_file, schema, output, config, verbose)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Output path for analysis report"
)
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def analyze(input_file, output, config, verbose):
    """Analyze CSV data and generate smart validation rules.

    INPUT_FILE: Path to the CSV file to analyze

    Examples:
        csv-cleaner analyze data.csv
        csv-cleaner analyze data.csv --output analysis_report.txt
        csv-cleaner analyze data.csv --verbose
    """
    analyze_command(input_file, output, config, verbose)


@cli.command()
def info():
    """Show information about CSV Data Cleaner.

    Displays available wrappers, operations, and performance statistics.

    Examples:
        csv-cleaner info
    """
    info_command()


@cli.command()
def operations():
    """Show all available operations for CSV Data Cleaner.

    Displays a complete list of all operations available in each wrapper.

    Examples:
        csv-cleaner operations
    """
    operations_command()


@cli.command()
@click.argument("action", type=click.Choice(["show", "set", "get", "init"]))
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def config(action, key, value, config, verbose):
    """Manage CSV Data Cleaner configuration.

    ACTION: Configuration action (show, set, get, init)
    KEY: Configuration key (for set/get actions)
    VALUE: Configuration value (for set action)

    Examples:
        csv-cleaner config show
        csv-cleaner config set backup_enabled true
        csv-cleaner config get chunk_size
        csv-cleaner config init
    """
    config_command(action, key, value, config, verbose)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--type",
    "-t",
    type=click.Choice(
        [
            "matrix",
            "bar",
            "heatmap",
            "dendrogram",
            "quality",
            "correlation",
            "distribution",
        ]
    ),
    default="matrix",
    help="Type of visualization to generate",
)
@click.option("--output", "-o", type=click.Path(), help="Output path for visualization")
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def visualize(input_file, type, output, config, verbose):
    """Generate data visualizations.

    INPUT_FILE: Path to the input CSV file

    Examples:
        csv-cleaner visualize data.csv
        csv-cleaner visualize data.csv --type heatmap
        csv-cleaner visualize data.csv --type quality --output quality_plot.png
    """
    visualize_command(input_file, type, output, config, verbose)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output path for report")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["html", "json"]),
    default="html",
    help="Report format",
)
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def report(input_file, output, format, config, verbose):
    """Generate comprehensive data quality reports.

    INPUT_FILE: Path to the input CSV file

    Examples:
        csv-cleaner report data.csv
        csv-cleaner report data.csv --format json --output report.json
        csv-cleaner report data.csv --output detailed_report.html
    """
    report_command(input_file, output, format, config, verbose)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=0.5,
    help="Deduplication threshold (0.0-1.0)",
)
@click.option("--interactive", "-i", is_flag=True, help="Enable interactive training")
@click.option("--training-file", type=click.Path(), help="Path to training data file")
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def dedupe(
    input_file, output_file, threshold, interactive, training_file, config, verbose
):
    """Perform ML-based deduplication on CSV data.

    INPUT_FILE: Path to the input CSV file
    OUTPUT_FILE: Path to the output CSV file

    Examples:
        csv-cleaner dedupe data.csv deduplicated.csv
        csv-cleaner dedupe data.csv deduplicated.csv --threshold 0.8
        csv-cleaner dedupe data.csv deduplicated.csv --interactive
        csv-cleaner dedupe data.csv deduplicated.csv --training-file training.json
    """
    show_upgrade_prompt("dedupe")
    dedupe_command(
        input_file, output_file, threshold, interactive, training_file, config, verbose
    )


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--operations", "-ops", help="Comma-separated list of operations to test")
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def performance(input_file, operations, config, verbose):
    """Analyze performance characteristics of data cleaning operations.

    INPUT_FILE: Path to the input CSV file

    Examples:
        csv-cleaner performance data.csv
        csv-cleaner performance data.csv --operations "remove_duplicates,clean_names"
        csv-cleaner performance data.csv --verbose
    """
    show_upgrade_prompt("performance")
    performance_command(input_file, operations, config, verbose)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--max-suggestions",
    type=int,
    default=5,
    help="Maximum number of suggestions to show",
)
@click.option("--no-analysis", is_flag=True, help="Skip data analysis in output")
def ai_suggest(input_file, config, verbose, max_suggestions, no_analysis):
    """Get AI-powered cleaning suggestions for a CSV file.

    INPUT_FILE: Path to the input CSV file

    Examples:
        csv-cleaner ai-suggest data.csv
        csv-cleaner ai-suggest data.csv --max-suggestions 10
        csv-cleaner ai-suggest data.csv --no-analysis
    """
    show_upgrade_prompt("ai-suggest")
    ai_suggest_command(input_file, config, verbose, max_suggestions, not no_analysis)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for analysis results (JSON format)",
)
def ai_analyze(input_file, config, verbose, output):
    """Get AI-powered data analysis for a CSV file.

    INPUT_FILE: Path to the input CSV file

    Examples:
        csv-cleaner ai-analyze data.csv
        csv-cleaner ai-analyze data.csv --output analysis.json
    """
    show_upgrade_prompt("ai-analyze")
    ai_analyze_command(input_file, config, verbose, output)


@cli.command()
@click.argument("action", type=click.Choice(["show", "set", "remove", "validate"]))
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "local"]),
    help="AI provider name",
)
@click.option("--api-key", help="API key for the provider")
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def ai_configure(action, provider, api_key, config, verbose):
    """Configure AI settings and API keys.

    ACTION: Configuration action (show, set, remove, validate)

    Examples:
        csv-cleaner ai-configure show
        csv-cleaner ai-configure set --provider openai --api-key sk-...
        csv-cleaner ai-configure remove --provider openai
        csv-cleaner ai-configure validate
    """
    show_upgrade_prompt("ai-configure")
    ai_configure_command(action, provider, api_key, config, verbose)


@cli.command()
@click.option(
    "--days", "-d", type=int, default=7, help="Number of days to include in summary"
)
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def ai_logs(days, config, verbose):
    """View AI interaction logs and usage summary.

    Examples:
        csv-cleaner ai-logs
        csv-cleaner ai-logs --days 30
        csv-cleaner ai-logs --verbose
    """
    show_upgrade_prompt("ai-logs")
    ai_logs_command(days, config, verbose)


@cli.command()
@click.argument("action", type=click.Choice(["show", "set"]))
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "local"]),
    help="Provider name",
)
@click.option("--model", help="Model name to set")
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def ai_model(action, provider, model, config, verbose):
    """Configure AI models for providers.

    Examples:
        csv-cleaner ai-model show
        csv-cleaner ai-model set --provider openai --model gpt-4o
        csv-cleaner ai-model set --provider anthropic --model claude-3-haiku-20240307
    """
    show_upgrade_prompt("ai-model")
    ai_model_command(action, provider, model, config, verbose)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--config", "-c", type=click.Path(), help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--auto-confirm", is_flag=True, help="Automatically confirm all AI suggestions"
)
@click.option(
    "--dry-run", is_flag=True, help="Show execution plan without modifying files"
)
@click.option(
    "--max-suggestions",
    type=int,
    default=5,
    help="Maximum number of suggestions to consider",
)
def ai_clean(
    input_file, output_file, config, verbose, auto_confirm, dry_run, max_suggestions
):
    """AI-powered automatic cleaning of CSV data.

    INPUT_FILE: Path to the input CSV file
    OUTPUT_FILE: Path to the output CSV file

    Examples:
        csv-cleaner ai-clean data.csv cleaned.csv
        csv-cleaner ai-clean data.csv cleaned.csv --auto-confirm
        csv-cleaner ai-clean data.csv cleaned.csv --dry-run
        csv-cleaner ai-clean data.csv cleaned.csv --max-suggestions 10
    """
    show_upgrade_prompt("ai-clean")
    ai_clean_command(
        input_file, output_file, config, verbose, auto_confirm, dry_run, max_suggestions
    )


if __name__ == "__main__":
    cli()
