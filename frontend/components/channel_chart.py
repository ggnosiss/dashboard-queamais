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
        marker_color="#1877F2",
        text=[f"R$ {v:,.0f}".replace(",", ".") for v in meta_vals],
        textposition="inside",
        textfont=dict(size=10),
    ))
    fig.add_trace(go.Bar(
        name="Google Ads",
        x=names, y=google_vals,
        marker_color="#EA4335",
        text=[f"R$ {v:,.0f}".replace(",", ".") for v in google_vals],
        textposition="inside",
        textfont=dict(size=10),
    ))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor="#0D0D1A",
        plot_bgcolor="#131324",
        font=dict(color="#DDD", family="Inter, sans-serif"),
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=40, b=50),
        height=280,
        xaxis=dict(showgrid=False, color="#555", tickangle=-30),
        yaxis=dict(showgrid=True, gridcolor="#1F1F3A", tickprefix="R$ ", color="#aaa"),
        title=dict(text="Investimento por Canal e Casa", font=dict(size=12, color="#aaa"), x=0.5),
    )

    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"width": "100%"})
