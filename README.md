## Assumptions made
1. If the assetX value is missing on day t, then the value at day t-1 is considered, i.e if assetX_t == null then assetX_t = assetX_{t-1}

2. If any date's data is missing completly then it is assumed as non-trading date.

3. Return at date_1 (01-01-2021) will be dropped as there is no previous date exists in the assets.csv.

4. For Strategy A, since the momentum measure requires a 30-day lookback period, monthly rebalancing cannot be computed on the first trading day of February 2021 due to insufficient prior data. Therefore, the strategy begins on the first trading day of March 2021, which is the first month where the required lookback window is fully available.