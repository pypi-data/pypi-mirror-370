#!/usr/bin/python3

import matplotlib.pyplot as plt
import math

def vertical_barchart1(   # Dados
                            xtitles = [ "Government", "Nonprofit", 
                                        "Foundation", "Consulting", 
                                        "Other"],
                            yvalues = [89, 57, 37, 28, 19],
                            bar_color = '#3476F6',
                            xtitles_fontsize = 12,
                            xtitles_fontweight = 'bold',
                            xtitles_color = '#7393B3',
                            xtitles_fontfamily = 'monospace',
                            output_filepath = "vertical_barchart1.png",
                            text_color      = '#3476F6',
                            text_fontsize   = 14,
                            text_fontweight = 'bold',
                            title            = "vertical",
                            title_color      = "#3476F6",
                            title_fontsize   = 20,
                            title_fontweight = 'bold',
                            title_fontfamily = 'monospace'
                        ):

    # Configuração da figura
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(xtitles, yvalues, color=bar_color)

    xtitles_font = {'fontsize':   xtitles_fontsize, 
                    'fontweight': xtitles_fontweight, 
                    'color':      xtitles_color, 
                    'fontfamily': xtitles_fontfamily
                   }

    ax.set_xticks(range(len(xtitles)))  # Define as posições das marcas no eixo Y
    ax.set_xticklabels(xtitles, **xtitles_font)

    # Text values in the side of bars
    for i, value in enumerate(yvalues):
        ax.text(i,
                value + 2, 
                str(value), 
                va='center', 
                fontsize= text_fontsize, 
                fontweight= text_fontweight, 
                color=text_color)


    # Formatação
    title_font = {  'fontsize':   title_fontsize, 
                    'fontweight': title_fontweight, 
                    'color':      title_color, 
                    'fontfamily': title_fontfamily
                 }
    plt.title(title, **title_font)

    max_y = math.ceil(max(yvalues)/10)*10
    min_y = math.floor(min(yvalues)/10)*10
    ax.set_ylim(min_y, max_y)
    ax.set_yticks([min_y, max_y])    

    plt.xticks(fontsize=12, color='gray')
    plt.yticks(fontsize=12, color='gray')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('gray')
    ax.spines['bottom'].set_visible(False)

    # Exibir gráfico
    plt.tight_layout(pad=0.5)  
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    vertical_barchart1(output_filepath = "vertical_barchart1.png")
