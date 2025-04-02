import tkinter as tk
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os
import re
import webbrowser
import platform
import subprocess

# Função para validar email
def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Função para validar telefone (mínimo 9 dígitos numéricos)
def validar_telefone(telefone):
    return re.match(r"\d{9,}", telefone)

# Função para abrir arquivo automaticamente
def abrir_arquivo(caminho):
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(caminho)
        elif sistema == "Darwin":  # macOS
            subprocess.call(["open", caminho])
        else:  # Linux e outros
            subprocess.call(["xdg-open", caminho])
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo: {e}")

# Função para gerar PDF e TXT com layout aprimorado
def gerar_relatorios():
    # Obter os dados do formulário
    dados = {campo: entradas[campo].get() for campo in entradas}

    # Validações
    if not dados["Nome do ficheiro"]:
        messagebox.showwarning("Atenção", "O campo 'Nome do ficheiro' é obrigatório.")
        return

    if not validar_email(dados["Email"]):
        messagebox.showwarning("Email inválido", "Por favor, insira um email válido.")
        return

    if not validar_telefone(dados["Telefone"]):
        messagebox.showwarning("Telefone inválido", "Por favor, insira um número de telefone válido (mínimo 9 dígitos).")
        return

    # Criar pasta para salvar os relatórios
    pasta = "FichasTecnicas"
    os.makedirs(pasta, exist_ok=True)
    nome_base = dados["Nome do ficheiro"].replace(" ", "_")
    caminho_pdf = os.path.join(pasta, f"Ficha_Técnica_{nome_base}.pdf")
    caminho_txt = os.path.join(pasta, f"Ficha_Técnica_{nome_base}.txt")

    # Gerar PDF
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    width, height = A4
    margin = 50

    # Cabeçalho centralizado
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - margin, "Ficha Técnica para Gráfica")
    # Linha divisória abaixo do cabeçalho
    c.setLineWidth(1)
    c.line(margin, height - margin - 10, width - margin, height - margin - 10)

    y = height - margin - 40
    # Exibe cada campo em duas colunas: campo e valor
    for campo in campos:
        valor = dados[campo]
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"{campo}:")
        c.setFont("Helvetica", 12)
        c.drawString(margin + 150, y, valor)
        y -= 25
        if y < margin:  # Se a página acabar, inicia nova página
            c.showPage()
            y = height - margin - 40

    c.save()

    # Gerar arquivo TXT
    try:
        with open(caminho_txt, 'w', encoding='utf-8') as f:
            f.write("Ficha Técnica para Gráfica\n")
            f.write("=" * 40 + "\n\n")
            for campo in campos:
                valor = dados[campo]
                f.write("{:<30}: {}\n".format(campo, valor))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar arquivo TXT: {e}")
        return

    messagebox.showinfo("Sucesso", f"PDF e TXT gerados com sucesso em:\n{os.path.abspath(pasta)}")
    abrir_arquivo(caminho_pdf)
    btn_email.config(state="normal")

# Função para enviar PDF por email (abre cliente de email)
def enviar_email():
    email = entradas["Email"].get()
    assunto = "Ficha Técnica para Gráfica"
    corpo = "Segue em anexo a ficha técnica do projeto editorial."
    ficheiro = f"Ficha_Técnica_{entradas['Nome do ficheiro'].get().replace(' ', '_')}.pdf"
    caminho_pdf = os.path.abspath(os.path.join("FichasTecnicas", ficheiro))
    url = f"mailto:{email}?subject={assunto}&body={corpo}"
    webbrowser.open(url)

# Lista de campos – agora com Email e Telefone separados
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

# Criação da interface com Tkinter
root = tk.Tk()
root.title("Ficha Técnica Editorial")
root.geometry("650x800")
root.configure(bg="#f0f0f0")  # Fundo cinza claro

tk.Label(root, text="Ficha Técnica Editorial", font=("Helvetica", 18, "bold"), bg="#f0f0f0").pack(pady=20)

frame = tk.Frame(root, bg="#f0f0f0")
frame.pack()

entradas = {}
for campo in campos:
    tk.Label(frame, text=campo + ":", anchor="w", bg="#f0f0f0", font=("Helvetica", 11)).pack(fill="x", padx=40)
    entry = tk.Entry(frame, font=("Helvetica", 11))
    entry.pack(fill="x", padx=40, pady=5)
    entradas[campo] = entry

# Preenche a data automaticamente
entradas["Data"].insert(0, datetime.now().strftime("%d/%m/%Y"))

tk.Button(root, text="Gerar PDF e TXT", command=gerar_relatorios,
          font=("Helvetica", 12, "bold"), bg="#222", fg="white", padx=10, pady=5).pack(pady=20)

btn_email = tk.Button(root, text="Enviar PDF por Email", command=enviar_email,
                      font=("Helvetica", 12), bg="#555", fg="white", padx=10, pady=5, state="disabled")
btn_email.pack(pady=5)

root.mainloop()
