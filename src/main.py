from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
import pages

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
    return pages.ceo.layout
  elif pathname == '/cfo':
    return pages.cfo.layout
  else:
    return html.H3("Página Inicial - Conteúdo vai aqui")

app.run(debug=True)