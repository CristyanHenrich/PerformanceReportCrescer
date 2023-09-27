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


# Função atualizada para gerar gráfico de barras
def gerar_grafico_barras(acertos, maximo, nome, prova, title):
    labels = list(acertos.keys())
    valores_acertos = list(acertos.values())
    valores_erros = [maximo[materia] - acertos[materia] for materia in labels]
    max_valores = [maximo[materia] for materia in labels]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.25  # Diminuída a largura da barra
    index = np.arange(len(labels))
    
    bar1 = ax.bar(index - bar_width, valores_acertos, bar_width, label='Acertos', color='green')
    bar2 = ax.bar(index, valores_erros, bar_width, label='Erros', color='red')
    bar3 = ax.bar(index + bar_width, max_valores, bar_width, label='Total', color='grey', alpha=0.5)
    
    ax.set_xlabel('Matérias')
    ax.set_ylabel('Quantidade')
    ax.set_title(f'Desempenho na {title}')
    ax.set_xticks(index)
    ax.set_xticklabels(labels, rotation=0, ha='right')
    ax.legend()
    
    # Adicionar o número em cima de cada barra
    for bar in bar1:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom', fontsize=9)
    
    for bar in bar2:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom', fontsize=9)
    
    for bar in bar3:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 2), ha='center', va='bottom', fontsize=9)
    
    # Adicionar fundo quadriculado mais aparente
    ax.grid(True, which='both', linestyle='--', linewidth=0.7, axis='y', alpha=0.9)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(f"{nome}_{prova}.png")
    plt.close()

# Função atualizada para gerar gráfico de aproveitamento
def gerar_grafico_aproveitamento(acertos, maximo, nome, prova, title):
    materias = list(acertos.keys())
    aproveitamentos = [(acertos[materia] / maximo[materia]) * 100 for materia in materias]
    total_acertos = sum(acertos.values())
    total_questoes = sum(maximo.values())
    aproveitamento_geral = (total_acertos / total_questoes) * 100
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.stem(materias, aproveitamentos, basefmt=" ", label='Por matéria', linefmt='-c', markerfmt='oc')
    ax.axhline(y=aproveitamento_geral, color='purple', linestyle='-', label=f'Geral: {aproveitamento_geral:.2f}%')
    
    for i, txt in enumerate(aproveitamentos):
        ax.text(i, txt + 3, f"{txt:.2f}%", ha='center', va='bottom', color='c')
    
    ax.set_ylim(0, 110)
    ax.set_ylabel('% de Aproveitamento')
    ax.set_title(f'Aproveitamento na {title}')
    
    # Adicionar fundo quadriculado mais aparente
    ax.grid(True, which='both', linestyle='--', linewidth=0.7, axis='y', alpha=0.9)
    ax.set_axisbelow(True)
    
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f"{nome}_Aproveitamento_{prova}.png")
    plt.close()

def gerar_pdf(nome, respostas1, respostas2, gabarito1, gabarito2):
    pdf_path = f'pdfs/resultado_{nome}.pdf'
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cabeçalho
    pdf.image('img/logo.png', x=10, y=8, w=30)
    pdf.ln(15)  # Reduzindo o espaço após a logo
    pdf.line(13, pdf.get_y(), 200, pdf.get_y())  # Linha divisória
    
    # Nome do aluno
    pdf.set_font('Arial', 'B', 14)
    pdf.ln(2)
    pdf.cell(0, 10, nome, 0, 1, 'C')
    pdf.ln(2)  # Espaço após o nome
    
    # Gráficos de acertos e erros
    pdf.image(f"{nome}_Prova 1.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"{nome}_Prova 2.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.ln(70)  # Espaço após os gráficos
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha divisória
    pdf.ln(10)  # Espaço após a linha

    # Gráficos de aproveitamento
    pdf.image(f"{nome}_Aproveitamento_Prova 1.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"{nome}_Aproveitamento_Prova 2.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.ln(70)  # Espaço após os gráficos
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Linha divisória
    pdf.ln(5)  # Espaço após a linha

     # Gabarito
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Prova Português, História e Geografia', 0, 1, 'C')
    pdf.set_font('Arial', '', 8)  # Reduzindo ainda mais a fonte
    col_width = 45  # Largura da coluna
    bolinha_diameter = 4
    space_between = 5  # Espaço entre as questões
    for idx, (resposta, gab) in enumerate(zip(respostas1, gabarito1), 1):
        cor = (0, 128, 0) if resposta == gab else (255, 0, 0)
        y = pdf.get_y()
        pdf.set_fill_color(*cor)
        pdf.ellipse(10 + (idx-1)%4*col_width, y, bolinha_diameter, bolinha_diameter, style='F')
        pdf.set_xy(10 + (idx-1)%4*col_width + bolinha_diameter + 2, y)  # Reposicionando o cursor
        pdf.cell(col_width-10, space_between, f'Questão {idx}: {resposta}', 0, (idx%4==0), 'L')
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Prova Matemática, Ciências e Inglês', 0, 1, 'C')
    pdf.set_font('Arial', '', 8)
    for idx, (resposta, gab) in enumerate(zip(respostas2, gabarito2), 1):
        cor = (0, 128, 0) if resposta == gab else (255, 0, 0)
        y = pdf.get_y()
        pdf.set_fill_color(*cor)
        pdf.ellipse(10 + (idx-1)%4*col_width, y, bolinha_diameter, bolinha_diameter, style='F')
        pdf.set_xy(10 + (idx-1)%4*col_width + bolinha_diameter + 2, y)  # Reposicionando o cursor
        pdf.cell(col_width-10, space_between, f'Questão {idx}: {resposta}', 0, (idx%4==0), 'L')
    
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

    gerar_grafico_barras(acertos1, maximo1, nome, 'Prova 1', 'Prova Português, História e Geografia')
    gerar_grafico_barras(acertos2, maximo2, nome, 'Prova 2', 'Prova Matemática, Ciências e Inglês')
    
    gerar_grafico_aproveitamento(acertos1, maximo1, nome, 'Prova 1', 'Prova Português, História e Geografia')
    gerar_grafico_aproveitamento(acertos2, maximo2, nome, 'Prova 2', 'Prova Matemática, Ciências e Inglês')

    gerar_pdf(nome, respostas1, respostas2, gabarito1, gabarito2)
