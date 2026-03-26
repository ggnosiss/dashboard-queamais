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
from components.attribution_chart import (
    build_attribution_bar,
    build_channel_funnel,
    build_spend_vs_reservations,
)

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


def _fetch_attribution(establishment_ids, brands, start_date, end_date, token=None) -> list | None:
    params = {"start_date": start_date, "end_date": end_date}
    if establishment_ids:
        params["establishment_ids"] = establishment_ids
    if brands:
        params["brands"] = brands
    try:
        r = requests.get(
            f"{API_URL}/api/ga4/attribution",
            headers=_headers(token),
            params=params,
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"[attribution] Erro ao buscar dados GA4: {exc}")
        return None


def _aggregate_channels(attribution_list: list) -> list[dict]:
    """Agrega canais de múltiplos estabelecimentos em uma lista única."""
    merged: dict[str, dict] = {}
    for est in attribution_list:
        for ch in est.get("channels", []):
            key = ch["channel"]
            if key not in merged:
                merged[key] = {
                    "channel": key,
                    "label": ch["label"],
                    "color": ch["color"],
                    "sessions": 0,
                    "reservations": 0,
                    "reservation_value": 0.0,
                    "ads_spend": 0.0,
                }
            merged[key]["sessions"] += ch.get("sessions", 0)
            merged[key]["reservations"] += ch.get("reservations", 0)
            merged[key]["reservation_value"] += ch.get("reservation_value", 0.0)
            merged[key]["ads_spend"] += ch.get("ads_spend", 0.0)
    return list(merged.values())


def register_dashboard_callbacks(app):

    @app.callback(
        Output("dashboard-data", "data"),
        Output("attribution-data", "data"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("establishment-filter", "value"),
        Input("brand-filter", "value"),
        Input("auto-refresh", "n_intervals"),
        State("auth-token", "data"),
    )
    def fetch_data(start_date, end_date, establishment_ids, brands, _, token):
        if not start_date or not end_date or not token:
            return None, None
        ids = establishment_ids or []
        brs = brands or []
        dashboard = _fetch_dashboard(ids, brs, start_date, end_date, token)
        attribution = _fetch_attribution(ids, brs, start_date, end_date, token)
        return dashboard, attribution

    @app.callback(
        Output("kpi-ads-row", "children"),
        Output("funnel-chart", "children"),
        Output("channel-chart", "children"),
        Output("trend-chart", "children"),
        Output("kpi-erp-row", "children"),
        Output("ranking-table", "children"),
        Input("dashboard-data", "data"),
        Input("attribution-data", "data"),
    )
    def update_dashboard(data, attribution):
        empty = html.Div("Carregando...", style={"color": "#555", "padding": "40px", "textAlign": "center"})
        if not data:
            return empty, empty, empty, empty, empty, empty

        establishments = data.get("establishments", [])
        total_spend = data.get("total_spend", 0)
        total_imp = data.get("total_impressions", 0)
        total_clk = data.get("total_clicks", 0)
        total_fat_salao = data.get("total_fat_salao")
        roas = data.get("blended_roas")

        ctr = round(total_clk / total_imp * 100, 2) if total_imp > 0 else None
        cpc = round(total_spend / total_clk, 2) if total_clk > 0 else None

        # Dados de atribuição GA4 (agregados)
        total_sessions = 0
        total_reservations = 0
        fat_total_all = None
        conv_rate = None
        overall_cpa = None
        overall_roas = None

        if attribution:
            total_sessions = sum(e.get("total_sessions", 0) for e in attribution)
            total_reservations = sum(e.get("total_reservations", 0) for e in attribution)
            fat_vals = [e.get("fat_total") for e in attribution if e.get("fat_total")]
            fat_total_all = sum(fat_vals) if fat_vals else None
            if total_sessions > 0:
                conv_rate = round(total_reservations / total_sessions * 100, 2)
            if total_spend > 0 and total_reservations > 0:
                overall_cpa = round(total_spend / total_reservations, 2)
            if total_spend > 0 and fat_total_all:
                overall_roas = round(fat_total_all / total_spend, 2)

        # KPIs Ads (topo do funil)
        kpi_ads = [
            kpi_card("Invest. Total", _fmt_brl(total_spend), "Meta + Google", color="#EF5350"),
            kpi_card("Impressões", f"{total_imp:,}".replace(",", "."), "", color="#1E88E5"),
            kpi_card("Cliques", f"{total_clk:,}".replace(",", "."), "", color="#42A5F5"),
            kpi_card("CTR", f"{ctr:.2f}%" if ctr else "—", "cliques/impressões", color="#AB47BC"),
            kpi_card("CPC Médio", f"R$ {cpc:.2f}".replace(".", ",") if cpc else "—", "", color="#FFA726"),
            kpi_card("Sessões", f"{total_sessions:,}".replace(",", ".") if total_sessions else "—", "GA4", color="#26C6DA"),
            kpi_card("Reservas", f"{total_reservations:,}".replace(",", ".") if total_reservations else "—", "GA4", color="#66BB6A"),
            kpi_card("Conv. Rate", f"{conv_rate:.1f}%" if conv_rate else "—", "reservas/sessões", color="#A5D6A7"),
        ]

        # Funil: completo com dados GA4
        funnel_steps = [
            {"label": "Impressões", "value": total_imp, "available": True},
            {"label": "Cliques", "value": total_clk, "available": True},
            {"label": "Sessões", "value": total_sessions if total_sessions else None, "available": total_sessions > 0},
            {"label": "Reservas", "value": total_reservations if total_reservations else None, "available": total_reservations > 0},
            {"label": "Fat. Total (R$)", "value": fat_total_all, "available": fat_total_all is not None},
        ]
        funnel = build_funnel_chart(funnel_steps)

        # Canal (investimento por canal de mídia paga)
        channel = build_channel_chart(establishments)

        # Tendência
        trend = build_trend_chart([], [], [])

        # KPIs ERP + Performance
        kpi_erp = [
            kpi_card("Fat. Total", _fmt_brl(fat_total_all), "ERP realizado", color="#66BB6A"),
            kpi_card("Fat. Salão", _fmt_brl(total_fat_salao), "ERP realizado", color="#4CAF50"),
            kpi_card("ROAS", f"{overall_roas:.2f}x" if overall_roas else "—", "Fat.Total / Invest.", color="#FFD54F"),
            kpi_card("CPA", _fmt_brl(overall_cpa), "custo por reserva", color="#FFA726"),
        ]

        # Tabela ranking com dados de atribuição
        table = build_ranking_table(establishments, attribution or [])

        return kpi_ads, funnel, channel, trend, kpi_erp, table

    @app.callback(
        Output("attribution-bar-chart", "children"),
        Output("channel-funnel-chart", "children"),
        Output("spend-vs-reservations-chart", "children"),
        Input("attribution-data", "data"),
    )
    def update_attribution_charts(attribution):
        empty = html.Div("Aguardando dados GA4...", style={"color": "#4a5568", "padding": "30px", "textAlign": "center", "fontStyle": "italic"})
        if not attribution:
            return empty, empty, empty

        channels = _aggregate_channels(attribution)
        return (
            build_attribution_bar(channels),
            build_channel_funnel(channels),
            build_spend_vs_reservations(channels),
        )

    @app.callback(
        Output("btn-sync", "children"),
        Input("btn-sync", "n_clicks"),
        State("auth-token", "data"),
        prevent_initial_call=True,
    )
    def trigger_sync(n, token):
        headers = _headers(token)
        try:
            requests.post(f"{API_URL}/api/erp/sync", headers=headers, timeout=30)
            requests.post(f"{API_URL}/api/ads/sync", headers=headers, timeout=60)
            requests.post(f"{API_URL}/api/ga4/sync", headers=headers, timeout=60)
            return "✅ Sincronizado"
        except Exception:
            return "❌ Erro"
