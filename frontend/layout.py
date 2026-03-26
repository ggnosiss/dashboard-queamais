"""Layout principal do dashboard (pós-login)."""
from datetime import date, timedelta
from dash import html, dcc
from components.navbar import build_navbar


def build_dashboard_layout(user_name: str = "", user_role: str = "") -> html.Div:
    today = date.today()
    default_end = today - timedelta(days=1)
    default_start = default_end - timedelta(days=29)

    initials = "".join(p[0].upper() for p in user_name.split()[:2]) if user_name else "?"

    return html.Div(
        style={"minHeight": "100vh"},
        children=[
            # Navbar
            build_navbar(user_name=user_name, user_role=user_role, initials=initials),

            # Filtros
            html.Div(
                id="filters-bar",
                className="filters-bar",
                children=[
                    html.Div([
                        html.Label("Período", className="filter-label"),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=default_start,
                            end_date=default_end,
                            display_format="DD/MM/YYYY",
                            style={"fontSize": "12px"},
                        ),
                    ], className="filter-group"),

                    html.Div([
                        html.Label("Atalhos", className="filter-label"),
                        html.Div(
                            style={"display": "flex", "gap": "6px"},
                            children=[
                                html.Button("7d",  id="btn-7d",  n_clicks=0, className="date-shortcut"),
                                html.Button("30d", id="btn-30d", n_clicks=0, className="date-shortcut"),
                                html.Button("90d", id="btn-90d", n_clicks=0, className="date-shortcut"),
                                html.Button("12m", id="btn-12m", n_clicks=0, className="date-shortcut"),
                            ],
                        ),
                    ], className="filter-group"),

                    html.Div([
                        html.Label("Marca", className="filter-label"),
                        dcc.Dropdown(
                            id="brand-filter",
                            options=[],
                            multi=True,
                            placeholder="Todas as marcas",
                            style={"minWidth": "190px", "fontSize": "12px"},
                            className="dark-dropdown",
                        ),
                    ], className="filter-group"),

                    html.Div([
                        html.Label("Casa", className="filter-label"),
                        dcc.Dropdown(
                            id="establishment-filter",
                            options=[],
                            multi=True,
                            placeholder="Todas as casas",
                            style={"minWidth": "220px", "fontSize": "12px"},
                            className="dark-dropdown",
                        ),
                    ], className="filter-group"),

                    html.Div([
                        html.Label("\u00a0", className="filter-label"),
                        html.Button("↺ Sincronizar", id="btn-sync", n_clicks=0, className="btn-sync"),
                    ], className="filter-group"),

                    # Botão admin (só aparece para role=admin via callback)
                    html.Div(id="admin-btn-container"),
                ],
            ),

            # Conteúdo principal
            html.Div(
                style={"padding": "20px 28px", "display": "flex", "flexDirection": "column", "gap": "16px"},
                children=[

                    # KPIs Ads (topo do funil)
                    html.Div([
                        html.Div("Investimento & Alcance", className="section-header"),
                        html.Div(id="kpi-ads-row",
                                 style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                                 className="kpi-row"),
                    ]),

                    # Funil central
                    html.Div([
                        html.Div("Funil de Conversão", className="section-header"),
                        html.Div(id="funnel-chart", className="chart-container"),
                    ]),

                    # Gráficos lado a lado
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "16px",
                        },
                        className="charts-grid",
                        children=[
                            html.Div([
                                html.Div("Investimento por Canal", className="section-header"),
                                html.Div(id="channel-chart", className="chart-container"),
                            ]),
                            html.Div([
                                html.Div("Tendência: Ads × Faturamento", className="section-header"),
                                html.Div(id="trend-chart", className="chart-container"),
                            ]),
                        ],
                    ),

                    # Atribuição por Canal (GA4)
                    html.Div([
                        html.Div("Atribuição por Canal", className="section-header"),
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
                            className="charts-grid",
                            children=[
                                html.Div([
                                    html.Div("Reservas por Canal", style={"fontSize": "11px", "color": "#555", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "8px"}),
                                    html.Div(id="attribution-bar-chart", className="chart-container"),
                                ]),
                                html.Div([
                                    html.Div("Sessões × Reservas por Canal", style={"fontSize": "11px", "color": "#555", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "8px"}),
                                    html.Div(id="channel-funnel-chart", className="chart-container"),
                                ]),
                            ],
                        ),
                        html.Div(
                            style={"marginTop": "16px"},
                            children=[
                                html.Div("Eficiência: Investimento × Reservas (Canais Pagos)", style={"fontSize": "11px", "color": "#555", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "8px"}),
                                html.Div(id="spend-vs-reservations-chart", className="chart-container"),
                            ],
                        ),
                    ]),

                    # KPIs ERP + Performance
                    html.Div([
                        html.Div("Resultado & Eficiência", className="section-header"),
                        html.Div(id="kpi-erp-row",
                                 style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                                 className="kpi-row"),
                    ]),

                    # Tabela ranking
                    html.Div([
                        html.Div("Ranking por Casa", className="section-header"),
                        html.Div(id="ranking-table", className="ranking-table"),
                    ]),
                ],
            ),

            # Painel admin (oculto por padrão)
            html.Div(id="admin-panel-container"),

            # Stores e timers
            dcc.Store(id="dashboard-data"),
            dcc.Store(id="attribution-data"),
            dcc.Store(id="establishments-list"),
            dcc.Interval(id="auto-refresh", interval=5 * 60 * 1000, n_intervals=0),
        ],
    )
