#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.patches import Arrow, Circle, RegularPolygon
import numpy as np


def radial_network_diagram3(central_label = "Writer",
                            central_color = "#e7c794",
                            central_radius  = 0.065, 
                            labels = ["Edit", "pdfLaTeX", "BibTeX", "make\nindex", "pdfLaTeX"], # 
                            colors = ["#dc8d6c", "#676e5e", "#97a884", "#cdd6a9", "#e6e7d5"], # plt.cm.tab10.colors
                            element_alpha   = 1.0, 
                            element_radius  = 0.065, 
                            proccess_radius = 0.150, 
                            text_fontsize = 24, 
                            text_weight = 'bold', 
                            text_color = "black", 
                            text_fontfamily = 'monospace', # {FONTNAME, 'serif', 
                                                           # 'sans-serif', 'cursive', 
                                                           # 'fantasy', 'monospace'}
                            arrow_color = "gray",  # arrow color
                            arrow_thick = 8,       # arrow line thickness
                            arrow_scale = 20,      # arrow head scale
                            output_filepath = "radial_network_diagram3.pdf"
                            ):
    
    # Drawing each "Labeled Node"
    L = len(labels)
    offset_angle = np.pi/2
    angles = np.linspace(offset_angle, 2*np.pi+ offset_angle, L, endpoint=False) 
    alfa = 2.0*np.pi/L
        
    orientation = -np.pi/2 + alfa/2 - offset_angle
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')

    # central circle
    polygon = RegularPolygon(   (0, 0),
                                numVertices=len(labels), 
                                radius=central_radius,    # circle radius
                                orientation=alfa/2,
                                edgecolor=central_color,  # circle edge color
                                facecolor=central_color,  # circle face color
                                alpha=element_alpha
                                )
                    
    ax.add_patch(polygon)

    ax.text(0, 0, 
            central_label, 
            ha='center', 
            va='center', 
            fontfamily=text_fontfamily,
            fontsize=text_fontsize, 
            weight=text_weight, 
            color=text_color)

    if len(labels)> len(colors):
        for idx in range(len(labels) - len(colors)):
            colors.append("white")
    
    for i, (label, color) in enumerate(zip(labels, colors)):
        
        # center of element circle in each "Labeled Node"
        x = proccess_radius * np.cos(angles[i])
        y = proccess_radius * np.sin(angles[i])
        
        # add circle that represents a "Labeled Node"
        polygon = RegularPolygon(   (x, y),
                                    numVertices=len(labels), 
                                    radius=element_radius, # circle radius
                                    orientation=-orientation,
                                    edgecolor=color,       # circle edge color
                                    facecolor=color,       # circle face color
                                    alpha=element_alpha
                                    )
        
        ax.add_patch(polygon)
        
        # add text inside of "Labeled Node"
        ax.text(x, y, 
                label, 
                ha='center', 
                va='center', 
                fontfamily=text_fontfamily,
                fontsize=text_fontsize, 
                weight=text_weight, 
                color=text_color)
        
        # Start and end of arrows
        start_x = (central_radius) * np.cos(angles[i])
        start_y = (central_radius) * np.sin(angles[i])
        end_x = (proccess_radius - element_radius*np.cos(alfa/2.0)) * np.cos(angles[i])
        end_y = (proccess_radius - element_radius*np.cos(alfa/2.0)) * np.sin(angles[i])
        
        # add arrow
        ax.annotate("",
            xy=(end_x, end_y),          # arrow end point
            xytext=(start_x, start_y),  # arrow initial point
            arrowprops=dict(
                arrowstyle="->,head_length=1,head_width=0.5",  # head size 
                color=arrow_color,
                lw=arrow_thick,            # arrow thickness
                shrinkA=0,       # Afastamento do ponto inicial
                shrinkB=0,                 # Afastamento do ponto final
                mutation_scale=arrow_scale # head size scale
            )
        )


    R = element_radius + proccess_radius


    plt.xlim(-R, R)
    plt.ylim(-R, R)
  
        
    plt.tight_layout(pad=0.5)  
    plt.savefig(output_filepath, bbox_inches='tight', pad_inches=0.1, dpi=600, transparent=True)

if __name__ == '__main__':
    # Configurações
    radial_network_diagram3(output_filepath = "radial_network_diagram3.png")
    
