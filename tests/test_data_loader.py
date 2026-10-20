"""
Unit tests for the data_loader module.
"""
import os
import tempfile
import pytest
import pandas as pd
from src.data_loader import load_data


def test_load_data_csv():
    """Test loading a CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('col1,col2\n1,2\n3,4')
        temp_path = f.name

    try:
        df = load_data(temp_path)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 2)
        assert list(df.columns) == ['col1', 'col2']
    finally:
        os.unlink(temp_path)


def test_load_data_excel():
    """Test loading an Excel file (if openpyxl is installed)."""
    pytest.importorskip('openpyxl')
    # Create a temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    df.to_excel(temp_path, index=False)

    try:
        df_loaded = load_data(temp_path)
        assert isinstance(df_loaded, pd.DataFrame)
        assert df_loaded.shape == (2, 2)
        assert list(df_loaded.columns) == ['col1', 'col2']
    finally:
        os.unlink(temp_path)


def test_load_data_file_not_found():
    """Test that loading a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_data('non_existent_file.csv')


def test_load_data_unsupported_extension():
    """Test that loading a file with unsupported extension raises ValueError."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        temp_path = f.name
    try:
        with pytest.raises(ValueError):
            load_data(temp_path)
    finally:
        os.unlink(temp_path)