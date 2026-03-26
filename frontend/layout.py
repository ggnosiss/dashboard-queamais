"""Layout principal do dashboard."""
from datetime import date, timedelta
from dash import html, dcc
import dash_bootstrap_components as dbc


def build_layout() -> html.Div:
    today = date.today()
    default_end = today - timedelta(days=1)
    default_start = default_end - timedelta(days=29)

    return html.Div(
        style={"backgroundColor": "#0A0A14", "minHeight": "100vh", "fontFamily": "Inter, sans-serif", "color": "#DDD"},
        children=[
            # Header
            html.Div(
                style={"borderBottom": "1px solid #1F1F3A", "padding": "16px 28px", "display": "flex", "alignItems": "center", "gap": "16px"},
                children=[
                    html.H1("Dashboard de Marketing", style={"fontSize": "18px", "fontWeight": "700", "color": "#fff", "margin": 0}),
                    html.Span("Funil: Ads → Reserva → Faturamento", style={"fontSize": "12px", "color": "#666"}),
                ],
            ),

            # Filtros
            html.Div(
                id="filters-bar",
                style={"padding": "16px 28px", "display": "flex", "gap": "16px", "flexWrap": "wrap", "alignItems": "flex-end", "borderBottom": "1px solid #1A1A2E"},
                children=[
                    html.Div([
                        html.Label("Período", style={"fontSize": "11px", "color": "#888", "display": "block", "marginBottom": "4px"}),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=default_start,
                            end_date=default_end,
                            display_format="DD/MM/YYYY",
                            style={"fontSize": "13px"},
                        ),
                    ]),
                    html.Div([
                        html.Label("Atalhos", style={"fontSize": "11px", "color": "#888", "display": "block", "marginBottom": "4px"}),
                        html.Div(
                            style={"display": "flex", "gap": "6px"},
                            children=[
                                html.Button("7d", id="btn-7d", n_clicks=0, className="date-shortcut"),
                                html.Button("30d", id="btn-30d", n_clicks=0, className="date-shortcut"),
                                html.Button("90d", id="btn-90d", n_clicks=0, className="date-shortcut"),
                                html.Button("12m", id="btn-12m", n_clicks=0, className="date-shortcut"),
                            ],
                        ),
                    ]),
                    html.Div([
                        html.Label("Marca", style={"fontSize": "11px", "color": "#888", "display": "block", "marginBottom": "4px"}),
                        dcc.Dropdown(
                            id="brand-filter",
                            options=[],  # populado pelo callback
                            multi=True,
                            placeholder="Todas as marcas",
                            style={"minWidth": "200px", "fontSize": "13px"},
                            className="dark-dropdown",
                        ),
                    ]),
                    html.Div([
                        html.Label("Casa", style={"fontSize": "11px", "color": "#888", "display": "block", "marginBottom": "4px"}),
                        dcc.Dropdown(
                            id="establishment-filter",
                            options=[],  # populado pelo callback (cascata de marca)
                            multi=True,
                            placeholder="Todas as casas",
                            style={"minWidth": "240px", "fontSize": "13px"},
                            className="dark-dropdown",
                        ),
                    ]),
                    html.Div([
                        html.Button(
                            "🔄 Sincronizar",
                            id="btn-sync",
                            n_clicks=0,
                            style={"padding": "8px 16px", "background": "#1E88E5", "color": "#fff", "border": "none", "borderRadius": "6px", "cursor": "pointer", "fontSize": "13px"},
                        ),
                    ]),
                ],
            ),

            # KPIs de Ads (topo do funil)
            html.Div(
                id="kpi-ads-row",
                style={"padding": "20px 28px 0", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
            ),

            # Funil central
            html.Div(
                style={"padding": "20px 28px 0"},
                children=[html.Div(id="funnel-chart")],
            ),

            # Gráficos lado a lado
            html.Div(
                style={"padding": "16px 28px 0", "display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
                children=[
                    html.Div(id="channel-chart"),
                    html.Div(id="trend-chart"),
                ],
            ),

            # KPIs de resultado ERP
            html.Div(
                id="kpi-erp-row",
                style={"padding": "16px 28px 0", "display": "flex", "gap": "12px", "flexWrap": "wrap"},
            ),

            # Tabela ranking
            html.Div(
                style={"padding": "16px 28px 28px"},
                children=[
                    html.H3("Ranking por Casa", style={"fontSize": "13px", "color": "#888", "marginBottom": "8px", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                    html.Div(id="ranking-table"),
                ],
            ),

            # Dados internos (store)
            dcc.Store(id="dashboard-data"),
            dcc.Store(id="establishments-list"),

            # Intervalo de refresh (a cada 5 minutos)
            dcc.Interval(id="auto-refresh", interval=5 * 60 * 1000, n_intervals=0),
        ],
    )
