import matplotlib
import networkx as nx
from PIL import Image, ImageOps

from macro_actions import Action, Actions, ImageRelatedAction
from macro_walk import Macro, NodeResults
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


def try_draw_node_image(node: Action, pos, node_result: NodeResults.Result) -> [int, int]:
    """ Returns image dims if detects them"""

    img_path = node.description_image_path()
    if not img_path:
        return None

    img = Image.open(img_path)
    if max(img.width, img.height) < 50:
        scale = 1  # 3
        img = img.resize((img.width * scale, img.height * scale))
    else:
        scale = 1  # 2
        img = img.resize((img.width * scale, img.height * scale))

    border_color = node_result.color if node_result else 'black'
    img = ImageOps.expand(img, border=2, fill=border_color)

    x, y = pos
    w, h = img.width, img.height
    extent = (x - w, x + w, y - h, y + h)
    plt.imshow(img, extent=extent, alpha=1)
    return w, h


def draw_macro_result(macro: Macro):
    graph = macro.actions_graph

    # nx.nx_pydot.graphviz_layout does not fix the warning, only hides cmd output

    graph.graph['rankdir'] = 'LR'
    graph.graph['ratio'] = 1
    graph.graph['size'] = (90.0, 90.0)
    # graph.graph['bb'] = "0,0,1000,1000"

    # All: ‘dot’, ‘twopi’, ‘fdp’, ‘sfdp’, ‘circo’, 'neato'
    # Good: ‘dot’, 'neato'
    pos = nx.nx_agraph.pygraphviz_layout(graph, prog='dot')

    # Relax the positions to reduce edge intersections, skip nodes on left and right sides
    # fixed = graph.leaves() + graph.roots()
    # pos = nx.spring_layout(graph, pos=pos, fixed=fixed, iterations=1, seed=42)

    img_nodes = []
    text_nodes = {}
    for node in graph.nodes:
        if isinstance(node, ImageRelatedAction):
            img_nodes += [node]
        elif type(node) in [Actions.KeyPress, Actions.Exit]:
            text_nodes[node] = node.info(short=True)
        else:
            raise NotImplementedError

    for node in img_nodes:
        img_shape = try_draw_node_image(node, pos[node], macro.nodes_run_result.get(node, None))
        if img_shape:
            graph.nodes[node]['shape'] = 'box'
            graph.nodes[node]['fixedsize'] = True
            graph.nodes[node]['width'] = img_shape[0]
            graph.nodes[node]['height'] = img_shape[1]

    nx.draw_networkx_labels(graph, labels=text_nodes, pos=pos)

    edges, walked_edges = [], []
    for edge in graph.edges:
        if edge in macro.walked_edges:
            walked_edges += [edge]
        else:
            edges += [edge]

    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color='black', arrows=True)
    nx.draw_networkx_edges(graph, pos, edgelist=walked_edges, edge_color='g', arrows=True)

    plt.suptitle(macro.description)
    plt.show()
