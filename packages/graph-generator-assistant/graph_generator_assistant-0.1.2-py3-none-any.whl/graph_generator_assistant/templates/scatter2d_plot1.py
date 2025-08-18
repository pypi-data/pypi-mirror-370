#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt

def scatter2d_plot1(xvalues = np.random.normal(loc=0.0, scale=1.0, size=1000),
                    yvalues = np.random.normal(loc=0.0, scale=1.0, size=1000),
                    xlabel = "X",
                    ylabel = "Y",
                    title = "2D points with Gaussian distribution",
                    output_filepath = "scatter2d_plot1.png"
                    ):
    # Criação do gráfico
    plt.figure(figsize=(6,5))
    plt.scatter(xvalues, yvalues, color='blue')

    # Adiciona título e eixos
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    # Exibe o gráfico
    
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)


if __name__ == '__main__':
    scatter2d_plot1(output_filepath = "scatter2d_plot1")
