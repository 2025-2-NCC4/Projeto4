# =============================================================================
# DASHBOARD CEO - VISÃO ESTRATÉGICA DO NEGÓCIO
# =============================================================================

# Importação das bibliotecas necessárias
from dash import dcc, html  # Componentes base do Dash
import dash_bootstrap_components as dbc  # Componentes estilizados Bootstrap
from dash.dependencies import Input, Output, State  # Para callbacks
from app import app  # Instância principal da aplicação
# Importação das funções de geração de gráficos
from utils.graphs import (
    criar_grafico_resgates_segmento,  # Gráfico de resgates por segmento
    criar_grafico_dia_semana,         # Gráfico de atividade por dia da semana
    criar_grafico_heatmap,            # Heatmap de atividade
    criar_grafico_faixa_etaria,       # Distribuição por faixa etária
    criar_grafico_segmento_tipo,      # Análise por tipo de segmento
    criar_grafico_dispositivos        # Uso por tipo de dispositivo
)
# Importação dos dataframes processados
from utils.db_utils import df_trans, df_players, df_pedestres
import pandas as pd
from components.botao_relatorio_ceo import gerar_layout_botao_ceo

# Preparação dos dados para filtros interativos
# Extraímos valores únicos e ordenamos para garantir consistência na interface
categorias = sorted(df_trans['categoria_estabelecimento'].dropna().unique())
tipos_cupom = sorted(df_trans['tipo_cupom'].dropna().unique())
bairros = sorted(df_trans['bairro_estabelecimento'].dropna().unique())

# Garantir que as colunas de data estão no formato correto
df_trans['data'] = pd.to_datetime(df_trans['data'], format='%d/%m/%Y')

# Definir cores do tema
COLORS = {
    'primary': '#351D5A',
    'success': '#28a745',
    'warning': '#ffc107',
    'info': '#17a2b8'
}

# ==================== KPI CARDS ====================
def create_kpi_card(title, value, icon, color):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas fa-{icon} fa-2x", style={'color': color}),
                html.H4(title, className="text-muted mb-0"),
                html.H2(value, className="font-weight-bold mb-0",
                       style={'color': color})
            ])
        ])
    ], className="text-center mb-3", style={'border-left': f'4px solid {color}'})

# Criar KPIs iniciais
kpi_cards = dbc.Row([
    dbc.Col(create_kpi_card(
        "Resgates Totais",
        f"{len(df_trans):,}",
        "ticket-alt",
        COLORS['primary']
    ), xs=12, sm=6, md=3, className="mb-3"),

    dbc.Col(create_kpi_card(
        "Usuários Ativos",
        f"{df_trans['celular'].nunique():,}",
        "users",
        COLORS['success']
    ), xs=12, sm=6, md=3, className="mb-3"),

    dbc.Col(create_kpi_card(
        "Estabelecimentos",
        f"{df_trans['nome_estabelecimento'].nunique()}",
        "store",
        COLORS['warning']
    ), xs=12, sm=6, md=3, className="mb-3"),

    dbc.Col(create_kpi_card(
        "Ticket Médio",
        f"R$ {df_trans['valor_cupom'].mean():.2f}",
        "dollar-sign",
        COLORS['info']
    ), xs=12, sm=6, md=3, className="mb-3"),
], className="mb-4 g-3")  # g-3 adiciona espaçamento entre colunas

# ==================== FILTROS ====================
filtros_card = dbc.Card([
    dbc.CardHeader([
        html.H5("🔍 Filtros Avançados", className="mb-0"),
    ]),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Categoria", className="font-weight-bold"),
                dbc.Select(
                    id='filtro-categoria',
                    options=[{'label': 'Todas', 'value': 'all'}] +
                            [{'label': c, 'value': c} for c in categorias],
                    value='all'
                )
            ], xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col([
                html.Label("Tipo de Cupom", className="font-weight-bold"),
                dbc.Select(
                    id='filtro-tipo-cupom',
                    options=[{'label': 'Todos', 'value': 'all'}] +
                            [{'label': t, 'value': t} for t in tipos_cupom],
                    value='all'
                )
            ], xs=12, sm=6, md=2, className="mb-3"),
            dbc.Col([
                html.Label("Bairro", className="font-weight-bold"),
                dbc.Select(
                    id='filtro-bairro',
                    options=[{'label': 'Todos', 'value': 'all'}] +
                            [{'label': b, 'value': b} for b in bairros],
                    value='all'
                )
            ], xs=12, sm=6, md=2, className="mb-3"),
            dbc.Col([
                html.Label("Período", className="font-weight-bold"),
                dcc.DatePickerRange(
                    id='filtro-data',
                    start_date=df_trans['data'].min(),
                    end_date=df_trans['data'].max(),
                    display_format='DD/MM/YYYY',
                    style={'width': '100%'}
                )
            ], xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col([
                html.Label("\u00A0", className="font-weight-bold"),
                dbc.Button("Aplicar Filtros", id='botao-aplicar', color="primary", className="w-100 mt-2")
            ], xs=12, sm=6, md=2, className="mb-3")
        ], className="mb-3 align-items-end"),
    ])
], className="mb-4")

# ==================== GRÁFICOS INICIAIS ====================
# Criar gráficos iniciais
fig_resg_seg = criar_grafico_resgates_segmento(df_trans)
fig_week = criar_grafico_dia_semana(df_trans)
fig_heatmap = criar_grafico_heatmap(df_trans)
fig_age_coupon = criar_grafico_faixa_etaria(df_trans, df_players)
fig_ht = criar_grafico_segmento_tipo(df_trans)
fig_devices = criar_grafico_dispositivos(df_pedestres)

# ==================== LAYOUT FINAL ====================
layout = html.Div([
    html.H1("Dashboard CEO - Análise Estratégica",
            style={'color': COLORS['primary']}),
    html.P("Visão consolidada de resgates totais, usuários e estabelecimentos",
            className="text-muted lead mb-4"),
    html.Hr(),

    # KPIs
    html.Div(id='kpi-cards', children=kpi_cards),

    # Filtros
    filtros_card,

    # Botão de Gerar Relatório
    #gerar_layout_botao(),
    html.Div([
        gerar_layout_botao_ceo(),
    ], className="mb-4"),

    # Gráficos
    dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id="graph-resg-seg", figure=fig_resg_seg))
            ]), xs=12, md=7, className="mb-3"),
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id="graph-week", figure=fig_week))
            ]), xs=12, md=5, className="mb-3"),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id="graph-heatmap", figure=fig_heatmap))
            ]), xs=12, md=8, className="mb-3"),
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id="graph-age-coupon", figure=fig_age_coupon))
            ]), xs=12, md=4, className="mb-3"),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id="graph-ht", figure=fig_ht))
            ]), xs=12, md=6, className="mb-3"),
            dbc.Col(dbc.Card([
                dbc.CardBody(dcc.Graph(id="graph-devices", figure=fig_devices))
            ]), xs=12, md=6, className="mb-3"),
        ], className="mb-4"),
    ], fluid=True)
], className="p-3")

# ==================== CALLBACK ÚNICO ====================
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('graph-resg-seg', 'figure'),
     Output('graph-week', 'figure'),
     Output('graph-heatmap', 'figure'),
     Output('graph-age-coupon', 'figure'),
     Output('graph-ht', 'figure'),
     Output('graph-devices', 'figure')],
    [Input('botao-aplicar', 'n_clicks')],
    [State('filtro-categoria', 'value'),
     State('filtro-tipo-cupom', 'value'),
     State('filtro-bairro', 'value'),
     State('filtro-data', 'start_date'),
     State('filtro-data', 'end_date')]
)
def atualizar_dashboard(n_clicks, categoria, tipo_cupom, bairro, start_date, end_date):
    if n_clicks is None or n_clicks == 0:
        # Não fazer nada se nenhum clique foi feito
        from dash import no_update
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    # Aplicar filtros
    df_filtrado = df_trans.copy()

    if categoria != 'all':
        df_filtrado = df_filtrado[df_filtrado['categoria_estabelecimento'] == categoria]

    if tipo_cupom != 'all':
        df_filtrado = df_filtrado[df_filtrado['tipo_cupom'] == tipo_cupom]

    if bairro != 'all':
        df_filtrado = df_filtrado[df_filtrado['bairro_estabelecimento'] == bairro]

    if start_date and end_date:
        df_filtrado = df_filtrado[
            (df_filtrado['data'] >= pd.to_datetime(start_date)) &
            (df_filtrado['data'] <= pd.to_datetime(end_date))
        ]

    # Criar KPIs
    total_resgates = len(df_filtrado)
    usuarios_ativos = df_filtrado['celular'].nunique()
    estabelecimentos = df_filtrado['nome_estabelecimento'].nunique()
    ticket_medio = df_filtrado['valor_cupom'].mean()

    kpi_cards = dbc.Row([
        dbc.Col(create_kpi_card(
            "Resgates Totais",
            f"{total_resgates:,}",
            "ticket-alt",
            COLORS['primary']
        ), width=3),
        dbc.Col(create_kpi_card(
            "Usuários Ativos",
            f"{usuarios_ativos:,}",
            "users",
            COLORS['success']
        ), width=3),
        dbc.Col(create_kpi_card(
            "Estabelecimentos",
            f"{estabelecimentos}",
            "store",
            COLORS['warning']
        ), width=3),
        dbc.Col(create_kpi_card(
            "Ticket Médio",
            f"R$ {ticket_medio:.2f}",
            "dollar-sign",
            COLORS['info']
        ), width=3),
    ], className="mb-4")

    # Criar gráficos com dados filtrados
    fig_resg_seg = criar_grafico_resgates_segmento(df_filtrado)
    fig_week = criar_grafico_dia_semana(df_filtrado)
    fig_heatmap = criar_grafico_heatmap(df_filtrado)
    fig_age_coupon = criar_grafico_faixa_etaria(df_filtrado, df_players)
    fig_ht = criar_grafico_segmento_tipo(df_filtrado)
    fig_devices = criar_grafico_dispositivos(df_pedestres)

    return kpi_cards, fig_resg_seg, fig_week, fig_heatmap, fig_age_coupon, fig_ht, fig_devices