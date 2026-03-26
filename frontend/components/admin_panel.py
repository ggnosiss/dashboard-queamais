"""Painel de administração: gestão de usuários e permissões por casa."""
import requests
import os
from dash import html, dcc

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

BRAND_COLORS = {
    "Guacamole": "#22c55e",
    "Guacamole Taqueria": "#16a34a",
    "Didge": "#3b82f6",
    "Híbrida": "#f59e0b",
}


def build_admin_panel(token: str, establishments: list[dict]) -> html.Div:
    """Busca usuários e renderiza o painel de admin."""
    try:
        r = requests.get(
            f"{API_URL}/auth/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=8,
        )
        users = r.json() if r.status_code == 200 else []
    except Exception:
        users = []

    est_options = [
        {"label": f"{e['sigla']} — {e['name']}", "value": e["id"]}
        for e in sorted(establishments, key=lambda x: x["name"])
    ]

    user_rows = []
    for u in users:
        role_style = {
            "fontSize": "9px", "fontWeight": "700", "textTransform": "uppercase",
            "padding": "2px 8px", "borderRadius": "20px",
            "background": "rgba(168,85,247,0.2)", "color": "#a855f7",
            "border": "1px solid rgba(168,85,247,0.3)",
        } if u["role"] == "admin" else {
            "fontSize": "9px", "fontWeight": "700", "textTransform": "uppercase",
            "padding": "2px 8px", "borderRadius": "20px",
            "background": "rgba(59,130,246,0.2)", "color": "#3b82f6",
            "border": "1px solid rgba(59,130,246,0.3)",
        }

        est_chips = []
        for eid in u.get("establishment_ids", []):
            match = next((e for e in establishments if e["id"] == eid), None)
            if match:
                color = BRAND_COLORS.get(match["brand"], "#666")
                est_chips.append(
                    html.Span(match["sigla"], style={
                        "fontSize": "10px", "padding": "2px 7px", "borderRadius": "4px",
                        "background": f"{color}22", "color": color,
                        "border": f"1px solid {color}44", "marginRight": "4px",
                    })
                )

        user_rows.append(
            html.Div(
                className="user-row",
                children=[
                    html.Div(
                        (u["name"][:2]).upper(),
                        style={
                            "width": "32px", "height": "32px", "borderRadius": "50%",
                            "background": "#a855f7" if u["role"] == "admin" else "#3b82f6",
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "fontSize": "11px", "fontWeight": "700", "color": "#fff", "flexShrink": "0",
                        }
                    ),
                    html.Div([
                        html.Div([
                            html.Span(u["name"], style={"fontSize": "13px", "fontWeight": "600", "marginRight": "8px"}),
                            html.Span(u["role"].upper(), style=role_style),
                            html.Span(" ●", style={"color": "#22c55e" if u["is_active"] else "#ef4444", "fontSize": "10px", "marginLeft": "6px"}),
                        ]),
                        html.Div(u["email"], style={"fontSize": "11px", "color": "#64748b"}),
                    ], style={"flex": "1"}),
                    html.Div(est_chips or [html.Span("Todas as casas", style={"fontSize": "11px", "color": "#64748b"})],
                             style={"display": "flex", "flexWrap": "wrap", "gap": "4px", "flex": "2"}),
                    # Seletor de casas (apenas para gerentes)
                    html.Div([
                        dcc.Dropdown(
                            id={"type": "user-est-select", "index": u["id"]},
                            options=est_options,
                            value=u.get("establishment_ids", []),
                            multi=True,
                            placeholder="Selecionar casas...",
                            style={"minWidth": "220px", "fontSize": "11px"},
                            className="dark-dropdown",
                        ) if u["role"] != "admin" else None,
                        html.Button(
                            "Salvar",
                            id={"type": "btn-save-est", "index": u["id"]},
                            n_clicks=0,
                            style={
                                "fontSize": "11px", "padding": "5px 12px", "marginLeft": "6px",
                                "background": "rgba(34,197,94,0.15)", "border": "1px solid rgba(34,197,94,0.3)",
                                "color": "#22c55e", "borderRadius": "6px", "cursor": "pointer",
                            }
                        ) if u["role"] != "admin" else None,
                    ], style={"display": "flex", "alignItems": "center"}),
                ],
            )
        )

    return html.Div(
        className="admin-panel",
        children=[
            html.Div(
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "16px"},
                children=[
                    html.H3("Gerenciamento de Usuários", style={"margin": 0, "fontSize": "14px", "fontWeight": "700"}),
                    html.Button(
                        "+ Novo Usuário",
                        id="btn-new-user",
                        n_clicks=0,
                        style={
                            "background": "rgba(59,130,246,0.15)", "border": "1px solid rgba(59,130,246,0.3)",
                            "color": "#3b82f6", "borderRadius": "8px", "padding": "7px 16px",
                            "fontSize": "12px", "fontWeight": "600", "cursor": "pointer",
                        }
                    ),
                ]
            ),
            html.Div(user_rows),

            # Modal novo usuário
            html.Div(
                id="new-user-modal",
                style={"display": "none"},
                children=[
                    html.Div(
                        style={
                            "position": "fixed", "top": 0, "left": 0, "right": 0, "bottom": 0,
                            "background": "rgba(0,0,0,0.7)", "zIndex": 200,
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                        },
                        children=[
                            html.Div(
                                className="login-card",
                                style={"maxWidth": "400px", "padding": "28px"},
                                children=[
                                    html.H3("Novo Usuário", style={"margin": "0 0 16px", "fontSize": "15px"}),
                                    dcc.Input(id="new-user-name", placeholder="Nome completo", className="login-input"),
                                    dcc.Input(id="new-user-email", placeholder="E-mail", type="email", className="login-input"),
                                    dcc.Input(id="new-user-password", placeholder="Senha temporária", type="password", className="login-input"),
                                    dcc.Dropdown(
                                        id="new-user-role",
                                        options=[{"label": "Gerente", "value": "manager"}, {"label": "Admin", "value": "admin"}],
                                        value="manager",
                                        clearable=False,
                                        className="dark-dropdown",
                                        style={"marginBottom": "12px"},
                                    ),
                                    html.Div(
                                        style={"display": "flex", "gap": "8px"},
                                        children=[
                                            html.Button("Criar", id="btn-create-user", n_clicks=0, className="btn-login",
                                                        style={"width": "auto", "flex": "1"}),
                                            html.Button("Cancelar", id="btn-cancel-user", n_clicks=0,
                                                        style={"flex": "1", "background": "transparent", "border": "1px solid #333",
                                                               "color": "#888", "borderRadius": "8px", "cursor": "pointer"}),
                                        ]
                                    ),
                                    html.Div(id="new-user-error", className="login-error"),
                                ]
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="admin-save-result"),
        ]
    )
