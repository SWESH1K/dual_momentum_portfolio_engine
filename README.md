# Dual Momentum Portfolio Engine with AI Performance Comparison

A comprehensive dashboard application for analyzing and comparing two momentum-based investment strategies with AI-powered performance insights.

## Overview

This project implements a momentum-based portfolio analysis platform that:
- Loads and processes historical asset price data
- Computes daily returns and momentum indicators
- Implements two different momentum strategies with monthly rebalancing
- Compares strategy performance using multiple financial metrics
- Generates AI-powered analysis using Google's Gemini API
- Provides an interactive dashboard visualization

## Setup Instructions

### Prerequisites
- Python 3.13 or higher
- uv package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/))

### Installation

1. **Clone or download the project** to your local directory:
   ```bash
   cd /path/to/NB_Assignment
   ```

2. **Initialize and sync dependencies with uv**:
   ```bash
   uv init
   uv sync
   ```

   This command will:
   - Create a virtual environment
   - Install all dependencies from `pyproject.toml`
   - Set up the project in editable mode

3. **Set up environment variables**:
   - Create a `.env` file in the project root directory
   - Add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Obtain a free API key from [Google AI Studio](https://aistudio.google.com/)

4. **Ensure data file exists**:
   - Place your `assets.csv` file in the project root directory
   - CSV format: Date column and asset price columns (e.g., Asset1, Asset2, Asset3, etc.)
### Running the Application

```bash
uv run python main.py
```

The dashboard will be available at `http://127.0.0.1:8050/` in your browser.

## Project Structure

- **main.py** - Dash application entry point with interactive dashboard
- **data_loader.py** - DataLoader class for CSV ingestion and data cleaning
- **strategy_engine.py** - StrategyEngine class implementing momentum calculations and portfolio returns
- **ai_analysis.py** - AI analysis module using Google Gemini for strategy comparison
- **metrics.py** - Metrics calculation (Total Return, CAGR, Max Drawdown, etc.)
- **custom_exceptions.py** - Custom exception classes for error handling
- **assets.csv** - Historical asset price data
- **test_notebook.ipynb** - Jupyter notebook for testing and exploration
- **pyproject.toml** - Project configuration and dependencies

## Assumptions Made

1. **Forward-fill missing values**: If an asset's value is missing on day t, the value from day t-1 is used.
   - Mathematically: if `assetX_t == null` then `assetX_t = assetX_{t-1}`

2. **Missing complete dates are non-trading dates**: If all assets are missing data for a date, that date is excluded from analysis.

3. **First return is discarded**: The return on the first date (01-01-2021) is dropped because there is no previous date in the dataset to compute the return.

4. **Momentum lookback period**: For any momentum-based strategy with an n-day lookback period, monthly rebalancing cannot be computed until sufficient historical data is available. Once n days of price history exist, the strategy begins on the first trading day of the month that achieves this threshold.

## Design Decisions

### 1. **Modular Architecture**
The codebase is organized into separate modules with clear responsibilities:
- **data_loader.py**: Handles all CSV I/O and data validation
- **strategy_engine.py**: Encapsulates portfolio strategy logic
- **metrics.py**: Isolated financial metric calculations
- **ai_analysis.py**: Dedicated AI integration layer

This separation enables testing, reusability, and maintainability.

### 2. **Class-Based Design**
- `DataLoader`: Manages data pipeline with validation and error handling
- `StrategyEngine`: Implements strategy logic with monthly rebalancing
- `Metrics`: Static methods for financial calculations

### 3. **Error Handling & Validation**
- Custom exceptions (`DataNotLoadedError`) for specific error scenarios
- Input validation at method entry points
- Type checking (DatetimeIndex validation, DataFrame validation)
- Graceful degradation with informative error messages

### 4. **Momentum Strategy Implementation**
- **Strategy A**: Top 2 assets selected by 30-day momentum, rebalanced monthly
- **Strategy B**: Top 2 assets selected by 90-day momentum, rebalanced monthly
- Equal-weight portfolio (50% each asset)
- Rebalancing occurs on the first trading day of each month

### 5. **Interactive Dashboard**
- Built with Dash and Plotly for real-time visualization
- Bootstrap styling for responsive design
- Dynamic metric cards and performance charts
- AI analysis panel displays strategy comparison insights

### 6. **API Integration with Google Gemini**
- Uses `google-genai` library for structured AI analysis
- Supports both streaming and non-streaming modes
- Isolated prompt engineering for maintainability
- Role-based prompting (quantitative analyst persona)

## Module and Class Documentation

### data_loader.py

#### **DataLoader Class**
Responsible for loading CSV data, cleaning, and preparing it for analysis.

**Constructor: `__init__(data_path: str, index_col: str)`**
- `data_path`: Path to the CSV file containing asset prices
- `index_col`: Column name to use as the datetime index (typically "Date")
- Initializes `self.data` as None until data is loaded

**Method: `load_data(clean_data: bool = True) -> None`**
- Validates file existence and reads CSV into a pandas DataFrame
- Sets the specified column as the index
- Converts index to datetime format using `dayfirst=True` (for DD-MM-YYYY format)
- Sorts data chronologically by the datetime index
- Applies forward-fill (ffill) to handle missing values if `clean_data=True`
- Validates data integrity (empty checks, duplicate index checks)
- Raises: `FileNotFoundError`, `ValueError`, `KeyError`, or custom `DataNotLoadedError`

**Method: `print_missing_values_count() -> None`**
- Displays count of missing values for each asset column
- Useful for understanding data quality before analysis
- Raises: `DataNotLoadedError` if data hasn't been loaded

**Method: `generate_daily_returns() -> pd.DataFrame`**
- Calculates daily percentage returns using `pct_change()` method
- Filters for numeric columns only (ignores non-numeric data)
- Removes NaN values from calculations
- Returns DataFrame with same structure as input data but with return values
- Formula: $\text{return}_t = \frac{\text{price}_t}{\text{price}_{t-1}} - 1$
- Raises: `DataNotLoadedError` or `ValueError` if data unavailable or empty

---

### strategy_engine.py

#### **StrategyEngine Class**
Implements momentum-based portfolio construction and performance calculations.

**Constructor: `__init__(cleaned_data: pd.DataFrame, daily_returns: pd.DataFrame)`**
- `cleaned_data`: Historical asset prices with DatetimeIndex
- `daily_returns`: Daily returns DataFrame with DatetimeIndex
- Validates both inputs are non-empty DataFrames with proper DatetimeIndex
- Raises: `ValueError` or `TypeError` if inputs are invalid

**Method: `generate_momentum_score(num_days: int) -> pd.DataFrame`**
- Calculates momentum as percentage change over `num_days` periods
- Momentum Score = $\text{pct\_change(periods=num\_days)}$
- Example: 30-day momentum shows percentage change over last 30 days
- Removes NaN values resulting from the lookback period
- Raises: `ValueError` if `num_days` is invalid or results in empty DataFrame

**Method: `get_monthly_rebalance(num_days: int) -> Dict[pd.Period, List[str]]`**
- Selects top 2 assets based on momentum on the **first trading day of each month**
- Process:
  1. Generates momentum score for `num_days` period
  2. Groups by month and selects first trading day of each month
  3. For each month's first day, identifies top 2 assets with highest momentum
  4. Returns dictionary mapping months to list of selected asset names
- Returns: `Dict[pd.Period, List[str]]` e.g., `{2021-03: ['Asset1', 'Asset2'], 2021-04: ['Asset3', 'Asset1']}`
- Raises: `ValueError` if grouping results in empty DataFrame

**Method: `compute_portfolio_daily_returns(num_days: int) -> pd.Series`**
- Computes equal-weighted daily returns of the portfolio
- Process:
  1. Gets top 2 assets for each month via `get_monthly_rebalance()`
  2. For each trading day, calculates mean of returns from selected assets
  3. Uses 50% weight for each of the top 2 assets
  4. Handles transitions at month boundaries (rebalancing)
- Formula: $\text{Portfolio Return}_t = \frac{\text{Return}_{\text{Asset1}, t} + \text{Return}_{\text{Asset2}, t}}{2}$
- Fills any gaps with 0 when no valid assets available for a period
- Returns: `pd.Series` with portfolio daily returns

**Method: `compute_cumulative_value(portfolio_daily_returns: pd.Series, initial_amount: float) -> pd.Series`**
- Converts daily returns into cumulative portfolio value
- Formula: $\text{Value}_t = (1 + \text{return}_1) \times (1 + \text{return}_2) \times ... \times (1 + \text{return}_t) \times \text{initial\_amount}$
- Assumes compounding of returns (compound growth model)
- Default initial investment: $1000
- Returns: `pd.Series` representing portfolio value over time

**Method: `compute_strategy(lookback_days: int, initial_amount: float = 1000) -> dict`**
- Runs entire strategy pipeline end-to-end
- Process:
  1. Calculates portfolio daily returns using `compute_portfolio_daily_returns()`
  2. Computes cumulative portfolio value using `compute_cumulative_value()`
  3. Instantiates `Metrics` class and computes all financial metrics
  4. Returns dictionary with: total_return, cagr, max_drawdown, volatility
- Returns: `dict` with all computed metrics
- This is the main public interface for running a strategy

---

### metrics.py

#### **Metrics Class**
Calculates financial performance metrics for a portfolio.

**Constructor: `__init__(portfolio_daily_returns: pd.Series, portfolio_value: pd.Series)`**
- `portfolio_daily_returns`: Series of daily returns with DatetimeIndex
- `portfolio_value`: Series of cumulative portfolio values with DatetimeIndex
- Validates both inputs have proper structure and DatetimeIndex
- Drops NaN values from both series
- Raises: `ValueError` or `TypeError` if inputs invalid

**Method: `total_return() -> float`**
- Calculates total return from start to end of period
- Formula: $\text{Total Return} = \frac{\text{End Value}}{\text{Start Value}} - 1$
- Example: If portfolio grew from $1000 to $1500, returns 0.50 (50%)
- Returns: `float` representing total return (as decimal, e.g., 0.25 = 25%)

**Method: `cagr(trading_days: int = 252) -> float`**
- Computes Compound Annual Growth Rate
- Annualizes returns by accounting for time period length
- Formula: $\text{CAGR} = \left(\frac{\text{End Value}}{\text{Start Value}}\right)^{\frac{1}{\text{years}}} - 1$
- Where `years = num_days / trading_days` (252 trading days per year)
- Example: 10% total return over 2 years = ~4.88% CAGR
- Returns: `float` representing annualized growth rate
- Raises: `ValueError` if trading_days <= 0 or invalid time period

**Method: `max_drawdown() -> float`**
- Calculates maximum loss from peak value
- Process:
  1. Computes running maximum (peak) of portfolio value
  2. Calculates drawdown at each point: $\text{Drawdown}_t = \frac{\text{Value}_t - \text{Peak}_t}{\text{Peak}_t}$
  3. Returns minimum (most negative) drawdown
- Formula: $\text{Max Drawdown} = \min\left(\frac{\text{Value}_t - \text{Peak}_t}{\text{Peak}_t}\right)$
- Example: -0.20 means portfolio fell 20% from its highest point
- Returns: `float` (negative value representing loss)
- Usage: Risk metric - smaller (less negative) is better

**Method: `volatility(trading_days: int = 252) -> float`**
- Calculates annualized standard deviation of returns
- Process:
  1. Computes standard deviation of daily returns (using sample std with ddof=1)
  2. Annualizes by multiplying by $\sqrt{\text{trading\_days}}$
- Formula: $\text{Volatility} = \text{std(daily returns)} \times \sqrt{252}$
- High volatility indicates unpredictable/risky returns
- Returns: `float` representing annualized volatility (as decimal)

---

### ai_analysis.py

#### **AIAnalysisError Exception**
- Custom exception raised when AI analysis fails
- Inherits from standard `Exception` class

#### **get_ai_analysis() Function**
Generates structured investment analysis by comparing two strategies using Google Gemini API.

**Signature: `get_ai_analysis(strategy_A_score: Dict[str, Any], strategy_B_score: Dict[str, Any], model: str = "gemini-2.5-flash-lite", stream: bool = False) -> str`**

**Parameters:**
- `strategy_A_score`: Dictionary containing metrics for Strategy A (e.g., `{"total_return": 0.25, "cagr": 0.12, ...}`)
- `strategy_B_score`: Dictionary containing metrics for Strategy B
- `model`: Gemini model to use (default: "gemini-2.5-flash-lite")
- `stream`: Boolean for streaming response (default: False)

**Process:**
1. Retrieves API key from environment variable `GEMINI_API_KEY`
2. Validates input dictionaries (type checking)
3. Serializes both strategy scores to JSON format for clarity
4. Constructs detailed prompt instructing AI to compare strategies
5. Sends prompt to Google Gemini API
6. Handles response (streaming or non-streaming based on parameter)
7. Validates response is not empty

**Output Format:**
Returns a string containing structured analysis with 5 sections:
1. Overall Performance
2. Risk Characteristics
3. Risk-Return Trade-off
4. Market Regime Suitability
5. One Concrete Improvement Suggestion

**Error Handling:**
- Raises `EnvironmentError` if GEMINI_API_KEY not set
- Raises `TypeError` if input parameters are not dictionaries
- Raises `ValueError` if JSON serialization fails
- Raises `AIAnalysisError` if API request fails or returns empty response

---

### custom_exceptions.py

#### **DataNotLoadedError Exception**
Custom exception for operations attempted on unloaded data.

**Constructor: `__init__(data, message: str = "...")`**
- `data`: The data object that wasn't loaded
- `message`: Custom error message (default: instructions to use DataLoader.load_data())

**Method: `__str__() -> str`**
- Customized error display showing the data object and message
- Format: `"data = {data} -> {message}"`

**Usage:**
- Raised by `DataLoader` methods when data hasn't been loaded yet
- Provides informative guidance to users about required setup steps

---

### main.py

#### **Application Setup**

**Function: `prepare_data() -> Tuple[pd.DataFrame, pd.DataFrame]`**
- Initializes DataLoader, loads asset data from CSV, and generates daily returns
- Returns tuple: (cleaned_data, daily_returns)
- Called during app initialization to prepare data for strategies

#### **Helper Functions for Dashboard UI**

**Function: `format_percent(x: float) -> str`**
- Converts decimal to percentage string with 2 decimal places
- Example: 0.25 → "25.00%"

**Function: `metric_card(title: str, value: str, positive_good: bool = True) -> dbc.Card`**
- Creates a styled metric display card
- Colors: Green (success) if metric is positive and positive_good=True
- Uses Bootstrap styling for consistent appearance

**Function: `strategy_metrics_section(strategy_name: str, metrics: dict) -> dbc.Card`**
- Creates a card displaying all 4 metrics (Total Return, CAGR, Volatility, Max Drawdown)
- Organizes metrics in a responsive grid layout
- Colors metrics based on whether higher/lower is better

**Function: `create_portfolio_chart(values: pd.Series, strategy_name: str) -> go.Figure`**
- Creates interactive line chart showing portfolio value over time
- Uses Plotly for interactive visualization
- Displays date on x-axis and portfolio value on y-axis

**Function: `create_momentum_heatmap(engine: StrategyEngine, lookback: int, strategy_name: str) -> go.Figure`**
- Creates heatmap of momentum scores across assets and months
- Shows which assets had highest momentum each month
- Visual representation of strategy asset selection process

#### **Dash App Initialization and Layout**
- Creates interactive web dashboard with multiple sections
- Callback functions handle user interactions (button clicks, input changes)
- Displays both strategies side-by-side for easy comparison
- Includes AI analysis panel powered by `get_ai_analysis()`

---

## AI Prompt Structure Explanation

The AI analysis module uses a structured prompt designed to generate professional investment analysis. Here's how it works:

### Prompt Foundation
- **Role Definition**: The model is instructed to act as a "quantitative investment analyst"
- **Input Format**: Strategy metrics are serialized as JSON for clarity and structure
- **Output Structure**: Enforced section-based analysis prevents rambling

### Prompt Sections

The AI is instructed to follow 5 strict sections:

1. **Overall Performance**
   - Compares total returns, cumulative performance
   - Identifies which strategy performed better

2. **Risk Characteristics**
   - Analyzes volatility, drawdown patterns
   - Compares risk metrics (Total Return, CAGR, Max Drawdown, etc)

3. **Risk-Return Trade-off**
   - Evaluates return per unit of risk
   - Identifies efficiency frontier position

4. **Market Regime Suitability**
   - Assesses which strategy works better in different market conditions
   - Considers momentum effectiveness in trending vs. ranging markets

5. **One Concrete Improvement Suggestion**
   - Provides actionable recommendations
   - Not theoretical but grounded in the specific metrics

### Formatting Guidelines
The prompt enforces:
- Use of section headings for structure
- Analytical and concise language
- No fabrication of data
- Reasoning strictly based on provided metrics

### Implementation Details
```python
prompt = f"""
You are a quantitative investment analyst.

You will receive JSON input containing performance metrics of two investment strategies.

Your task is to perform a structured professional comparison.

Follow these sections strictly:

1. Overall Performance
2. Risk Characteristics
3. Risk-Return Trade-off
4. Market Regime Suitability
5. One Concrete Improvement Suggestion

Formatting:
- Use section headings
- Be analytical and concise
- Do not fabricate data
- Base reasoning strictly on provided metrics

Strategy A:
{strategy_A_json}

Strategy B:
{strategy_B_json}
"""
```

### Why This Structure?
- **Consistency**: Every AI analysis follows the same format for predictability
- **Relevance**: Sections focus on investment decision-making criteria
- **Guardrails**: Explicit constraints prevent hallucination or irrelevant analysis
- **Actionability**: The improvement suggestion provides practical next steps

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| dash | ≥4.0.0 | Web dashboard framework |
| dash-bootstrap-components | ≥2.0.4 | Bootstrap styling |
| google-genai | ≥1.64.0 | Google AI API client |
| google-generativeai | ≥0.8.6 | Generative AI integration |
| numpy | ≥2.4.2 | Numerical computing |
| pandas | ≥3.0.1 | Data manipulation |
| plotly | ≥6.5.2 | Interactive charts |
| python-dotenv | ≥1.2.1 | Environment variable management |

## Key Features

- **Data Cleaning**: Forward-fill missing values, handle non-trading dates
- **Momentum Calculation**: 30-day and 90-day lookback periods
- **Portfolio Construction**: Equal-weight monthly rebalancing
- **Performance Metrics**: Total Return, CAGR, Max Drawdown, etc
- **AI Comparison**: Automated strategy analysis using Google Gemini
- **Interactive Dashboard**: Real-time visualization and metric display

## Notes

- API key required for AI analysis features (free tier available)
- Asset data must be in CSV format with dates and numeric asset columns
- Dashboard runs in debug mode by default