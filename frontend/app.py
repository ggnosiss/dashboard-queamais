import os
import dash
import dash_bootstrap_components as dbc

from layout import build_layout
from callbacks.filter_callbacks import register_filter_callbacks
from callbacks.dashboard_callbacks import register_dashboard_callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
    ],
    title="Dashboard de Marketing",
    suppress_callback_exceptions=True,
)

app.layout = build_layout()

register_filter_callbacks(app)
register_dashboard_callbacks(app)

if __name__ == "__main__":
    debug = os.getenv("DASH_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8050, debug=debug)
