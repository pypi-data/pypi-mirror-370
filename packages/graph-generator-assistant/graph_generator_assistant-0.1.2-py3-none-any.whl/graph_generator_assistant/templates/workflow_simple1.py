#!/usr/bin/python3


import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import textwrap

def workflow_simple1(
    steps = [
        ("Step 1", "Mapping and Diagnosis of Current Processes"),
        ("Step 2", "Process Design"),
        ("Step 3", "Identification of Improvement Opportunities"),
        ("Step 4", "Manualization of Processes"),
        ("Step 4", "Training to Ensure Standardization and Continuous Improvement")
    ],
    colors = ["#002b3e", "#00475d", "#967179", "#5d2d45", "#441326"],
    text_max_width = 16,
    text_color = "#c1a097",
    text_fontsize = 8,
    title_color= "#c1a097",
    title_fontsize = 12,
    grid_size = 2,
    box_edgecolor = "black",
    box_pad = 0.1,
    box_width = 1.3,
    box_height = 1.5,
    box_linewidth = 1,
    arrow_head_length = 0.2,
    arrow_linewidth = 1,
    arrow_edgecolor = "black",
    arrow_facecolor = "#441326",
    output_filepath = "workflow_simple1.png"
    ):
    
    fig, ax = plt.subplots(figsize=(10, 2))
    #ax.set_xlim(0, 10)
    #ax.set_ylim(0, 2)
    ax.axis("off")
    
    L = len(steps)
    
    for i, (title, text) in enumerate(steps):
        x = i * grid_size
        rect = patches.FancyBboxPatch(  (x, 0),  # x0y0 
                                        box_width,   # width
                                        box_height,  # height
                                        boxstyle=f"round,pad={box_pad}", 
                                        linewidth=box_linewidth, 
                                        edgecolor=box_edgecolor, 
                                        facecolor=colors[i]
                                        )
        ax.add_patch(rect)
        
        wrapped_text = "\n".join(textwrap.wrap(text, width=text_max_width))
        
        ax.text(x + box_width/2, box_height*0.9, 
                title, 
                fontweight='bold', 
                fontsize=title_fontsize, 
                ha='center', 
                va='center', 
                color=title_color)
        
        ax.text(x + box_width/2, 
                box_height*0.5, 
                wrapped_text, 
                fontweight='bold', 
                fontsize=text_fontsize, 
                ha='center', 
                va='center', 
                color=text_color)
        
        if i < len(steps) - 1:
            ax.arrow(   x + box_width+box_pad+box_linewidth/72.0,   # x0
                        box_height/2,                       # y0
                        grid_size-box_width-2*box_pad-arrow_head_length-box_linewidth/72.0,# dx
                        0,              # dy
                        head_width=0.3, 
                        head_length=arrow_head_length, 
                        fc=arrow_facecolor, 
                        ec=arrow_edgecolor, 
                        linewidth=arrow_linewidth
                        )
    
    plt.xlim(-1.5*box_pad, grid_size*(L-1)+box_width+1.5*box_pad)
    plt.ylim(-1.5*box_pad, box_height+1.5*box_pad)
    
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout(pad=0.5)  

    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    workflow_simple1(output_filepath = "workflow_simple1.png")


