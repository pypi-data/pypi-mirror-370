import pandas as pd
import numpy as np
import os

# Import the modules from library
from aydie_dataset_cleaner.file_loader import load_dataset
from aydie_dataset_cleaner.validator import DatasetValidator
from aydie_dataset_cleaner.cleaner import DatasetCleaner
from aydie_dataset_cleaner.reporter import ReportGenerator

def create_sample_dataset(filepath: str = 'sample_data.csv'):
    """Creates a sample csv file with intentional data quality issues."""
    print(f"Creating a sample dataset at '{filepath}'...")
    data = {
        'productclear_id': ['A101', 'A102', 'A103', 'A104', 'A101', 'A105', 'A106', 'A107'],
        'category': ['Electronics', 'Apparel', 'Electronics', 'Home Goods', 'Electronics', 'Apparel', 'Books', 'Books'],
        'price': [1200.50, 75.00, np.nan, 250.75, 1200.50, 80.00, 15.99, 19.99],
        'stock_quantity': [15, 200, 30, np.nan, 15, 195, 500, 450],
        'rating': [4.5, 4.0, 3.5, 4.8, 4.5, 3.9, 4.9, '7.8'],
        'region': ['USA', 'EU', 'USA', 'USA', 'USA', 'EU', 'UK', 'UK_typo'] # Add a categorical anomaly
    }
    df = pd.DataFrame(data)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print("Sample dataset created successfully.")
    return filepath

def main_workflow():
    """ 
    Demonstrates the full workflow of the aydie-dataset-cleaner library
    """
    # --- 1. Setup messy data
    data_dir = 'data'
    dirty_filepath = os.path.join(data_dir, 'dirty_products.csv')
    cleaned_filepath = os.path.join(data_dir, 'cleaned_products.csv')
    report_dir = 'reports'
    os.makedirs(report_dir, exist_ok=True)
    
    create_sample_dataset(dirty_filepath)
    
    # --- 2. LOAD: Load the dataset from the file
    print("\n--- Step 2: Loading Dataset ---")
    try:
        dirty_df = load_dataset(dirty_filepath)
        print("Original (Dirty) DataFrame:")
        print(dirty_df.head(10))
        print("\nData types of original dataframe:")
        dirty_df.info()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading dataset: {e}")
        return
    
    # --- 3. VALIDATE: Run all validation checks
    print("\n--- Step 3: Validation Dataset ---")
    validator = DatasetValidator(dirty_df)
    validation_result = validator.run_all_checks()
    
    # --- 4. REPORT: Generate reports from the validation results
    print("\n--- Step 4: Generating Reports ---")
    reporter = ReportGenerator(validation_result)
    reporter.to_json(os.path.join(report_dir, 'validation_report.json'))
    reporter.to_html(os.path.join(report_dir, 'validation_report.html'))
    print(f"Reports saved in the '{report_dir}/' directory.")

    # --- 5. CLEAN: Clean the dataset based on the report
    print("\n--- Step 5: Cleaning Dataset ---")
    cleaner = DatasetCleaner(dirty_df, validation_result)
    cleaned_df = cleaner.clean_dataset(missing_value_strategy='median')
    
    # --- 6. EXPORT & VERIFY: Save the cleaned data and show the result
    print("\n--- Step 6: Exporting and Verifying Cleaned Dataset ---")
    cleaned_df.to_csv(cleaned_filepath, index=False)
    print(f"Cleaned dataset saved to '{cleaned_filepath}'")
    
    print("\nCleaned DataFrame:")
    print(cleaned_df.head(10))
    print("\nData types of cleaned dataframe:")
    cleaned_df.info()
    
    print("\n\nWorkflow complete! Check the 'reports' folder for the HTML report.")
    
if __name__ == "__main__":
    main_workflow()