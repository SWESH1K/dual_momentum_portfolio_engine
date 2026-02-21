import pandas as pd
from custom_exceptions import DataNotLoadedError
from metrics import Metrics

class StrategyEngine:

  def __init__(
      self,
      cleaned_data: pd.DataFrame,
      daily_returns: pd.DataFrame
  ):
    self.data = cleaned_data
    self.daily_returns = daily_returns

  def generate_momentum_score(self, num_days: int):

    if self.data is None:
      raise DataNotLoadedError(self.data)

    momentum_score = self.data.copy()
    momentum_score = self.data.pct_change(periods=num_days)
    momentum_score = momentum_score.iloc[num_days:]

    return momentum_score

  def get_monthly_rebalance(self, num_days: int):

    momentum_score = self.generate_momentum_score(num_days)

    momentum_on_first_trading_days = momentum_score.groupby(momentum_score.index.to_period("M")).first()
    momentum_on_first_trading_days = momentum_on_first_trading_days[1:]

    top_assets_each_month = (
        momentum_on_first_trading_days
            .apply(lambda row: row.nlargest(2).index.tolist(), axis=1)
            .to_dict()
    )
    return top_assets_each_month

  def compute_portfolio_daily_returns(self, num_days: int):
    top_assets_each_month = self.get_monthly_rebalance(num_days)

    monthly_period = self.daily_returns.index.to_period("M")

    portfolio_daily_returns = pd.Series(index=self.daily_returns.index, dtype=float)

    for month, assets in top_assets_each_month.items():
        mask = monthly_period == month

        portfolio_daily_returns.loc[mask] = (
            self.daily_returns.loc[mask, assets].mean(axis=1)
        )

    portfolio_daily_returns = portfolio_daily_returns.fillna(0)

    return portfolio_daily_returns

  def compute_cumulative_value(self, portfolio_daily_returns: pd.Series, initial_amount: int):

      portfolio_value = (
          (1 + portfolio_daily_returns)
          .cumprod()
          * initial_amount
      )

      return portfolio_value

  def compute_strategy(self, lookback_days: int, initial_amount: int = 1000):

    portfolio_daily_returns = self.compute_portfolio_daily_returns(lookback_days)
    portfolio_value = self.compute_cumulative_value(portfolio_daily_returns, initial_amount=initial_amount)
    metrics = Metrics(portfolio_daily_returns, portfolio_value)

    all_metrics = {
      "total_return": metrics.total_return(),
      "cagr": metrics.cagr(),
      "max_drawdown": metrics.max_drawdown(),
      "volatility": metrics.volatility()
    }

    return all_metrics