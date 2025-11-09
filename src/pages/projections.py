from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from app import app
from utils.db_utils import df_trans, df_massa, df_players
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

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

# ==================== CÁLCULOS BASE (HISTÓRICO) ====================
def calcular_metricas_historicas():
    """Calcula métricas históricas para usar como base das projeções"""
    # Período histórico: últimos 30 dias
    data_limite = df_trans['data'].max()
    data_inicio = data_limite - pd.Timedelta(days=30)
    
    df_recente = df_trans[df_trans['data'] >= data_inicio]
    
    # Métricas diárias médias
    dias_hist = (df_recente['data'].max() - df_recente['data'].min()).days + 1
    if dias_hist == 0:
        dias_hist = 1
    
    metricas = {
        'usuarios_unicos': df_recente['celular'].nunique(),
        'transacoes_dia': len(df_recente) / dias_hist,
        'receita_dia': df_recente['valor_cupom'].sum() / dias_hist,
        'receita_liquida_dia': (df_recente['valor_cupom'].sum() - df_recente['repasse_picmoney'].sum()) / dias_hist,
        'ticket_medio': df_recente['valor_cupom'].mean(),
        'transacoes_por_usuario': len(df_recente) / df_recente['celular'].nunique() if df_recente['celular'].nunique() > 0 else 0,
        'crescimento_mensal_usuarios': 0.05,  # 5% padrão (pode ser calculado)
        'crescimento_mensal_transacoes': 0.03,  # 3% padrão
    }
    
    return metricas

metricas_base = calcular_metricas_historicas()

# ==================== FUNÇÕES DE PROJEÇÃO ====================
def calcular_projecoes(horizonte_meses, crescimento_usuarios, crescimento_transacoes, 
                       crescimento_ticket, taxa_aquisicao, custo_por_usuario, 
                       margem_operacional_base):
    """Calcula projeções financeiras e operacionais"""
    
    # Criar série temporal
    data_inicio = df_trans['data'].max()
    datas = pd.date_range(start=data_inicio, periods=horizonte_meses * 30, freq='D')
    
    # Inicializar valores base
    usuarios_base = metricas_base['usuarios_unicos']
    transacoes_dia_base = metricas_base['transacoes_dia']
    ticket_medio_base = metricas_base['ticket_medio']
    receita_liquida_dia_base = metricas_base['receita_liquida_dia']
    
    # Arrays para armazenar projeções
    usuarios_proj = []
    transacoes_proj = []
    receita_bruta_proj = []
    receita_liquida_proj = []
    custos_proj = []
    lucro_proj = []
    
    usuarios_atual = usuarios_base
    transacoes_dia_atual = transacoes_dia_base
    ticket_medio_atual = ticket_medio_base
    
    # Calcular crescimento mensal composto
    crescimento_diario_usuarios = (1 + crescimento_usuarios) ** (1/30) - 1
    crescimento_diario_transacoes = (1 + crescimento_transacoes) ** (1/30) - 1
    crescimento_diario_ticket = (1 + crescimento_ticket) ** (1/30) - 1
    
    for i, data in enumerate(datas):
        # Aplicar crescimento diário
        usuarios_atual = usuarios_atual * (1 + crescimento_diario_usuarios) + taxa_aquisicao
        # Garantir que não temos valores negativos
        usuarios_atual = max(usuarios_atual, 0)
        
        transacoes_dia_atual = transacoes_dia_atual * (1 + crescimento_diario_transacoes)
        transacoes_dia_atual = max(transacoes_dia_atual, 0)
        
        ticket_medio_atual = ticket_medio_atual * (1 + crescimento_diario_ticket)
        ticket_medio_atual = max(ticket_medio_atual, 0)
        
        # Calcular receitas
        receita_bruta = transacoes_dia_atual * ticket_medio_atual
        
        # Calcular custos (margem operacional = lucro / receita_bruta)
        # Se margem é 85%, significa que custos variáveis são 15% da receita bruta
        custos_variaveis = receita_bruta * (1 - margem_operacional_base / 100)
        custos_fixos = usuarios_atual * (custo_por_usuario / 30)  # Custo diário por usuário
        custos_totais = custos_variaveis + custos_fixos
        
        # Receita líquida = Receita bruta - Custos variáveis
        receita_liquida = receita_bruta - custos_variaveis
        
        # Lucro = Receita líquida - Custos fixos (ou Receita bruta - Custos totais)
        lucro = receita_bruta - custos_totais
        
        usuarios_proj.append(usuarios_atual)
        transacoes_proj.append(transacoes_dia_atual)
        receita_bruta_proj.append(receita_bruta)
        receita_liquida_proj.append(receita_liquida)
        custos_proj.append(custos_totais)
        lucro_proj.append(lucro)
    
    # Criar DataFrame
    df_proj = pd.DataFrame({
        'data': datas,
        'usuarios': usuarios_proj,
        'transacoes_dia': transacoes_proj,
        'receita_bruta': receita_bruta_proj,
        'receita_liquida': receita_liquida_proj,
        'custos': custos_proj,
        'lucro': lucro_proj
    })
    
    # Agregar por mês para visualização
    df_proj['ano_mes'] = df_proj['data'].dt.to_period('M')
    df_proj_mensal = df_proj.groupby('ano_mes').agg({
        'usuarios': 'last',
        'transacoes_dia': 'mean',
        'receita_bruta': 'sum',
        'receita_liquida': 'sum',
        'custos': 'sum',
        'lucro': 'sum'
    }).reset_index()
    df_proj_mensal['ano_mes'] = df_proj_mensal['ano_mes'].astype(str)
    
    return df_proj, df_proj_mensal

# ==================== GRÁFICOS DE PROJEÇÃO ====================
def criar_grafico_projecao_receita(df_proj_mensal):
    """Gráfico de projeção de receita"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_proj_mensal['ano_mes'],
        y=df_proj_mensal['receita_bruta'],
        mode='lines+markers',
        name='Receita Bruta',
        line=dict(color=COLORS['success'], width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_proj_mensal['ano_mes'],
        y=df_proj_mensal['receita_liquida'],
        mode='lines+markers',
        name='Receita Líquida',
        line=dict(color=COLORS['info'], width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Projeção de Receita Mensal',
        xaxis_title='Mês',
        yaxis_title='Receita (R$)',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def criar_grafico_projecao_usuarios(df_proj_mensal):
    """Gráfico de projeção de usuários"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_proj_mensal['ano_mes'],
        y=df_proj_mensal['usuarios'],
        mode='lines+markers',
        name='Usuários Únicos',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='Projeção de Usuários Únicos',
        xaxis_title='Mês',
        yaxis_title='Número de Usuários',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def criar_grafico_projecao_lucro(df_proj_mensal):
    """Gráfico de projeção de lucro vs custos"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_proj_mensal['ano_mes'],
        y=df_proj_mensal['custos'],
        name='Custos',
        marker_color=COLORS['danger']
    ))
    
    fig.add_trace(go.Bar(
        x=df_proj_mensal['ano_mes'],
        y=df_proj_mensal['lucro'],
        name='Lucro',
        marker_color=COLORS['success']
    ))
    
    fig.update_layout(
        title='Projeção de Lucro vs Custos Mensais',
        xaxis_title='Mês',
        yaxis_title='Valor (R$)',
        barmode='group',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def criar_grafico_projecao_transacoes(df_proj_mensal):
    """Gráfico de projeção de transações"""
    fig = go.Figure()
    
    # Calcular transações mensais (média diária * 30)
    transacoes_mensais = df_proj_mensal['transacoes_dia'] * 30
    
    fig.add_trace(go.Scatter(
        x=df_proj_mensal['ano_mes'],
        y=transacoes_mensais,
        mode='lines+markers',
        name='Transações Mensais',
        line=dict(color=COLORS['warning'], width=3),
        marker=dict(size=8),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title='Projeção de Transações Mensais',
        xaxis_title='Mês',
        yaxis_title='Número de Transações',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

# ==================== LAYOUT ====================
layout = html.Div([
    # Cabeçalho
    html.Div([
        html.H1([
            html.I(className="fas fa-chart-line mr-3"),
            "Simulador de Projeções"
        ], className="mb-2", style={'color': COLORS['primary']}),
        html.P("Simule cenários futuros de receita, usuários e operações",
               className="text-muted lead")
    ], className="mb-4"),
    
    html.Hr(),
    
    # Seção de Controles
    dbc.Card([
        dbc.CardHeader([
            html.H5("⚙️ Parâmetros de Simulação", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Horizonte de Projeção (meses)", className="font-weight-bold"),
                    dcc.Slider(
                        id='slider-horizonte',
                        min=3,
                        max=24,
                        step=3,
                        value=12,
                        marks={i: f'{i}m' for i in range(3, 25, 3)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], xs=12, md=6, className="mb-3"),
                
                dbc.Col([
                    html.Label("Crescimento Mensal de Usuários (%)", className="font-weight-bold"),
                    dcc.Slider(
                        id='slider-crescimento-usuarios',
                        min=-5,
                        max=20,
                        step=0.5,
                        value=5,
                        marks={i: f'{i}%' for i in range(-5, 21, 5)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], xs=12, md=6, className="mb-3"),
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Crescimento Mensal de Transações (%)", className="font-weight-bold"),
                    dcc.Slider(
                        id='slider-crescimento-transacoes',
                        min=-5,
                        max=15,
                        step=0.5,
                        value=3,
                        marks={i: f'{i}%' for i in range(-5, 16, 5)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], xs=12, md=6, className="mb-3"),
                
                dbc.Col([
                    html.Label("Crescimento do Ticket Médio (%)", className="font-weight-bold"),
                    dcc.Slider(
                        id='slider-crescimento-ticket',
                        min=-10,
                        max=10,
                        step=0.5,
                        value=0,
                        marks={i: f'{i}%' for i in range(-10, 11, 5)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], xs=12, md=6, className="mb-3"),
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Taxa de Aquisição de Usuários/dia", className="font-weight-bold"),
                    html.Small("(negativo = perda de usuários)", className="text-muted d-block mb-1"),
                    dcc.Input(
                        id='input-taxa-aquisicao',
                        type='number',
                        value=10,
                        step=1,
                        className="form-control"
                    )
                ], xs=12, md=4, className="mb-3"),
                
                dbc.Col([
                    html.Label("Custo por Usuário/mês (R$)", className="font-weight-bold"),
                    dcc.Input(
                        id='input-custo-usuario',
                        type='number',
                        value=2.50,
                        min=0,
                        step=0.1,
                        className="form-control"
                    )
                ], xs=12, md=4, className="mb-3"),
                
                dbc.Col([
                    html.Label("Margem Operacional Base (%)", className="font-weight-bold"),
                    dcc.Input(
                        id='input-margem',
                        type='number',
                        value=85,
                        min=0,
                        max=100,
                        step=1,
                        className="form-control"
                    )
                ], xs=12, md=4, className="mb-3"),
            ], className="mb-3"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-calculator mr-2"), "Calcular Projeções"],
                        id='botao-calcular',
                        color="primary",
                        size="lg",
                        className="w-100"
                    )
                ], xs=12, className="mb-3")
            ])
        ])
    ], className="mb-4 shadow-sm"),
    
    # Gráficos de Projeção
    html.Div(id='graficos-projecoes', className="mb-4")
])

# ==================== CALLBACKS ====================
@app.callback(
    Output('graficos-projecoes', 'children'),
    [Input('botao-calcular', 'n_clicks')],
    [State('slider-horizonte', 'value'),
     State('slider-crescimento-usuarios', 'value'),
     State('slider-crescimento-transacoes', 'value'),
     State('slider-crescimento-ticket', 'value'),
     State('input-taxa-aquisicao', 'value'),
     State('input-custo-usuario', 'value'),
     State('input-margem', 'value')]
)
def atualizar_projecoes(n_clicks, horizonte, crescimento_usuarios, crescimento_transacoes,
                        crescimento_ticket, taxa_aquisicao, custo_usuario, margem):
    
    if n_clicks is None or n_clicks == 0:
        # Valores iniciais
        return html.Div([
            dbc.Alert("Ajuste os parâmetros acima e clique em 'Calcular Projeções' para ver as simulações.",
                     color="info", className="text-center")
        ])
    
    # Converter valores percentuais e tratar None
    crescimento_usuarios = (crescimento_usuarios or 0) / 100
    crescimento_transacoes = (crescimento_transacoes or 0) / 100
    crescimento_ticket = (crescimento_ticket or 0) / 100
    taxa_aquisicao = taxa_aquisicao if taxa_aquisicao is not None else 0
    custo_usuario = custo_usuario if custo_usuario is not None else 2.50
    margem = margem if margem is not None else 85
    horizonte = horizonte if horizonte is not None else 12
    
    # Calcular projeções
    df_proj, df_proj_mensal = calcular_projecoes(
        horizonte, crescimento_usuarios, crescimento_transacoes,
        crescimento_ticket, taxa_aquisicao, custo_usuario, margem
    )
    
    # Criar gráficos
    fig_receita = criar_grafico_projecao_receita(df_proj_mensal)
    fig_usuarios = criar_grafico_projecao_usuarios(df_proj_mensal)
    fig_lucro = criar_grafico_projecao_lucro(df_proj_mensal)
    fig_transacoes = criar_grafico_projecao_transacoes(df_proj_mensal)
    
    graficos = dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_receita, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_usuarios, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-3"),
        ], className="mb-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_lucro, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_transacoes, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], xs=12, md=6, className="mb-3"),
        ])
    ], fluid=True)
    
    return graficos

