#!/usr/bin/python3

import matplotlib.pyplot as plt
import math

def horizontal_barchart1(   # Dados
                            ytitles = [ "Government", "Nonprofit", 
                                        "Foundation", "Consulting", 
                                        "Other"],
                            xvalues = [89, 57, 37, 28, 19],
                            bar_color = '#3476F6',
                            ytitles_fontsize = 12,
                            ytitles_fontweight = 'bold',
                            ytitles_color = '#7393B3',
                            ytitles_fontfamily = 'monospace',
                            output_filepath = "horizontal_barchart1.png",
                            text_color      = '#3476F6',
                            text_fontsize   = 14,
                            text_fontweight = 'bold',
                            title            = "Horizontal",
                            title_color      = "#3476F6",
                            title_fontsize   = 20,
                            title_fontweight = 'bold',
                            title_fontfamily = 'monospace'
                        ):

    # Configuração da figura
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(ytitles, xvalues, color=bar_color)
    ax.invert_yaxis()  # Inverter a ordem para coincidir com a imagem
    # Ajusta os rótulos do eixo Y com as configurações definidas
    
    ytitles_font = {'fontsize':   ytitles_fontsize, 
                    'fontweight': ytitles_fontweight, 
                    'color':      ytitles_color, 
                    'fontfamily': ytitles_fontfamily
                   }
    ax.set_yticks(range(len(ytitles)))  # Define as posições das marcas no eixo Y
    ax.set_yticklabels(ytitles, **ytitles_font)

    # Text values in the side of bars
    for i, value in enumerate(xvalues):
        ax.text(value + 2, 
                i, 
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
    max_x = math.ceil(max(xvalues)/10)*10
    min_x = math.floor(min(xvalues)/10)*10
    ax.set_xlim(min_x, max_x)
    ax.set_xticks([min_x, max_x])
    plt.xticks(fontsize=12, color='gray')
    plt.yticks(fontsize=12, color='gray')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('gray')

    # Exibir gráfico
    plt.tight_layout(pad=0.5)  
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    horizontal_barchart1(output_filepath = "horizontal_barchart1.png")
