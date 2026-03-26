"""KPI card glassmorphism com acento colorido, delta e estado locked."""
from dash import html


BRAND_COLORS = {
    "Guacamole": "#22c55e",
    "Guacamole Taqueria": "#16a34a",
    "Didge": "#3b82f6",
    "Híbrida": "#f59e0b",
}

ACCENT_COLORS = {
    "blue":   "#3b82f6",
    "green":  "#22c55e",
    "red":    "#ef4444",
    "amber":  "#f59e0b",
    "purple": "#a855f7",
    "cyan":   "#06b6d4",
    "orange": "#f97316",
}


def kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    color: str = "#3b82f6",
    locked: bool = False,
    delta: str | None = None,       # ex: "+12%" ou "-3.2%"
    delta_positive: bool | None = None,  # True=verde, False=vermelho, None=neutro
) -> html.Div:

    # Classe de delta
    if delta is not None:
        if delta_positive is True:
            delta_class = "kpi-delta up"
            delta_arrow = "↑"
        elif delta_positive is False:
            delta_class = "kpi-delta down"
            delta_arrow = "↓"
        else:
            delta_class = "kpi-delta neutral"
            delta_arrow = "→"
        delta_el = html.Div(
            [html.Span(delta_arrow), html.Span(f" {delta} vs período anterior")],
            className=delta_class,
        )
    else:
        delta_el = html.Div(subtitle, className="kpi-subtitle") if subtitle else None

    card_class = "kpi-card locked" if locked else "kpi-card"

    return html.Div(
        className=card_class,
        style={"--card-accent": color},
        children=[
            html.Div(
                [
                    html.Span(title, className="kpi-label"),
                    html.Span(" 🔒", style={"fontSize": "9px", "color": "#444"}) if locked else None,
                ],
                className="kpi-label",
            ),
            html.Div(value if not locked else "—", className="kpi-value",
                     style={"color": color if not locked else "#333"}),
            delta_el,
        ],
    )
