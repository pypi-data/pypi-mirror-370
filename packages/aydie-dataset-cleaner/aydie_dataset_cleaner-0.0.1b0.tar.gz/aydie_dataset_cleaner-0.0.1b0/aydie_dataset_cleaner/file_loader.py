import os
from typing import Union, Dict, Any
import pandas as pd
from pandas import DataFrame


def load_dataset(filepath: str, **kwargs: Any) -> DataFrame:
    """ 
    Loads a dataset from a given file path into a pandas DataFrame.

    This function automatically detects the file type based on the extension
    and uses the appropriate pandas function to read the data. It supports

    CSV, Excel (xlsx, xls), and Parquet formats.

    Args:
        filepath (str): The full path to the dataset file.
        **kwargs (Any): Arbitrary keyword arguments to be passed to the
                        respective pandas read function (e.g., `read_csv`,
                        `read_excel`, `read_parquet`).

    Returns:
        pd.DataFrame: A pandas DataFrame containing the loaded data.

    Raises:
        FileNotFoundError: If the file specified by `filepath` does not exist.
        ValueError: If the file format is not supported or recognized.
        Exception: For any other pandas-related loading errors.

    Example:
        >>> from aydie_dataset_cleaner.file_loader import load_dataset
        >>> # Load a CSV file
        >>> df_csv = load_dataset('data/my_data.csv', sep=',')
        >>>
        >>> # Load an Excel file
        >>> df_excel = load_dataset('data/my_data.xlsx', sheet_name='Sheet1')
        >>>
        >>> # Load a Parquet file
        >>> df_parquet = load_dataset('data/my_data.parquet')
    """
    
    # 1. Validate that the file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Error: The file '{filepath}' was not found.")
    

    # 2. Get the file extension to determine the file type
    # os.path.splitext splits 'path/to/file.csv' into ('path/to/file', '.csv')
    _, file_extension = os.path.splitext(filepath)
    file_extension = file_extension.lower()
    
    print(f"Attempting to load file: {filepath} (type: {file_extension})")
    
    try:
        if file_extension == '.csv':
            return pd.read_csv(filepath, **kwargs)
        elif file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(filepath, **kwargs)
        elif file_extension in ['.parquet', '.pq']:
            return pd.read_parquet(filepath, **kwargs)
        elif file_extension == '.json':
            return pd.read_json(filepath, **kwargs)
        elif file_extension == '.feather':
            return pd.read_feather(filepath, **kwargs)
        elif file_extension in ['.h5', '.hdf5']:
            if 'key' not in kwargs:
                raise ValueError("HDF5 files require a 'key' argument to specify the dataset.")
            return pd.read_hdf(filepath, **kwargs)
        else:
            supported_formats = "CSV (.csv), Excel (.xlsx, .xls), Parquet (.parquet), JSON (.json), Feather (.feather), HDF5 (.h5, .hdf5)"
            raise ValueError(
                f"Unsupported file format: '{file_extension}'. "
                f"Supported formats are: {supported_formats}"
            )
    except Exception as e:
        print(f"An error occurred while loading the file: {filepath}")
        raise e