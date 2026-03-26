"""Callbacks principais: busca dados e atualiza todos os componentes do dashboard."""
from datetime import date
from dash import Input, Output, State, callback, html, no_update
import requests
import os

from components.kpi_card import kpi_card
from components.funnel_chart import build_funnel_chart
from components.channel_chart import build_channel_chart
from components.trend_chart import build_trend_chart
from components.ranking_table import build_ranking_table

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _headers(token: str | None) -> dict:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _fmt_brl(v) -> str:
    if v is None:
        return "—"
    return f"R$ {float(v):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fetch_dashboard(establishment_ids, brands, start_date, end_date, token=None) -> dict | None:
    params = {"start_date": start_date, "end_date": end_date, "erp_months": 1}
    if establishment_ids:
        params["establishment_ids"] = establishment_ids
    if brands:
        params["brands"] = brands
    try:
        r = requests.get(
            f"{API_URL}/api/dashboard/combined",
            headers=_headers(token),
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"[dashboard] Erro ao buscar dados: {exc}")
        return None


def register_dashboard_callbacks(app):

    @app.callback(
        Output("dashboard-data", "data"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("establishment-filter", "value"),
        Input("brand-filter", "value"),
        Input("auto-refresh", "n_intervals"),
        State("auth-token", "data"),
    )
    def fetch_data(start_date, end_date, establishment_ids, brands, _, token):
        if not start_date or not end_date or not token:
            return None
        return _fetch_dashboard(establishment_ids or [], brands or [], start_date, end_date, token)

    @app.callback(
        Output("kpi-ads-row", "children"),
        Output("funnel-chart", "children"),
        Output("channel-chart", "children"),
        Output("trend-chart", "children"),
        Output("kpi-erp-row", "children"),
        Output("ranking-table", "children"),
        Input("dashboard-data", "data"),
    )
    def update_dashboard(data):
        if not data:
            empty = html.Div("Carregando...", style={"color": "#555", "padding": "40px", "textAlign": "center"})
            return empty, empty, empty, empty, empty, empty

        establishments = data.get("establishments", [])
        total_spend = data.get("total_spend", 0)
        total_imp = data.get("total_impressions", 0)
        total_clk = data.get("total_clicks", 0)
        total_fat = data.get("total_fat_salao")
        roas = data.get("blended_roas")

        ctr = round(total_clk / total_imp * 100, 2) if total_imp > 0 else None
        cpc = round(total_spend / total_clk, 2) if total_clk > 0 else None
        cpm = round(total_spend / total_imp * 1000, 2) if total_imp > 0 else None

        # KPIs Ads
        kpi_ads = [
            kpi_card("Invest. Total", _fmt_brl(total_spend), "Meta + Google", color="#EF5350"),
            kpi_card("Impressões", f"{total_imp:,}".replace(",", "."), "", color="#1E88E5"),
            kpi_card("Cliques", f"{total_clk:,}".replace(",", "."), "", color="#42A5F5"),
            kpi_card("CTR", f"{ctr:.2f}%" if ctr else "—", "cliques/impressões", color="#AB47BC"),
            kpi_card("CPC Médio", f"R$ {cpc:.2f}".replace(".", ",") if cpc else "—", "", color="#FFA726"),
            kpi_card("CPM", f"R$ {cpm:.2f}".replace(".", ",") if cpm else "—", "por mil impressões", color="#FF7043"),
            kpi_card("Sessões", "—", "GA4", color="#26C6DA", locked=True),
            kpi_card("Reservas", "—", "GA4", color="#66BB6A", locked=True),
        ]

        # Funil: usar dados do primeiro estabelecimento ou aggregado
        funnel_steps = [
            {"label": "Investimento (R$)", "value": total_spend, "available": True},
            {"label": "Impressões", "value": total_imp, "available": True},
            {"label": "Cliques", "value": total_clk, "available": True},
            {"label": "Sessões", "value": None, "available": False},
            {"label": "Reservas", "value": None, "available": False},
            {"label": "Fat. Salão (R$)", "value": total_fat, "available": total_fat is not None},
        ]
        funnel = build_funnel_chart(funnel_steps)

        # Canal
        channel = build_channel_chart(establishments)

        # Tendência: não temos dados diários ainda no endpoint combined — placeholder
        trend = build_trend_chart([], [], [])

        # KPIs ERP
        total_cmv = None
        total_cmo = None
        fat_vals = [e.get("fat_total") for e in establishments if e.get("fat_total")]
        fat_total_all = sum(fat_vals) if fat_vals else None

        kpi_erp = [
            html.H3(
                "Resultado (ERP)",
                style={"width": "100%", "fontSize": "11px", "color": "#555", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "0"},
            ),
            kpi_card("Fat. Total", _fmt_brl(fat_total_all), "realizado", color="#66BB6A"),
            kpi_card("Fat. Salão", _fmt_brl(total_fat), "realizado", color="#4CAF50"),
            kpi_card("ROAS", f"{roas:.2f}x" if roas else "—", "Fat.Salão / Invest.", color="#FFD54F"),
            kpi_card("CMV%", "—", "aguardando sync", color="#EF9A9A"),
            kpi_card("CMO%", "—", "aguardando sync", color="#FFCC80"),
        ]

        # Tabela
        table = build_ranking_table(establishments)

        return kpi_ads, funnel, channel, trend, kpi_erp, table

    @app.callback(
        Output("btn-sync", "children"),
        Input("btn-sync", "n_clicks"),
        prevent_initial_call=True,
    )
    def trigger_sync(n):
        try:
            requests.post(f"{API_URL}/api/erp/sync", headers=HEADERS, timeout=30)
            requests.post(f"{API_URL}/api/ads/sync", headers=HEADERS, timeout=60)
            return "✅ Sincronizado"
        except Exception:
            return "❌ Erro"
