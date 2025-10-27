from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
from app import app
import plotly.io as pio
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io
import base64
from concurrent.futures import ThreadPoolExecutor

def gerar_layout_botao_ceo():
    return html.Div([
        dbc.Button(
            [html.I(className="fas fa-file-pdf mr-2"), " Gerar Relatório PDF"],
            id="btn-gerar-pdf-ceo",
            color="danger",
            className="mt-4"
        ),
        dcc.Loading(
            id="loading-pdf-ceo",
            type="circle",
            children=html.Div(id="download-pdf-ceo")
        )
    ])

def converter_figura_para_imagem(fig, width=600, height=350):
    """Converte figura Plotly para imagem PNG de forma otimizada"""
    try:
        img_bytes = pio.to_image(
            fig, 
            format="png", 
            width=width, 
            height=height,
            engine="kaleido"  # Motor mais rápido
        )
        return img_bytes
    except Exception as e:
        print(f"Erro ao converter figura: {e}")
        return None

@app.callback(
    Output("download-pdf-ceo", "children"),
    Input("btn-gerar-pdf-ceo", "n_clicks"),
    [
        State("graph-resg-seg", "figure"),
        State("graph-week", "figure"),
        State("graph-heatmap", "figure"),
        State("graph-age-coupon", "figure"),
        State("graph-ht", "figure"),
        State("graph-devices", "figure"),
        State("kpi-cards", "children"),
    ],
    prevent_initial_call=True
)
def gerar_relatorio_pdf_ceo(n_clicks, fig_resg_seg, fig_week, fig_heatmap, 
                            fig_age_coupon, fig_ht, fig_devices, kpis):
    """Gera relatório em PDF com todos os gráficos e KPIs da página CEO"""
    if not n_clicks:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Título
    story.append(Paragraph("<b>Relatório Estratégico - CEO Dashboard</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    
    # Adicionar KPIs em formato de texto
    story.append(Paragraph("<b>KPIs Estratégicos:</b>", styles["Heading2"]))
    for card in kpis:
        if isinstance(card, dict) and "props" in card:
            try:
                # Extrai informações do KPI
                card_body = card["props"]["children"][0]["props"]["children"][0]["props"]["children"]
                if isinstance(card_body, list) and len(card_body) >= 3:
                    titulo = card_body[1]["props"]["children"]
                    valor = card_body[2]["props"]["children"]
                    story.append(Paragraph(f"{titulo}: {valor}", styles["Normal"]))
            except Exception:
                continue
    story.append(Spacer(1, 20))

    # Lista de figuras para processar em paralelo
    figuras = [
        (fig_resg_seg, "Resgates por Segmento"),
        (fig_week, "Resgates por Dia da Semana"),
        (fig_heatmap, "Heatmap de Atividade"),
        (fig_age_coupon, "Distribuição por Faixa Etária"),
        (fig_ht, "Segmento vs Tipo de Cupom"),
        (fig_devices, "Dispositivos Utilizados")
    ]

    # Converter todas as figuras em paralelo (MUITO MAIS RÁPIDO!)
    with ThreadPoolExecutor(max_workers=6) as executor:
        imagens_bytes = list(executor.map(
            lambda fig: converter_figura_para_imagem(fig[0], 600, 350),
            figuras
        ))

    # Adicionar imagens ao PDF
    for (fig, titulo), img_bytes in zip(figuras, imagens_bytes):
        if img_bytes:
            img = Image(io.BytesIO(img_bytes), width=380, height=220)
            story.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
            story.append(img)
            story.append(Spacer(1, 15))

    # Finaliza o PDF
    doc.build(story)
    buffer.seek(0)
    pdf_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return html.A(
        "📥 Baixar Relatório PDF",
        href=f"data:application/pdf;base64,{pdf_base64}",
        download="relatorio_ceo.pdf",
        className="btn btn-success mt-3"
    )