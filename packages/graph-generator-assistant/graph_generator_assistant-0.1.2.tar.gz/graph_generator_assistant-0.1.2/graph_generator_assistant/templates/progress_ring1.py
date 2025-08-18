#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge

def progress_ring1( percentage = 42,
                    percentage_fontsize = 24, 
                    percentage_color = "black",
                    ring_color = '#33c1c9', 
                    ring_width = 0.3, 
                    subring_enable = True,
                    subring_scale = 0.1, 
                    output_filepath = "progress_ring1.png"):

    fig, ax = plt.subplots(figsize=(2, 2))

    # ângulos
    start_angle = 90 - (percentage / 100) * 360
    end_angle = 90

    # Anel 
    background = Wedge( center=(0, 0), 
                        r=1, 
                        theta1=0, 
                        theta2=360,
                        width=ring_width, 
                        facecolor="white")
    ax.add_patch(background)

    # Anel preenchido
    filled     = Wedge( center=(0, 0), 
                        r=1, 
                        theta1=start_angle, 
                        theta2=end_angle,
                        width=ring_width, 
                        facecolor=ring_color)
    ax.add_patch(filled)

    # subring
    if subring_enable:
        ring = Wedge(   center=(0, 0), 
                        r=1-ring_width/2+subring_scale*ring_width/2, 
                        theta1=0, 
                        theta2=360,
                        width=subring_scale*ring_width, 
                        facecolor=ring_color)
        ax.add_patch(ring)

    # Texto central
    ax.text(0, 0, 
            f"{percentage}%", 
            ha='center', 
            va='center', 
            color = percentage_color, 
            fontsize = percentage_fontsize, 
            weight='bold')

    ax.set(aspect='equal')
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    plt.axis('off')

    plt.tight_layout(pad=0)
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    progress_ring1(output_filepath = "progress_ring1.png")
