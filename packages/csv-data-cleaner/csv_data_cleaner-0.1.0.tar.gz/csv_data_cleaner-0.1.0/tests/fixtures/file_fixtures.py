"""
Test fixtures for file operations testing.
"""

import tempfile
import os
import gzip
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional


def create_sample_csv_file(file_path: str, encoding: str = 'utf-8',
                          data: Optional[Dict[str, List]] = None) -> None:
    """Create a sample CSV file with specified encoding.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
        data: Optional custom data to use instead of default.
    """
    if data is None:
        data = {
            'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
            'Age': [25, 30, 35, 28],
            'City': ['New York', 'Los Angeles', 'Chicago', 'Boston'],
            'Salary': [50000, 60000, 70000, 55000],
            'Department': ['Engineering', 'Marketing', 'Sales', 'HR']
        }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_csv_with_special_chars(file_path: str, encoding: str = 'utf-8') -> None:
    """Create a CSV file with special characters and accents.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
    """
    data = {
        'Name': ['José García', 'François Dubois', 'Müller Schmidt', '李小明'],
        'Country': ['España', 'France', 'Deutschland', '中国'],
        'Currency': ['€', '€', '€', '¥'],
        'Special': ['áéíóú', 'àèìòù', 'äëïöü', '汉字']
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_csv_with_missing_values(file_path: str, encoding: str = 'utf-8') -> None:
    """Create a CSV file with missing values.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
    """
    data = {
        'Name': ['John', 'Jane', None, 'Bob', 'Alice'],
        'Age': [25, None, 35, 28, None],
        'City': ['NYC', 'LA', 'Chicago', None, 'Boston'],
        'Salary': [50000, 60000, None, 70000, 55000],
        'Department': [None, 'Marketing', 'Sales', 'HR', None]
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_csv_with_duplicates(file_path: str, encoding: str = 'utf-8') -> None:
    """Create a CSV file with duplicate rows.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
    """
    data = {
        'Name': ['John', 'Jane', 'John', 'Bob', 'Jane', 'Alice'],
        'Age': [25, 30, 25, 35, 30, 28],
        'City': ['NYC', 'LA', 'NYC', 'Chicago', 'LA', 'Boston'],
        'Salary': [50000, 60000, 50000, 70000, 60000, 55000]
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_large_csv_file(file_path: str, rows: int = 10000, encoding: str = 'utf-8') -> None:
    """Create a large CSV file for performance testing.

    Args:
        file_path: Path to create the CSV file.
        rows: Number of rows to generate.
        encoding: Encoding to use for the file.
    """
    np.random.seed(42)  # For reproducible data

    data = {
        'ID': range(1, rows + 1),
        'Name': [f'User_{i}' for i in range(1, rows + 1)],
        'Age': np.random.randint(18, 80, rows),
        'Salary': np.random.randint(30000, 150000, rows),
        'Department': np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR', 'Finance'], rows),
        'City': np.random.choice(['NYC', 'LA', 'Chicago', 'Boston', 'Seattle'], rows),
        'Score': np.random.uniform(0, 100, rows),
        'Active': np.random.choice([True, False], rows)
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_wide_csv_file(file_path: str, columns: int = 50, encoding: str = 'utf-8') -> None:
    """Create a wide CSV file with many columns.

    Args:
        file_path: Path to create the CSV file.
        columns: Number of columns to generate.
        encoding: Encoding to use for the file.
    """
    np.random.seed(42)

    data = {}
    for i in range(columns):
        col_name = f'Column_{i:02d}'
        if i % 4 == 0:
            data[col_name] = np.random.randint(1, 100, 100)
        elif i % 4 == 1:
            data[col_name] = np.random.uniform(0, 1, 100)
        elif i % 4 == 2:
            data[col_name] = [f'Text_{i}_{j}' for j in range(100)]
        else:
            data[col_name] = np.random.choice([True, False], 100)

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_empty_csv_file(file_path: str, encoding: str = 'utf-8') -> None:
    """Create an empty CSV file with headers only.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
    """
    data = {
        'Name': [],
        'Age': [],
        'City': [],
        'Salary': []
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_csv_with_different_line_endings(file_path: str, line_ending: str = '\n',
                                         encoding: str = 'utf-8') -> None:
    """Create a CSV file with specific line endings.

    Args:
        file_path: Path to create the CSV file.
        line_ending: Line ending to use ('\n', '\r\n', '\r').
        encoding: Encoding to use for the file.
    """
    data = {
        'Name': ['John', 'Jane', 'Bob', 'Alice'],
        'Age': [25, 30, 35, 28],
        'City': ['NYC', 'LA', 'Chicago', 'Boston']
    }

    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False, encoding=encoding)

    # Replace line endings
    if line_ending != '\n':
        csv_content = csv_content.replace('\n', line_ending)

    with open(file_path, 'w', encoding=encoding) as f:
        f.write(csv_content)


def create_corrupted_csv_file(file_path: str, corruption_type: str = 'truncated') -> None:
    """Create a corrupted CSV file for error testing.

    Args:
        file_path: Path to create the CSV file.
        corruption_type: Type of corruption ('truncated', 'malformed', 'binary').
    """
    if corruption_type == 'truncated':
        # Create a file that's cut off in the middle
        data = {
            'Name': ['John', 'Jane', 'Bob'],
            'Age': [25, 30, 35],
            'City': ['NYC', 'LA', 'Chicago']
        }
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False)
        # Truncate the content
        truncated_content = csv_content[:len(csv_content) // 2]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(truncated_content)

    elif corruption_type == 'malformed':
        # Create a file with malformed CSV structure
        malformed_content = """Name,Age,City
John,25,NYC
Jane,30,LA
Bob,35,"Chicago,IL"
Alice,28,Boston
Invalid,row,with,too,many,columns
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(malformed_content)

    elif corruption_type == 'binary':
        # Create a file with binary content
        binary_content = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
        with open(file_path, 'wb') as f:
            f.write(binary_content)


def create_compressed_csv_file(file_path: str, compression_type: str = 'gzip',
                              encoding: str = 'utf-8') -> None:
    """Create a compressed CSV file.

    Args:
        file_path: Path to create the compressed file.
        compression_type: Type of compression ('gzip', 'zip').
        encoding: Encoding to use for the CSV content.
    """
    data = {
        'Name': ['John', 'Jane', 'Bob', 'Alice'],
        'Age': [25, 30, 35, 28],
        'City': ['NYC', 'LA', 'Chicago', 'Boston'],
        'Salary': [50000, 60000, 70000, 55000]
    }

    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False, encoding=encoding)

    if compression_type == 'gzip':
        with gzip.open(file_path, 'wt', encoding=encoding) as f:
            f.write(csv_content)

    elif compression_type == 'zip':
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Create a temporary CSV file
            temp_csv = file_path.replace('.zip', '_temp.csv')
            with open(temp_csv, 'w', encoding=encoding) as f:
                f.write(csv_content)

            # Add to zip and clean up
            zf.write(temp_csv, 'data.csv')
            os.remove(temp_csv)


def create_csv_with_mixed_data_types(file_path: str, encoding: str = 'utf-8') -> None:
    """Create a CSV file with mixed data types.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
    """
    data = {
        'String': ['text1', 'text2', 'text3', 'text4'],
        'Integer': [1, 2, 3, 4],
        'Float': [1.1, 2.2, 3.3, 4.4],
        'Boolean': [True, False, True, False],
        'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
        'DateTime': ['2023-01-01 10:00:00', '2023-01-02 11:00:00',
                    '2023-01-03 12:00:00', '2023-01-04 13:00:00'],
        'Null': [None, None, None, None],
        'Mixed': ['text', 123, 45.67, True]
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding)


def create_csv_with_quotes_and_commas(file_path: str, encoding: str = 'utf-8') -> None:
    """Create a CSV file with quoted fields and embedded commas.

    Args:
        file_path: Path to create the CSV file.
        encoding: Encoding to use for the file.
    """
    data = {
        'Name': ['John "Johnny" Doe', 'Jane Smith', 'Bob, Jr.', 'Alice O\'Connor'],
        'Address': ['123 Main St, Apt 4B', '456 Oak Ave, Suite 100',
                   '789 Pine Rd, Unit 2', '321 Elm St, Floor 3'],
        'Description': ['Likes "pizza" and movies', 'Enjoys reading, writing, and hiking',
                       'Works at "ABC, Inc."', 'Studies "Math, Science, and Art"'],
        'Tags': ['tag1,tag2', 'tag3', 'tag4,tag5,tag6', 'tag7']
    }

    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding=encoding, quoting=1)  # QUOTE_ALL


def get_test_file_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get various test file scenarios.

    Returns:
        Dictionary of test scenario names and their configuration.
    """
    return {
        'small_utf8': {
            'encoding': 'utf-8',
            'rows': 10,
            'description': 'Small file with UTF-8 encoding'
        },
        'large_latin1': {
            'encoding': 'latin-1',
            'rows': 1000,
            'description': 'Large file with Latin-1 encoding'
        },
        'wide_utf8': {
            'encoding': 'utf-8',
            'columns': 20,
            'description': 'Wide file with many columns'
        },
        'missing_values': {
            'encoding': 'utf-8',
            'has_missing': True,
            'description': 'File with missing values'
        },
        'special_chars': {
            'encoding': 'utf-8',
            'has_special_chars': True,
            'description': 'File with special characters and accents'
        },
        'duplicates': {
            'encoding': 'utf-8',
            'has_duplicates': True,
            'description': 'File with duplicate rows'
        },
        'mixed_types': {
            'encoding': 'utf-8',
            'has_mixed_types': True,
            'description': 'File with mixed data types'
        },
        'quoted_fields': {
            'encoding': 'utf-8',
            'has_quotes': True,
            'description': 'File with quoted fields and embedded commas'
        }
    }


def cleanup_test_files(file_paths: List[str]) -> None:
    """Clean up test files.

    Args:
        file_paths: List of file paths to remove.
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # File might already be deleted


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get information about a file.

    Args:
        file_path: Path to the file.

    Returns:
        Dictionary with file information.
    """
    if not os.path.exists(file_path):
        return {'exists': False}

    stat = os.stat(file_path)
    return {
        'exists': True,
        'size_bytes': stat.st_size,
        'size_mb': stat.st_size / (1024 * 1024),
        'created_time': stat.st_ctime,
        'modified_time': stat.st_mtime,
        'is_file': os.path.isfile(file_path),
        'is_readable': os.access(file_path, os.R_OK),
        'is_writable': os.access(file_path, os.W_OK)
    }
