from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
from app import app
import plotly.io as pio
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io
import base64

def gerar_layout_botao():
    return html.Div([
        dbc.Button(
            [html.I(className="fas fa-file-pdf mr-2"), "Gerar Relatório PDF"],
            id="btn-gerar-pdf",
            color="danger",
            className="mt-4"
        ),
        html.Div(id="download-pdf")
    ])

@app.callback(
    Output("download-pdf", "children"),
    Input("btn-gerar-pdf", "n_clicks"),
    [
        State("graph-receita-segmento", "figure"),
        State("graph-scatter", "figure"),
        State("graph-ticket-loja", "figure"),
        State("graph-distribuicao", "figure"),
        State("kpi-cards-cfo", "children"),
    ],
    prevent_initial_call=True
)
def gerar_relatorio_pdf(n_clicks, fig_receita, fig_scatter, fig_ticket, fig_distribuicao, kpis):
    """Gera relatório em PDF com todos os gráficos e KPIs da página CFO"""
    if not n_clicks:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Título
    story.append(Paragraph("<b>Relatório Financeiro - CFO Dashboard</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    
    # Adicionar KPIs em formato de texto
    story.append(Paragraph("<b>KPIs Financeiros:</b>", styles["Heading2"]))
    for card in kpis:
        if isinstance(card, dict) and "props" in card:
            try:
                texto = card["props"]["children"][0]["props"]["children"][0]["props"]["children"][1]["props"]["children"][1]["props"]["children"]
                story.append(Paragraph(str(texto), styles["Normal"]))
            except Exception:
                continue
    story.append(Spacer(1, 20))

    # Função auxiliar para adicionar gráficos
    def adicionar_figura(fig, titulo):
        img_bytes = pio.to_image(fig, format="png", width=800, height=500)
        img = Image(io.BytesIO(img_bytes), width=400, height=250)
        story.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
        story.append(img)
        story.append(Spacer(1, 20))

    # Adiciona os gráficos no PDF
    adicionar_figura(fig_receita, "Receita por Segmento de Negócio")
    adicionar_figura(fig_scatter, "Análise: Valor Cupom × Valor Compra")
    adicionar_figura(fig_ticket, "Ticket Médio por Estabelecimento")
    adicionar_figura(fig_distribuicao, "Distribuição de Cupons")

    # Finaliza o PDF
    doc.build(story)
    buffer.seek(0)
    pdf_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return html.A(
        "📥 Baixar Relatório PDF",
        href=f"data:application/pdf;base64,{pdf_base64}",
        download="relatorio_cfo.pdf",
        className="btn btn-success mt-3"
    )
