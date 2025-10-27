# ==================== IMPORTAÇÕES ====================
from utils.db_utils import df_massa, df_pedestres, df_players, df_trans
import pandas as pd
import plotly.express as px

#======================================== GRÁFICOS CFO ========================================

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
    df_seg = (df
              .dropna(subset=["categoria_estabelecimento","valor_cupom"])
              .groupby("categoria_estabelecimento", as_index=False)["valor_cupom"].sum()
              .sort_values("valor_cupom", ascending=True))
    
    fig = px.bar(df_seg, x="valor_cupom", y="categoria_estabelecimento", orientation="h",
                 title="Receita total por segmento",
                 labels={"valor_cupom":"Receita (R$)","categoria_estabelecimento":"Segmento"})
    fig.update_layout(margin=dict(l=150), template='plotly_white')
    return fig

def criar_grafico_scatter(df_massa):
    df_scatter = df_massa.dropna(subset=["valor_cupom","valor_compra"])
    fig = px.scatter(df_scatter, x="valor_cupom", y="valor_compra", trendline="ols",
                     title="Relacionamento: valor do cupom x valor final da compra",
                     labels={"valor_cupom":"Valor do Cupom (R$)","valor_compra":"Valor da Compra (R$)"})
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_ticket_medio(df_massa):
    df_mean = (df_massa.dropna(subset=["nome_loja","valor_compra"])
               .groupby("nome_loja", as_index=False)["valor_compra"].mean()
               .sort_values("valor_compra", ascending=False))
    
    fig = px.bar(df_mean, x="nome_loja", y="valor_compra", 
                 title="Valor médio de venda por loja")
    fig.update_layout(xaxis_tickangle=-45, template='plotly_white')
    return fig

def criar_grafico_distribuicao(df):
    df_v = df.dropna(subset=["valor_cupom"])
    fig = px.histogram(df_v, x="valor_cupom", nbins=20, 
                       title="Distribuição de valor dos cupons resgatados")
    fig.update_xaxes(title="Valor do cupom (R$)")
    fig.update_layout(template='plotly_white', bargap=0.1)
    return fig


# ======================================== GRÁFICOS CEO ========================================

def criar_grafico_resgates_segmento(df):
    df_resg_seg = (df
                   .dropna(subset=["categoria_estabelecimento","id_cupom"])
                   .groupby("categoria_estabelecimento", as_index=False)["id_cupom"].count()
                   .rename(columns={"id_cupom":"resgates"})
                   .sort_values("resgates", ascending=False)
                   .head(10))
    
    fig = px.bar(df_resg_seg, x="categoria_estabelecimento", y="resgates",
                 title="Resgates por segmento (Top 10)")
    fig.update_layout(xaxis_tickangle=-45, template='plotly_white')
    return fig

def criar_grafico_dia_semana(df):
    # Garantir que weekday existe
    if 'weekday' not in df.columns:
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['weekday'] = df['data'].dt.day_name()
        weekday_map = {
            'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        df['weekday'] = df['weekday'].map(weekday_map)
    
    df_week = (df.dropna(subset=["weekday","id_cupom"])
               .groupby("weekday", as_index=False)["id_cupom"].count()
               .rename(columns={"id_cupom":"resgates"}))
    df_week = df_week.sort_values("resgates", ascending=False)
    
    fig = px.bar(df_week, x="weekday", y="resgates", title="Resgates por dia da semana")
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_heatmap(df):
    # Garantir que hour existe
    if 'hour' not in df.columns:
        df['hour'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.hour
    
    df_hm = df.dropna(subset=["hour","categoria_estabelecimento","id_cupom"])
    df_hm = df_hm.groupby(["hour","categoria_estabelecimento"], as_index=False)["id_cupom"].count().rename(columns={"id_cupom":"count"})
    
    top_categorias = df_hm.groupby("categoria_estabelecimento")["count"].sum().nlargest(15).index
    df_hm = df_hm[df_hm["categoria_estabelecimento"].isin(top_categorias)]
    
    hm = df_hm.pivot(index="hour", columns="categoria_estabelecimento", values="count").fillna(0)
    
    fig = px.imshow(hm, title="Heatmap: hora do resgate x categoria", aspect="auto")
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_faixa_etaria(df, df_players):
    df_tx = df.merge(df_players[["celular","idade"]], on="celular", how="left")
    df_tx["idade"] = pd.to_numeric(df_tx["idade"], errors="coerce")
    bins = [0,17,24,34,44,54,64,200]
    labels = ["<=17","18-24","25-34","35-44","45-54","55-64","65+"]
    
    # CORREÇÃO: Removido o parâmetro 'observed'
    df_tx["faixa_etaria"] = pd.cut(df_tx["idade"], bins=bins, labels=labels)
    
    df_age_coupon = (df_tx.dropna(subset=["faixa_etaria","tipo_cupom"])
                     .groupby(["faixa_etaria","tipo_cupom"], as_index=False)["id_cupom"].count()
                     .rename(columns={"id_cupom":"resgates"}))
    
    fig = px.bar(df_age_coupon, x="faixa_etaria", y="resgates", color="tipo_cupom",
                 barmode="group", title="Resgates por faixa etária e tipo de cupom")
    fig.update_layout(template='plotly_white')
    return fig

def criar_grafico_segmento_tipo(df):
    df_ht = (df.dropna(subset=["categoria_estabelecimento","tipo_cupom", "id_cupom"])
             .groupby(["categoria_estabelecimento","tipo_cupom"], as_index=False)["id_cupom"].count())
    pivot = df_ht.pivot(index="tipo_cupom", columns="categoria_estabelecimento", values="id_cupom").fillna(0)
    
    fig = px.imshow(pivot, title="Segmento da loja x Tipo de Cupom", aspect="auto")
    fig.update_layout(template='plotly_white', height=500)
    return fig

def criar_grafico_dispositivos(df_pedestres):
    if "tipo_celular" in df_pedestres.columns:
        df_pedestres['possui_app_str'] = df_pedestres['possui_app_picmoney'].astype(str).str.lower().str.strip()
        df_d = df_pedestres[df_pedestres['possui_app_str'].isin(['true', '1', '1.0', 'sim', 'yes'])]
        
        dd = df_d.groupby("tipo_celular", as_index=False)["celular"].nunique().rename(columns={"celular":"usuarios"})
        fig = px.pie(dd, values="usuarios", names="tipo_celular", 
                     title="Distribuição de dispositivos entre usuários que têm o app")
    else:
        fig = px.pie(values=[1], names=['Dados não disponíveis'], 
                     title="Distribuição de dispositivos - Dados não disponíveis")
    
    fig.update_layout(template='plotly_white')
    return fig

# Gráficos estáticos para uso inicial (remova se não for usar)
fig_df_resg_seg = criar_grafico_resgates_segmento(df_trans)
fig_df_week = criar_grafico_dia_semana(df_trans)
fig_df_hm = criar_grafico_heatmap(df_trans)
fig_df_age_coupon = criar_grafico_faixa_etaria(df_trans, df_players)
fig_df_ht = criar_grafico_segmento_tipo(df_trans)
fig_df_d = criar_grafico_dispositivos(df_pedestres)