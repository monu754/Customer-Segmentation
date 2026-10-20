"""
Data loading module for the customer segmentation project.
"""
import pandas as pd
import os
from typing import Union


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV or Excel file.

    Parameters
    ----------
    file_path : str
        Path to the data file.

    Returns
    -------
    pd.DataFrame
        Loaded data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file extension is not supported.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Supported extensions are .csv, .xlsx, .xls")

    return df