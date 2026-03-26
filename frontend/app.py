import os
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from callbacks.filter_callbacks import register_filter_callbacks
from callbacks.dashboard_callbacks import register_dashboard_callbacks
from callbacks.auth_callbacks import register_auth_callbacks
from callbacks.admin_callbacks import register_admin_callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    title="Queamais — Dashboard",
    suppress_callback_exceptions=True,
)

# Layout raiz com roteamento por auth
app.layout = html.Div([
    dcc.Store(id="auth-token", storage_type="session"),
    dcc.Store(id="auth-user",  storage_type="session"),
    html.Div(id="page-content"),
])

register_auth_callbacks(app)
register_filter_callbacks(app)
register_dashboard_callbacks(app)
register_admin_callbacks(app)

if __name__ == "__main__":
    debug = os.getenv("DASH_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8050, debug=debug)
