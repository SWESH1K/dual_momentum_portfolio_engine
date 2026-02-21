import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from data_loader import DataLoader
from strategy_engine import StrategyEngine
from ai_analysis import get_ai_analysis


# -----------------------------------
# Data Preparation
# -----------------------------------
def prepare_data():
    dl = DataLoader("assets.csv", "Date")
    dl.load_data()
    daily_returns = dl.generate_daily_returns()
    return dl.data, daily_returns


data, daily_returns = prepare_data()


# -----------------------------------
# App Initialization
# -----------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Momentum Strategy Dashboard"


# -----------------------------------
# Helper Functions
# -----------------------------------
def format_percent(x):
    return f"{x * 100:.2f}%"


def metric_card(title, value, positive_good=True):
    color = "success" if positive_good else "danger"

    return dbc.Card(
        dbc.CardBody([
            html.Div(title, className="text-muted small"),
            html.H4(value, className=f"text-{color} fw-bold")
        ]),
        className="shadow-sm mb-3"
    )


def strategy_metrics_section(strategy_name, metrics):
    return dbc.Card(
        dbc.CardBody([
            html.H4(strategy_name, className="mb-4"),

            dbc.Row([
                dbc.Col(metric_card("Total Return",
                                    format_percent(metrics["total_return"]),
                                    positive_good=metrics["total_return"] >= 0)),
                dbc.Col(metric_card("CAGR",
                                    format_percent(metrics["cagr"]),
                                    positive_good=metrics["cagr"] >= 0)),
                dbc.Col(metric_card("Volatility",
                                    format_percent(metrics["volatility"]),
                                    positive_good=False)),
                dbc.Col(metric_card("Max Drawdown",
                                    format_percent(metrics["max_drawdown"]),
                                    positive_good=False)),
            ])
        ]),
        className="shadow-sm mb-4"
    )


def create_portfolio_chart(values, strategy_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=values.index,
        y=values.values,
        mode="lines",
        line=dict(width=3)
    ))

    fig.update_layout(
        title=f"{strategy_name} – Portfolio Value",
        template="plotly_white",
        height=600,
        xaxis_title="Date",
        yaxis_title="Portfolio Value"
    )

    return fig


def create_momentum_heatmap(engine, lookback, strategy_name):
    momentum = engine.generate_momentum_score(lookback)

    momentum_monthly = momentum.groupby(momentum.index.to_period("M")).first()
    momentum_monthly.index = momentum_monthly.index.astype(str)

    top2_mask = momentum_monthly.apply(
        lambda row: row.nlargest(2).index.tolist(),
        axis=1
    )

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=momentum_monthly.T.values,
        x=momentum_monthly.index,
        y=momentum_monthly.columns,
        colorscale="RdYlGn",
        colorbar=dict(title=f"{lookback}D Momentum")
    ))

    for month in momentum_monthly.index:
        for asset in top2_mask.loc[month]:
            fig.add_trace(go.Scatter(
                x=[month],
                y=[asset],
                mode="markers",
                marker=dict(symbol="star", size=8, color="black"),
                showlegend=False
            ))

    fig.update_layout(
        title=f"{strategy_name} – Monthly Momentum Heatmap",
        template="plotly_white",
        height=500,
        xaxis_title="Month",
        yaxis_title="Asset"
    )

    return fig


def heatmap_legend_note():
    return html.Div(
        [
            html.Span("★ ", style={"fontSize": "16px", "fontWeight": "bold"}),
            html.Span(
                "Star marker indicates the Top-2 assets selected for portfolio allocation in that month."
            )
        ],
        style={
            "fontSize": "14px",
            "color": "#555",
            "marginTop": "8px",
            "marginBottom": "30px"
        }
    )


# -----------------------------------
# Layout
# -----------------------------------
app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(
            html.H2("Momentum Strategy Dashboard",
                    className="mt-4 mb-4"),
            width=9,
        ),
        dbc.Col(
            dbc.Switch(
                id="ai_toggle",
                label="AI Analysis",
                value=True,
                className="mt-4",
            ),
            width=3,
        )
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Strategy A Lookback"),
            dcc.Slider(id="lookback_A", min=10, max=180, step=5, value=30),
        ], width=6),

        dbc.Col([
            html.Label("Strategy B Lookback"),
            dcc.Slider(id="lookback_B", min=10, max=180, step=5, value=90),
        ], width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Initial Capital"),
            dcc.Input(id="initial_amount", type="number", value=100),
        ], width=4),
    ], className="mb-4"),

    dbc.Button("Run Backtest", id="run_button", color="primary"),

    html.Hr(),

    html.Div(id="strategy_A_section"),
    html.Hr(),
    html.Div(id="strategy_B_section"),

    html.Hr(),

    dbc.Card(
        dbc.CardBody(
            [html.H4("AI Analysis", className="mt-1 ml", style={"textAlign": "center"}),
             html.Hr(),
            html.Div(id="ai_output")]
        ),
        className="shadow-sm",
    )

], fluid=True)


# -----------------------------------
# Main Callback
# -----------------------------------
@app.callback(
    Output("strategy_A_section", "children"),
    Output("strategy_B_section", "children"),
    Output("ai_output", "children"),
    Input("run_button", "n_clicks"),
    State("lookback_A", "value"),
    State("lookback_B", "value"),
    State("initial_amount", "value"),
    State("ai_toggle", "value"),
)
def update_dashboard(n_clicks, lookback_A, lookback_B, initial_amount, ai_toggle):

    if not n_clicks:
        return "", "", ""

    engine_A = StrategyEngine(data, daily_returns)
    engine_B = StrategyEngine(data, daily_returns)

    metrics_A = engine_A.compute_strategy(lookback_A, initial_amount)
    metrics_B = engine_B.compute_strategy(lookback_B, initial_amount)

    portfolio_returns_A = engine_A.compute_portfolio_daily_returns(lookback_A)
    portfolio_returns_B = engine_B.compute_portfolio_daily_returns(lookback_B)

    value_A = engine_A.compute_cumulative_value(portfolio_returns_A, initial_amount)
    value_B = engine_B.compute_cumulative_value(portfolio_returns_B, initial_amount)

    section_A = dbc.Container([
        strategy_metrics_section("Strategy A", metrics_A),
        dcc.Graph(figure=create_portfolio_chart(value_A, "Strategy A")),
        dcc.Graph(figure=create_momentum_heatmap(engine_A, lookback_A, "Strategy A")),
        heatmap_legend_note(),
    ], fluid=True)

    section_B = dbc.Container([
        strategy_metrics_section("Strategy B", metrics_B),
        dcc.Graph(figure=create_portfolio_chart(value_B, "Strategy B")),
        dcc.Graph(figure=create_momentum_heatmap(engine_B, lookback_B, "Strategy B")),
        heatmap_legend_note(),
    ], fluid=True)

    if ai_toggle:
        analysis = get_ai_analysis(metrics_A, metrics_B)
        ai_content = dcc.Markdown(
            analysis,
            style={"whiteSpace": "pre-wrap"}
        )
    else:
        ai_content = html.Div(
            "AI analysis is disabled.",
            style={"color": "#888"}
        )

    return section_A, section_B, ai_content


if __name__ == "__main__":
    app.run(debug=True)