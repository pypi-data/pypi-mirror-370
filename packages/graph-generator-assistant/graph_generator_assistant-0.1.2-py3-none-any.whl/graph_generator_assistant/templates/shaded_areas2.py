#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# Definindo a curva (função exemplo - pode ser ajustada)
def ex_function(z):
    return 0.3 * np.exp(-0.5*(z-0.5)**2/0.8**2)  # Curva gaussiana

def shaded_areas2(  function_f = ex_function,
                    function_limit = (-3,3),
                    function_legend = "Curve",
                    function_color = "#dc8d6c",
                    intervals = [(0.5, 2), (-2, -0.5)],
                    intervals_color = ["#e7c794","#cdd6a9"],
                    intervals_legend = ["Int.1", "Int.2"],
                    legend_fontsize = 16,
                    xlabel="x",
                    xlabel_fontsize = 16,
                    ylabel="value",
                    ylabel_fontsize = 16,
                    axes_fontsize = 14,
                    output_filepath = "shaded_areas1.png"
                    ):

    # Configuração do gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    # 
    z_values = np.linspace(function_limit[0],function_limit[1], 1000)
    y_zeros = np.zeros_like(z_values)
    y_curve = function_f(z_values)

    #
    ax.plot(z_values, y_curve, color=function_color, linewidth=2, label=function_legend)


    # 
    for i, interval in enumerate(intervals):
        mask_int1 = (z_values >= interval[0]) & (z_values <= interval[1])
        ax.fill_between(z_values[mask_int1], y_zeros[mask_int1], y_curve[mask_int1], 
                        color=intervals_color[i], 
                        label=intervals_legend[i])

    # Configurações dos eixos
    plt.xticks(fontsize=axes_fontsize)#  rotation=90
    plt.yticks(fontsize=axes_fontsize)#  rotation=90

    ax.set_xlim(function_limit[0],function_limit[1])
    ax.set_ylim(-np.abs(np.max(y_curve))*0.05, np.abs(np.max(y_curve))*1.05)
    
    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize,position=(1, 0), ha='right', va='center')
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize,position=(0, 1), ha='right', va='center')
    
    ax.spines['left'].set_position('zero')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_position('zero')

    # Adiciona marcadores no eixo z
    #for z in [-4, -2, 0, 1, 2, 4]:
    #    ax.plot([z, z], [-0.02, 0.02], color='black')
    #    ax.text(z, -0.05, str(z), ha='center', va='top')

    # Legenda
    ax.legend(fontsize=legend_fontsize, loc='upper right')


    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    shaded_areas2(output_filepath = "shaded_areas2.png")
