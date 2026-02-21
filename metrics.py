import numpy as np
import pandas as pd


class Metrics:

  def __init__(
      self,
      portfolio_daily_returns: pd.Series,
      portfolio_value: pd.Series
  ):
    self.portfolio_daily_returns = portfolio_daily_returns
    self.portfolio_value = portfolio_value

  def total_return(self):
    return (self.portfolio_value.iloc[-1] / self.portfolio_value.iloc[0]) - 1

  def cagr(self, trading_days=252):
    start_value = self.portfolio_value.iloc[0]
    end_value = self.portfolio_value.iloc[-1]
    n_days = len(self.portfolio_value)

    years = n_days / trading_days

    return (end_value / start_value) ** (1 / years) - 1

  def max_drawdown(self):
    if self.portfolio_value.empty:
        return None

    rolling_max = self.portfolio_value.cummax()
    drawdown = (self.portfolio_value - rolling_max) / rolling_max

    return drawdown.min()

  def volatility(self, trading_days=252):
    if self.portfolio_daily_returns.empty:
        return None

    daily_vol = self.portfolio_daily_returns.std()
    return daily_vol * np.sqrt(trading_days)