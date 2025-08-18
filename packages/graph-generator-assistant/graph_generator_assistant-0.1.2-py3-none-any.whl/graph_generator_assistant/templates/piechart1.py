#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

def piechart1(  # Dados
                labels = ['Mathematics', 'Science', 'Social science', 'English', 'Hindi'], 
                values = [108, 81, 45, 72, 54], 
                colors = ['#3a3f05', '#87930d', '#ff6647', '#f90b2d', '#5e0f15'], 
                explode = (0.0, 0.0, 0.0, 0.0, 0.0),  # >0 Nenhum pedaço destacado
                pie_edgecolor = 'white', 
                pie_doughnut = 0.3, 
                pie_fontsize = 16, 
                pie_fontcolor = 'white', 
                legend_title = 'Subject', 
                legend_title_fontsize = 18,
                legend_fontcolor = 'purple', 
                legend_fontsize = 16,
                output_filepath = "piechart1.png"
                ):
    # Criação do gráfico
    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')
    wedges, texts = ax.pie(
        values,
        explode = explode, 
        colors=colors,
        startangle=0,
        counterclock=True,
        wedgeprops=dict(width=1-pie_doughnut, edgecolor = pie_edgecolor) 
    )

    # Adiciona os ângulos no centro de cada fatia
    sum_values = np.sum(values)
    angle_sum = 0
    for i, w in enumerate(wedges):
        angle = angle_sum + np.pi * values[i]/sum_values
        x = 0.65 * np.cos(angle)
        y = 0.65 * np.sin(angle)
        ax.text(x, y, 
                f"{values[i]}", 
                ha='center', 
                va='center', 
                fontsize=pie_fontsize, 
                color=pie_fontcolor)
        angle_sum = angle + np.pi * values[i]/sum_values 

    # Legenda
    new_labels = [f"{100*sz/sum_values:.1f}% {label}" for sz,label in zip(values,labels)]
    ax.legend(  wedges, 
                new_labels, 
                title=legend_title, 
                title_fontsize=legend_title_fontsize,
                loc="center left", 
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize = legend_fontsize, 
                labelcolor=legend_fontcolor)

    # Borda roxa
    plt.setp(wedges, edgecolor=pie_edgecolor)

    ax.set_axis_off()
    plt.tight_layout(pad=0.5)
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    piechart1(output_filepath = "piechart1.png")
