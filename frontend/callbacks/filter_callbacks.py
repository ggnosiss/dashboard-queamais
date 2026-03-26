"""Callbacks dos filtros: atalhos de data, cascata marca→casa, carregamento inicial."""
from datetime import date, timedelta
from dash import Input, Output, State, callback, no_update
import requests
import os

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "change-me-before-deploy")
HEADERS = {"X-API-Key": API_KEY}


def _fetch_establishments() -> list[dict]:
    try:
        r = requests.get(f"{API_URL}/api/establishments/", headers=HEADERS, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def register_filter_callbacks(app):

    @app.callback(
        Output("establishments-list", "data"),
        Input("auto-refresh", "n_intervals"),
    )
    def load_establishments(_):
        return _fetch_establishments()

    @app.callback(
        Output("brand-filter", "options"),
        Input("establishments-list", "data"),
    )
    def update_brand_options(establishments):
        if not establishments:
            return []
        brands = sorted({e["brand"] for e in establishments})
        return [{"label": b, "value": b} for b in brands]

    @app.callback(
        Output("establishment-filter", "options"),
        Input("brand-filter", "value"),
        State("establishments-list", "data"),
    )
    def update_establishment_options(selected_brands, establishments):
        if not establishments:
            return []
        if selected_brands:
            filtered = [e for e in establishments if e["brand"] in selected_brands]
        else:
            filtered = establishments
        return [
            {"label": f"{e['sigla']} — {e['name']}", "value": e["id"]}
            for e in sorted(filtered, key=lambda x: x["name"])
        ]

    # Atalhos de data
    @app.callback(
        Output("date-range", "start_date"),
        Output("date-range", "end_date"),
        Input("btn-7d", "n_clicks"),
        Input("btn-30d", "n_clicks"),
        Input("btn-90d", "n_clicks"),
        Input("btn-12m", "n_clicks"),
        prevent_initial_call=True,
    )
    def apply_date_shortcut(n7, n30, n90, n12m):
        from dash import ctx
        end = date.today() - timedelta(days=1)
        deltas = {"btn-7d": 6, "btn-30d": 29, "btn-90d": 89, "btn-12m": 364}
        days = deltas.get(ctx.triggered_id, 29)
        return end - timedelta(days=days), end
