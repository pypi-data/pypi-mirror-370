#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

def piechart2(  labels = ['Apple', 'Orange', 'Melon', 'Kiwi', 'Lemon'],
                values = [10, 15, 20, 25, 30],
                colors = ['#c2b6aa', '#363034', '#4f0818', '#992a31', '#c3a95c'],
                explode = (0.0, 0.0, 0.0, 0.0, 0.0),  # >0 Nenhum pedaço destacado
                pie_fontsize = 18,
                pie_fontcolor = 'white', 
                pie_edgecolor = 'white', 
                pie_doughnut = 0.3, 
                output_filepath = "piechart2.png"
                ):
    # Criando a figura e os subplots
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Gráfico de pizza
    axes[0].pie(values, 
                #labels=labels, 
                explode = explode,
                colors=colors, 
                startangle=0,
                counterclock=True, 
                textprops={'fontsize': 14, 'weight': 'bold'},
                wedgeprops=dict(width=1-pie_doughnut, edgecolor = pie_edgecolor)
                )
    axes[0].set_aspect('equal')  # Mantém o gráfico circular

    # Adiciona os ângulos no centro de cada fatia
    sum_values = np.sum(values)
    angle_sum = 0
    for i, _ in enumerate(values):
        factor = values[i]/sum_values
        angle = angle_sum + np.pi * factor
        x = 0.65 * np.cos(angle)
        y = 0.65 * np.sin(angle)
        axes[0].text(x, y, 
                f"{100*factor:.1f}%", 
                ha='center', 
                va='center', 
                fontsize=pie_fontsize, 
                color=pie_fontcolor)
        angle_sum = angle + np.pi * factor 

    # Gráfico de barras horizontais
    axes[1].barh(labels, values, color=colors)
    axes[1].set_xlim(0, max(values) + 5)  # Ajusta o limite do eixo X
    axes[1].invert_yaxis()  # Inverte a ordem para ficar igual ao exemplo
    axes[1].set_xticks(range(0, max(values) + 10, 5))
    axes[1].tick_params(axis='x', labelsize=14, width=2)
    axes[1].tick_params(axis='y', labelsize=14, width=2, labelcolor='black')
    axes[1].grid(visible=True, which='major', axis='x',color='#AAAAAA', linestyle='--',alpha=0.5)

    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)
    axes[1].spines['left'].set_visible(False)

    # Ajuste do layout
    plt.tight_layout()
    
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    piechart2(output_filepath = "piechart2.png")
