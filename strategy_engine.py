import pandas as pd
from typing import Dict, List
from custom_exceptions import DataNotLoadedError
from metrics import Metrics


class StrategyEngine:

    def __init__(
        self,
        cleaned_data: pd.DataFrame,
        daily_returns: pd.DataFrame
    ):
        if cleaned_data is None or cleaned_data.empty:
            raise ValueError("cleaned_data must be a non-empty DataFrame.")

        if daily_returns is None or daily_returns.empty:
            raise ValueError("daily_returns must be a non-empty DataFrame.")

        if not isinstance(cleaned_data.index, pd.DatetimeIndex):
            raise TypeError("cleaned_data must have a DatetimeIndex.")

        if not isinstance(daily_returns.index, pd.DatetimeIndex):
            raise TypeError("daily_returns must have a DatetimeIndex.")

        self.data = cleaned_data
        self.daily_returns = daily_returns

    def generate_momentum_score(self, num_days: int) -> pd.DataFrame:
        """
        Generates momentum score using percentage change over num_days.
        """

        if num_days <= 0:
            raise ValueError("num_days must be a positive integer.")

        if num_days >= len(self.data):
            raise ValueError("num_days is too large for the dataset length.")

        momentum_score = self.data.pct_change(periods=num_days).dropna()

        if momentum_score.empty:
            raise ValueError("Momentum score calculation resulted in empty DataFrame.")

        return momentum_score

    def get_monthly_rebalance(self, num_days: int) -> Dict[pd.Period, List[str]]:
        """
        Selects top 2 assets based on momentum on first trading day of each month.
        """

        momentum_score = self.generate_momentum_score(num_days)

        monthly_first = (
            momentum_score
            .groupby(momentum_score.index.to_period("M"))
            .first()
        )

        if monthly_first.empty:
            raise ValueError("Monthly grouping resulted in empty DataFrame.")

        top_assets_each_month = (
            monthly_first
            .apply(lambda row: row.nlargest(2).dropna().index.tolist(), axis=1)
            .to_dict()
        )

        if not top_assets_each_month:
            raise ValueError("No assets selected during monthly rebalance.")

        return top_assets_each_month

    def compute_portfolio_daily_returns(self, num_days: int) -> pd.Series:
        """
        Computes equal-weighted portfolio daily returns based on monthly top assets.
        """

        top_assets_each_month = self.get_monthly_rebalance(num_days)

        monthly_period = self.daily_returns.index.to_period("M")

        portfolio_daily_returns = pd.Series(
            index=self.daily_returns.index,
            dtype=float
        )

        for month, assets in top_assets_each_month.items():

            if not assets:
                continue

            mask = monthly_period == month

            valid_assets = [
                asset for asset in assets
                if asset in self.daily_returns.columns
            ]

            if not valid_assets:
                continue

            portfolio_daily_returns.loc[mask] = (
                self.daily_returns.loc[mask, valid_assets]
                .mean(axis=1)
            )

        portfolio_daily_returns.fillna(0, inplace=True)

        return portfolio_daily_returns

    def compute_cumulative_value(
        self,
        portfolio_daily_returns: pd.Series,
        initial_amount: float
    ) -> pd.Series:
        """
        Computes cumulative portfolio value.
        """

        if initial_amount <= 0:
            raise ValueError("initial_amount must be positive.")

        if portfolio_daily_returns is None or portfolio_daily_returns.empty:
            raise ValueError("portfolio_daily_returns must be non-empty.")

        portfolio_value = (
            (1 + portfolio_daily_returns)
            .cumprod()
            * initial_amount
        )

        return portfolio_value

    def compute_strategy(
        self,
        lookback_days: int,
        initial_amount: float = 1000
    ) -> dict:
        """
        Runs full strategy pipeline and returns performance metrics.
        """

        portfolio_daily_returns = self.compute_portfolio_daily_returns(lookback_days)

        portfolio_value = self.compute_cumulative_value(
            portfolio_daily_returns,
            initial_amount
        )

        metrics = Metrics(portfolio_daily_returns, portfolio_value)

        all_metrics = {
            "total_return": metrics.total_return(),
            "cagr": metrics.cagr(),
            "max_drawdown": metrics.max_drawdown(),
            "volatility": metrics.volatility()
        }

        return all_metrics