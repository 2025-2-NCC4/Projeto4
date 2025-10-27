from dash import Dash
import dash_bootstrap_components as dbc

# ==================== INICIALIZAR APP ====================
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],  # ✅ ESSENCIAL
    suppress_callback_exceptions=True
)
