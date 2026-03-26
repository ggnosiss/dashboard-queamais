"""Gráficos de atribuição por canal de marketing."""
import plotly.graph_objects as go
from dash import dcc, html

CHANNEL_ORDER = [
    "paid_social", "paid_search", "organic_search",
    "direct", "whatsapp", "link_in_bio", "email_marketing", "other",
]


def build_attribution_bar(channels: list[dict]) -> dcc.Graph:
    """Barras horizontais: reservas por canal com taxa de conversão."""
    # Ordenar por reservas desc
    sorted_ch = sorted(
        [c for c in channels if c.get("sessions", 0) > 0 or c.get("reservations", 0) > 0],
        key=lambda x: x.get("reservations", 0), reverse=True,
    )

    if not sorted_ch:
        return _empty_chart("Sem dados de GA4 ainda — configure o Property ID")

    labels = [c["label"] for c in sorted_ch]
    reservations = [c.get("reservations", 0) for c in sorted_ch]
    sessions = [c.get("sessions", 0) for c in sorted_ch]
    colors = [c.get("color", "#475569") for c in sorted_ch]
    conv_rates = [
        f"{round(r/s*100,1)}% conv." if s > 0 else "—"
        for r, s in zip(reservations, sessions)
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=reservations,
        orientation="h",
        marker=dict(
            color=colors,
            opacity=0.85,
            line=dict(color="rgba(255,255,255,0.1)", width=0.5),
        ),
        text=[f"{r:,}  ({cr})".replace(",", ".") for r, cr in zip(reservations, conv_rates)],
        textposition="outside",
        textfont=dict(size=11, color="#94a3b8"),
        hovertemplate="<b>%{y}</b><br>Reservas: %{x}<br>Sessões: %{customdata}<extra></extra>",
        customdata=sessions,
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#DDD", family="Inter, sans-serif", size=11),
        margin=dict(l=10, r=80, t=20, b=20),
        height=max(220, len(sorted_ch) * 42),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#555", title="Reservas"),
        yaxis=dict(showgrid=False, color="#94a3b8"),
        showlegend=False,
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def build_channel_funnel(channels: list[dict]) -> dcc.Graph:
    """Gráfico de funil por canal: Sessões → Reservas → Revenue."""
    sorted_ch = sorted(
        [c for c in channels if c.get("sessions", 0) > 0],
        key=lambda x: x.get("sessions", 0), reverse=True,
    )[:6]  # top 6

    if not sorted_ch:
        return _empty_chart("Configure GA4 Property ID para ver o funil por canal")

    labels = [c["label"] for c in sorted_ch]
    colors = [c.get("color", "#475569") for c in sorted_ch]

    fig = go.Figure()

    # Sessões
    fig.add_trace(go.Bar(
        name="Sessões", x=labels,
        y=[c.get("sessions", 0) for c in sorted_ch],
        marker_color=[f"{col}55" for col in colors],
        marker_line=dict(color=colors, width=1.5),
    ))

    # Reservas
    fig.add_trace(go.Bar(
        name="Reservas", x=labels,
        y=[c.get("reservations", 0) for c in sorted_ch],
        marker_color=colors,
    ))

    fig.update_layout(
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#DDD", family="Inter, sans-serif", size=11),
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        margin=dict(l=10, r=10, t=36, b=50),
        height=260,
        xaxis=dict(showgrid=False, color="#555", tickangle=-20),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#555"),
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def build_spend_vs_reservations(channels: list[dict]) -> dcc.Graph:
    """Scatter: Investimento × Reservas por canal (eficiência)."""
    paid = [c for c in channels if c.get("ads_spend", 0) > 0]

    if not paid:
        return _empty_chart("Configure contas de Meta Ads / Google Ads para ver eficiência")

    fig = go.Figure()
    for c in paid:
        reservations = c.get("reservations", 0)
        spend = c.get("ads_spend", 0)
        cpa = round(spend / reservations, 2) if reservations > 0 else None
        fig.add_trace(go.Scatter(
            x=[spend], y=[reservations],
            mode="markers+text",
            name=c["label"],
            text=[c["label"]],
            textposition="top center",
            textfont=dict(size=10),
            marker=dict(
                size=max(16, min(48, reservations * 2 + 8)),
                color=c.get("color", "#475569"),
                opacity=0.8,
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            hovertemplate=(
                f"<b>{c['label']}</b><br>"
                f"Invest.: R$ {spend:,.0f}<br>"
                f"Reservas: {reservations}<br>"
                f"CPA: {'R$ ' + str(cpa) if cpa else '—'}<extra></extra>"
            ),
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#DDD", family="Inter, sans-serif", size=11),
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=40),
        height=260,
        xaxis=dict(title="Investimento (R$)", showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   color="#555", tickprefix="R$ "),
        yaxis=dict(title="Reservas", showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#555"),
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


def _empty_chart(msg: str) -> html.Div:
    return html.Div(
        msg,
        style={
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "height": "180px", "color": "#4a5568", "fontSize": "13px",
            "fontStyle": "italic", "textAlign": "center", "padding": "20px",
        }
    )
