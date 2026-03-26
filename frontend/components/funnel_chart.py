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

    COLOR_AVAILABLE = "#1E88E5"
    COLOR_LOCKED = "#333355"

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
        paper_bgcolor="#0D0D1A",
        plot_bgcolor="#0D0D1A",
        font=dict(color="#DDD", family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
        title=dict(text="Funil: Investimento → Reserva → Faturamento", font=dict(size=13, color="#aaa"), x=0.5),
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%"})
