from data_loader import DataLoader
from strategy_engine import StrategyEngine
from ai_analysis import get_ai_analysis


def main():
    dl = DataLoader(
        data_path="assets.csv",
        index_col="Date"
    )

    dl.load_data()
    daily_returns = dl.generate_daily_returns()

    st_eng = StrategyEngine(cleaned_data=dl.data, daily_returns=daily_returns)
    strategy_A_metrics = st_eng.compute_strategy(lookback_days=30)
    strategy_B_metrics = st_eng.compute_strategy(lookback_days=90)

    get_ai_analysis(strategy_A_metrics, strategy_B_metrics)

if __name__ == "__main__":
    main()