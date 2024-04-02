from typing import Optional
import cv2
import matplotlib
import networkx as nx
import numpy as np
from PIL import Image, ImageOps
from matplotlib import pyplot as plt

from helpers.pygraphviz import DiGraphEx
from helpers.python import SizeTuple
from macro_actions import Action
from macro_walk import Macro

matplotlib.use('TkAgg')

TARGET_IMAGE_SIZE = 80
DEFAULT_NODE_SIZE = 40
DEFAULT_NODE_SIZE_LETTERS = 3


def improve_scale(width, height, target_size):
    sz = (width + height) / 2
    if abs(sz - target_size) > target_size * 0.2:
        scale = target_size / sz

        if scale > 1:
            scale = (1 + scale) / 2
        # power_2_scale = pow(2, int(math.log(scale * 4, 2)) - 1) / 2

        width, height = int(width * scale), int(height * scale)

    return width, height


def plot_node_image(node: Action, pos, node_result: Macro.NodeResults.NodeResult) -> Optional[SizeTuple]:
    """ Returns image dims if detects them"""

    img_path = node.description_image_path()
    if not img_path:
        return

    img = Image.open(img_path)
    w, h = improve_scale(img.width, img.height, TARGET_IMAGE_SIZE)
    img = img.resize((w, h), Image.Resampling.BICUBIC)

    border_color = node_result.color if node_result else 'black'
    img = ImageOps.expand(img, border=5, fill=border_color)

    x, y = pos
    w, h = img.width, img.height
    extent = (x - w, x + w, y - h, y + h)
    plt.imshow(img, extent=extent, alpha=1)


def get_node_sizes(graph) -> [SizeTuple]:
    """	Tries to estimate nessesary size in pixels for drawing """

    node: Action
    node_sizes = []
    for node in graph.nodes:
        if node.draw_mode == Action.DrawMode.TEXT:
            ratio = max(len(node.info(short=True)) / DEFAULT_NODE_SIZE_LETTERS, 1)
            node_sizes += [SizeTuple(int(DEFAULT_NODE_SIZE * ratio), DEFAULT_NODE_SIZE)]
        elif node.draw_mode == Action.DrawMode.IMAGE:
            img = Image.open(node.description_image_path())
            w, h = improve_scale(img.width, img.height, TARGET_IMAGE_SIZE)
            node_sizes += [SizeTuple(w, h)]
        else:
            raise NotImplementedError
    return node_sizes


def draw_with_networkx(desc: str, graph: DiGraphEx, walk_log: Macro.WalkLog, nodes_pos: {}):
    """	Matplotlib render: 	reliable, but does not support rectangle nodes """
    plt.figure(desc)

    nodes_info = {n: n.info(short=True) for n in graph.indexed_nodes(Action.DrawMode.TEXT)}
    nx.draw_networkx_labels(graph, labels=nodes_info, pos=nodes_pos)

    for node in graph.indexed_nodes(Action.DrawMode.IMAGE):
        plot_node_image(node, nodes_pos[node], walk_log.node_results.get(node, None))

    node_sizes = [max(sz.h, sz.w) * 15 for sz in get_node_sizes(graph)]

    # nx.draw_networkx_nodes(graph, nodes_pos, node_size=node_sizes, alpha=0.3)

    nx.draw_networkx_edges(graph, nodes_pos, edgelist=walk_log.unvisited_edges, edge_color='black', width=1,
                           node_size=node_sizes, style='dashed')
    nx.draw_networkx_edges(graph, nodes_pos, edgelist=walk_log.visited_edges, edge_color='green', width=2,
                           node_size=node_sizes)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.show()


def draw_with_graphviz(desc: str, graph: DiGraphEx, walk_log: Macro.WalkLog, nodes_pos: {}):
    """ Supposed to draw HQ graph with correct rectangle nodes """

    dpi_factor = 2

    for i, node in enumerate(graph.nodes):
        graph.nodes[node]['shape'] = 'box'
        cx, cy = nodes_pos[node]
        graph.nodes[node]['pos'] = f"{cx},{cy}"
        graph.nodes[node]['label'] = ""

        nr = walk_log.node_results.get(node, None)
        graph.nodes[node]['color'] = nr.color if nr else 'black'

    node_sizes = get_node_sizes(graph)
    for node, i in graph.indexed_nodes(Action.DrawMode.IMAGE).items():
        graph.nodes[node]['fixedsize'] = True
        graph.nodes[node]['width'] = node_sizes[i].w / 100
        graph.nodes[node]['height'] = node_sizes[i].h / 100
        graph.nodes[node]['image'] = node.description_image_path()
        graph.nodes[node]['imagescale'] = 'both'
        # fast fix for imaages overlap half of border
        graph.nodes[node]['penwidth'] = dpi_factor * 2

    for node, i in graph.indexed_nodes(Action.DrawMode.TEXT).items():
        graph.nodes[node]['label'] = node.info(short=True)

    for edge in graph.edges:
        if edge in walk_log.visited_edges:
            graph.edges[edge]['color'] = 'green'
        else:
            graph.edges[edge]['color'] = 'black'
            graph.edges[edge]['style'] = 'dashed'

    graph.graph['dpi'] = 100 * dpi_factor
    agraph = nx.nx_agraph.to_agraph(graph)

    img_bytes = agraph.draw(prog='dot', format='png')
    nparr = np.frombuffer(img_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # cv2.imshow(desc, img)
    plt.figure(desc)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    plt.imshow(image_rgb)
    plt.show()


def estimate_graph_layout(graph):
    graph.graph['rankdir'] = 'LR'
    graph.graph['ratio'] = 3 / 4

    # All: ‘dot’, ‘twopi’, ‘fdp’, ‘sfdp’, ‘circo’, 'neato'
    # Good: ‘dot’, 'neato'
    pos = nx.nx_agraph.pygraphviz_layout(graph, prog='dot')

    # Relax the positions to reduce edge intersections, skip nodes on left and right sides
    fixed = graph.leaves() + graph.roots()
    pos = nx.spring_layout(graph, pos=pos, fixed=fixed, iterations=1, seed=1)

    return pos


def draw_macro_result(macro: Macro):
    graph = macro.actions_graph
    nodes_pos = estimate_graph_layout(graph)

    # draw_with_networkx(macro.description, graph, macro.walk_log, nodes_pos)
    draw_with_graphviz(macro.description, graph, macro.walk_log,  nodes_pos)
