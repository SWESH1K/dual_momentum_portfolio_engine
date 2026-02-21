import numpy as np
import pandas as pd


class Metrics:

    def __init__(
        self,
        portfolio_daily_returns: pd.Series,
        portfolio_value: pd.Series
    ):
        if portfolio_daily_returns is None or portfolio_daily_returns.empty:
            raise ValueError("portfolio_daily_returns must be a non-empty Series.")

        if portfolio_value is None or portfolio_value.empty:
            raise ValueError("portfolio_value must be a non-empty Series.")

        if not isinstance(portfolio_daily_returns.index, pd.DatetimeIndex):
            raise TypeError("portfolio_daily_returns must have a DatetimeIndex.")

        if not isinstance(portfolio_value.index, pd.DatetimeIndex):
            raise TypeError("portfolio_value must have a DatetimeIndex.")

        if len(portfolio_value) < 2:
            raise ValueError("portfolio_value must contain at least two observations.")

        self.portfolio_daily_returns = portfolio_daily_returns.dropna()
        self.portfolio_value = portfolio_value.dropna()

        if self.portfolio_value.iloc[0] <= 0:
            raise ValueError("Initial portfolio value must be positive.")

    def total_return(self) -> float:
        """
        Computes total return over the entire period.
        """
        start_value = self.portfolio_value.iloc[0]
        end_value = self.portfolio_value.iloc[-1]

        if start_value == 0:
            raise ZeroDivisionError("Initial portfolio value is zero.")

        return (end_value / start_value) - 1

    def cagr(self, trading_days: int = 252) -> float:
        """
        Computes Compound Annual Growth Rate.
        """

        if trading_days <= 0:
            raise ValueError("trading_days must be positive.")

        start_value = self.portfolio_value.iloc[0]
        end_value = self.portfolio_value.iloc[-1]
        n_days = len(self.portfolio_value)

        years = n_days / trading_days

        if years <= 0:
            raise ValueError("Invalid time period for CAGR calculation.")

        return (end_value / start_value) ** (1 / years) - 1

    def max_drawdown(self) -> float:
        """
        Computes maximum drawdown.
        """

        rolling_max = self.portfolio_value.cummax()

        drawdown = (self.portfolio_value - rolling_max) / rolling_max

        return drawdown.min()

    def volatility(self, trading_days: int = 252) -> float:
        """
        Computes annualized volatility.
        """

        if trading_days <= 0:
            raise ValueError("trading_days must be positive.")

        if len(self.portfolio_daily_returns) < 2:
            raise ValueError("Not enough return observations to compute volatility.")

        daily_vol = self.portfolio_daily_returns.std(ddof=1)

        return daily_vol * np.sqrt(trading_days)