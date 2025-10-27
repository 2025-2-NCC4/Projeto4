import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from app import app
from pages import ceo, cfo
import pandas as pd
from utils.db_utils import df_trans

# ==================== CONFIGURAÇÕES DE ESTILO ====================
COLORS = {
    'primary': '#351D5A',
    'secondary': '#6C757D',
    'dark': '#1a1a2e',
    'light': '#f8f9fa',
    'accent': '#7B68EE',
}

# ==================== LOGO E HEADER ====================
sidebar_header = html.Div([
    html.Div([
        html.Div([
            html.I(className="fas fa-chart-line fa-3x",
                   style={'color': COLORS['accent']}),
        ], style={'textAlign': 'center', 'marginBottom': '10px'}),
        html.H5("PICMONEY",
                style={'textAlign': 'center', 'letterSpacing': '2px', 'marginBottom': '5px'}),
        html.P("Analytics Dashboard",
               style={'textAlign': 'center', 'fontSize': '12px', 'opacity': '0.8', 'marginBottom': '0'}),
    ], style={'padding': '30px 20px', 'borderBottom': f'2px solid {COLORS["accent"]}', 'background': 'rgba(0,0,0,0.2)'}),
], style={'marginBottom': '20px'})

# ==================== MENU DE NAVEGAÇÃO ====================
def create_nav_item(label, href, icon, badge=None):
    item_content = [
        html.I(className=f"fas fa-{icon}",
               style={'width': '30px', 'fontSize': '18px', 'marginRight': '12px'}),
        html.Span(label, style={'fontSize': '15px', 'fontWeight': '500'}),
    ]
    if badge:
        item_content.append(
            dbc.Badge(badge, color="danger", className="ml-auto", pill=True)
        )
    return dbc.NavLink(
        item_content,
        href=href,
        active="exact",
        style={
            'borderRadius': '8px',
            'margin': '5px 15px',
            'padding': '12px 15px',
            'transition': 'all 0.3s ease',
            'display': 'flex',
            'alignItems': 'center',
        },
        className="sidebar-nav-item"
    )

nav_items = html.Div([
    html.P("NAVEGAÇÃO",
           style={'fontSize': '11px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.6', 'margin': '20px 15px 10px 15px'}),
    dbc.Nav([
        create_nav_item("Dashboard Geral", "/", "home"),
        create_nav_item("Visão CEO", "/ceo", "user-tie"),
        create_nav_item("Visão CFO", "/cfo", "hand-holding-usd"),
    ], vertical=True, pills=True),
], style={'marginBottom': '30px'})

# ==================== CÁLCULOS ====================
total_resgates = len(df_trans)
usuarios_unicos = df_trans['celular'].nunique()
valor_total_cupons = df_trans['valor_cupom'].sum()

# ==================== SEÇÃO DE ESTATÍSTICAS RÁPIDAS ====================
quick_stats = html.Div([
    html.P("RESUMO RÁPIDO",
           style={'fontSize': '11px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.6', 'margin': '20px 15px 15px 15px'}),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-users me-2", style={'color': COLORS['accent']}),
                        html.Div([
                            html.H5(f"{usuarios_unicos:,}", className="mb-0", style={'color': COLORS['light']}),
                            html.P("Usuários Únicos", style={'color': COLORS['light']})
                        ])
                    ], className="d-flex align-items-center")
                ]),
                className="mb-2 bg-transparent border-0"
            ),
            xs=12, sm=6, md=12, lg=12
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-ticket-alt me-2", style={'color': '#28a745'}),
                        html.Div([
                            html.H5(f"{total_resgates:,}", className="mb-0", style={'color': COLORS['light']}),
                            html.P("Total de Resgates", style={'color': COLORS['light']})
                        ])
                    ], className="d-flex align-items-center")
                ]),
                className="mb-2 bg-transparent border-0"
            ),
            xs=12, sm=6, md=12, lg=12
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-dollar-sign me-2", style={'color': '#ffc107'}),
                        html.Div([
                            html.H5(f"R$ {valor_total_cupons:,.0f}", className="mb-0", style={'color': COLORS['light']}),
                            html.P("Valor em Cupons", style={'color': COLORS['light']})
                        ])
                    ], className="d-flex align-items-center")
                ]),
                className="mb-2 bg-transparent border-0"
            ),
            xs=12, sm=12, md=12, lg=12
        ),
    ], className="px-2")
])


# ==================== SIDEBAR ====================
sidebar = dbc.Card(
    [
        sidebar_header,
        nav_items,
        quick_stats
    ],
    body=True,
    className="bg-dark text-white h-100 shadow-sm",
    style={"minHeight": "100vh", "borderRadius": "10px", "margin": "0", "padding": "10px", "boxSizing": "border-box", "position": "sticky", "top": "0"}
)


# ==================== BOTÃO MOBILE ====================
toggle_button = dbc.Button(
    html.I(className="fas fa-bars"),
    color="primary",
    className="mb-3 d-md-none",  # aparece só em telas pequenas
    id="toggle-btn"
)

# ==================== CONTEÚDO ====================
content = html.Div([
    toggle_button,
    html.Div(id="page-content")
])

# ==================== LAYOUT PRINCIPAL ====================
app.layout = dbc.Container(fluid=True, children=[
    dcc.Location(id="url"),
    dbc.Row([
        # SIDEBAR: ocupa 12 colunas no celular, 3 no md, 2 no lg
        dbc.Col(
            [
                sidebar
            ],
            id="sidebar-col",
            xs=12, sm=12, md=3, lg=2,
            className="d-none d-md-block p-0"  # começa escondida no mobile
        ),

        # CONTEÚDO PRINCIPAL
        dbc.Col(
            [
                dbc.Button(
                    html.I(className="fas fa-bars"),
                    color="primary",
                    id="toggle-btn",
                    className="mb-3 d-md-none"  # só aparece em telas pequenas
                ),
                html.Div(id="page-content", className="p-3 bg-light rounded-3 shadow-sm")
            ],
            xs=12, sm=12, md=9, lg=10,
            id="content-col"
        ),
    ], className="gx-0 gy-0 align-items-start")
])


# ==================== CALLBACK PARA TOGGLE MENU ====================
@app.callback(
    Output("sidebar-col", "className"),
    Input("toggle-btn", "n_clicks"),
    State("sidebar-col", "className"),
    prevent_initial_call=True
)
def toggle_sidebar(n, current_class):
    if current_class and "d-none" in current_class:
        # Mostrar sidebar em mobile
        return "d-block p-0 bg-dark"
    else:
        # Esconder sidebar em mobile novamente
        return "d-none d-md-block p-0 bg-dark"


# ==================== CALLBACK DE PÁGINAS ====================
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([
            html.H1("Bem-vindo ao Dashboard PicMoney!", style={'color': COLORS['primary']}),
            html.P("Selecione uma opção no menu lateral para começar.", className="lead text-muted"),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-user-tie fa-3x mb-3", style={'color': COLORS['primary']}),
                            html.H4("Visão CEO"),
                            html.P("Análise estratégica de resgates e comportamento de usuários"),
                            dbc.Button("Acessar", href="/ceo", color="primary", className="w-100")
                        ])
                    ], className="text-center shadow-sm h-100")
                ], xs=12, md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-hand-holding-usd fa-3x mb-3", style={'color': '#28a745'}),
                            html.H4("Visão CFO"),
                            html.P("Análise financeira de receitas, ROI e performance comercial"),
                            dbc.Button("Acessar", href="/cfo", color="success", className="w-100")
                        ])
                    ], className="text-center shadow-sm h-100")
                ], xs=12, md=6),
            ], className="mt-4"),
        ])
    elif pathname == "/ceo":
        return ceo.layout
    elif pathname == "/cfo":
        return cfo.layout
    return html.Div([
        html.H1("404: Página não encontrada", className="text-danger"),
        html.P(f"O caminho '{pathname}' não foi reconhecido."),
        dbc.Button("Voltar ao início", href="/", color="primary")
    ], className="p-5 text-center")

# ==================== CSS CUSTOMIZADO ====================
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.15.4/css/all.css">
        <style>
            .sidebar-nav-item:hover {
                background: rgba(255,255,255,0.1) !important;
                transform: translateX(5px);
            }
            .sidebar-nav-item.active {
                background: rgba(123,104,238,0.3) !important;
                border-left: 4px solid #7B68EE;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
