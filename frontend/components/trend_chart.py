"""Gráfico de tendência: Investimento x Faturamento Salão ao longo do tempo."""
import plotly.graph_objects as go
from dash import dcc


def build_trend_chart(dates: list, spend_values: list, fat_values: list) -> dcc.Graph:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=spend_values,
        name="Investimento Ads",
        line=dict(color="#EF5350", width=2),
        fill="tozeroy",
        fillcolor="rgba(239,83,80,0.08)",
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=fat_values,
        name="Fat. Salão (ERP)",
        line=dict(color="#66BB6A", width=2),
        fill="tozeroy",
        fillcolor="rgba(102,187,106,0.08)",
        yaxis="y2",
    ))

    fig.update_layout(
        paper_bgcolor="#0D0D1A",
        plot_bgcolor="#131324",
        font=dict(color="#DDD", family="Inter, sans-serif"),
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=40, b=30),
        height=280,
        xaxis=dict(showgrid=False, color="#555"),
        yaxis=dict(
            title="Investimento (R$)",
            showgrid=True,
            gridcolor="#1F1F3A",
            color="#EF5350",
            tickprefix="R$ ",
        ),
        yaxis2=dict(
            title="Faturamento (R$)",
            overlaying="y",
            side="right",
            color="#66BB6A",
            tickprefix="R$ ",
            showgrid=False,
        ),
        hovermode="x unified",
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%"})
