import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np

# Função para limpar dados
def limpar_dados(df):
    # Remover linhas completamente vazias
    df = df.dropna(how='all')
    # Remover colunas completamente vazias
    df = df.dropna(axis=1, how='all')
    # Substituir NaN por uma string vazia
    df = df.fillna('')
    return df

# Função para calcular acertos
def calcular_acertos(aluno, gabarito, materias):
    acertos = {}
    total_acertos = 0
    for materia, questoes in materias.items():
        acertos_materia = sum([1 for q, (r, g) in enumerate(zip(aluno, gabarito), 1) if r == g and q in questoes])
        acertos[materia] = acertos_materia
        total_acertos += acertos_materia
    return acertos, total_acertos

# Função para gerar gráfico de barras
def gerar_grafico_barras(acertos, maximo, nome, prova):
    labels = list(acertos.keys())
    valores = list(acertos.values())
    max_valores = [maximo[materia] for materia in labels]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.35
    index = np.arange(len(labels))
    
    bar1 = ax.bar(index, valores, bar_width, label='Acertos', color='b')
    bar2 = ax.bar(index + bar_width, max_valores, bar_width, label='Total', color='grey', alpha=0.5)
    
    ax.set_xlabel('Matérias')
    ax.set_ylabel('Quantidade')
    ax.set_title(f'Desempenho na {prova}')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f"{nome}_{prova}.png")
    plt.close()

# Função para gerar gráfico de aproveitamento
def gerar_grafico_aproveitamento(acertos, maximo, nome, prova):
    total_acertos = sum(acertos.values())
    total_questoes = sum(maximo.values())
    aproveitamento = (total_acertos / total_questoes) * 100
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Aproveitamento'], [aproveitamento], color='c')
    ax.set_ylim(0, 100)
    ax.set_ylabel('%')
    ax.set_title(f'Aproveitamento na {prova}')
    
    plt.tight_layout()
    plt.savefig(f"{nome}_Aproveitamento_{prova}.png")
    plt.close()

# Função para gerar PDF
def gerar_pdf(nome, respostas1, respostas2, gabarito1, gabarito2):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Turma: 3º Ano', 0, 1, 'L')
    pdf.cell(0, 10, f'Resultado de {nome}', 0, 1, 'C')
    
    # Gráficos de desempenho
    pdf.image(f"{nome}_Prova 1.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"{nome}_Prova 2.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.ln(65)
    
    # Gráficos de aproveitamento
    pdf.image(f"{nome}_Aproveitamento_Prova 1.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"{nome}_Aproveitamento_Prova 2.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.ln(65)
    
    # Respostas dos alunos
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Respostas Prova 1:', 0, 1)
    for idx, (resposta, gab) in enumerate(zip(respostas1, gabarito1), 1):
        cor = 'green' if resposta == gab else 'red'
        pdf.set_text_color(0, 128, 0) if cor == 'green' else pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 8, f'Questão {idx}: {resposta} (Correta: {gab})', 0, 1)
    
    pdf.ln(10)
    pdf.cell(0, 10, 'Respostas Prova 2:', 0, 1)
    for idx, (resposta, gab) in enumerate(zip(respostas2, gabarito2), 1):
        cor = 'green' if resposta == gab else 'red'
        pdf.set_text_color(0, 128, 0) if cor == 'green' else pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 8, f'Questão {idx}: {resposta} (Correta: {gab})', 0, 1)
    
    # Salvar PDF
    pdf_path = f'pdfs/resultado_{nome}.pdf'
    pdf.output(pdf_path)
    
    # Remover imagens dos gráficos
    os.remove(f"{nome}_Prova 1.png")
    os.remove(f"{nome}_Prova 2.png")
    os.remove(f"{nome}_Aproveitamento_Prova 1.png")
    os.remove(f"{nome}_Aproveitamento_Prova 2.png")
    
    return pdf_path

# Carregar os dados
prova1 = pd.read_csv('prova1.csv')
prova2 = pd.read_csv('prova2.csv')

# Gabaritos
gabarito1 = ['A', 'B', 'C', 'B', 'B', 'C', 'A', 'D', 'B', 'C', 'D', 'A']
gabarito2 = ['B', 'B', 'C', 'C', 'C', 'A', 'B', 'B', 'C', 'D', 'C', 'B', 'D', 'C', 'B', 'D']

# Mapeamento de matérias
materias1 = {
    'Lingua portuguesa': list(range(1, 9)),
    'Historia e Geografia': list(range(9, 13))
}

materias2 = {
    'Matematica': list(range(1, 9)),
    'Ciencias': list(range(9, 13)),
    'Lingua Inglesa': list(range(13, 17))
}

# Limpar os dados
prova1 = limpar_dados(prova1)
prova2 = limpar_dados(prova2)

# Verificar e criar a pasta 'pdfs' se ela não existir
if not os.path.exists('pdfs'):
    os.makedirs('pdfs')

# Processar dados e gerar PDFs
for _, aluno in prova1.iterrows():
    nome = aluno['Aluno']
    respostas1 = aluno[1:].values
    respostas2 = prova2[prova2['Aluno'] == nome].iloc[0, 1:].values

    acertos1, _ = calcular_acertos(respostas1, gabarito1, materias1)
    acertos2, _ = calcular_acertos(respostas2, gabarito2, materias2)

    maximo1 = {materia: len(questoes) for materia, questoes in materias1.items()}
    maximo2 = {materia: len(questoes) for materia, questoes in materias2.items()}

    gerar_grafico_barras(acertos1, maximo1, nome, 'Prova 1')
    gerar_grafico_barras(acertos2, maximo2, nome, 'Prova 2')
    
    gerar_grafico_aproveitamento(acertos1, maximo1, nome, 'Prova 1')
    gerar_grafico_aproveitamento(acertos2, maximo2, nome, 'Prova 2')

    gerar_pdf(nome, respostas1, respostas2, gabarito1, gabarito2)
