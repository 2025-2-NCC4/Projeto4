from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
from utils.graphs import (
    criar_grafico_receita_segmento, criar_grafico_scatter,
    criar_grafico_ticket_medio, criar_grafico_distribuicao
)
from utils.db_utils import df_massa, df_trans
import pandas as pd
#from components.botao_relatorio import gerar_layout_botao
from components.botao_relatorio_cfo import gerar_layout_botao_cfo

# Definir cores do tema
COLORS = {
    'primary': '#351D5A',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8'
}

# Garantir que as datas estão no formato correto
df_trans['data'] = pd.to_datetime(df_trans['data'], format='%d/%m/%Y')
df_massa['data_captura'] = pd.to_datetime(df_massa['data_captura'], format='%d/%m/%Y')

# ==================== KPI CARDS FINANCEIROS ====================
def create_financial_kpi(title, value, subtitle, icon, color):
    """Card KPI financeiro"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"fas fa-{icon} fa-2x mb-2", 
                           style={'color': color}),
                ], style={'float': 'left', 'marginRight': '15px'}),
                html.Div([
                    html.H6(title, className="text-muted mb-1"),
                    html.H3(value, className="font-weight-bold mb-0", 
                           style={'color': color}),
                    html.Small(subtitle, className="text-muted"),
                ])
            ], style={'display': 'flex', 'alignItems': 'center'})
        ])
    ], className="mb-3 shadow-sm", style={
        'border-left': f'5px solid {color}',
    })

# Calcular KPIs iniciais
receita_total = df_trans['valor_cupom'].sum()
receita_liquida = df_trans['valor_cupom'].sum() - df_trans['repasse_picmoney'].sum()
margem_operacional = (receita_liquida / receita_total) * 100 if receita_total > 0 else 0
ticket_medio = df_trans['valor_cupom'].mean()
cupom_medio = df_trans['valor_cupom'].mean()

# KPIs iniciais
kpi_cards = dbc.Row([
    dbc.Col(create_financial_kpi(
        "Receita Total",
        f"R$ {receita_total:,.2f}",
        "Todos os dados",
        "chart-line",
        COLORS['success']
    ), xs=12, sm=6, md=3, className="mb-3 g-3"),

    dbc.Col(create_financial_kpi(
        "Receita Líquida",
        f"R$ {receita_liquida:,.2f}",
        "Todos os dados",
        "chart-line",
        COLORS['success']
    ), xs=12, sm=6, md=3, className="mb-3 g-3"),

    dbc.Col(create_financial_kpi(
        "Margem Operacional",
        f"{margem_operacional:,.2f}%",
        "Todos os dados",
        "percent",
        COLORS['info']
    ), xs=12, sm=6, md=3, className="mb-3 g-3"),
    
    dbc.Col(create_financial_kpi(
        "Ticket Médio",
        f"R$ {ticket_medio:.2f}",
        "Por transação",
        "receipt",
        COLORS['info']
    ), xs=12, sm=6, md=3, className="mb-3 g-3"),
], className="mb-4")

# ==================== FILTROS FINANCEIROS ====================
# Extrair segmentos e lojas para filtros
segmentos = sorted(df_trans['categoria_estabelecimento'].dropna().unique())
lojas = sorted(df_trans['nome_estabelecimento'].dropna().unique())

filtros_financeiros = dbc.Card([
    dbc.CardHeader([
        html.Div([
            html.H5("💰 Filtros Financeiros", className="mb-0 d-inline"),
        ])
    ]),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Segmento de Loja", className="font-weight-bold"),
                dbc.Select(
                    id='filtro-segmento',
                    options=[{'label': 'Todos os Segmentos', 'value': 'all'}] + 
                            [{'label': s, 'value': s} for s in segmentos],
                    value='all'
                )
            ], xs=12, sm=6, md=3, className="mb-3"),
            
            dbc.Col([
                html.Label("Loja Específica", className="font-weight-bold"),
                dbc.Select(
                    id='filtro-loja',
                    options=[{'label': 'Todas as Lojas', 'value': 'all'}] + 
                            [{'label': l, 'value': l} for l in lojas[:50]],
                    value='all'
                )
            ], xs=12, sm=6, md=3, className="mb-3"),
            
            dbc.Col([
                html.Label("Período de Análise", className="font-weight-bold"),
                dcc.DatePickerRange(
                    id='filtro-data-cfo',
                    start_date=df_trans['data'].min(),
                    end_date=df_trans['data'].max(),
                    display_format='DD/MM/YYYY',
                    style={'width': '100%'}
                )
            ], xs=12, sm=6, md=4, className="mb-3"),
            
            dbc.Col([
                html.Label("\u00A0", className="font-weight-bold"),
                dbc.Button(
                    [html.I(className="fas fa-filter mr-2"), "Aplicar Filtros"],
                    id='botao-aplicar-cfo',
                    color="primary",
                    className="w-100"
                )
            ], xs=12, sm=6, md=2, className="mb-3"),
        ], className="align-items-end"),
    ])
], className="mb-4 shadow-sm")

# ==================== GRÁFICOS INICIAIS ====================
# Criar gráficos iniciais
fig_receita_segmento = criar_grafico_receita_segmento(df_trans)
fig_scatter = criar_grafico_scatter(df_massa)
fig_ticket_loja = criar_grafico_ticket_medio(df_massa)
fig_distribuicao = criar_grafico_distribuicao(df_trans)

# Estilizar gráficos iniciais
for fig in [fig_receita_segmento, fig_scatter, fig_ticket_loja, fig_distribuicao]:
    fig.update_layout(
        template='plotly_white',
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        title_font_size=16,
        title_font_color=COLORS['primary'],
        hovermode='x unified',
        margin=dict(l=60, r=40, t=60, b=60)
    )

fig_receita_segmento.update_traces(marker_color=COLORS['success'])
fig_ticket_loja.update_traces(marker_color=COLORS['info'])
fig_distribuicao.update_traces(marker_color=COLORS['warning'])

# Stats iniciais da distribuição
stats_distribuicao = html.Div([
    html.Small([
        html.Strong("Média: "),
        f"R$ {cupom_medio:.2f}"
    ], className="text-muted d-block"),
    html.Small([
        html.Strong("Mediana: "),
        f"R$ {df_trans['valor_cupom'].median():.2f}"
    ], className="text-muted d-block"),
])

# Meta mensal inicial
percentual_meta = (receita_total/1000000)*100
meta_text = f"Atingido {percentual_meta:.1f}% da meta de R$ 1M"

# ==================== LAYOUT FINAL ====================
layout = html.Div([
    # Cabeçalho
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-chart-pie mr-3"),
                "Dashboard CFO - Análise Financeira"
            ], className="mb-2", style={'color': COLORS['primary']}),
            html.P("Visão consolidada de receitas, ticket médio e performance de cupons",
                   className="text-muted lead")
        ]),
    ], className="mb-4"),
    
    html.Hr(),
    
    # KPIs Dinâmicos
    html.Div(id='kpi-cards-cfo', children=kpi_cards),
    
    # Filtros
    filtros_financeiros,

    html.Div([
        # Botão de Gerar Relatório
        gerar_layout_botao_cfo(),
    ], className="mb-4"),
    
    # Gráficos
    dbc.Container([
        # LINHA 1: Gráfico principal + Scatter
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-bar mr-2"),
                        html.Strong("Receita por Segmento de Negócio")
                    ], style={'backgroundColor': '#f8f9fa'}),
                    dbc.CardBody([
                        dcc.Graph(id="graph-receita-segmento", figure=fig_receita_segmento,
                                 config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], xs=12, sm=6, md=7, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-scatter mr-2"),
                        html.Strong("Análise: Valor Cupom × Valor Compra"),
                    ], style={'backgroundColor': '#f8f9fa'}),
                    dbc.CardBody([
                        dcc.Graph(id="graph-scatter", figure=fig_scatter,
                                 config={'displayModeBar': False}),
                        html.Small([
                            html.I(className="fas fa-info-circle mr-1"),
                            "Linha de tendência indica correlação entre cupom e compra final"
                        ], className="text-muted d-block mt-2")
                    ])
                ], className="shadow-sm")
            ], xs=12, sm=6, md=5, className="mb-3"),
        ], className="mb-4"),
        
        # LINHA 2: Análise por loja + Distribuição
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-store mr-2"),
                        html.Strong("Ticket Médio por Estabelecimento"),
                    ], style={'backgroundColor': '#f8f9fa'}),
                    dbc.CardBody([
                        dcc.Graph(id="graph-ticket-loja", figure=fig_ticket_loja,
                                 config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], xs=12, sm=6, md=8, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-histogram mr-2"),
                        html.Strong("Distribuição de Cupons")
                    ], style={'backgroundColor': '#f8f9fa'}),
                    dbc.CardBody([
                        dcc.Graph(id="graph-distribuicao", figure=fig_distribuicao,
                                 config={'displayModeBar': False}),
                        html.Div(id="stats-distribuicao", children=stats_distribuicao, 
                                className="mt-2 pt-2", style={'borderTop': '1px solid #dee2e6'})
                    ])
                ], className="shadow-sm")
            ], xs=12, sm=6, md=4, className="mb-3"),
        ], className="mb-4"),
        
        # LINHA 3: Insights e Alertas
        dbc.Row([     
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-bell mr-2", style={'color': COLORS['danger']}),
                        html.Strong("Alertas Financeiros")
                    ], style={'backgroundColor': '#f8d7da'}),
                    dbc.CardBody([
                        dbc.Alert([
                            html.H6([html.I(className="fas fa-chart-line mr-2"), "Meta Mensal"], 
                                   className="alert-heading"),
                            html.P(id="meta-mensal-text", children=meta_text, className="mb-0"),
                            dbc.Progress(id="progress-meta", value=percentual_meta, className="mt-2")
                        ], color="info", className="mb-0"),
                    ])
                ], className="shadow-sm")
            ]),
        ], className="mb-4 g-3"),
        
    ], fluid=True, id='graph-content-cfo'),
    
    # Footer com timestamp
    html.Footer([
        html.Hr(),
        html.Small([
            html.I(className="fas fa-clock mr-2"),
            f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}"
        ], className="text-muted")
    ], className="mt-4")
])

# ==================== CALLBACK ÚNICO ====================
@app.callback(
    [Output('kpi-cards-cfo', 'children'),
     Output('graph-receita-segmento', 'figure'),
     Output('graph-scatter', 'figure'),
     Output('graph-ticket-loja', 'figure'),
     Output('graph-distribuicao', 'figure'),
     Output('stats-distribuicao', 'children'),
     Output('meta-mensal-text', 'children'),
     Output('progress-meta', 'value')],
    [Input('botao-aplicar-cfo', 'n_clicks')],
    [State('filtro-segmento', 'value'),
     State('filtro-loja', 'value'),
     State('filtro-data-cfo', 'start_date'),
     State('filtro-data-cfo', 'end_date')]
)
def atualizar_dashboard_cfo(n_clicks, segmento, loja, start_date, end_date):
    if n_clicks is None or n_clicks == 0:
        # Não fazer nada se nenhum clique foi feito
        from dash import no_update
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Aplicar filtros ao df_trans
    df_filtrado_trans = df_trans.copy()
    df_filtrado_massa = df_massa.copy()
    
    if segmento != 'all':
        df_filtrado_trans = df_filtrado_trans[df_filtrado_trans['categoria_estabelecimento'] == segmento]
        # Para df_massa, usar tipo_loja como equivalente
        if 'tipo_loja' in df_filtrado_massa.columns:
            df_filtrado_massa = df_filtrado_massa[df_filtrado_massa['tipo_loja'] == segmento]
    
    if loja != 'all':
        df_filtrado_trans = df_filtrado_trans[df_filtrado_trans['nome_estabelecimento'] == loja]
        df_filtrado_massa = df_filtrado_massa[df_filtrado_massa['nome_loja'] == loja]
    
    if start_date and end_date:
        df_filtrado_trans = df_filtrado_trans[
            (df_filtrado_trans['data'] >= pd.to_datetime(start_date)) & 
            (df_filtrado_trans['data'] <= pd.to_datetime(end_date))
        ]
        df_filtrado_massa = df_filtrado_massa[
            (df_filtrado_massa['data_captura'] >= pd.to_datetime(start_date)) & 
            (df_filtrado_massa['data_captura'] <= pd.to_datetime(end_date))
        ]
    
    # Calcular KPIs com dados filtrados
    receita_total = df_filtrado_trans['valor_cupom'].sum()
    receita_liquida = df_filtrado_trans['valor_cupom'].sum() - df_filtrado_trans['repasse_picmoney'].sum()
    margem_operacional = (receita_liquida / receita_total) * 100 if receita_total > 0 else 0
    ticket_medio = df_filtrado_trans['valor_cupom'].mean()
    cupom_medio = df_filtrado_trans['valor_cupom'].mean()
    
    # Criar KPIs
    kpi_cards = dbc.Row([
        dbc.Col(create_financial_kpi(
            "Receita Total",
            f"R$ {receita_total:,.2f}",
            "Período selecionado",
            "chart-line",
            COLORS['success']
        ), xs=12, sm=6, md=3, className="mb-3 g-3"),

        dbc.Col(create_financial_kpi(
            "Receita Líquida",
            f"R$ {receita_liquida:,.2f}",
            "Período selecionado",
            "chart-line",
            COLORS['success']
        ), xs=12, sm=6, md=3, className="mb-3 g-3"),

        dbc.Col(create_financial_kpi(
            "Margem Operacional",
            f"{margem_operacional:,.2f}%",
            "Período selecionado",
            "percent",
            COLORS['info']
        ), xs=12, sm=6, md=3, className="mb-3 g-3"),
        
        dbc.Col(create_financial_kpi(
            "Ticket Médio",
            f"R$ {ticket_medio:.2f}",
            "Por transação",
            "receipt",
            COLORS['info']
        ), xs=12, sm=6, md=3, className="mb-3 g-3"),
    ], className="mb-4")
    
    # Criar gráficos com dados filtrados
    fig_receita_segmento = criar_grafico_receita_segmento(df_filtrado_trans)
    fig_scatter = criar_grafico_scatter(df_filtrado_massa)
    fig_ticket_loja = criar_grafico_ticket_medio(df_filtrado_massa)
    fig_distribuicao = criar_grafico_distribuicao(df_filtrado_trans)
    
    # Estilizar gráficos
    for fig in [fig_receita_segmento, fig_scatter, fig_ticket_loja, fig_distribuicao]:
        fig.update_layout(
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            title_font_size=16,
            title_font_color=COLORS['primary'],
            hovermode='x unified',
            margin=dict(l=60, r=40, t=60, b=60)
        )
    
    fig_receita_segmento.update_traces(marker_color=COLORS['success'])
    fig_ticket_loja.update_traces(marker_color=COLORS['info'])
    fig_distribuicao.update_traces(marker_color=COLORS['warning'])
    
    # Stats da distribuição
    stats_distribuicao = html.Div([
        html.Small([
            html.Strong("Média: "),
            f"R$ {cupom_medio:.2f}"
        ], className="text-muted d-block"),
        html.Small([
            html.Strong("Mediana: "),
            f"R$ {df_filtrado_trans['valor_cupom'].median():.2f}"
        ], className="text-muted d-block"),
    ])
    
    # Meta mensal
    percentual_meta = (receita_total/1000000)*100
    meta_text = f"Atingido {percentual_meta:.1f}% da meta de R$ 1M"
    
    return kpi_cards, fig_receita_segmento, fig_scatter, fig_ticket_loja, fig_distribuicao, stats_distribuicao, meta_text, percentual_meta