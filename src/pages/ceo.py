from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from utils.graphs import fig_df_resg_seg, fig_df_week, fig_df_hm, fig_df_age_coupon, fig_df_ht, fig_df_d

layout = html.Div([
  #html.H3("Página CEO - Conteúdo vai aqui"),
  dcc.Graph(figure=fig_df_resg_seg),
  dcc.Graph(figure=fig_df_week),
  dcc.Graph(figure=fig_df_hm),
  dcc.Graph(figure=fig_df_age_coupon),
  dcc.Graph(figure=fig_df_ht),
  dcc.Graph(figure=fig_df_d),

])