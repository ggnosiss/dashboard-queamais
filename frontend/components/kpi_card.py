"""Componente reutilizável de KPI card."""
from dash import html


BRAND_COLORS = {
    "Guacamole": "#2E7D32",
    "Guacamole Taqueria": "#43A047",
    "Didge": "#1565C0",
    "Híbrida": "#E65100",
}


def kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    color: str = "#1E88E5",
    locked: bool = False,
    icon: str = "",
) -> html.Div:
    lock_badge = (
        html.Span("🔒 Em breve", style={"fontSize": "10px", "color": "#888", "marginLeft": "6px"})
        if locked
        else None
    )
    return html.Div(
        className="kpi-card",
        style={
            "background": "#1E1E2E" if not locked else "#14141F",
            "border": f"1px solid {color}44",
            "borderRadius": "8px",
            "padding": "16px 20px",
            "minWidth": "160px",
            "flex": "1",
            "opacity": "0.5" if locked else "1",
        },
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "marginBottom": "4px"},
                children=[
                    html.Span(icon + " " if icon else "", style={"marginRight": "4px"}),
                    html.Span(title, style={"fontSize": "12px", "color": "#aaa", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
                    lock_badge,
                ],
            ),
            html.Div(
                value,
                style={"fontSize": "24px", "fontWeight": "700", "color": color if not locked else "#555"},
            ),
            html.Div(subtitle, style={"fontSize": "11px", "color": "#666", "marginTop": "2px"}),
        ],
    )
