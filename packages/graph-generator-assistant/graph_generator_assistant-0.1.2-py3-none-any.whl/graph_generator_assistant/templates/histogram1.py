#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

def histogram1( data = np.random.randn(1000), 
                bins = 20, 
                title="Histogram", 
                xlabel="Values", 
                ylabel="Frequency", 
                color='blue',
                edgecolor = 'white',
                alpha=0.7,
                fontsize = 12,
                title_fontsize = 14,
                output_filepath = 'histogram1.png'):

    fig, ax = plt.subplots(figsize=(8, 5))
    plt.hist(data, bins=bins, color=color, edgecolor=edgecolor, alpha=alpha)
    plt.title(title, fontsize=title_fontsize)
    plt.xlabel(xlabel, fontsize=fontsize)
    plt.ylabel(ylabel, fontsize=fontsize)
    plt.grid(axis='y', linestyle='--', alpha=0.6, color='#AAAAAA')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    histogram1(output_filepath = 'histogram1.png')

