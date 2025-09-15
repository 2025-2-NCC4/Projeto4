from utils.db_utils import df_massa, df_pedestres, df_players, df_trans
import pandas as pd
import plotly.express as px

#---------------------------------------------------------- CFO ----------------------------------------------------------#

# Receita por segmento (tipo_loja) — Bar horizontal
df_seg = (df_massa
          .dropna(subset=["tipo_loja","valor_compra"])
          .groupby("tipo_loja", as_index=False)["valor_compra"].sum()
          .sort_values("valor_compra", ascending=True))
fig_df_seg = px.bar(df_seg, x="valor_compra", y="tipo_loja", orientation="h",
             title="Receita total por segmento (tipo_loja)",
             labels={"valor_compra":"Receita (R$)","tipo_loja":"Segmento"})
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
fig_df_v = px.histogram(df_v, x="valor_cupom", nbins=10, title="Distribuição de valor dos cupons resgatados", text_auto=True)
fig_df_v.update_xaxes(title="Valor do cupom (R$)")
fig_df_v.update_layout(
    bargap=0.2  # controla o espaço entre as barras (0 = sem espaço, 1 = só espaço)
)






# --------------------------------------------------------- CEO --------------------------------------------------------#

# Resgates por categoria_estabelecimento
df_resg_seg = (df_trans
               .dropna(subset=["categoria_estabelecimento","id_cupom"])
               .groupby("categoria_estabelecimento", as_index=False)["id_cupom"].count()
               .rename(columns={"id_cupom":"resgates"})
               .sort_values("resgates", ascending=False))
fig_df_resg_seg = px.bar(df_resg_seg, x="categoria_estabelecimento", y="resgates",
             title="Resgates por segmento (categoria_estabelecimento)",  text_auto=True,)
fig_df_resg_seg.update_layout(xaxis_tickangle=-45)

# Dia da semana mais resgates (df_trans)
df_week = (df_trans
           .dropna(subset=["weekday","id_cupom"])
           .groupby("weekday", as_index=False)["id_cupom"].count()
           .rename(columns={"id_cupom":"resgates"}))

# ordenar por valor em ordem decrescente
df_week = df_week.sort_values("resgates", ascending=False)

fig_df_week = px.bar(
    df_week, 
    x="weekday", 
    y="resgates", 
    title="Resgates por dia da semana", 
    text_auto=True
)

# Heatmap de hora x estabelecimento (contagem de resgates)
df_hm = df_trans.dropna(subset=["hour","nome_estabelecimento","id_cupom"])
df_hm = df_hm.groupby(["hour","nome_estabelecimento"], as_index=False)["id_cupom"].count().rename(columns={"id_cupom":"count"})
# Pivot para heatmap
hm = df_hm.pivot(index="hour", columns="nome_estabelecimento", values="count").fillna(0)
fig_df_hm = px.imshow(hm,
                labels=dict(x="Estabelecimento", y="Hora do dia", color="Resgates"),
                title="Heatmap: hora do resgate x estabelecimento",
                aspect="auto",)


#faixa etaria x cupons
# Merge transactions with players (idade/faixa)
df_tx = df_trans.merge(df_players[["celular","idade"]], on="celular", how="left")
df_tx["idade"] = pd.to_numeric(df_tx["idade"], errors="coerce")
bins = [0,17,24,34,44,54,64,200]
labels = ["<=17","18-24","25-34","35-44","45-54","55-64","65+"]
df_tx["faixa_etaria"] = pd.cut(df_tx["idade"], bins=bins, labels=labels)
# agrupar por faixa e tipo_cupom
df_age_coupon = (df_tx.dropna(subset=["faixa_etaria","tipo_cupom"])
                 .groupby(["faixa_etaria","tipo_cupom"], as_index=False)["id_cupom"].count()
                 .rename(columns={"id_cupom":"resgates"}))
fig_df_age_coupon = px.bar(df_age_coupon, x="faixa_etaria", y="resgates", color="tipo_cupom",
             barmode="group", title="Resgates por faixa etária e tipo de cupom", text_auto=True,)

# pivot categoria_estabelecimento x tipo_cupom
df_ht = (df_trans.dropna(subset=["categoria_estabelecimento","tipo_cupom", "id_cupom"])
         .groupby(["categoria_estabelecimento","tipo_cupom"], as_index=False)["id_cupom"].count())
pivot = df_ht.pivot(index="tipo_cupom", columns="categoria_estabelecimento", values="id_cupom").fillna(0)
fig_df_ht = px.imshow(pivot, title="Segmento da loja x Tipo de Cupom (contagem)", labels={"x":"Segmento","y":"Tipo de Cupom","color":"Contagem"})
fig_df_ht.update_layout(height=700)

# pie por tipo_celular (df_pedestres) — filtrar possui_app_picmoney
df_d = df_pedestres[df_pedestres["possui_app_picmoney"].astype(str).isin(["True","true","1","1.0","Sim","sim"])]
if "tipo_celular" in df_d.columns:
    dd = df_d.groupby("tipo_celular", as_index=False)["celular"].nunique().rename(columns={"celular":"usuarios"})
    fig_df_d = px.pie(dd, values="usuarios", names="tipo_celular", title="Distribuição de dispositivos entre usuários que têm o app")
else:
    print("Coluna tipo_celular não encontrada.")






