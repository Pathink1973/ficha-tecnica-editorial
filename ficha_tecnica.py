import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os
import re
import platform
import subprocess

# Funções auxiliares
def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validar_telefone(telefone):
    return re.match(r"\d{9,}", telefone)

def abrir_arquivo(caminho):
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(caminho)
        elif sistema == "Darwin":
            subprocess.call(["open", caminho])
        else:
            subprocess.call(["xdg-open", caminho])
    except Exception as e:
        st.error(f"Não foi possível abrir o arquivo: {e}")

def gerar_pdf_txt(dados):
    pasta = "FichasTecnicas"
    os.makedirs(pasta, exist_ok=True)
    nome_base = dados["Nome do ficheiro"].replace(" ", "_")
    caminho_pdf = os.path.join(pasta, f"Ficha_Técnica_{nome_base}.pdf")
    caminho_txt = os.path.join(pasta, f"Ficha_Técnica_{nome_base}.txt")

    # PDF
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    width, height = A4
    margin = 50
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - margin, "Ficha Técnica para Gráfica")
    c.setLineWidth(1)
    c.line(margin, height - margin - 10, width - margin, height - margin - 10)
    y = height - margin - 40

    for campo in campos:
        valor = dados.get(campo, "")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"{campo}:")
        c.setFont("Helvetica", 12)
        c.drawString(margin + 150, y, valor)
        y -= 25
        if y < margin:
            c.showPage()
            y = height - margin - 40
    c.save()

    # TXT
    try:
        with open(caminho_txt, 'w', encoding='utf-8') as f:
            f.write("Ficha Técnica para Gráfica\n")
            f.write("=" * 40 + "\n\n")
            for campo in campos:
                valor = dados.get(campo, "")
                f.write("{:<30}: {}\n".format(campo, valor))
    except Exception as e:
        st.error(f"Erro ao gerar arquivo TXT: {e}")
        return None, None

    return caminho_pdf, caminho_txt

# Campos
campos = [
    "Nome do ficheiro",
    "Nome do designer",
    "Formato do livro",
    "Cores aplicadas",
    "Dimensão do livro",
    "Dimensão da capa",
    "Acabamentos do miolo",
    "Acabamentos da capa",
    "Fontes usadas",
    "Ficheiro PDF vs Editável",
    "Data",
    "Email",
    "Telefone"
]

# Interface Streamlit
st.set_page_config(page_title="Ficha Técnica Editorial", layout="centered")
st.title("📝 Ficha Técnica Editorial")

with st.form("formulario"):
    dados = {}
    for campo in campos:
        if campo == "Data":
            dados[campo] = st.text_input(campo, datetime.now().strftime("%d/%m/%Y"))
        else:
            dados[campo] = st.text_input(campo)

    submit = st.form_submit_button("Gerar PDF e TXT")

# Ação ao submeter
if submit:
    if not dados["Nome do ficheiro"]:
        st.warning("O campo 'Nome do ficheiro' é obrigatório.")
    elif not validar_email(dados["Email"]):
        st.warning("Por favor, insira um email válido.")
    elif not validar_telefone(dados["Telefone"]):
        st.warning("Por favor, insira um número de telefone válido (mínimo 9 dígitos).")
    else:
        pdf_path, txt_path = gerar_pdf_txt(dados)
        if pdf_path and txt_path:
            st.success("Relatórios gerados com sucesso!")
            st.download_button("📄 Baixar PDF", open(pdf_path, "rb"), file_name=os.path.basename(pdf_path))
            st.download_button("📄 Baixar TXT", open(txt_path, "rb"), file_name=os.path.basename(txt_path))

            # Pré-preenchimento do email
            mailto = f"mailto:{dados['Email']}?subject=Ficha Técnica para Gráfica&body=Segue em anexo a ficha técnica do projeto editorial."
            st.markdown(f"[📧 Enviar por email]({mailto})", unsafe_allow_html=True)
