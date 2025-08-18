#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


# Contador global de linhas
class Linha:
    def __init__(self):
        self.valor = 0

def number_of_levels(d):
    if not isinstance(d, dict) or not d:
        return 0
    return max(number_of_levels(sub) for sub in d.values()) + 1


def draw_box(   ax, 
                label, 
                x, y, 
                box_width, 
                box_height, 
                dashed=False, 
                fontsize=14, 
                facecolor='white', 
                edgecolor='black', 
                linewidth=1,
                rounding_size_factor=0.10):
                
    rect = FancyBboxPatch((x, y - box_height), box_width, box_height,
                      boxstyle=f"round,pad=0.00,rounding_size={rounding_size_factor*box_height}",
                      linewidth=linewidth, edgecolor=edgecolor,
                      facecolor=facecolor,
                      linestyle='--' if dashed else '-')
    ax.add_patch(rect)
    ax.text(x + box_width / 2, y - box_height / 2, label,
            ha='center', va='center', fontsize=fontsize)

def draw_connector(ax, parent_x, parent_y, child_x, child_y, box_width, box_height, linewidth):
    # vertical do meio inferior do pai até o nível do filho
    ax.plot([parent_x, parent_x], 
            [parent_y, child_y- box_height/2.0], 
            color='black',
            linewidth=linewidth)
    # horizontal até o meio superior do filho
    ax.plot([parent_x, child_x-box_width/2.0], 
            [child_y - box_height/2.0, child_y - box_height/2.0], 
            color='black',
            linewidth=linewidth)

def draw_node(  ax, 
                name, 
                subtree, 
                level, 
                linha, 
                box_width, 
                box_height, 
                level_indent, 
                line_gap, 
                parent_coord=None, 
                fontsize=14, 
                facecolor='white', 
                edgecolor='black', 
                linewidth=1,
                rounding_size_factor=0.10):
    x = level * level_indent
    y = -linha.valor * (box_height + line_gap)
    linha.valor += 1  # próxima linha disponível

    dashed = subtree is None
    draw_box(   ax, 
                name, 
                x, y, 
                box_width, 
                box_height, 
                dashed,
                fontsize=fontsize, 
                facecolor=facecolor, 
                edgecolor=edgecolor, 
                linewidth=linewidth,
                rounding_size_factor=rounding_size_factor
                )

    if parent_coord:
        px, py = parent_coord
        draw_connector(ax, px + box_width / 2, py - box_height, x + box_width / 2, y, box_width, box_height, linewidth)

    if isinstance(subtree, dict):
        for child_name, child_tree in subtree.items():
            draw_node(  ax, 
                        child_name, 
                        child_tree, 
                        level + 1, 
                        linha, 
                        box_width, 
                        box_height, 
                        level_indent, 
                        line_gap, 
                        (x, y),
                        fontsize=fontsize, 
                        facecolor=facecolor, 
                        edgecolor=edgecolor, 
                        linewidth=linewidth,
                        rounding_size_factor=rounding_size_factor)

def tree_files1(structure = {
                    "project": {
                        "README.md": None,
                        "doc": {
                            "file1.tex": None,
                            "file2.tex": None
                        },
                        "images": {},
                        "source": {
                            "generic": {},
                            "main.c": None,
                        }
                    }
                },
                box_width = 0.8,
                box_height = 0.15,
                level_indent = 0.5,
                line_gap = 0.03,
                fontsize=48, 
                facecolor='white', 
                edgecolor='black', 
                linewidth=4,
                rounding_size_factor=0.3,
                output_filepath="tree_files1.png"):
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_aspect('equal') 
    
    linha = Linha()  # inicializa contador de linhas

    root_name = list(structure.keys())[0]
    root_content = structure[root_name]
    draw_node(  ax, 
                root_name, 
                root_content, 
                level=0, 
                linha=linha, 
                box_width = box_width, 
                box_height = box_height, 
                level_indent = level_indent,
                line_gap = line_gap,
                fontsize=fontsize, 
                facecolor=facecolor, 
                edgecolor=edgecolor, 
                linewidth=linewidth,
                rounding_size_factor=rounding_size_factor)

    profundidade = number_of_levels(structure)
    ax.set_xlim(-line_gap/2, (profundidade-1) * level_indent + box_width + line_gap/2)
    ax.set_ylim(-linha.valor * (box_height + line_gap)+line_gap/2, line_gap/2)
    ax.axis('off')
    plt.tight_layout()
    
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)


# Estrutura JSON


if __name__ == '__main__':
    tree_files1(output_filepath="tree_files1.png")

