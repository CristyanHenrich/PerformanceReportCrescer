import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np
from matplotlib.colors import to_rgb

def limpar_dados(df):
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    df = df.fillna('')
    return df

def calcular_acertos(aluno, gabarito, materias):
    acertos = {}
    total_acertos = 0
    for materia, questoes in materias.items():
        acertos_materia = sum([1 for q, (r, g) in enumerate(zip(aluno[:len(gabarito)], gabarito), 1) if r == g and r.strip() != '' and q in questoes])
        acertos[materia] = acertos_materia
        total_acertos += acertos_materia
    return acertos, total_acertos

def calcular_acertos_turma(prova, gabarito, materias):
    total_acertos_turma = {}
    for materia, questoes in materias.items():
        total_acertos = sum(
            [1 for _, aluno in prova.iterrows() for q, (r, g) in enumerate(zip(aluno[1:].values[:len(gabarito)], gabarito), 1) 
             if r == g and r.strip() != '' and q in questoes]
        )
        total_acertos_turma[materia] = total_acertos
    return total_acertos_turma

def adicionar_tabela_acertos(pdf, acertos_turma, maximo, prova, num_alunos):
    col_widths = [95, 47.5, 47.5]  # Distribuição para ocupar toda a largura (190mm)
    col_names = ["Matéria", "Total de Questões", "Total de Acertos"]
    y_before = pdf.get_y()
    
    # Título da tabela
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Resumo dos Acertos na {prova}", 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    
    # Cabeçalho da tabela
    for col_width, col_name in zip(col_widths, col_names):
        pdf.cell(col_width, 10, col_name, 1)
    pdf.ln()

    # Preenchendo a tabela
    for materia, total_questoes_materia in maximo.items():
        total_questoes = total_questoes_materia * num_alunos
        pdf.cell(col_widths[0], 10, materia, 1)
        pdf.cell(col_widths[1], 10, str(total_questoes), 1)
        pdf.cell(col_widths[2], 10, str(acertos_turma[materia]), 1)
        pdf.ln()

    y_after = pdf.get_y()
    space_needed = y_after - y_before
    if space_needed > 270:
        pdf.add_page()


def gerar_grafico_barras_geral(acertos, maximo, prova):
    labels = list(acertos.keys())
    valores_acertos = [acertos[materia]['mean'] for materia in labels]
    max_valores = [maximo[materia] for materia in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(labels, valores_acertos, color='green', alpha=0.7)
    ax.bar(labels, max_valores, color='grey', alpha=0.5, fill=False, linestyle='dashed')

    ax.set_xlabel('Matérias')
    ax.set_ylabel('Quantidade Média de Acertos')
    ax.set_title(f'Desempenho Médio na {prova}')
    ax.set_ylim(0, max(max_valores) + 1)

    for i, v in enumerate(valores_acertos):
        ax.text(i, v + 0.2, f"{v:.2f}", ha='center', va='bottom', fontsize=9)

    ax.grid(True, which='both', linestyle='--', linewidth=0.7, axis='y', alpha=0.9)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(f"Desempenho_Medio_{prova}.png")
    plt.close()

def gerar_grafico_aproveitamento_geral(acertos, maximo, prova):
    labels = list(acertos.keys())
    aproveitamentos = [(acertos[materia]['mean'] / maximo[materia]) * 100 for materia in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.stem(labels, aproveitamentos, basefmt=" ", linefmt='-c', markerfmt='oc', label='Matérias')
    
    # Adicionando linha de média de acertos
    media_aproveitamento = np.mean(aproveitamentos)
    ax.axhline(media_aproveitamento, color='blue', linestyle='dashed', linewidth=1, label=f'Média: {media_aproveitamento:.2f}%')

    ax.set_ylim(0, 110)
    ax.set_ylabel('% de Aproveitamento Médio')
    ax.set_title(f'Aproveitamento Médio na {prova}')

    for i, txt in enumerate(aproveitamentos):
        ax.text(i, txt + 3, f"{txt:.2f}%", ha='center', va='bottom', color='c')

    ax.grid(True, which='both', linestyle='--', linewidth=0.7, axis='y', alpha=0.9)
    ax.set_axisbelow(True)
    
    # Adicionando a legenda
    ax.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig(f"Aproveitamento_Medio_{prova}.png")
    plt.close()



def map_color(value, min_val, max_val):
    # Mapeia um valor no intervalo [min_val, max_val] para um valor no intervalo [0, 1]
    normalized = (value - min_val) / (max_val - min_val)
    
    # Cores de início (amarelo) e fim (verde)
    color_start = np.array(to_rgb('yellow'))
    color_end = np.array(to_rgb('green'))
    
    # Interpolação linear entre as cores
    mapped_color = (1 - normalized) * color_start + normalized * color_end
    return mapped_color

def gerar_histograma(acertos, maximo, prova):
    total_acertos = [sum(acertos.values()) for acertos in acertos]
    max_questoes = sum(maximo.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    
    n, bins, patches = ax.hist(total_acertos, bins=range(0, max_questoes + 2), edgecolor='black', alpha=0.7)
    
    # Colorindo as barras
    for patch, left, right in zip(patches, bins[:-1], bins[1:]):
        color = map_color(left, 0, max_questoes)
        patch.set_facecolor(color)
    
    ax.set_xlabel('Número de Acertos')
    ax.set_ylabel('Número de Alunos')
    ax.set_title(f'Distribuição de Acertos na {prova}')

    ax.grid(True, which='both', linestyle='--', linewidth=0.7, axis='y', alpha=0.9)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(f"Histograma_{prova}.png")
    plt.close()


def gerar_pdf_geral(acertos1, acertos2, maximo1, maximo2):
    pdf_path = 'pdfs/resultado_geral.pdf'

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Cabeçalho
    pdf.image('img/logo.png', x=10, y=8, w=30)
    pdf.ln(15)
    pdf.line(13, pdf.get_y(), 200, pdf.get_y())

    # Título
    pdf.set_font('Arial', 'B', 14)
    pdf.ln(2)
    pdf.cell(0, 10, "Relatório Geral da Turma", 0, 1, 'C')
    pdf.ln(2)

    # Gráficos de desempenho e aproveitamento médio
    pdf.image(f"Desempenho_Medio_Prova Português, História e Geografia.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"Desempenho_Medio_Prova Matemática, Ciências e Inglês.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.ln(70)

    pdf.image(f"Aproveitamento_Medio_Prova Português, História e Geografia.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"Aproveitamento_Medio_Prova Matemática, Ciências e Inglês.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.ln(70)

    # Histogramas de distribuição de acertos
    pdf.image(f"Histograma_Prova Português, História e Geografia.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"Histograma_Prova Matemática, Ciências e Inglês.png", x = 105, y = pdf.get_y(), w = 90)

    pdf.output(pdf_path)

    # Remover imagens dos gráficos
    os.remove(f"Desempenho_Medio_Prova Português, História e Geografia.png")
    os.remove(f"Desempenho_Medio_Prova Matemática, Ciências e Inglês.png")
    os.remove(f"Aproveitamento_Medio_Prova Português, História e Geografia.png")
    os.remove(f"Aproveitamento_Medio_Prova Matemática, Ciências e Inglês.png")
    os.remove(f"Histograma_Prova Português, História e Geografia.png")
    os.remove(f"Histograma_Prova Matemática, Ciências e Inglês.png")

    return pdf_path

def relatorio_geral(prova1, prova2, gabarito1, gabarito2, materias1, materias2):
    acertos_gerais1 = []
    acertos_gerais2 = []
    for _, aluno in prova1.iterrows():
        respostas1 = aluno[1:].values
        respostas2 = prova2[prova2['Aluno'] == aluno['Aluno']].iloc[0, 1:].values

        acertos1, _ = calcular_acertos(respostas1, gabarito1, materias1)
        acertos2, _ = calcular_acertos(respostas2, gabarito2, materias2)

        acertos_gerais1.append(acertos1)
        acertos_gerais2.append(acertos2)

    acertos_medios1 = {materia: {} for materia in materias1.keys()}
    acertos_medios2 = {materia: {} for materia in materias2.keys()}

    for materia in materias1:
        acertos_medios1[materia]['mean'] = np.mean([acertos[materia] for acertos in acertos_gerais1])
    for materia in materias2:
        acertos_medios2[materia]['mean'] = np.mean([acertos[materia] for acertos in acertos_gerais2])

    maximo1 = {materia: len(questoes) for materia, questoes in materias1.items()}
    maximo2 = {materia: len(questoes) for materia, questoes in materias2.items()}

    # Geração dos gráficos
    gerar_grafico_barras_geral(acertos_medios1, maximo1, 'Prova Português, História e Geografia')
    gerar_grafico_barras_geral(acertos_medios2, maximo2, 'Prova Matemática, Ciências e Inglês')
    gerar_grafico_aproveitamento_geral(acertos_medios1, maximo1, 'Prova Português, História e Geografia')
    gerar_grafico_aproveitamento_geral(acertos_medios2, maximo2, 'Prova Matemática, Ciências e Inglês')
    gerar_histograma(acertos_gerais1, maximo1, 'Prova Português, História e Geografia')
    gerar_histograma(acertos_gerais2, maximo2, 'Prova Matemática, Ciências e Inglês')

    pdf = FPDF()
    pdf.add_page()

    # Inserção dos gráficos no PDF
    pdf.image(f"Desempenho_Medio_Prova Português, História e Geografia.png", x=10, y=pdf.get_y(), w=90)
    pdf.image(f"Desempenho_Medio_Prova Matemática, Ciências e Inglês.png", x=105, y=pdf.get_y(), w=90)
    pdf.ln(70)
    pdf.image(f"Aproveitamento_Medio_Prova Português, História e Geografia.png", x=10, y=pdf.get_y(), w=90)
    pdf.image(f"Aproveitamento_Medio_Prova Matemática, Ciências e Inglês.png", x=105, y=pdf.get_y(), w=90)
    pdf.ln(70)
    pdf.image(f"Histograma_Prova Português, História e Geografia.png", x=10, y=pdf.get_y(), w=90)
    pdf.image(f"Histograma_Prova Matemática, Ciências e Inglês.png", x=105, y=pdf.get_y(), w=90)
    pdf.ln(70)

    # Inserção da tabela no PDF
    acertos_turma1 = calcular_acertos_turma(prova1, gabarito1, materias1)
    acertos_turma2 = calcular_acertos_turma(prova2, gabarito2, materias2)

    adicionar_tabela_acertos(pdf, acertos_turma1, maximo1, 'Prova Português, História e Geografia', len(prova1))
    pdf.ln(10)
    adicionar_tabela_acertos(pdf, acertos_turma2, maximo2, 'Prova Matemática, Ciências e Inglês', len(prova2))


    # Geração do PDF
    pdf_path = 'pdfs/resultado_geral.pdf'
    pdf.output(pdf_path, 'F')

    # Remoção dos gráficos para economizar espaço
    os.remove(f"Desempenho_Medio_Prova Português, História e Geografia.png")
    os.remove(f"Desempenho_Medio_Prova Matemática, Ciências e Inglês.png")
    os.remove(f"Aproveitamento_Medio_Prova Português, História e Geografia.png")
    os.remove(f"Aproveitamento_Medio_Prova Matemática, Ciências e Inglês.png")
    os.remove(f"Histograma_Prova Português, História e Geografia.png")
    os.remove(f"Histograma_Prova Matemática, Ciências e Inglês.png")

    return pdf_path

# Carregar os dados
prova1 = limpar_dados(pd.read_csv('prova1.csv'))
prova2 = limpar_dados(pd.read_csv('prova2.csv'))

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

# Chamar a função para gerar o relatório geral
relatorio_geral(prova1, prova2, gabarito1, gabarito2, materias1, materias2)

