"""Gráfico de funil de marketing."""
import plotly.graph_objects as go
from dash import dcc


def build_funnel_chart(funnel_steps: list[dict]) -> dcc.Graph:
    """
    funnel_steps: lista de dicts com keys: label, value, available
    """
    labels = []
    values = []
    colors = []
    text = []

    COLOR_AVAILABLE = "rgba(249,115,22,0.75)"
    COLOR_LOCKED = "rgba(255,255,255,0.06)"

    for step in funnel_steps:
        labels.append(step["label"])
        available = step.get("available", True)
        val = step.get("value")

        if not available or val is None:
            values.append(0)
            colors.append(COLOR_LOCKED)
            text.append("🔒 Aguardando GA4")
        else:
            values.append(float(val))
            colors.append(COLOR_AVAILABLE)
            if isinstance(val, float) and val > 1000:
                text.append(f"R$ {val:,.0f}".replace(",", "."))
            else:
                text.append(f"{int(val):,}".replace(",", "."))

    fig = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            textinfo="text+percent previous",
            text=text,
            marker=dict(color=colors),
            connector=dict(line=dict(color="#333", width=1)),
            opacity=0.9,
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=11),
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
        title=dict(
            text="Funil: Investimento → Reserva → Faturamento",
            font=dict(size=12, color="#4a5568"),
            x=0.5,
        ),
        hoverlabel=dict(
            bgcolor="rgba(15,23,42,0.9)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(color="#eef2f7", size=12),
        ),
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%"})
