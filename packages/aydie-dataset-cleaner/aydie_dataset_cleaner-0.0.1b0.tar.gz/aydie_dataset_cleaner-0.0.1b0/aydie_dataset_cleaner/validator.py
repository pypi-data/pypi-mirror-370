from typing import Dict, List, Any, Union
import pandas as pd
import numpy as np
from pandas import DataFrame

class DatasetValidator:
    """
    A class to perform a series of validation checks on a pandas DataFrame.

    This validator checks for common data quality issues such as missing values,
    duplicate rows, inconsistent data types, and anomalies in categorical and
    numerical data.

    Attributes:
        df (DataFrame): The pandas DataFrame to be validated.
        results (Dict[str, Any]): A dictionary to store the results of the
                                  validation checks.
    """
    
    def __init__(self, df: DataFrame):
        """
        Initializes the DatasetValidator with a DataFrame.

        Args:
            df (DataFrame): The pandas DataFrame to validate.

        Raises:
            TypeError: If the input is not a pandas DataFrame.
        """ 
        if not isinstance(df, DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")
        self.df = df
        self.results: Dict[str, Any] = {}
        
    def check_missing_values(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Checks for missing (NaN) values in each column of the DataFrame.

        Calculates the count and percentage of missing values for any column
        that contains at least one missing value.

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where keys are
            column names with missing values and values are another dictionary
            containing the 'count' and 'percentage' of missing values.
        """
        missing_values_report = {}
        missing_series = self.df.isnull().sum()
        
        # Filter for columns that have one or more missing values
        columns_with_missing = missing_series[missing_series > 0]
        
        if not columns_with_missing.empty:
            total_rows = len(self.df)
            for col, count in columns_with_missing.items():
                percentage = (count / total_rows) * 100
                missing_values_report[col] = {
                    "count": int(count),
                    "percentage": round(percentage, 2)
                }
        return missing_values_report
    
    def check_duplicate_rows(self) -> Dict[str, int]:
        """
        Checks for and counts completely duplicate rows in the DataFrame.

        Returns:
            Dict[str, int]: A dictionary containing the count of duplicate rows.
        """
        duplicate_count = int(self.df.duplicated().sum())
        return {"count": duplicate_count}

    def check_data_types(self) -> Dict[str, str]:
        """
        Identifies columns with mixed or potentially incorrect data types.

        This check flags columns with the 'object' dtype which might be better
        represented as numeric or datetime types.

        Returns:
            Dict[str, str]: A dictionary where keys are column names and
            values are their identified data types (e.g., 'object', 'int64').
        """
        type_report = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        return type_report
        
    def check_categorical_anomalies(self, threshold: float = 0.01) -> Dict[str, List[str]]:
        """ 
                Identifies potential anomalies in categorical columns.

        Anomalies are defined as categories that appear less frequently than a
        given threshold. This is useful for spotting typos or rare values.

        Args:
            threshold (float): The frequency threshold (between 0 and 1) below
                               which a category is considered an anomaly.
                               Defaults to 0.01 (1%).

        Returns:
            Dict[str, List[str]]: A dictionary where keys are categorical
            column names and values are lists of anomalous category values.
        """
        anomaly_report = {}
        
        # select columns with 'object' or 'category' dtype
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            value_counts = self.df[col].value_counts(normalize=True)
            # Find anomalies (categories with frequency below the threshold)
            anomalies = value_counts[value_counts < threshold].index.tolist()
            if anomalies:
                anomaly_report[col] = anomalies
        return anomaly_report
    
    def check_outliers(self, method: str = 'iqr', multiplier: float = 1.5) -> Dict[str, Dict[str, int]]:
        """
        Detects outliers in numerical columns using the specified method.

        Args:
            method (str): The method to use for outlier detection.
                          Currently, only 'iqr', 'zscore', 'mad', 'percentile' are supported.
                          Defaults to 'iqr'.
            multiplier (float): The multiplier for the IQR range. Values outside
                                Q1 - multiplier*IQR and Q3 + multiplier*IQR are
                                considered outliers. Defaults to 1.5.

        Returns:
            Dict[str, Dict[str, int]]: A dictionary where keys are numerical
            column names and values are a dict containing the count of outliers.
        """
        outlier_report = {}
        numerical_cols = self.df.select_dtypes(include=np.number).columns
        
        if method == 'iqr':
            for col in numerical_cols:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - (multiplier * IQR)
                upper_bound = Q3 + (multiplier * IQR)
                
                # Count outliers
                outlier_count = self.df[
                    (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                ].shape[0]
                
                if outlier_count > 0:
                    outlier_report[col] = {"count": outlier_count}
        
        elif method == 'zscore':
            for col in numerical_cols:
                mean = self.df[col].mean()
                std = self.df[col].std()
                z_scores = (self.df[col] - mean) / std
                outlier_count = (abs(z_scores) > multiplier).sum()
                if outlier_count > 0:
                    outlier_report[col] = {"count": int(outlier_count)}
                    
        elif method == 'mad':
            for col in numerical_cols:
                median = self.df[col].median()
                mad = np.median(np.abs(self.df[col] - median))
                if mad == 0:
                    continue
                modified_z_scores = 0.6745 * (self.df[col] - median) / mad
                outlier_count = (abs(modified_z_scores) > multiplier).sum()
                if outlier_count > 0:
                    outlier_report[col] = {"count": int(outlier_count)}
                    
        elif method == 'percentile':
            lower_bound = self.df[col].quantile(0.01)
            upper_bound = self.df[col].quantile(0.99)
            outlier_count = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)].shape[0]
                    
        else:
            raise ValueError("Unsupported outlier detection method. Use 'iqr', 'mad', 'zscore', 'percentile'.")

        return outlier_report
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Runs all available validation checks and compiles the results.

        This is the main method to execute the entire validation pipeline.

        Returns:
            Dict[str, Any]: A nested dictionary containing the results of all
                            validation checks. This dictionary is also stored
                            in the `self.results` attribute.
        """
        print("Running all dataset validation checks...")
        self.results = {
            "summary": {
                "total_rows": len(self.df),
                "total_columns": len(self.df.columns),
            },
            "missing_values": self.check_missing_values(),
            "duplicate_rows": self.check_duplicate_rows(),
            "data_types": self.check_data_types(),
            "categorical_anomalies": self.check_categorical_anomalies(),
            "outliers": self.check_outliers(),
        }
        print("Validation checks complete.")
        return self.results