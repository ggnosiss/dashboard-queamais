"""Callbacks do painel de admin: criar usuário, salvar permissões."""
import requests
import os
from dash import Input, Output, State, callback, ALL, ctx, no_update, html

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_admin_callbacks(app):

    # Mostrar/ocultar painel admin
    @app.callback(
        Output("admin-btn-container", "children"),
        Output("admin-panel-container", "children"),
        Input("dashboard-data", "data"),
        State("auth-token", "data"),
        State("auth-user", "data"),
        State("establishments-list", "data"),
    )
    def toggle_admin_elements(_, token, user_data, establishments):
        if not user_data or user_data.get("role") != "admin":
            return None, None

        from components.admin_panel import build_admin_panel
        btn = html.Button(
            "⚙ Usuários",
            id="btn-toggle-admin",
            n_clicks=0,
            style={
                "background": "rgba(168,85,247,0.15)", "border": "1px solid rgba(168,85,247,0.3)",
                "color": "#a855f7", "borderRadius": "6px", "padding": "7px 14px",
                "fontSize": "12px", "fontWeight": "600", "cursor": "pointer",
            }
        )
        panel = build_admin_panel(token or "", establishments or [])
        return btn, panel

    # Toggle visibilidade do painel
    @app.callback(
        Output("admin-panel-container", "style"),
        Input("btn-toggle-admin", "n_clicks"),
        State("admin-panel-container", "style"),
        prevent_initial_call=True,
    )
    def toggle_panel_visibility(n, current_style):
        if not current_style:
            return {"display": "block"}
        return {"display": "none"} if current_style.get("display") != "none" else {"display": "block"}

    # Mostrar/ocultar modal novo usuário
    @app.callback(
        Output("new-user-modal", "style"),
        Input("btn-new-user", "n_clicks"),
        Input("btn-cancel-user", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_modal(n_new, n_cancel):
        if ctx.triggered_id == "btn-new-user":
            return {"display": "block"}
        return {"display": "none"}

    # Criar novo usuário
    @app.callback(
        Output("new-user-error", "children"),
        Output("new-user-modal", "style", allow_duplicate=True),
        Input("btn-create-user", "n_clicks"),
        State("new-user-name", "value"),
        State("new-user-email", "value"),
        State("new-user-password", "value"),
        State("new-user-role", "value"),
        State("auth-token", "data"),
        prevent_initial_call=True,
    )
    def create_user(n, name, email, password, role, token):
        if not all([name, email, password, role]):
            return "Preencha todos os campos.", no_update
        try:
            r = requests.post(
                f"{API_URL}/auth/users",
                json={"name": name, "email": email, "password": password, "role": role},
                headers=_headers(token),
                timeout=8,
            )
            if r.status_code == 201:
                return "", {"display": "none"}
            return r.json().get("detail", "Erro ao criar usuário."), no_update
        except Exception:
            return "Erro de conexão.", no_update

    # Salvar permissões de casas por usuário
    @app.callback(
        Output("admin-save-result", "data"),
        Input({"type": "btn-save-est", "index": ALL}, "n_clicks"),
        State({"type": "user-est-select", "index": ALL}, "value"),
        State({"type": "btn-save-est", "index": ALL}, "id"),
        State("auth-token", "data"),
        prevent_initial_call=True,
    )
    def save_user_establishments(n_clicks_list, est_values, ids, token):
        if not any(n_clicks_list):
            return no_update
        triggered_idx = next(
            (i for i, n in enumerate(n_clicks_list) if n and n > 0), None
        )
        if triggered_idx is None:
            return no_update
        user_id = ids[triggered_idx]["index"]
        establishment_ids = est_values[triggered_idx] or []
        try:
            r = requests.put(
                f"{API_URL}/auth/users/{user_id}/establishments",
                json={"establishment_ids": establishment_ids},
                headers=_headers(token),
                timeout=8,
            )
            return {"ok": r.status_code == 200, "user_id": user_id}
        except Exception:
            return {"ok": False}
