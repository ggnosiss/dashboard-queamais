"""Barra de navegação glassmorphism com logo, título e info do usuário."""
from dash import html
import os


def build_navbar(user_name: str = "", user_role: str = "", initials: str = "") -> html.Div:
    logo_src = "/assets/logo.svg"
    # Fallback para PNG se SVG não existir
    if not os.path.exists("assets/logo.svg") and os.path.exists("assets/logo.png"):
        logo_src = "/assets/logo.png"

    has_logo = os.path.exists("assets/logo.svg") or os.path.exists("assets/logo.png")

    logo_el = html.Img(src=logo_src, className="navbar-logo") if has_logo else None

    role_label = "Admin" if user_role == "admin" else "Gerente"
    badge_class = "navbar-badge admin" if user_role == "admin" else "navbar-badge"

    return html.Div(
        className="navbar-glass",
        children=[
            logo_el,
            html.H1("Dashboard de Marketing", className="navbar-title"),
            html.Span("Funil: Ads → Reserva → Faturamento", className="navbar-subtitle"),
            html.Div(className="navbar-spacer"),
            html.Div(
                className="navbar-user",
                children=[
                    html.Div(initials or (user_name[:2].upper() if user_name else "?"), className="navbar-avatar"),
                    html.Span(user_name or "Usuário", style={"fontSize": "12px"}),
                    html.Span(role_label, className=badge_class),
                    html.Button("Sair", id="btn-logout", className="btn-logout"),
                ],
            ),
        ],
    )
