# =============================================================================
# MÓDULO DE VISUALIZAÇÕES E GRÁFICOS
# =============================================================================

"""
Este módulo contém todas as funções necessárias para gerar visualizações 
e gráficos para os dashboards do CFO e CEO. Utiliza principalmente a 
biblioteca Plotly Express para criar gráficos interativos.
"""

# Importação dos dados processados
from utils.db_utils import (
    df_massa,      # Dados de valores e lojas
    df_pedestres,  # Dados de fluxo de pedestres
    df_players,    # Dados dos usuários
    df_trans       # Dados das transações
)
import pandas as pd        # Para manipulação de dados
import plotly.express as px  # Para criação de gráficos interativos

# =============================================================================
# GRÁFICOS DO DASHBOARD FINANCEIRO (CFO)
# =============================================================================

# Receita por segmento (tipo_loja) — Bar horizontal
df_seg = (df_trans
          .dropna(subset=["categoria_estabelecimento","valor_cupom"])
          .groupby("categoria_estabelecimento", as_index=False)["valor_cupom"].sum()
          .sort_values("valor_cupom", ascending=True))
fig_df_seg = px.bar(df_seg, x="valor_cupom", y="categoria_estabelecimento", orientation="h",
             title="Receita total por segmento",
             labels={"valor_cupom":"Receita (R$)","categoria_estabelecimento":"Segmento"})
fig_df_seg.update_layout(margin=dict(l=150))

# Usando df_massa (possui valor_cupom e valor_compra)
df_scatter = df_massa.dropna(subset=["valor_cupom","valor_compra"])
fig_df_scatter = px.scatter(df_scatter, x="valor_cupom", y="valor_compra", trendline="ols",
                 title="Relacionamento: valor do cupom x valor final da compra",
                 labels={"valor_cupom":"Valor do Cupom (R$)","valor_compra":"Valor da Compra (R$)"})


# Média de valor_compra por loja
df_mean = (df_massa.dropna(subset=["nome_loja","valor_compra"])
           .groupby("nome_loja", as_index=False)["valor_compra"].mean()
           .sort_values("valor_compra", ascending=False))
fig_df_mean = px.bar(df_mean, x="nome_loja", y="valor_compra", title="Valor médio de venda por loja")
fig_df_mean.update_layout(xaxis_tickangle=-45)

# Histograma de valor_cupom (df_trans)
df_v = df_trans.dropna(subset=["valor_cupom"])
fig_df_v = px.histogram(df_v, x="valor_cupom", nbins=10, title="Distribuição de valor dos cupons resgatados")
fig_df_v.update_xaxes(title="Valor do cupom (R$)")
fig_df_v.update_layout(
    bargap=0.2  # controla o espaço entre as barras (0 = sem espaço, 1 = só espaço)
)

def criar_grafico_receita_segmento(df):
    """
    Cria um gráfico de barras horizontais mostrando a receita total por segmento de negócio.
    
    Args:
        df: DataFrame contendo as colunas 'categoria_estabelecimento' e 'valor_cupom'
    
    Returns:
        figura Plotly com o gráfico de barras horizontais
    """
    # Agrupa os dados por categoria e calcula a soma dos valores
    df_seg = (df
              .dropna(subset=["categoria_estabelecimento","valor_cupom"])  # Remove linhas com valores ausentes
              .groupby("categoria_estabelecimento", as_index=False)["valor_cupom"].sum()  # Agrupa e soma
              .sort_values("valor_cupom", ascending=True))  # Ordena por valor
    
    # Cria o gráfico de barras horizontais
    fig = px.bar(df_seg, 
                 x="valor_cupom",
                 y="categoria_estabelecimento", 
                 orientation="h",
                 title="Receita total por segmento",
                 labels={"valor_cupom":"Receita (R$)","categoria_estabelecimento":"Segmento"})
    
    # Ajusta o layout para melhor visualização
    fig.update_layout(margin=dict(l=150), template='plotly_white')
    return fig

def criar_grafico_scatter(df_massa):
    """
    Cria um gráfico de dispersão relacionando o valor dos cupons com o valor final das compras.
    Inclui uma linha de tendência para análise de correlação.
    
    Args:
        df_massa: DataFrame contendo as colunas 'valor_cupom' e 'valor_compra'
    
    Returns:
        figura Plotly com o gráfico de dispersão
    """
    # Remove valores ausentes para garantir a qualidade da análise
    df_scatter = df_massa.dropna(subset=["valor_cupom","valor_compra"])
    
    # Cria o gráfico de dispersão com linha de tendência
    fig = px.scatter(df_scatter, 
                    x="valor_cupom", 
                    y="valor_compra", 
                    trendline="ols",  # Adiciona linha de tendência linear
                    title="Relacionamento: valor do cupom x valor final da compra",
                    labels={"valor_cupom":"Valor do Cupom (R$)","valor_compra":"Valor da Compra (R$)"})
    
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_ticket_medio(df_massa):
    """
    Cria um gráfico de barras mostrando o ticket médio (valor médio de compra) por loja.
    
    Args:
        df_massa: DataFrame contendo as colunas 'nome_loja' e 'valor_compra'
    
    Returns:
        figura Plotly com o gráfico de barras
    """
    # Calcula a média de valor de compra por loja
    df_mean = (df_massa.dropna(subset=["nome_loja","valor_compra"])
               .groupby("nome_loja", as_index=False)["valor_compra"].mean()
               .sort_values("valor_compra", ascending=False))
    
    # Cria o gráfico de barras
    fig = px.bar(df_mean, 
                 x="nome_loja", 
                 y="valor_compra", 
                 title="Valor médio de venda por loja")
    
    # Rotaciona os rótulos do eixo X para melhor legibilidade
    fig.update_layout(xaxis_tickangle=-45, template='plotly_white')
    return fig

def criar_grafico_distribuicao(df):
    """
    Cria um histograma mostrando a distribuição dos valores dos cupons resgatados.
    
    Args:
        df: DataFrame contendo a coluna 'valor_cupom'
    
    Returns:
        figura Plotly com o histograma
    """
    # Remove valores ausentes
    df_v = df.dropna(subset=["valor_cupom"])
    
    # Cria o histograma
    fig = px.histogram(df_v, 
                      x="valor_cupom", 
                      nbins=20,  # Define o número de intervalos
                      title="Distribuição de valor dos cupons resgatados")
    
    # Configura os eixos e o layout
    fig.update_xaxes(title="Valor do cupom (R$)")
    fig.update_layout(template='plotly_white', bargap=0.1)  # Adiciona espaço entre as barras
    return fig


# =============================================================================
# GRÁFICOS DO DASHBOARD ESTRATÉGICO (CEO)
# =============================================================================

def criar_grafico_resgates_segmento(df):
    """
    Cria um gráfico de barras mostrando os 10 segmentos com mais resgates de cupons.
    
    Esta visualização é crucial para o CEO entender quais segmentos de negócio 
    estão tendo maior engajamento com os cupons.
    
    Args:
        df: DataFrame contendo as colunas 'categoria_estabelecimento' e 'id_cupom'
    
    Returns:
        figura Plotly com o gráfico de barras dos top 10 segmentos
    """
    # Processamento dos dados
    df_resg_seg = (df
                   .dropna(subset=["categoria_estabelecimento","id_cupom"])  # Remove dados incompletos
                   .groupby("categoria_estabelecimento", as_index=False)["id_cupom"].count()  # Conta resgates
                   .rename(columns={"id_cupom":"resgates"})  # Renomeia para clareza
                   .sort_values("resgates", ascending=False)  # Ordena do maior para o menor
                   .head(10))  # Seleciona apenas os top 10
    
    # Criação do gráfico
    fig = px.bar(df_resg_seg, 
                 x="categoria_estabelecimento", 
                 y="resgates",
                 title="Resgates por segmento (Top 10)")
    
    # Ajustes de layout para melhor visualização
    fig.update_layout(xaxis_tickangle=-45,  # Rotaciona labels para legibilidade
                     template='plotly_white')  # Usa template limpo
    return fig

def criar_grafico_dia_semana(df):
    """
    Cria um gráfico de barras mostrando a distribuição de resgates por dia da semana.
    
    Esta visualização ajuda o CEO a entender padrões semanais de uso dos cupons,
    permitindo otimizar campanhas e recursos baseado nos dias de maior atividade.
    
    Args:
        df: DataFrame contendo as colunas 'data' e 'id_cupom'
    
    Returns:
        figura Plotly com o gráfico de barras dos resgates por dia da semana
    """
    # Preparação dos dados: criação da coluna de dia da semana se não existir
    if 'weekday' not in df.columns:
        # Converte coluna de data para datetime
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        # Extrai o nome do dia da semana
        df['weekday'] = df['data'].dt.day_name()
        # Mapeamento para traduzir os dias para português
        weekday_map = {
            'Monday': 'Segunda', 
            'Tuesday': 'Terça', 
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 
            'Friday': 'Sexta', 
            'Saturday': 'Sábado', 
            'Sunday': 'Domingo'
        }
        # Aplica a tradução
        df['weekday'] = df['weekday'].map(weekday_map)
    
    # Processamento dos dados: contagem de resgates por dia
    df_week = (df.dropna(subset=["weekday","id_cupom"])  # Remove dados incompletos
               .groupby("weekday", as_index=False)["id_cupom"].count()  # Agrupa e conta
               .rename(columns={"id_cupom":"resgates"}))  # Renomeia para clareza
    # Ordena por número de resgates
    df_week = df_week.sort_values("resgates", ascending=False)
    
    # Criação do gráfico
    fig = px.bar(df_week, 
                 x="weekday", 
                 y="resgates", 
                 title="Resgates por dia da semana")
    
    # Ajuste do template para visual limpo
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_heatmap(df):
    """
    Cria um heatmap (mapa de calor) mostrando a relação entre horário do dia 
    e categoria do estabelecimento para resgates de cupons.
    
    Esta visualização é fundamental para o CEO entender padrões temporais 
    de uso dos cupons em diferentes tipos de estabelecimento, permitindo 
    otimizar estratégias de marketing e operações.
    
    Args:
        df: DataFrame contendo as colunas 'hora', 'categoria_estabelecimento' e 'id_cupom'
    
    Returns:
        figura Plotly com o heatmap de horário x categoria
    """
    # Preparação do horário: extrai apenas a hora se necessário
    if 'hour' not in df.columns:
        df['hour'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.hour
    
    # Remove dados ausentes e agrupa por hora e categoria
    df_hm = df.dropna(subset=["hour","categoria_estabelecimento","id_cupom"])
    df_hm = (df_hm.groupby(["hour","categoria_estabelecimento"], as_index=False)
             ["id_cupom"].count()
             .rename(columns={"id_cupom":"count"}))
    
    # Seleciona as 15 categorias com mais resgates para manter o visual limpo
    top_categorias = (df_hm.groupby("categoria_estabelecimento")["count"]
                     .sum().nlargest(15).index)
    df_hm = df_hm[df_hm["categoria_estabelecimento"].isin(top_categorias)]
    
    # Cria matriz pivô para o heatmap
    hm = (df_hm.pivot(index="hour", 
                      columns="categoria_estabelecimento", 
                      values="count")
          .fillna(0))  # Preenche valores ausentes com 0
    
    # Cria o heatmap
    fig = px.imshow(hm, 
                    title="Heatmap: hora do resgate x categoria", 
                    aspect="auto")
    
    # Ajusta o template para visual limpo
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_faixa_etaria(df, df_players):
    """
    Cria um gráfico de barras agrupadas mostrando a distribuição de resgates 
    por faixa etária e tipo de cupom.
    
    Esta visualização permite ao CEO entender o perfil etário dos usuários
    e como diferentes tipos de cupons se comportam em cada faixa etária.
    
    Args:
        df: DataFrame com dados de transações
        df_players: DataFrame com dados dos usuários
    
    Returns:
        figura Plotly com o gráfico de barras agrupadas
    """
    # Mescla dados de transações com dados de usuários
    df_tx = df.merge(df_players[["celular","idade"]], on="celular", how="left")
    # Converte idade para numérico, tratando erros
    df_tx["idade"] = pd.to_numeric(df_tx["idade"], errors="coerce")
    
    # Define as faixas etárias
    bins = [0,17,24,34,44,54,64,200]  # Limites das faixas
    labels = ["<=17","18-24","25-34","35-44","45-54","55-64","65+"]  # Rótulos
    
    # Categoriza as idades em faixas
    df_tx["faixa_etaria"] = pd.cut(df_tx["idade"], bins=bins, labels=labels)
    
    # Agrupa dados por faixa etária e tipo de cupom
    df_age_coupon = (df_tx.dropna(subset=["faixa_etaria","tipo_cupom"])
                     .groupby(["faixa_etaria","tipo_cupom"], as_index=False)["id_cupom"].count()
                     .rename(columns={"id_cupom":"resgates"}))
    
    # Cria o gráfico de barras agrupadas
    fig = px.bar(df_age_coupon, 
                 x="faixa_etaria",  # Eixo X: faixas etárias
                 y="resgates",      # Eixo Y: quantidade de resgates
                 color="tipo_cupom", # Cor: diferencia tipos de cupom
                 barmode="group",    # Agrupa barras por faixa etária
                 title="Resgates por faixa etária e tipo de cupom")
    
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_segmento_tipo(df):
    """
    Cria um heatmap relacionando segmentos de lojas com tipos de cupons.
    
    Esta visualização ajuda o CEO a entender quais tipos de cupons são 
    mais populares em cada segmento de negócio.
    
    Args:
        df: DataFrame com dados de transações
    
    Returns:
        figura Plotly com o heatmap
    """
    # Processa os dados para o heatmap
    df_ht = (df.dropna(subset=["categoria_estabelecimento","tipo_cupom", "id_cupom"])
             .groupby(["categoria_estabelecimento","tipo_cupom"], as_index=False)["id_cupom"].count())
    
    # Cria matriz pivô para o heatmap
    pivot = df_ht.pivot(index="tipo_cupom", 
                       columns="categoria_estabelecimento", 
                       values="id_cupom").fillna(0)
    
    # Cria o heatmap
    fig = px.imshow(pivot, 
                    title="Segmento da loja x Tipo de Cupom", 
                    aspect="auto")
    
    # Ajusta o layout
    fig.update_layout(template='plotly_white', height=500)
    return fig

def criar_grafico_dispositivos(df_pedestres):
    """
    Cria um gráfico de pizza mostrando a distribuição de tipos de dispositivos
    entre usuários que têm o aplicativo instalado.
    
    Esta visualização ajuda o CEO a entender a distribuição de plataformas
    móveis entre os usuários, auxiliando em decisões de desenvolvimento.
    
    Args:
        df_pedestres: DataFrame com dados de pedestres e dispositivos
    
    Returns:
        figura Plotly com o gráfico de pizza
    """
    # Verifica se os dados de tipo de celular estão disponíveis
    if "tipo_celular" in df_pedestres.columns:
        # Normaliza a coluna de possui_app para facilitar filtragem
        df_pedestres['possui_app_str'] = (df_pedestres['possui_app_picmoney']
                                        .astype(str).str.lower().str.strip())
        
        # Filtra apenas usuários que têm o app
        df_d = df_pedestres[df_pedestres['possui_app_str']
                          .isin(['true', '1', '1.0', 'sim', 'yes'])]
        
        # Conta usuários únicos por tipo de dispositivo
        dd = (df_d.groupby("tipo_celular", as_index=False)["celular"]
              .nunique()
              .rename(columns={"celular":"usuarios"}))
        
        # Cria o gráfico de pizza
        fig = px.pie(dd, 
                    values="usuarios", 
                    names="tipo_celular", 
                    title="Distribuição de dispositivos entre usuários que têm o app")
    else:
        # Cria gráfico alternativo se dados não estiverem disponíveis
        fig = px.pie(values=[1], 
                    names=['Dados não disponíveis'], 
                    title="Distribuição de dispositivos - Dados não disponíveis")
    
    # Ajusta o layout
    fig.update_layout(template='plotly_white')
    return fig

# Gráficos estáticos para uso inicial (remova se não for usar)
fig_df_resg_seg = criar_grafico_resgates_segmento(df_trans)
fig_df_week = criar_grafico_dia_semana(df_trans)
fig_df_hm = criar_grafico_heatmap(df_trans)
fig_df_age_coupon = criar_grafico_faixa_etaria(df_trans, df_players)
fig_df_ht = criar_grafico_segmento_tipo(df_trans)
fig_df_d = criar_grafico_dispositivos(df_pedestres)