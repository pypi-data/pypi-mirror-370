#!/usr/bin/python3

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap

def wrap_text(text, width=20):
    """Quebra o texto em múltiplas linhas para caber dentro da caixa."""
    return "\n".join(textwrap.wrap(text, width))

def workflow_diagram1(  # Defining "Step Markers"
                        steps = [
                            ("Step 01", "Defining the Objectives of the Event"),
                            ("Step 02", "Selecting the Best Venue for the Occasion"),
                            ("Step 03", "Developing a Comprehensive Program for Attendees"),
                            ("Step 04", "Coordinating Logistics and Ensuring Smooth Operations"),
                            ("Step 05", "Evaluating the Success and Gathering Feedback")
                        ],
                        # background colors of "Step Markers"
                        colors = ["#8ED7C6", "#1E4D7A", "#1DB5A0", "#1E4D7A", "#1DB5A0"],
                        box_textcolor = "white", # text color in "Step Markers" 
                        box_edgecolor = "black", # edge color of "Step Markers"
                        box_beak = 0.4, 
                        box_width = 2.2, # less or equal than: 2+box_beak
                        box_height = 0.7, 
                        box_fontsize = 12, 
                        box_fontfamily= 'monospace', # {FONTNAME, 'serif', 
                                                     # 'sans-serif', 'cursive', 
                                                     # 'fantasy', 'monospace'}
                        delta_boxs = 0.2, 
                        extrabox_width = 1.5, # less or equal than box_width
                        extrabox_height = 1.0, 
                        extrabox_pad = 0.15, 
                        extrabox_fontsize = 9, 
                        extrabox_textcolor = "black", # text color in "Information Boxes" 
                        extrabox_backcolor = "white", # background color in "Information Boxes" 
                        extrabox_edgecolor = "black", # edge color of "Information Boxes"
                        extrabox_fontfamily='monospace', # {FONTNAME, 'serif', 
                                                         # 'sans-serif', 'cursive', 
                                                         # 'fantasy', 'monospace'}
                        output_filepath = "workflow_diagram1.pdf"
                        ):

    if len(steps) ==0:
        return False
    
    if len(steps) > len(colors):
        for j in range(len(steps) - len(colors)):
            colors.append("white")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')

    # drawing "Information Boxes" and "Step Markers"
    for i, (step, text) in enumerate(steps):
        x = i * 2
        
        extrabox_y0 = 0.0
        box_y0 = extrabox_y0 + extrabox_pad + extrabox_height + delta_boxs
        
        # Creating conection triangles between "Information Boxes" and "Step Markers"
        triangle = patches.Polygon(
            [(x + 0.5 * box_width, box_y0), 
             (x + 0.5 * box_width-delta_boxs, box_y0-delta_boxs), 
             (x + 0.5 * box_width+delta_boxs, box_y0-delta_boxs)],
            closed=True, facecolor=colors[i], edgecolor=box_edgecolor)
        ax.add_patch(triangle)
        
        # Creating "Step Markers" as block in arrow form
        arrow = patches.Polygon(
            [(x, box_y0), 
             (x + box_width - box_beak, box_y0), 
             (x + box_width, box_y0+ 0.5*box_height),
             (x + box_width - box_beak, box_y0 + box_height), 
             (x, box_y0 + box_height), 
             (x + box_beak, box_y0+ 0.5*box_height)],
            closed=True, facecolor=colors[i], edgecolor=box_edgecolor)
        ax.add_patch(arrow)
        
        # Text inside "Step Markers" blocks
        ax.text(    x + 0.5*(box_width), box_y0+ 0.5*box_height, 
                    step, 
                    ha="center", 
                    va="center", 
                    fontsize=box_fontsize,
                    fontfamily=box_fontfamily, 
                    color=box_textcolor, 
                    fontweight="bold"
                    )
        
        # Creating "Information Boxes"
        box = patches.FancyBboxPatch(
            (x + 0.5*box_width-0.5*extrabox_width, extrabox_y0), #(tupla: coordenadas x e y do canto inferior esquerdo da caixa)
            extrabox_width, # box width
            extrabox_height, # box height
            boxstyle="round,pad="+str(extrabox_pad), # pad=0.1: around the text
            facecolor=extrabox_backcolor, # background color in "Information Boxes"
            edgecolor=extrabox_edgecolor # edge color of "Information Boxes"
            )
        ax.add_patch(box)
        
        # spliting the text of "Information Boxes"
        wrapped_text = wrap_text(text, width=18)
        ax.text(x + 0.5 * box_width, 
                extrabox_y0+0.5*extrabox_height, 
                wrapped_text, 
                ha="center", 
                va="center", 
                fontfamily=extrabox_fontfamily,
                fontsize=extrabox_fontsize, 
                fontweight="bold",
                color = extrabox_textcolor
                )



    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlim(extrabox_y0, (len(steps)-1) * 2 + box_width)
    plt.ylim(extrabox_y0-extrabox_pad, box_y0+box_height)

    plt.tight_layout(pad=0.5)  

    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

    return True

if __name__ == '__main__':
    
    workflow_diagram1(output_filepath = "workflow_diagram1.png")
