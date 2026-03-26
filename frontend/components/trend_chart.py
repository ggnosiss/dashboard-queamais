"""Gráfico de tendência: Investimento x Faturamento Salão ao longo do tempo."""
import plotly.graph_objects as go
from dash import dcc


def build_trend_chart(dates: list, spend_values: list, fat_values: list) -> dcc.Graph:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=spend_values,
        name="Investimento Ads",
        mode="lines",
        line=dict(color="#F97316", width=2.5, shape="spline", smoothing=1.3),
        fill="tozeroy",
        fillcolor="rgba(249,115,22,0.12)",
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=fat_values,
        name="Fat. Salão (ERP)",
        mode="lines",
        line=dict(color="rgba(255,255,255,0.55)", width=2, shape="spline", smoothing=1.3, dash="dot"),
        fill="tozeroy",
        fillcolor="rgba(255,255,255,0.04)",
        yaxis="y2",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=11),
        legend=dict(
            orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#94a3b8"),
        ),
        margin=dict(l=10, r=10, t=44, b=30),
        height=280,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color="#4a5568",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            color="#F97316",
            tickprefix="R$ ",
            tickfont=dict(size=10),
        ),
        yaxis2=dict(
            title="",
            overlaying="y",
            side="right",
            color="rgba(255,255,255,0.4)",
            tickprefix="R$ ",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=10),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,23,42,0.9)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(color="#eef2f7", size=12),
        ),
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%"})
