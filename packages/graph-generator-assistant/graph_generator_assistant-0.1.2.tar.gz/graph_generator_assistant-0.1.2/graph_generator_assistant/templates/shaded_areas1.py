#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Criação da curva normal padrão
# Definindo a curva (função exemplo - pode ser ajustada)
def ex_function(x):
    return 0.3 * np.exp(-0.5*(x-0.5)**2/0.8**2)  # Curva gaussiana


def shaded_areas1(  function_f = ex_function,
                    function_limit = (-4,4),
                    function_legend = "Curve",
                    function_color = "#dc8d6c",
                    intervals = [(0.5, 2), (-2, -0.5)],
                    intervals_color = ["#e7c794","#cdd6a9"],
                    intervals_legend = ["Int.1", "Int.2"],
                    intervals_hatch = ['//',"\\\\"],
                    legend_fontsize = 14,
                    xlabel="x",
                    xlabel_fontsize = 14,
                    ylabel="value",
                    ylabel_fontsize = 14,
                    axes_fontsize = 12,
                    output_filepath = "shaded_areas1.png"
                    ):

    x = np.linspace(function_limit[0], function_limit[1], 1000)
    y = function_f(x)

    fig, ax = plt.subplots()


    ax.plot(x, y, color = function_color, label=function_legend)

    # Preenchimento do Intervalo 1
    for i, interval in enumerate(intervals):
        x_fill = np.linspace(interval[0], interval[1], 100)
        y_fill = function_f(x_fill)
        
        ax.fill_between(x_fill, 0, y_fill, 
                        color=intervals_color[i], 
                        hatch=intervals_hatch[i], 
                        edgecolor='black', 
                        label=intervals_legend[i])

    # Configurações adicionais
    ax.set_xlim(function_limit[0], function_limit[1])
    ax.set_ylim(0, max(y)*1.05)
    ax.set_xlabel(xlabel,fontsize=xlabel_fontsize)
    ax.set_ylabel(ylabel,fontsize=ylabel_fontsize)
    ax.legend(fontsize=legend_fontsize, loc='upper right')
    
    plt.xticks(fontsize=axes_fontsize)#  rotation=90
    plt.yticks(fontsize=axes_fontsize)#  rotation=90


    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    shaded_areas1(output_filepath = "shaded_areas1.png")
