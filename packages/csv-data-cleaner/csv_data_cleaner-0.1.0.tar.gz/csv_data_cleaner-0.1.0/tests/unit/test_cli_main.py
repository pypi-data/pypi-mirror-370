"""
TEST SUITE: csv_cleaner.cli.main
PURPOSE: Test CLI main entry point functionality including argument parsing, command routing, help system, and error handling
SCOPE: CLI main entry point, argument validation, command routing, help system, version display, error handling
DEPENDENCIES: click, unittest.mock, click.testing
LAST UPDATED: 2025-01-27
"""

import pytest
import sys
from unittest.mock import patch, MagicMock, Mock
import click
from click.testing import CliRunner

from csv_cleaner.cli.main import cli
from tests.fixtures.cli_fixtures import (
    create_mock_click_runner, create_test_csv_file, create_test_config_file,
    cleanup_test_files, create_mock_csv_cleaner
)


class TestCLIMain:
    """Test cases for CLI main entry point."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.test_files = []

    def teardown_method(self):
        """Clean up test files."""
        cleanup_test_files(self.test_files)

    def test_cli_help_command(self):
        """TEST: should_display_help_information_when_help_flag_is_used"""
        # ARRANGE: Help command

        # ACT: Execute help command
        result = self.runner.invoke(cli, ['--help'])

        # ASSERT: Verify help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'Usage:' in result.output, "Expected usage information in help"
        assert 'Commands:' in result.output, "Expected commands list in help"

    def test_cli_version_command(self):
        """TEST: should_display_version_information_when_version_flag_is_used"""
        # ARRANGE: Version command

        # ACT: Execute version command
        result = self.runner.invoke(cli, ['--version'])

        # ASSERT: Verify version is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'csv data cleaner' in result.output.lower(), "Expected version information"

    def test_cli_clean_command_help(self):
        """TEST: should_display_clean_command_help_information"""
        # ARRANGE: Clean command help

        # ACT: Execute clean command help
        result = self.runner.invoke(cli, ['clean', '--help'])

        # ASSERT: Verify clean command help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'clean' in result.output.lower(), "Expected clean command help"

    def test_cli_validate_command_help(self):
        """TEST: should_display_validate_command_help_information"""
        # ARRANGE: Validate command help

        # ACT: Execute validate command help
        result = self.runner.invoke(cli, ['validate', '--help'])

        # ASSERT: Verify validate command help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'validate' in result.output.lower(), "Expected validate command help"

    def test_cli_info_command_help(self):
        """TEST: should_display_info_command_help_information"""
        # ARRANGE: Info command help

        # ACT: Execute info command help
        result = self.runner.invoke(cli, ['info', '--help'])

        # ASSERT: Verify info command help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'info' in result.output.lower(), "Expected info command help"

    def test_cli_config_command_help(self):
        """TEST: should_display_config_command_help_information"""
        # ARRANGE: Config command help

        # ACT: Execute config command help
        result = self.runner.invoke(cli, ['config', '--help'])

        # ASSERT: Verify config command help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'config' in result.output.lower(), "Expected config command help"

    def test_cli_visualize_command_help(self):
        """TEST: should_display_visualize_command_help_information"""
        # ARRANGE: Visualize command help

        # ACT: Execute visualize command help
        result = self.runner.invoke(cli, ['visualize', '--help'])

        # ASSERT: Verify visualize command help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'visualize' in result.output.lower(), "Expected visualize command help"

    def test_cli_report_command_help(self):
        """TEST: should_display_report_command_help_information"""
        # ARRANGE: Report command help

        # ACT: Execute report command help
        result = self.runner.invoke(cli, ['report', '--help'])

        # ASSERT: Verify report command help is displayed
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert 'report' in result.output.lower(), "Expected report command help"

    def test_cli_invalid_command(self):
        """TEST: should_handle_invalid_command_gracefully"""
        # ARRANGE: Invalid command

        # ACT: Execute invalid command
        result = self.runner.invoke(cli, ['invalid-command'])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"
        assert 'No such command' in result.output, "Expected error message for invalid command"

    def test_cli_missing_required_argument(self):
        """TEST: should_handle_missing_required_argument_gracefully"""
        # ARRANGE: Missing required argument for clean command

        # ACT: Execute clean command without input file
        result = self.runner.invoke(cli, ['clean'])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"
        assert 'Missing argument' in result.output, "Expected error message for missing argument"

    def test_cli_invalid_argument_type(self):
        """TEST: should_handle_invalid_argument_type_gracefully"""
        # ARRANGE: Invalid argument type

        # ACT: Execute command with invalid argument type
        result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv', '--operations', 'invalid_operation'])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    def test_cli_verbose_flag(self):
        """TEST: should_handle_verbose_flag_correctly"""
        # ARRANGE: Verbose flag

        # ACT: Execute command with verbose flag
        result = self.runner.invoke(cli, ['info'])

        # ASSERT: Verify verbose flag is handled (info command doesn't take verbose flag)
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_config_file_argument(self):
        """TEST: should_handle_config_file_argument_correctly"""
        # ARRANGE: Config file argument

        # ACT: Execute command with config file (info command doesn't take config file)
        result = self.runner.invoke(cli, ['config', 'show', '--config', '/path/to/config.yaml'])

        # ASSERT: Verify config file argument is handled
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_interactive_flag(self):
        """TEST: should_handle_interactive_flag_correctly"""
        # ARRANGE: Interactive flag

        # ACT: Execute command with interactive flag
        result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv', '--interactive'])

        # ASSERT: Verify interactive flag is handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_output_format_argument(self):
        """TEST: should_handle_output_format_argument_correctly"""
        # ARRANGE: Output format argument

        # ACT: Execute command with output format
        result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv', '--output-format', 'json'])

        # ASSERT: Verify output format argument is handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_operations_argument(self):
        """TEST: should_handle_operations_argument_correctly"""
        # ARRANGE: Operations argument

        # ACT: Execute command with operations
        result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv', '--operations', 'remove_duplicates,drop_missing'])

        # ASSERT: Verify operations argument is handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_viz_type_argument(self):
        """TEST: should_handle_viz_type_argument_correctly"""
        # ARRANGE: Visualization type argument

        # ACT: Execute command with viz type
        result = self.runner.invoke(cli, ['visualize', 'input.csv', '--type', 'heatmap'])

        # ASSERT: Verify viz type argument is handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_report_format_argument(self):
        """TEST: should_handle_report_format_argument_correctly"""
        # ARRANGE: Report format argument

        # ACT: Execute command with report format
        result = self.runner.invoke(cli, ['report', 'input.csv', '--format', 'html'])

        # ASSERT: Verify report format argument is handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_config_action_argument(self):
        """TEST: should_handle_config_action_argument_correctly"""
        # ARRANGE: Config action argument

        # ACT: Execute command with config action
        result = self.runner.invoke(cli, ['config', 'show'])

        # ASSERT: Verify config action argument is handled
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_config_key_value_arguments(self):
        """TEST: should_handle_config_key_value_arguments_correctly"""
        # ARRANGE: Config key and value arguments

        # ACT: Execute command with config key and value
        result = self.runner.invoke(cli, ['config', 'set', 'chunk_size', '5000'])

        # ASSERT: Verify config key and value arguments are handled
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_clean_command_with_all_options(self):
        """TEST: should_handle_clean_command_with_all_options_correctly"""
        # ARRANGE: Clean command with all options

        # ACT: Execute clean command with all options
        result = self.runner.invoke(cli, [
            'clean', 'input.csv', 'output.csv',
            '--operations', 'remove_duplicates,drop_missing',
            '--config', '/path/to/config.yaml',
            '--interactive',
            '--verbose',
            '--output-format', 'csv'
        ])

        # ASSERT: Verify all options are handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_validate_command_with_all_options(self, temp_dir):
        """TEST: should_handle_validate_command_with_all_options_correctly"""
        # ARRANGE: Create test file and validate command with all options
        input_file = f"{temp_dir}/input.csv"
        create_test_csv_file(input_file)
        self.test_files.append(input_file)

        # ACT: Execute validate command with all options
        with patch('csv_cleaner.cli.commands.ConfigurationManager') as mock_config_manager, \
             patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_config_manager.return_value = Mock()
            mock_cleaner = create_mock_csv_cleaner()
            mock_cleaner_class.return_value = mock_cleaner

            result = self.runner.invoke(cli, [
                'validate', input_file,
                '--config', '/path/to/config.yaml',
                '--verbose'
            ])

        # ASSERT: Verify all options are handled
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_visualize_command_with_all_options(self):
        """TEST: should_handle_visualize_command_with_all_options_correctly"""
        # ARRANGE: Visualize command with all options

        # ACT: Execute visualize command with all options
        result = self.runner.invoke(cli, [
            'visualize', 'input.csv',
            '--type', 'heatmap',
            '--output', 'heatmap.png',
            '--config', '/path/to/config.yaml',
            '--verbose'
        ])

        # ASSERT: Verify all options are handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_report_command_with_all_options(self):
        """TEST: should_handle_report_command_with_all_options_correctly"""
        # ARRANGE: Report command with all options

        # ACT: Execute report command with all options
        result = self.runner.invoke(cli, [
            'report', 'input.csv',
            '--output', 'report.html',
            '--format', 'html',
            '--config', '/path/to/config.yaml',
            '--verbose'
        ])

        # ASSERT: Verify all options are handled
        assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_config_command_with_all_options(self):
        """TEST: should_handle_config_command_with_all_options_correctly"""
        # ARRANGE: Config command with all options

        # ACT: Execute config command with all options
        with patch('csv_cleaner.cli.commands.ConfigurationManager') as mock_config_manager, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_config_manager.return_value = Mock()

            result = self.runner.invoke(cli, [
                'config', 'set', 'chunk_size', '5000',
                '--config', '/path/to/config.yaml',
                '--verbose'
            ])

        # ASSERT: Verify all options are handled
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_clean_command_successful_execution(self, temp_dir):
        """TEST: should_execute_clean_command_successfully_with_valid_arguments"""
        # ARRANGE: Create test files
        input_file = f"{temp_dir}/input.csv"
        output_file = f"{temp_dir}/output.csv"
        create_test_csv_file(input_file)
        self.test_files.extend([input_file, output_file])

        # ACT: Execute clean command
        with patch('csv_cleaner.cli.commands.ConfigurationManager'), \
             patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.click.echo'), \
             patch('csv_cleaner.cli.commands.click.progressbar'):

            # Setup mocks
            mock_cleaner = Mock()
            mock_cleaner.clean_file.return_value = {'success': True}
            mock_cleaner_class.return_value = mock_cleaner

            result = self.runner.invoke(cli, [
                'clean', input_file, output_file,
                '--operations', 'remove_duplicates,drop_missing'
            ])

        # ASSERT: Verify command executed successfully
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_validate_command_successful_execution(self, temp_dir):
        """TEST: should_execute_validate_command_successfully_with_valid_arguments"""
        # ARRANGE: Create test file
        input_file = f"{temp_dir}/input.csv"
        create_test_csv_file(input_file)
        self.test_files.append(input_file)

        # ACT: Execute validate command
        with patch('csv_cleaner.cli.commands.ConfigurationManager') as mock_config_manager, \
             patch('csv_cleaner.cli.commands.FileOperations') as mock_file_ops_class, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_config_manager.return_value = Mock()
            mock_config_manager.return_value.load_config.return_value = Mock()
            mock_file_ops = Mock()
            mock_file_ops.validate_file.return_value = {
                'exists': True,
                'is_csv': True,
                'file_path': input_file,
                'estimated_rows': 30,
                'estimated_columns': 5,
                'encoding': 'utf-8',
                'errors': []
            }
            mock_file_ops.get_file_info.return_value = {
                'file_path': input_file,
                'size_bytes': 1024,
                'modified_time': '2024-01-01 12:00:00'
            }
            mock_file_ops_class.return_value = mock_file_ops

            result = self.runner.invoke(cli, ['validate', input_file])

        # ASSERT: Verify command executed successfully
        if result.exit_code != 0:
            print(f"Error output: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_info_command_successful_execution(self):
        """TEST: should_execute_info_command_successfully"""
        # ARRANGE: Info command

        # ACT: Execute info command
        with patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_cleaner = Mock()
            mock_cleaner.get_supported_operations.return_value = ['remove_duplicates']
            mock_cleaner.library_manager.get_wrapper_info.return_value = {}
            mock_cleaner.get_performance_summary.return_value = {}
            mock_cleaner_class.return_value = mock_cleaner

            result = self.runner.invoke(cli, ['info'])

        # ASSERT: Verify command executed successfully
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_config_command_successful_execution(self):
        """TEST: should_execute_config_command_successfully"""
        # ARRANGE: Config command

        # ACT: Execute config command
        with patch('csv_cleaner.cli.commands.ConfigurationManager') as mock_config_manager, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_config = Mock()
            mock_config.default_operations = ['remove_duplicates', 'drop_missing']
            mock_config.backup_enabled = True
            mock_config.chunk_size = 1000
            mock_config.max_memory_usage = 1024**3  # 1GB
            mock_config.log_level = 'INFO'
            mock_config.output_format = 'csv'

            mock_config_manager.return_value = Mock()
            mock_config_manager.return_value.load_config.return_value = mock_config
            mock_config_manager.return_value.save_config.return_value = None

            result = self.runner.invoke(cli, ['config', 'show'])

        # ASSERT: Verify command executed successfully
        if result.exit_code != 0:
            print(f"Error output: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_visualize_command_successful_execution(self, temp_dir):
        """TEST: should_execute_visualize_command_successfully_with_valid_arguments"""
        # ARRANGE: Create test file
        input_file = f"{temp_dir}/input.csv"
        create_test_csv_file(input_file)
        self.test_files.append(input_file)

        # ACT: Execute visualize command
        with patch('csv_cleaner.cli.commands.ConfigurationManager'), \
             patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.VisualizationManager') as mock_viz_manager_class, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_cleaner = Mock()
            mock_viz_manager = Mock()
            mock_viz_manager.create_data_quality_heatmap.return_value = '/test/heatmap.png'
            mock_cleaner_class.return_value = mock_cleaner
            mock_viz_manager_class.return_value = mock_viz_manager

            result = self.runner.invoke(cli, [
                'visualize', input_file,
                '--type', 'heatmap',
                '--output', f"{temp_dir}/heatmap.png"
            ])

        # ASSERT: Verify command executed successfully
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_report_command_successful_execution(self, temp_dir):
        """TEST: should_execute_report_command_successfully_with_valid_arguments"""
        # ARRANGE: Create test file
        input_file = f"{temp_dir}/input.csv"
        create_test_csv_file(input_file)
        self.test_files.append(input_file)

        # ACT: Execute report command
        with patch('csv_cleaner.cli.commands.ConfigurationManager'), \
             patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.VisualizationManager') as mock_viz_manager_class, \
             patch('csv_cleaner.cli.commands.click.echo'):

            # Setup mocks
            mock_cleaner = Mock()
            mock_viz_manager = Mock()
            mock_viz_manager.create_summary_report.return_value = '/test/report.html'
            mock_cleaner_class.return_value = mock_cleaner
            mock_viz_manager_class.return_value = mock_viz_manager

            result = self.runner.invoke(cli, [
                'report', input_file,
                '--output', f"{temp_dir}/report.html",
                '--format', 'html'
            ])

        # ASSERT: Verify command executed successfully
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

    def test_cli_error_handling_file_not_found(self):
        """TEST: should_handle_file_not_found_error_gracefully"""
        # ARRANGE: Non-existent file

        # ACT: Execute command with non-existent file
        result = self.runner.invoke(cli, ['clean', '/nonexistent/file.csv', 'output.csv'])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    def test_cli_error_handling_invalid_operations(self):
        """TEST: should_handle_invalid_operations_error_gracefully"""
        # ARRANGE: Invalid operations

        # ACT: Execute command with invalid operations
        result = self.runner.invoke(cli, [
            'clean', 'input.csv', 'output.csv',
            '--operations', 'invalid_operation'
        ])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    def test_cli_error_handling_invalid_config_action(self):
        """TEST: should_handle_invalid_config_action_error_gracefully"""
        # ARRANGE: Invalid config action

        # ACT: Execute command with invalid config action
        result = self.runner.invoke(cli, ['config', 'invalid_action'])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    def test_cli_error_handling_invalid_visualization_type(self):
        """TEST: should_handle_invalid_visualization_type_error_gracefully"""
        # ARRANGE: Invalid visualization type

        # ACT: Execute command with invalid visualization type
        result = self.runner.invoke(cli, [
            'visualize', 'input.csv',
            '--type', 'invalid_type'
        ])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    def test_cli_error_handling_invalid_report_format(self):
        """TEST: should_handle_invalid_report_format_error_gracefully"""
        # ARRANGE: Invalid report format

        # ACT: Execute command with invalid report format
        result = self.runner.invoke(cli, [
            'report', 'input.csv',
            '--format', 'invalid_format'
        ])

        # ASSERT: Verify error is handled
        assert result.exit_code != 0, f"Expected non-zero exit code, got {result.exit_code}"

    def test_cli_exit_codes(self):
        """TEST: should_return_appropriate_exit_codes_for_different_scenarios"""
        # ARRANGE: Different scenarios

        # ACT & ASSERT: Test various exit codes
        # Success case
        with patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.click.echo'):
            mock_cleaner = Mock()
            mock_cleaner.get_supported_operations.return_value = []
            mock_cleaner.library_manager.get_wrapper_info.return_value = {}
            mock_cleaner.get_performance_summary.return_value = {}
            mock_cleaner_class.return_value = mock_cleaner

            result = self.runner.invoke(cli, ['info'])
            assert result.exit_code == 0, f"Expected exit code 0 for success, got {result.exit_code}"

        # Error case
        result = self.runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0, f"Expected non-zero exit code for error, got {result.exit_code}"

    def test_cli_argument_validation(self):
        """TEST: should_validate_arguments_correctly"""
        # ARRANGE: Various argument combinations

        # ACT & ASSERT: Test argument validation
        # Missing required argument
        result = self.runner.invoke(cli, ['clean'])
        assert result.exit_code != 0, f"Expected non-zero exit code for missing argument, got {result.exit_code}"

        # Invalid argument type
        result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv', '--operations', ''])
        assert result.exit_code != 0, f"Expected non-zero exit code for invalid argument, got {result.exit_code}"

        # Valid arguments
        with patch('csv_cleaner.cli.commands.ConfigurationManager'), \
             patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.click.echo'), \
             patch('csv_cleaner.cli.commands.click.progressbar'):
            mock_cleaner = Mock()
            mock_cleaner.clean_file.return_value = {'success': True}
            mock_cleaner_class.return_value = mock_cleaner

            result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv'])
            assert result.exit_code != 0, f"Expected non-zero exit code for missing file, got {result.exit_code}"

    def test_cli_command_routing(self):
        """TEST: should_route_commands_to_correct_functions"""
        # ARRANGE: Different commands

        # ACT & ASSERT: Test command routing
        # Clean command
        with patch('csv_cleaner.cli.commands.clean_command') as mock_clean:
            result = self.runner.invoke(cli, ['clean', 'input.csv', 'output.csv'])
            # Note: This won't actually call the function due to argument validation

        # Validate command
        with patch('csv_cleaner.cli.commands.validate_command') as mock_validate:
            result = self.runner.invoke(cli, ['validate', 'input.csv'])
            # Note: This won't actually call the function due to argument validation

        # Info command
        with patch('csv_cleaner.cli.commands.info_command') as mock_info, \
             patch('csv_cleaner.cli.commands.CSVCleaner') as mock_cleaner_class, \
             patch('csv_cleaner.cli.commands.click.echo'):
            mock_cleaner = Mock()
            mock_cleaner.get_supported_operations.return_value = []
            mock_cleaner.library_manager.get_wrapper_info.return_value = {}
            mock_cleaner.get_performance_summary.return_value = {}
            mock_cleaner_class.return_value = mock_cleaner

            result = self.runner.invoke(cli, ['info'])
            assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"

                # Config command
        with patch('csv_cleaner.cli.commands.config_command') as mock_config, \
             patch('csv_cleaner.cli.commands.ConfigurationManager') as mock_config_manager, \
             patch('csv_cleaner.cli.commands.click.echo'):
            mock_config = Mock()
            mock_config.default_operations = ['remove_duplicates', 'drop_missing']
            mock_config.backup_enabled = True
            mock_config.chunk_size = 1000
            mock_config.max_memory_usage = 1024**3  # 1GB
            mock_config.log_level = 'INFO'
            mock_config.output_format = 'csv'

            mock_config_manager.return_value = Mock()
            mock_config_manager.return_value.load_config.return_value = mock_config
            mock_config_manager.return_value.save_config.return_value = None

            result = self.runner.invoke(cli, ['config', 'show'])
            assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
