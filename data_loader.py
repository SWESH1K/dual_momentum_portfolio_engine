import pandas as pd
import os
from typing import Optional
from custom_exceptions import DataNotLoadedError


class DataLoader:

    def __init__(self, data_path: str, index_col: str):
        self.data_path = data_path
        self.index_col = index_col
        self.data: Optional[pd.DataFrame] = None

    def load_data(self, clean_data: bool = True) -> None:
        """
        Loads CSV data, sets the index column, converts it to datetime,
        optionally cleans missing values, and validates dataset integrity.
        """

        # Validate file path
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"File not found at path: {self.data_path}")

        try:
            self.data = pd.read_csv(self.data_path)

        except pd.errors.EmptyDataError:
            raise ValueError("The provided CSV file is empty.")

        except pd.errors.ParserError:
            raise ValueError("Error parsing CSV file. Please check file format.")

        # Validate index column existence
        if self.index_col not in self.data.columns:
            raise KeyError(
                f"Index column '{self.index_col}' does not exist in dataset columns."
            )

        # Set index
        self.data.set_index(self.index_col, inplace=True)

        # Convert index to datetime
        try:
            self.data.index = pd.to_datetime(self.data.index, dayfirst=True)
        except Exception:
            raise ValueError(
                f"Index column '{self.index_col}' cannot be converted to datetime."
            )

        # Sort by datetime index
        self.data.sort_index(inplace=True)

        # Optional forward fill cleaning
        if clean_data:
            self.data.ffill(inplace=True)

        # Validate dataset after processing
        if self.data.empty:
            raise ValueError("Dataset is empty after loading and cleaning.")

        # Check duplicate index values
        if self.data.index.duplicated().any():
            raise ValueError("Duplicate values found in index column.")

    def print_missing_values_count(self) -> None:
        """
        Prints missing value count for each column.
        """

        if self.data is None:
            raise DataNotLoadedError("Data must be loaded before checking missing values.")

        missing_counts = self.data.isna().sum()

        for col, count in missing_counts.items():
            print(f"{col}: {count}")

    def generate_daily_returns(self) -> pd.DataFrame:
        """
        Generates daily percentage returns using numeric columns only.
        """

        if self.data is None:
            raise DataNotLoadedError("Data must be loaded before generating returns.")

        if self.data.empty:
            raise ValueError("Cannot calculate returns on empty dataset.")

        numeric_data = self.data.select_dtypes(include=["number"])

        if numeric_data.empty:
            raise ValueError("No numeric columns available to calculate returns.")

        daily_returns = numeric_data.pct_change().dropna()

        if daily_returns.empty:
            raise ValueError("Daily returns calculation resulted in an empty dataset.")

        return daily_returns