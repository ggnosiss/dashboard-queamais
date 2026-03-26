"""Tela de login glassmorphism."""
from dash import html, dcc
import os


def build_login_layout() -> html.Div:
    has_logo = os.path.exists("assets/logo.svg") or os.path.exists("assets/logo.png")
    logo_src = "/assets/logo.svg" if os.path.exists("assets/logo.svg") else "/assets/logo.png"

    return html.Div(
        className="login-page",
        children=[
            html.Div(
                className="login-card",
                children=[
                    html.Img(src=logo_src, className="login-logo") if has_logo else None,
                    html.H2("Queamais", className="login-title"),
                    html.P("Dashboard de Marketing", className="login-subtitle"),

                    html.Div([
                        html.Label("E-mail", className="filter-label", style={"marginBottom": "4px", "display": "block"}),
                        dcc.Input(
                            id="login-email",
                            type="email",
                            placeholder="seu@email.com",
                            className="login-input",
                            debounce=False,
                            n_submit=0,
                        ),
                    ]),

                    html.Div([
                        html.Label("Senha", className="filter-label", style={"marginBottom": "4px", "display": "block"}),
                        dcc.Input(
                            id="login-password",
                            type="password",
                            placeholder="••••••••",
                            className="login-input",
                            debounce=False,
                            n_submit=0,
                        ),
                    ]),

                    html.Button("Entrar", id="btn-login", n_clicks=0, className="btn-login"),
                    html.Div(id="login-error", className="login-error"),
                ],
            ),
        ],
    )
