from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app

navbar = dbc.NavbarSimple(
  children=[
    dbc.NavItem(dbc.NavLink("CEO", href="/ceo")),
    dbc.NavItem(dbc.NavLink("CFO", href="/cfo")), 
  ],
  brand="Projeto Dash - PI4",
  brand_href="/",
  color="primary",
  dark=True,
  fluid=True,
  className="mb-4 w-100"
)

app.layout = html.Div([
  dcc.Location(id='url', refresh=False),
  navbar,
  html.Div(id='page-content')
])

@app.callback(
  Output('page-content', 'children'),
  Input('url', 'pathname')
)
def display_page(pathname):
  if pathname == '/ceo':
    #from ceo import layout as ceo_layout
    #return ceo_layout
    return html.H3("Página CEO - Conteúdo vai aqui")
  elif pathname == '/cfo':
    #from cfo import layout as cfo_layout
    #return cfo_layout
    return html.H3("Página CFO - Conteúdo vai aqui")
  else:
    return html.H3("Página Inicial - Conteúdo vai aqui")

app.run(debug=True)