import pandas as pd
import numpy as np
from custom_exceptions import DataNotLoadedError

class DataLoader:

  def __init__(
      self,
      data_path: str,
      index_col: str
  ):
    self.data_path = data_path
    self.index_col = index_col
    self.data = None

  def load_data(self, clean_data=True):

    try:
      # Data loading
      self.data = pd.read_csv(self.data_path)
      self.data = self.data.set_index(self.index_col)
      self.data.index = pd.to_datetime(self.data.index, dayfirst=True)
      # Data cleaning
      if clean_data:
        self.data.ffill(axis=0, inplace=True)

    except Exception as e:
      if isinstance(e, FileNotFoundError):
        raise FileNotFoundError("Given File Path doesn't exist!")
      if isinstance(e, KeyError):
        raise KeyError(f"Given index_col='{self.index_col}' doesn't exist in the dataset columns!")

      raise e

  def print_missing_values_count(self):

    if self.data is None:
      raise DataNotLoadedError(self.data)

    for col in self.data.iloc(1):
      missing_val = col[col.isna()==True]
      print(f"{col.name}: {len(missing_val)}")

  def generate_daily_returns(self):
    if self.data is None:
      raise DataNotLoadedError(self.data)

    daily_returns = self.data.copy()
    daily_returns = self.data.pct_change()
    daily_returns = daily_returns[1:]

    return daily_returns