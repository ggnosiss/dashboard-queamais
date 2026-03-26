"""Callbacks de autenticação: login, logout, roteamento por role."""
import requests
import os
from dash import Input, Output, State, callback, no_update, html, dcc

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def register_auth_callbacks(app):

    @app.callback(
        Output("auth-token", "data"),
        Output("auth-user", "data"),
        Output("login-error", "children"),
        Input("btn-login", "n_clicks"),
        State("login-email", "value"),
        State("login-password", "value"),
        prevent_initial_call=True,
    )
    def do_login(n_clicks, email, password):
        if not email or not password:
            return no_update, no_update, "Preencha e-mail e senha."
        try:
            r = requests.post(
                f"{API_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=8,
            )
            if r.status_code == 200:
                data = r.json()
                return data["access_token"], {
                    "name": data["name"],
                    "role": data["role"],
                    "user_id": data["user_id"],
                }, ""
            return no_update, no_update, "E-mail ou senha incorretos."
        except Exception:
            return no_update, no_update, "Erro ao conectar com o servidor."

    @app.callback(
        Output("auth-token", "data", allow_duplicate=True),
        Output("auth-user", "data", allow_duplicate=True),
        Input("btn-logout", "n_clicks"),
        prevent_initial_call=True,
    )
    def do_logout(n_clicks):
        return None, None

    @app.callback(
        Output("page-content", "children"),
        Input("auth-token", "data"),
        State("auth-user", "data"),
    )
    def route_page(token, user_data):
        from pages.login import build_login_layout
        from layout import build_dashboard_layout

        if not token or not user_data:
            return build_login_layout()
        return build_dashboard_layout(
            user_name=user_data.get("name", ""),
            user_role=user_data.get("role", ""),
        )
