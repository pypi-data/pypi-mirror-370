"""
TEST SUITE: csv_cleaner.core.visualization_manager
PURPOSE: Test data visualization generation and file management capabilities
SCOPE: VisualizationManager class, backend setup, visualization methods, file operations, error handling
DEPENDENCIES: pandas, matplotlib, seaborn, plotly, file system operations, unittest.mock
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path

from csv_cleaner.core.visualization_manager import VisualizationManager


class TestVisualizationManager:
    """Test cases for VisualizationManager class."""

    def test_initialization_with_default_backend(self, temp_visualization_dir, mock_matplotlib):
        """TEST: should_initialize_successfully_with_default_backend"""
        # ARRANGE: Default backend configuration
        # ACT: Initialize VisualizationManager with default backend
        manager = VisualizationManager(output_dir=str(temp_visualization_dir))

        # ASSERT: Verify manager is initialized
        assert manager is not None, "Expected VisualizationManager to be initialized successfully"
        assert isinstance(manager, VisualizationManager), "Expected VisualizationManager instance"
        assert manager.backend == "matplotlib", f"Expected default backend 'matplotlib', got '{manager.backend}'"
        assert manager.output_dir == Path(temp_visualization_dir), "Expected output_dir to be set correctly"

    def test_initialization_with_custom_backend(self, temp_visualization_dir, mock_seaborn, mock_matplotlib):
        """TEST: should_initialize_successfully_with_custom_backend"""
        # ARRANGE: Custom backend configuration
        custom_backend = "seaborn"
        # ACT: Initialize VisualizationManager with custom backend
        manager = VisualizationManager(output_dir=str(temp_visualization_dir), backend=custom_backend)

        # ASSERT: Verify manager is initialized with custom backend
        assert manager is not None, "Expected VisualizationManager to be initialized successfully"
        assert manager.backend == custom_backend, f"Expected backend '{custom_backend}', got '{manager.backend}'"
        assert manager.output_dir == Path(temp_visualization_dir), "Expected output_dir to be set correctly"

    def test_setup_backend_matplotlib(self, temp_visualization_dir, mock_matplotlib):
        """TEST: should_setup_matplotlib_backend_correctly"""
        # ARRANGE: Mock matplotlib
        with patch('matplotlib.use') as mock_use:
            with patch('matplotlib.pyplot') as mock_plt:
                # ACT: Initialize VisualizationManager with matplotlib backend
                manager = VisualizationManager(output_dir=str(temp_visualization_dir), backend="matplotlib")

                # ASSERT: Verify matplotlib backend is set up correctly
                mock_use.assert_called_once_with('Agg')
                assert manager.backend == "matplotlib", "Expected matplotlib backend"

    def test_setup_backend_seaborn(self, temp_visualization_dir, mock_seaborn, mock_matplotlib):
        """TEST: should_setup_seaborn_backend_correctly"""
        # ARRANGE: Mock seaborn
        with patch('seaborn.set_theme') as mock_set_theme:
            # ACT: Initialize VisualizationManager with seaborn backend
            manager = VisualizationManager(output_dir=str(temp_visualization_dir), backend="seaborn")

            # ASSERT: Verify seaborn backend is set up correctly
            mock_set_theme.assert_called_once_with(style="whitegrid")
            assert manager.backend == "seaborn", "Expected seaborn backend"

    def test_setup_backend_plotly(self, temp_visualization_dir, mock_plotly):
        """TEST: should_setup_plotly_backend_correctly"""
        # ARRANGE: Mock plotly
        with patch('plotly.graph_objects') as mock_go:
            with patch('plotly.express') as mock_px:
                # ACT: Initialize VisualizationManager with plotly backend
                manager = VisualizationManager(output_dir=str(temp_visualization_dir), backend="plotly")

                # ASSERT: Verify plotly backend is set up correctly
                assert manager.backend == "plotly", "Expected plotly backend"

    def test_create_data_quality_heatmap(self, basic_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_create_data_quality_heatmap_successfully"""
        # ARRANGE: VisualizationManager and DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            with patch('seaborn.heatmap') as mock_heatmap:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                save_path = os.path.join(temp_visualization_dir, "test_heatmap.png")

                # ACT: Create data quality heatmap
                result_path = manager.create_data_quality_heatmap(basic_df, save_path=save_path)

                # ASSERT: Verify heatmap is created
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_plt.figure.assert_called_once()
                mock_heatmap.assert_called_once()
                mock_plt.savefig.assert_called_once()
                mock_plt.close.assert_called_once()

    def test_create_before_after_comparison(self, basic_df, temp_visualization_dir, mock_matplotlib):
        """TEST: should_create_before_after_comparison_visualization"""
        # ARRANGE: VisualizationManager and DataFrames
        with patch('matplotlib.pyplot') as mock_plt:
            # Mock subplots to return proper values
            mock_fig = Mock()
            mock_axes = [Mock(), Mock()]  # Two axes for before/after comparison
            mock_plt.subplots.return_value = (mock_fig, mock_axes)

            # Mock pandas plotting to avoid backend issues
            with patch('pandas.Series.plot') as mock_plot:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                before_df = basic_df.copy()
                after_df = basic_df.drop_duplicates()  # Simulate cleaned data
                save_path = os.path.join(temp_visualization_dir, "test_comparison.png")

                # ACT: Create before/after comparison
                result_path = manager.create_before_after_comparison(before_df, after_df, save_path=save_path)

                # ASSERT: Verify comparison visualization is created
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_plt.subplots.assert_called_once()
                mock_plt.savefig.assert_called_once()
                mock_plt.close.assert_called_once()

    def test_create_missing_data_visualization(self, missing_data_df, temp_visualization_dir, mock_matplotlib):
        """TEST: should_create_missing_data_visualization"""
        # ARRANGE: VisualizationManager and DataFrame with missing data
        with patch('matplotlib.pyplot') as mock_plt:
            # Mock subplots to return proper values
            mock_fig = Mock()
            mock_axes = [Mock(), Mock()]  # Two axes for missing data visualization
            mock_plt.subplots.return_value = (mock_fig, mock_axes)

            # Mock pandas plotting to avoid backend issues
            with patch('pandas.Series.plot') as mock_plot:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                save_path = os.path.join(temp_visualization_dir, "test_missing.png")

                # ACT: Create missing data visualization
                result_path = manager.create_missing_data_visualization(missing_data_df, save_path=save_path)

                # ASSERT: Verify missing data visualization is created
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_plt.subplots.assert_called_once()
                mock_plt.savefig.assert_called_once()
                mock_plt.close.assert_called_once()

    def test_create_correlation_matrix(self, basic_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_create_correlation_matrix_visualization"""
        # ARRANGE: VisualizationManager and DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            with patch('seaborn.heatmap') as mock_heatmap:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                save_path = os.path.join(temp_visualization_dir, "test_correlation.png")

                # ACT: Create correlation matrix
                result_path = manager.create_correlation_matrix(basic_df, save_path=save_path)

                # ASSERT: Verify correlation matrix is created
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_plt.figure.assert_called_once()
                mock_heatmap.assert_called_once()
                mock_plt.savefig.assert_called_once()
                mock_plt.close.assert_called_once()

    def test_create_distribution_plots(self, basic_df, temp_visualization_dir, mock_matplotlib):
        """TEST: should_create_distribution_plots"""
        # ARRANGE: VisualizationManager and DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            # Mock subplots to return proper values for 2 columns
            mock_fig = Mock()
            mock_axes = [Mock(), Mock()]  # 1 row, 2 columns (flattened)
            mock_plt.subplots.return_value = (mock_fig, mock_axes)

            # Mock pandas plotting to avoid backend issues
            with patch('pandas.Series.hist') as mock_hist:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                save_path = os.path.join(temp_visualization_dir, "test_distribution.png")

                # ACT: Create distribution plots
                result_path = manager.create_distribution_plots(basic_df, columns=['age', 'salary'], save_path=save_path)

                # ASSERT: Verify distribution plots are created
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_plt.subplots.assert_called_once()
                mock_plt.savefig.assert_called_once()
                mock_plt.close.assert_called_once()

    def test_create_outlier_visualization(self, basic_df, temp_visualization_dir, mock_matplotlib):
        """TEST: should_create_outlier_visualization"""
        # ARRANGE: VisualizationManager and DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            # Mock subplots to return proper values for 2 columns
            mock_fig = Mock()
            mock_axes = [Mock(), Mock()]  # 1 row, 2 columns (flattened)
            mock_plt.subplots.return_value = (mock_fig, mock_axes)

            # Mock pandas plotting to avoid backend issues
            with patch('pandas.Series.plot') as mock_plot:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                save_path = os.path.join(temp_visualization_dir, "test_outliers.png")

                # ACT: Create outlier visualization
                result_path = manager.create_outlier_visualization(basic_df, columns=['age', 'salary'], save_path=save_path)

                # ASSERT: Verify outlier visualization is created
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_plt.subplots.assert_called_once()
                mock_plt.savefig.assert_called_once()
                mock_plt.close.assert_called_once()

    def test_save_visualization_to_file(self, temp_visualization_dir, mock_matplotlib):
        """TEST: should_save_visualization_to_file_successfully"""
        # ARRANGE: VisualizationManager and mock figure
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            save_path = os.path.join(temp_visualization_dir, "test_save.png")

            # ACT: Save visualization to file
            result_path = manager.save_visualization_to_file(mock_plt, save_path)

            # ASSERT: Verify file is saved
            assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
            assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
            mock_plt.savefig.assert_called_once_with(save_path, dpi=300, bbox_inches='tight')

    def test_error_handling_invalid_data(self, temp_visualization_dir, mock_matplotlib):
        """TEST: should_handle_invalid_data_gracefully"""
        # ARRANGE: VisualizationManager with invalid data
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            invalid_df = pd.DataFrame()  # Empty DataFrame
            save_path = os.path.join(temp_visualization_dir, "test_invalid.png")

            # ACT & ASSERT: Verify error handling for invalid data
            with pytest.raises(ValueError, match="DataFrame is empty"):
                manager.create_data_quality_heatmap(invalid_df, save_path=save_path)

    def test_error_handling_file_system_errors(self, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_handle_file_system_errors_gracefully"""
        # ARRANGE: VisualizationManager with invalid save path
        with patch('matplotlib.pyplot') as mock_plt:
            # Mock savefig to raise OSError
            mock_plt.savefig.side_effect = OSError("Permission denied")

            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            basic_df = pd.DataFrame({'col1': [1, 2, 3]})
            save_path = os.path.join(temp_visualization_dir, "test.png")

            # ACT & ASSERT: Verify error handling for file system errors
            with pytest.raises(OSError):
                manager.create_data_quality_heatmap(basic_df, save_path=save_path)

    def test_performance_large_datasets(self, large_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_handle_large_datasets_efficiently"""
        # ARRANGE: VisualizationManager and large DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            save_path = os.path.join(temp_visualization_dir, "test_large.png")

            # ACT: Create visualization with large dataset
            result_path = manager.create_data_quality_heatmap(large_df, save_path=save_path)

            # ASSERT: Verify visualization is created for large dataset
            assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
            assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
            mock_plt.figure.assert_called_once()
            mock_seaborn.assert_called_once()
            mock_plt.savefig.assert_called_once()
            mock_plt.close.assert_called_once()

    def test_calculate_quality_metrics(self, basic_df, temp_visualization_dir, mock_matplotlib):
        """TEST: should_calculate_quality_metrics_correctly"""
        # ARRANGE: VisualizationManager
        manager = VisualizationManager(output_dir=str(temp_visualization_dir))

        # ACT: Calculate quality metrics
        quality_metrics = manager._calculate_quality_metrics(basic_df)

        # ASSERT: Verify quality metrics are calculated
        assert isinstance(quality_metrics, pd.Series), f"Expected Series, got {type(quality_metrics)}"
        assert len(quality_metrics) > 0, "Expected non-empty quality metrics"
        # Check that metrics are between 0 and 1
        for value in quality_metrics.values:
            assert 0 <= value <= 1, f"Expected quality metric between 0 and 1, got {value}"

    def test_create_visualization_with_custom_parameters(self, basic_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_create_visualization_with_custom_parameters"""
        # ARRANGE: VisualizationManager with custom parameters
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            save_path = os.path.join(temp_visualization_dir, "test_custom.png")
            custom_params = {'figsize': (12, 8), 'cmap': 'viridis'}

            # ACT: Create visualization with custom parameters
            result_path = manager.create_data_quality_heatmap(basic_df, save_path=save_path, **custom_params)

            # ASSERT: Verify visualization is created with custom parameters
            assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
            assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
            mock_plt.figure.assert_called_once()
            mock_seaborn.assert_called_once()
            mock_plt.savefig.assert_called_once()

    def test_multiple_visualizations_sequence(self, basic_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_create_multiple_visualizations_in_sequence"""
        # ARRANGE: VisualizationManager
        with patch('matplotlib.pyplot') as mock_plt:
            # Mock subplots to return proper values
            mock_fig = Mock()
            mock_axes = [Mock(), Mock()]  # 1 row, 2 columns (flattened)
            mock_plt.subplots.return_value = (mock_fig, mock_axes)

            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            visualizations = [
                ('heatmap', 'test_heatmap.png'),
                ('correlation', 'test_correlation.png'),
                ('distribution', 'test_distribution.png')
            ]

            # ACT: Create multiple visualizations
            results = []
            for viz_type, filename in visualizations:
                save_path = os.path.join(temp_visualization_dir, filename)
                if viz_type == 'heatmap':
                    result = manager.create_data_quality_heatmap(basic_df, save_path=save_path)
                elif viz_type == 'correlation':
                    result = manager.create_correlation_matrix(basic_df, save_path=save_path)
                elif viz_type == 'distribution':
                    # Mock pandas plotting for distribution plots
                    with patch('pandas.Series.hist') as mock_hist:
                        result = manager.create_distribution_plots(basic_df, save_path=save_path)
                results.append(result)

            # ASSERT: Verify all visualizations are created
            assert len(results) == len(visualizations), f"Expected {len(visualizations)} results, got {len(results)}"
            for result in results:
                assert isinstance(result, str), "Expected string path from each visualization"

    def test_backend_switching(self, temp_visualization_dir, mock_matplotlib, mock_seaborn, mock_plotly):
        """TEST: should_switch_between_different_backends"""
        # ARRANGE: Different backend configurations
        backends = ['matplotlib', 'seaborn', 'plotly']

        for backend in backends:
            # ACT: Initialize VisualizationManager with different backend
            manager = VisualizationManager(output_dir=str(temp_visualization_dir), backend=backend)

            # ASSERT: Verify backend is set correctly
            assert manager.backend == backend, f"Expected backend '{backend}', got '{manager.backend}'"

    def test_output_directory_creation(self, temp_visualization_dir, mock_matplotlib):
        """TEST: should_create_output_directory_if_not_exists"""
        # ARRANGE: Non-existent directory
        non_existent_dir = os.path.join(temp_visualization_dir, "new_dir")

        # ACT: Initialize VisualizationManager with non-existent directory
        manager = VisualizationManager(output_dir=non_existent_dir)

        # ASSERT: Verify directory is created
        assert manager.output_dir.exists(), "Expected output directory to be created"

    def test_visualization_with_empty_dataframe(self, edge_case_dfs, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_handle_empty_dataframe_gracefully"""
        # ARRANGE: VisualizationManager with empty DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            empty_df = edge_case_dfs['empty']
            save_path = os.path.join(temp_visualization_dir, "test_empty.png")

            # ACT & ASSERT: Verify error handling for empty DataFrame
            with pytest.raises(ValueError, match="DataFrame is empty"):
                manager.create_data_quality_heatmap(empty_df, save_path=save_path)

    def test_visualization_with_single_column(self, edge_case_dfs, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_handle_single_column_dataframe"""
        # ARRANGE: VisualizationManager with single column DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            single_column_df = edge_case_dfs['single_column']
            save_path = os.path.join(temp_visualization_dir, "test_single.png")

            # ACT: Create visualization with single column
            result_path = manager.create_data_quality_heatmap(single_column_df, save_path=save_path)

            # ASSERT: Verify visualization is created for single column
            assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
            assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"

    def test_visualization_with_mixed_data_types(self, complex_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_handle_mixed_data_types_correctly"""
        # ARRANGE: VisualizationManager with mixed data types DataFrame
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))
            save_path = os.path.join(temp_visualization_dir, "test_mixed.png")

            # ACT: Create visualization with mixed data types
            result_path = manager.create_data_quality_heatmap(complex_df, save_path=save_path)

            # ASSERT: Verify visualization is created for mixed data types
            assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
            assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"

    def test_visualization_file_naming(self, basic_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_generate_appropriate_file_names"""
        # ARRANGE: VisualizationManager
        with patch('matplotlib.pyplot') as mock_plt:
            manager = VisualizationManager(output_dir=str(temp_visualization_dir))

            # ACT: Create visualization without specifying save_path
            result_path = manager.create_data_quality_heatmap(basic_df)

            # ASSERT: Verify appropriate file name is generated
            assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
            assert result_path.endswith('.png'), "Expected file to have .png extension"
            assert 'data_quality_heatmap' in result_path, "Expected descriptive filename"

    def test_visualization_with_custom_colormap(self, basic_df, temp_visualization_dir, mock_matplotlib, mock_seaborn):
        """TEST: should_use_custom_colormap_for_visualizations"""
        # ARRANGE: VisualizationManager with custom colormap
        with patch('matplotlib.pyplot') as mock_plt:
            with patch('seaborn.heatmap') as mock_heatmap:
                manager = VisualizationManager(output_dir=str(temp_visualization_dir))
                save_path = os.path.join(temp_visualization_dir, "test_colormap.png")
                custom_colormap = 'viridis'

                # ACT: Create visualization with custom colormap
                result_path = manager.create_data_quality_heatmap(basic_df, save_path=save_path, cmap=custom_colormap)

                # ASSERT: Verify visualization is created with custom colormap
                assert isinstance(result_path, str), f"Expected string path, got {type(result_path)}"
                assert result_path == save_path, f"Expected path '{save_path}', got '{result_path}'"
                mock_heatmap.assert_called_once()
                # Check that colormap parameter is passed
                call_args = mock_heatmap.call_args
                assert 'cmap' in call_args[1], "Expected cmap parameter to be passed"
