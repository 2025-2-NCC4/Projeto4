from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from utils.graphs import fig_df_seg, fig_df_scatter, fig_df_mean, fig_df_v

layout = html.Div([
  html.H3("Página CFO - Conteúdo vai aqui"),
  dcc.Graph(figure=fig_df_seg),
  dcc.Graph(figure=fig_df_scatter),
  dcc.Graph(figure=fig_df_mean),
  dcc.Graph(figure=fig_df_v),
])