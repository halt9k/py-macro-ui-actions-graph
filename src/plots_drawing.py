from typing import Type
import matplotlib
import networkx as nx
from PIL import Image, ImageOps

from actions import Action, Actions
from macro_walk import Macro
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


def try_draw_node_image(graph, node: Action, pos):
    img_path = node.description_image_path()
    if not img_path:
        return

    img = Image.open(img_path)
    if max(img.width, img.height) < 50:
        img = img.resize((img.width*3, img.height*3))
    else:
        img = img.resize((img.width * 2, img.height * 2))

    # add border
    img = ImageOps.expand(img, border=2, fill='black')

    x, y = pos
    w, h = img.width, img.height
    extent = (x - w, x + w, y - h, y + h)
    plt.imshow(img, extent=extent, alpha=1)


def draw_macro_result(macro: Type[Macro]):
    graph, walk_result = macro.actions_graph, macro.result_record

    # TODO try ‘dot’, ‘twopi’, ‘fdp’, ‘sfdp’, ‘circo’
    # pos = nx.nx_pydot.pydot_layout(graph, prog='dot', root=list(graph.nodes)[0])
    pos = nx.nx_agraph.graphviz_layout(graph, prog='dot', root=list(graph.nodes)[0])

    # bugfix, LR
    for node in graph.nodes:
        pos[node] = -pos[node.__repr__()][1] * 5, pos[node.__repr__()][0]

    img_nodes = []
    text_nodes = {}
    for node in graph.nodes:
        if type(node) in [Actions.ImageClick, Actions.LocateImage]:
            img_nodes += [node]
        elif type(node) in [Actions.KeyPress, Actions.Exit]:
            text_nodes[node] = node.info(short=True)
        else:
            raise NotImplementedError

    for node in img_nodes:
        try_draw_node_image(graph, node, pos[node])

    nx.draw_networkx_labels(graph, labels=text_nodes, pos=pos)

    green_edges = [edge for edge in graph.edges if edge in walk_result]
    red_edges = [edge for edge in graph.edges if edge not in walk_result]
    nx.draw_networkx_edges(graph, pos, edgelist=red_edges, edge_color='r', arrows=True)
    nx.draw_networkx_edges(graph, pos, edgelist=green_edges, edge_color='g', arrows=True)

    plt.suptitle(macro.__name__)
    plt.show()
