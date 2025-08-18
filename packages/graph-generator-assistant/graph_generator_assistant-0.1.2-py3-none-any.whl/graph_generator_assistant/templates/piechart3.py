#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt



from io import BytesIO
from PIL import Image
import requests

def load_image(source, fallback_size=(100, 100)):
    try:
        if isinstance(source, str) and source.startswith(('http://', 'https://')):
            # Caso seja URL
            response = requests.get(source)
            img = Image.open(BytesIO(response.content)).convert('RGBA')
        else:
            # Caso seja arquivo local
            img = Image.open(source).convert('RGBA')
            
        return np.array(img)
    except Exception as e:
        print(f"Aviso: erro ao carregar imagem de {source}: {str(e)}")
        # Criar uma imagem branca fallback
        width, height = fallback_size
        white_img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        return np.array(white_img)

def add_proportional_image(ax, image_source, width, x_center, y_center=0, alpha=1.0, zorder=10):
    try:
        img = load_image(image_source)
        
        # Calcular altura mantendo proporção
        height = width * (img.shape[0] / img.shape[1])
        
        # Adicionar ao gráfico
        ax.imshow(img,
                 extent=[x_center-width/2, x_center+width/2, y_center-height/2, y_center+height/2],
                 alpha=alpha, zorder = zorder)
        
    except Exception as e:
        print(f"Aviso: Não foi possível adicionar a imagem. {str(e)}")


def piechart3(  # Dados
                labels = ['Mathematics', 'Science', 'Social science', 'English', 'Hindi'], 
                values = [108, 81, 45, 72, 54], 
                colors = ['#3a3f05', '#87930d', '#ff6647', '#f90b2d', '#5e0f15'], 
                explode = (0.0, 0.0, 0.0, 0.0, 0.0),  # >0 Nenhum pedaço destacado
                img_path = "https://github.com/trucomanx/GraphGeneratorAssistant/blob/main/src/graph_generator_assistant/images/pc.png?raw=true",
                img_width =1.1,
                pie_edgecolor = 'white', 
                pie_doughnut = 0.5, 
                pie_fontsize = 16, 
                pie_fontcolor = 'white', 
                legend_title = 'Subject', 
                legend_title_fontsize = 18,
                legend_fontcolor = 'purple', 
                legend_fontsize = 16,
                output_filepath = "piechart3.png"
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
        x = (0.5+pie_doughnut/2) * np.cos(angle)
        y = (0.5+pie_doughnut/2) * np.sin(angle)
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
    
    add_proportional_image(ax, img_path, width=img_width, x_center=0, y_center=0, alpha=1.0, zorder=10)
    
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    piechart3(output_filepath = "piechart3.png")
