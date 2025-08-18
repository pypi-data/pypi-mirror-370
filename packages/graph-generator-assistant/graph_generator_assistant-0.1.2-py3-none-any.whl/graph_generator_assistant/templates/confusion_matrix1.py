#!/usr/bin/python3

from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import numpy as np

def confusion_matrix1(  conf_mat = np.array([[5,1,0],[2,6,1],[0,1,5]]),
                        target_names = ['A','B','C'],
                        colormap = plt.cm.Blues,
                        fontsize = 12,
                        fontfamily="sans-serif", # {FONTNAME, 'serif', 
                                                 # 'sans-serif', 'cursive', 
                                                 # 'fantasy', 'monospace'}
                        output_filepath = "workflow_diagram1.png"):
    
    if conf_mat.shape[0] > len(target_names):
        for i in range(conf_mat.shape[0]-len(target_names)):
            target_names.append("Class"+str(len(target_names)+i+1))
    
    fig, ax = plt.subplots(figsize=(4,3))
    
    plt.rcParams.update({"font.family": fontfamily})
    
    disp = ConfusionMatrixDisplay(confusion_matrix=conf_mat, display_labels=target_names)
    disp.plot(ax=ax,cmap=colormap,text_kw={"fontsize": fontsize, "family": fontfamily})
    
    # Ajustando o tamanho da fonte dos rótulos dos eixos
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=fontsize)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=fontsize)
    
    plt.tight_layout(pad=0.5)  
    
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    confusion_matrix1(output_filepath = "confusion_matrix1.png")
