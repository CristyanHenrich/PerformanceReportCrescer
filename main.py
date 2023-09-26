import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# Verificar e criar a pasta 'pdfs' se ela não existir
if not os.path.exists('pdfs'):
    os.makedirs('pdfs')

# Ler as planilhas
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

def calcular_acertos(aluno, gabarito, materias):
    acertos = {}
    total_acertos = 0
    for materia, questoes in materias.items():
        acertos_materia = sum([1 for q, (r, g) in enumerate(zip(aluno, gabarito), 1) if r == g and q in questoes])
        acertos[materia] = acertos_materia
        total_acertos += acertos_materia
    return acertos, total_acertos

def gerar_grafico(acertos, nome, prova):
    labels = list(acertos.keys())
    sizes = list(acertos.values())
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(f'Desempenho na {prova}')
    plt.savefig(f"{nome}_{prova}.png")
    plt.close()

for _, aluno in prova1.iterrows():
    nome = aluno['Aluno']
    respostas1 = aluno[1:].values
    respostas2 = prova2[prova2['Aluno'] == nome].iloc[0, 1:].values

    acertos1, _ = calcular_acertos(respostas1, gabarito1, materias1)
    acertos2, _ = calcular_acertos(respostas2, gabarito2, materias2)

    gerar_grafico(acertos1, nome, 'Prova 1')
    gerar_grafico(acertos2, nome, 'Prova 2')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Resultado de {nome}', 0, 1, 'C')
    pdf.image(f"{nome}_Prova 1.png", x = 10, y = pdf.get_y(), w = 90)
    pdf.image(f"{nome}_Prova 2.png", x = 105, y = pdf.get_y(), w = 90)
    pdf.output(f'pdfs/resultado_{nome}.pdf')

