#!/usr/bin/python3

import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import requests
from io import BytesIO

def load_image(path):
    """Carrega a imagem de um caminho local ou URL.
    Se não for possível carregar, retorna uma imagem vazia com fundo branco.
    """
    try:
        if path.startswith("http"):
            response = requests.get(path, timeout=5)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        return Image.open(path)
    except Exception:
        return Image.new("RGB", (100, 100), "red")

def network_graph1( network_dict = {
                        "icons": {
                            "router": "https://github.com/trucomanx/GraphGeneratorAssistant/blob/main/src/graph_generator_assistant/images/router.png?raw=true",
                            "switch": "https://github.com/trucomanx/GraphGeneratorAssistant/blob/main/src/graph_generator_assistant/images/switch.png?raw=true",
                            "PC":     "https://github.com/trucomanx/GraphGeneratorAssistant/blob/main/src/graph_generator_assistant/images/pc.png?raw=true",
                            "LT":     "https://github.com/trucomanx/GraphGeneratorAssistant/blob/main/src/graph_generator_assistant/images/laptop.png?raw=true"
                        },
                        "nodes": {
                            "router": "router",
                            "switch_1": "switch",
                            "switch_2": "switch",
                            "PC_1_1": "PC",
                            "PC_1_2": "PC",
                            "PC_1_3": "LT",
                            "PC_2_1": "PC",
                            "PC_2_2": "PC"
                        },
                        "edges": [
                            ("router", "switch_1"),
                            ("router", "switch_2"),
                            ("switch_1", "PC_1_1"), 
                            ("switch_1", "PC_1_2"), 
                            ("switch_1", "PC_1_3"),
                            ("switch_2", "PC_2_1"), 
                            ("switch_2", "PC_2_2")
                        ]
                    },
                    output_filepath = "network_graph1.pdf"
                ):
    """Cria um gráfico de rede a partir de um dicionário."""
    
    # Carregar imagens
    images = {name: load_image(path) for name, path in network_dict["icons"].items()}
    
    # Criar grafo
    G = nx.Graph()
    
    # Adicionar nós
    for node, node_type in network_dict["nodes"].items():
        G.add_node(node, image=images[node_type])
    
    # Adicionar conexões
    for edge in network_dict["edges"]:
        G.add_edge(*edge)
    
    # Gerar layout
    pos = nx.spring_layout(G, seed=1734289230)
    fig, ax = plt.subplots()
    
    # Desenhar conexões
    nx.draw_networkx_edges(G, pos=pos, ax=ax, arrows=True, arrowstyle="-", 
                           min_source_margin=15, min_target_margin=15)
    
    # Ajustar ícones
    tr_figure = ax.transData.transform
    tr_axes = fig.transFigure.inverted().transform
    icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
    icon_center = icon_size / 2.0
    
    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
        a.imshow(G.nodes[n]["image"])
        a.axis("off")
    
    ax.set_axis_off()
    plt.savefig(output_filepath, 
                bbox_inches='tight', 
                pad_inches=0.1, 
                dpi=600, 
                transparent=True)


if __name__ == '__main__':
    network_graph1(output_filepath = "network_graph1.png")

