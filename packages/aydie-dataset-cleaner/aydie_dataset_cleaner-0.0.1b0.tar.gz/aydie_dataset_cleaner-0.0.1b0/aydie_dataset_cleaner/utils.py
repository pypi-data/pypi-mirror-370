import os
import pandas as pd
from typing import Optional, Any

def load_dataset(filepath: str, **kwargs: Any) -> Optional[pd.DataFrame]:
    """
    Loads a dataset from various file formats into a pandas DataFrame.

    Supported formats:
        - CSV (.csv)
        - Excel (.xls, .xlsx, .xlsm, .xlsb, .odf, .ods, .odt)
        - JSON (.json)
        - Parquet (.parquet)
        - Feather (.feather)
        - ORC (.orc)
        - Stata (.dta)
        - SAS (.sas7bdat, .xpt)
        - Pickle (.pkl)
        - HDF5 (.h5, .hdf5)

    Args:
        filepath (str): Path to the file.
        **kwargs: Additional arguments passed to pandas readers.

    Returns:
        Optional[pd.DataFrame]: A DataFrame if loading is successful, otherwise None.
    """
    print(f"Attempting to load dataset from: {filepath}")

    if not os.path.exists(filepath):
        print(f"Error: The file was not found at {filepath}")
        return None

    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == ".csv":
            df = pd.read_csv(filepath, **kwargs)
        elif ext in [".xls", ".xlsx", ".xlsm", ".xlsb", ".odf", ".ods", ".odt"]:
            df = pd.read_excel(filepath, **kwargs)
        elif ext == ".json":
            df = pd.read_json(filepath, **kwargs)
        elif ext == ".parquet":
            df = pd.read_parquet(filepath, **kwargs)
        elif ext == ".feather":
            df = pd.read_feather(filepath, **kwargs)
        elif ext == ".orc":
            df = pd.read_orc(filepath, **kwargs)
        elif ext == ".dta":
            df = pd.read_stata(filepath, **kwargs)
        elif ext in [".sas7bdat", ".xpt"]:
            df = pd.read_sas(filepath, **kwargs)
        elif ext in [".h5", ".hdf5"]:
            df = pd.read_hdf(filepath, **kwargs)
        elif ext == ".pkl":
            df = pd.read_pickle(filepath, **kwargs)
        else:
            print(f"Error: Unsupported file extension '{ext}'.")
            return None

        print("Dataset loaded successfully.")
        return df

    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {ext} file: {e}")
        return None