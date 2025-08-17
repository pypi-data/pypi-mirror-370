"""
Test fixtures for wrapper modules.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os


@pytest.fixture
def basic_df():
    """Basic DataFrame with simple data types."""
    return pd.DataFrame({
        'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
        'age': [25, 30, 35, 28, 42],
        'city': ['NYC', 'LA', 'Chicago', 'Boston', 'Seattle'],
        'salary': [50000, 60000, 70000, 55000, 80000],
        'active': [True, False, True, True, False]
    })


@pytest.fixture
def missing_data_df():
    """DataFrame with various missing value patterns."""
    return pd.DataFrame({
        'name': ['John', None, 'Bob', 'Alice', None],
        'age': [25, 30, None, 28, 42],
        'city': ['NYC', 'LA', 'Chicago', None, 'Seattle'],
        'salary': [50000, None, 70000, 55000, None],
        'active': [True, False, None, True, False],
        'date': [datetime.now(), None, datetime.now() - timedelta(days=1), None, datetime.now() - timedelta(days=2)]
    })


@pytest.fixture
def large_df():
    """Large DataFrame for performance testing."""
    np.random.seed(42)
    n_rows = 1000
    return pd.DataFrame({
        'id': range(n_rows),
        'numeric_col': np.random.randn(n_rows),
        'categorical_col': np.random.choice(['A', 'B', 'C', 'D'], n_rows),
        'text_col': [f'text_{i}' for i in range(n_rows)],
        'date_col': [datetime.now() - timedelta(days=i) for i in range(n_rows)],
        'boolean_col': np.random.choice([True, False], n_rows)
    })


@pytest.fixture
def complex_df():
    """DataFrame with complex data types and edge cases."""
    return pd.DataFrame({
        'mixed_types': ['text', 123, 45.67, True, None],
        'special_chars': ['test@email.com', 'phone: 123-456-7890', 'price: $99.99', 'percent: 25%', 'normal'],
        'dates': ['2023-01-01', '2023/02/15', '03-15-2023', '2023.04.20', None],
        'numbers_as_strings': ['1', '2.5', '1000', '1,000', '1.5e3'],
        'whitespace': ['  leading', 'trailing  ', '  both  ', '\t\ntab\nnewline', 'normal']
    })


@pytest.fixture
def edge_case_dfs():
    """Collection of edge case DataFrames."""
    return {
        'empty': pd.DataFrame(),
        'single_row': pd.DataFrame({'col1': [1], 'col2': ['a']}),
        'single_column': pd.DataFrame({'col1': [1, 2, 3, 4, 5]}),
        'all_nulls': pd.DataFrame({
            'col1': [None, None, None],
            'col2': [None, None, None]
        }),
        'duplicates': pd.DataFrame({
            'col1': [1, 1, 2, 2, 3],
            'col2': ['a', 'a', 'b', 'b', 'c']
        }),
        'mixed_nulls': pd.DataFrame({
            'col1': [1, None, 3, None, 5],
            'col2': ['a', 'b', None, 'd', None]
        })
    }


@pytest.fixture
def text_data_df():
    """DataFrame with text data for cleaning operations."""
    return pd.DataFrame({
        'dirty_text': [
            '  HELLO world  ',
            'test@email.com',
            'phone: 123-456-7890',
            'price: $99.99',
            'UPPERCASE TEXT'
        ],
        'names': [
            'john doe',
            'JANE SMITH',
            'Bob Wilson',
            'alice brown',
            'CHARLIE DAVIS'
        ],
        'addresses': [
            '123 Main St, New York, NY 10001',
            '456 Oak Ave, Los Angeles, CA 90210',
            '789 Pine Rd, Chicago, IL 60601',
            '321 Elm St, Boston, MA 02101',
            '654 Maple Dr, Seattle, WA 98101'
        ]
    })


@pytest.fixture
def date_data_df():
    """DataFrame with various date formats for testing date operations."""
    return pd.DataFrame({
        'iso_dates': ['2023-01-01', '2023-02-15', '2023-03-20', '2023-04-25'],
        'slash_dates': ['01/01/2023', '02/15/2023', '03/20/2023', '04/25/2023'],
        'dot_dates': ['01.01.2023', '15.02.2023', '20.03.2023', '25.04.2023'],
        'mixed_dates': ['2023-01-01', '02/15/2023', '20.03.2023', '2023-04-25'],
        'invalid_dates': ['not-a-date', '2023-13-01', '2023-02-30', 'invalid']
    })


@pytest.fixture
def mock_missingno():
    """Mock missingno library for testing."""
    # Create a mock missingno module
    mock_missingno_module = MagicMock()
    mock_missingno_module.matrix.return_value = None
    mock_missingno_module.bar.return_value = None
    mock_missingno_module.heatmap.return_value = None
    mock_missingno_module.dendrogram.return_value = None
    mock_missingno_module.summary.return_value = None

    # Create a mock matplotlib module
    mock_matplotlib_module = MagicMock()
    mock_matplotlib_module.use.return_value = None

    # Create a mock matplotlib.pyplot module
    mock_plt_module = MagicMock()
    mock_plt_module.savefig.return_value = None
    mock_plt_module.close.return_value = None

    # Patch sys.modules to simulate both missingno and matplotlib being available
    with patch.dict('sys.modules', {
        'missingno': mock_missingno_module,
        'matplotlib': mock_matplotlib_module,
        'matplotlib.pyplot': mock_plt_module
    }):
        # Also patch the MISSINGNO_AVAILABLE flag and the msno variable
        with patch('csv_cleaner.wrappers.missingno_wrapper.MISSINGNO_AVAILABLE', True):
            with patch('csv_cleaner.wrappers.missingno_wrapper.msno', mock_missingno_module, create=True):
                yield mock_missingno_module


@pytest.fixture
def mock_pyjanitor():
    """Mock pyjanitor library for testing."""
    # Create a mock pyjanitor module
    mock_pj_module = MagicMock()
    mock_pj_module.clean_names.return_value = MagicMock()
    mock_pj_module.remove_empty.return_value = MagicMock()
    mock_pj_module.fill_empty.return_value = MagicMock()
    mock_pj_module.remove_duplicates.return_value = MagicMock()
    mock_pj_module.handle_missing.return_value = MagicMock()
    mock_pj_module.remove_constant_columns.return_value = MagicMock()
    mock_pj_module.remove_columns_with_nulls.return_value = MagicMock()
    mock_pj_module.coalesce_columns.return_value = MagicMock()

    # Patch sys.modules to simulate pyjanitor being available
    with patch.dict('sys.modules', {'pyjanitor': mock_pj_module}):
        # Also patch the PYJANITOR_AVAILABLE flag and the pj variable
        with patch('csv_cleaner.wrappers.pyjanitor_wrapper.PYJANITOR_AVAILABLE', True):
            with patch('csv_cleaner.wrappers.pyjanitor_wrapper.pj', mock_pj_module, create=True):
                yield mock_pj_module


@pytest.fixture
def mock_feature_engine():
    """Mock feature-engine library for testing."""
    # Create a mock feature-engine module
    mock_fe_module = MagicMock()
    mock_fe_module.MeanMedianImputer.return_value = Mock()
    mock_fe_module.CategoricalImputer.return_value = Mock()
    mock_fe_module.RandomSampleImputer.return_value = Mock()
    mock_fe_module.EndTailImputer.return_value = Mock()
    mock_fe_module.AddMissingIndicator.return_value = Mock()
    mock_fe_module.OneHotEncoder.return_value = Mock()
    mock_fe_module.OrdinalEncoder.return_value = Mock()
    mock_fe_module.MeanEncoder.return_value = Mock()
    mock_fe_module.RareLabelEncoder.return_value = Mock()
    mock_fe_module.OutlierTrimmer.return_value = Mock()
    mock_fe_module.Winsorizer.return_value = Mock()
    mock_fe_module.DropConstantFeatures.return_value = Mock()
    mock_fe_module.DropCorrelatedFeatures.return_value = Mock()
    mock_fe_module.DropDuplicateFeatures.return_value = Mock()
    mock_fe_module.LogTransformer.return_value = Mock()
    mock_fe_module.PowerTransformer.return_value = Mock()

    # Patch sys.modules to simulate feature-engine being available
    with patch.dict('sys.modules', {'feature_engine': mock_fe_module}):
        # Also patch the FEATURE_ENGINE_AVAILABLE flag and the specific classes
        with patch('csv_cleaner.wrappers.feature_engine_wrapper.FEATURE_ENGINE_AVAILABLE', True):
            with patch('csv_cleaner.wrappers.feature_engine_wrapper.MeanMedianImputer', mock_fe_module.MeanMedianImputer, create=True):
                with patch('csv_cleaner.wrappers.feature_engine_wrapper.CategoricalImputer', mock_fe_module.CategoricalImputer, create=True):
                    with patch('csv_cleaner.wrappers.feature_engine_wrapper.RandomSampleImputer', mock_fe_module.RandomSampleImputer, create=True):
                        with patch('csv_cleaner.wrappers.feature_engine_wrapper.EndTailImputer', mock_fe_module.EndTailImputer, create=True):
                            with patch('csv_cleaner.wrappers.feature_engine_wrapper.AddMissingIndicator', mock_fe_module.AddMissingIndicator, create=True):
                                with patch('csv_cleaner.wrappers.feature_engine_wrapper.OneHotEncoder', mock_fe_module.OneHotEncoder, create=True):
                                    with patch('csv_cleaner.wrappers.feature_engine_wrapper.OrdinalEncoder', mock_fe_module.OrdinalEncoder, create=True):
                                        with patch('csv_cleaner.wrappers.feature_engine_wrapper.MeanEncoder', mock_fe_module.MeanEncoder, create=True):
                                            with patch('csv_cleaner.wrappers.feature_engine_wrapper.RareLabelEncoder', mock_fe_module.RareLabelEncoder, create=True):
                                                with patch('csv_cleaner.wrappers.feature_engine_wrapper.OutlierTrimmer', mock_fe_module.OutlierTrimmer, create=True):
                                                    with patch('csv_cleaner.wrappers.feature_engine_wrapper.Winsorizer', mock_fe_module.Winsorizer, create=True):
                                                        with patch('csv_cleaner.wrappers.feature_engine_wrapper.DropConstantFeatures', mock_fe_module.DropConstantFeatures, create=True):
                                                            with patch('csv_cleaner.wrappers.feature_engine_wrapper.DropCorrelatedFeatures', mock_fe_module.DropCorrelatedFeatures, create=True):
                                                                with patch('csv_cleaner.wrappers.feature_engine_wrapper.DropDuplicateFeatures', mock_fe_module.DropDuplicateFeatures, create=True):
                                                                    with patch('csv_cleaner.wrappers.feature_engine_wrapper.LogTransformer', mock_fe_module.LogTransformer, create=True):
                                                                        with patch('csv_cleaner.wrappers.feature_engine_wrapper.PowerTransformer', mock_fe_module.PowerTransformer, create=True):
                                                                            yield mock_fe_module


@pytest.fixture
def mock_matplotlib():
    """Mock matplotlib for testing."""
    # Create a mock matplotlib module
    mock_matplotlib_module = MagicMock()
    mock_matplotlib_module.use.return_value = None

    # Create a mock pyplot module
    mock_plt = MagicMock()
    mock_plt.figure.return_value = Mock()

    # Create proper mock for subplots that returns (fig, axes)
    mock_fig = Mock()
    mock_axes = Mock()
    mock_plt.subplots.return_value = (mock_fig, mock_axes)

    mock_plt.savefig.return_value = None
    mock_plt.close.return_value = None
    mock_plt.style.use.return_value = None
    mock_plt.rcParams = {}

    # Create a proper mock for pandas plotting backend
    mock_plotting_backend = MagicMock()
    mock_plotting_backend.__name__ = 'matplotlib'

    # Patch sys.modules to simulate matplotlib being available
    with patch.dict('sys.modules', {
        'matplotlib': mock_matplotlib_module,
        'matplotlib.pyplot': mock_plt,
        'matplotlib.use': mock_matplotlib_module.use,
        'pandas.plotting._matplotlib': mock_plotting_backend
    }):
        yield mock_plt


@pytest.fixture
def mock_seaborn():
    """Mock seaborn for testing."""
    # Create a mock seaborn module
    mock_seaborn_module = MagicMock()
    mock_heatmap = MagicMock()
    mock_heatmap.return_value = Mock()
    mock_seaborn_module.heatmap = mock_heatmap
    mock_seaborn_module.set_theme.return_value = None

    # Patch sys.modules to simulate seaborn being available
    with patch.dict('sys.modules', {
        'seaborn': mock_seaborn_module,
        'seaborn.heatmap': mock_heatmap
    }):
        yield mock_heatmap


@pytest.fixture
def mock_plotly():
    """Mock plotly for testing."""
    # Create a mock plotly module
    mock_plotly_module = MagicMock()
    mock_go = MagicMock()
    mock_go.Figure.return_value = Mock()
    mock_plotly_module.graph_objects = mock_go

    # Create mock express module
    mock_px = MagicMock()
    mock_plotly_module.express = mock_px

    # Patch sys.modules to simulate plotly being available
    with patch.dict('sys.modules', {
        'plotly': mock_plotly_module,
        'plotly.graph_objects': mock_go,
        'plotly.express': mock_px
    }):
        yield mock_go


@pytest.fixture
def temp_visualization_dir():
    """Temporary directory for visualization tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    from csv_cleaner.core.config import Config
    return Config(
        default_encoding='utf-8',
        max_memory_usage=1024 * 1024 * 1024,
        chunk_size=10000,
        parallel_processing=True,
        max_workers=4,
        ai_enabled=False,
        default_llm_provider='openai',
        ai_api_keys={},
        ai_cost_limit=10.0,
        backup_enabled=True,
        backup_suffix='.backup',
        output_format='csv',
        log_level='INFO',
        log_file=None,
        default_operations=['remove_duplicates', 'clean_names', 'handle_missing']
    )
