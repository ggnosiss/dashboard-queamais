"""Gráfico de investimento por canal (Meta Ads vs Google Ads)."""
import plotly.graph_objects as go
from dash import dcc


def build_channel_chart(establishments: list[dict]) -> dcc.Graph:
    """
    establishments: lista de dicts com establishment_name, meta_spend, google_spend
    """
    names = [e["sigla"] for e in establishments]
    meta_vals = [e.get("meta_spend", 0) for e in establishments]
    google_vals = [e.get("google_spend", 0) for e in establishments]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Meta Ads",
        x=names, y=meta_vals,
        marker=dict(
            color="rgba(59,130,246,0.75)",
            line=dict(color="rgba(59,130,246,0.9)", width=1),
        ),
        text=[f"R$ {v:,.0f}".replace(",", ".") for v in meta_vals],
        textposition="inside",
        textfont=dict(size=9, color="rgba(255,255,255,0.7)"),
    ))
    fig.add_trace(go.Bar(
        name="Google Ads",
        x=names, y=google_vals,
        marker=dict(
            color="rgba(249,115,22,0.75)",
            line=dict(color="rgba(249,115,22,0.9)", width=1),
        ),
        text=[f"R$ {v:,.0f}".replace(",", ".") for v in google_vals],
        textposition="inside",
        textfont=dict(size=9, color="rgba(255,255,255,0.7)"),
    ))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter, sans-serif", size=11),
        legend=dict(
            orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#94a3b8"),
        ),
        margin=dict(l=10, r=10, t=44, b=50),
        height=280,
        xaxis=dict(
            showgrid=False, zeroline=False,
            color="#4a5568", tickangle=-30,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            zeroline=False, tickprefix="R$ ",
            color="#4a5568", tickfont=dict(size=10),
        ),
        bargap=0.25,
        hoverlabel=dict(
            bgcolor="rgba(15,23,42,0.9)",
            bordercolor="rgba(255,255,255,0.1)",
            font=dict(color="#eef2f7", size=12),
        ),
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%"})
