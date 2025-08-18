#!/usr/bin/python3

import networkx as nx
import matplotlib.pyplot as plt

def network_graph2( # Definir a posição dos nós manualmente para melhor estética
                    pos = {
                        "LaTeX": (0, 3),
                        "Diagramas": (-1, 1.5),
                        "Editores": (1, 1.5),
                        "PGFPlo​​ts": (-1.5, 0),
                        "TikZ": (-0.5, 0),
                        "Overleaf": (0.5, 0),
                        "TeXstudio": (1.5, 0),
                    },
                    # Adicionando conexões
                    edges = [
                        ("LaTeX", "Diagramas"),
                        ("LaTeX", "Editores"),
                        ("Diagramas", "PGFPlo​​ts"),
                        ("Diagramas", "TikZ"),
                        ("Editores", "Overleaf"),
                        ("Editores", "TeXstudio")
                    ],
                    node_size=4500,
                    node_color="mediumpurple",
                    font_size=10,
                    font_weight="bold",
                    edge_color="black", 
                    alpha=1.00,
                    arrowsize=15, 
                    # output
                    output_filepath = "network_graph2.pdf"
                ):

    # Criando o grafo
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Criando a figura
    plt.figure(figsize=(7, 5))
    nx.draw(
        G, pos, 
        with_labels=True, 
        node_size=node_size, 
        node_color=node_color,
        font_size=font_size, 
        font_weight=font_weight, 
        edge_color=edge_color, 
        alpha=alpha,
        arrowsize=arrowsize, 
        connectionstyle="arc3,rad=0.2"  # make smooth curves
    )

    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)

if __name__ == '__main__':
    network_graph2(output_filepath = "network_graph2.png")
