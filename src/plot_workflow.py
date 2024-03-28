import math
from typing import Optional

import cv2
import matplotlib
import networkx as nx
import numpy as np
from PIL import Image, ImageOps
from matplotlib import pyplot as plt

from helpers.gui import debug_show_images
from helpers.pygraphviz import DiGraphEx
from helpers.python import SizeTuple
from macro_actions import Action, Actions
from macro_walk import Macro

matplotlib.use('TkAgg')

TARGET_IMAGE_SIZE = 80


def improve_image_scale(img, target_size):
	sz = min(img.width, img.height)
	if not abs(sz - target_size) < target_size * 0.3:
		scale = target_size / sz

		relaxed_scale = 1 - (1 - scale) / 2
		power_2_scale = pow(2, int(math.log(relaxed_scale * 4, 2)) - 1) / 2

		w, h = int(img.width * power_2_scale), int(img.height * power_2_scale)
		img = img.resize((w, h), Image.Resampling.BICUBIC)
	return img


def try_draw_node_image(node: Action, pos, node_result: Macro.NodeResults.NodeResult) -> Optional[SizeTuple]:
	""" Returns image dims if detects them"""

	img_path = node.description_image_path()
	if not img_path:
		return None

	img = Image.open(img_path)
	img = improve_image_scale(img, TARGET_IMAGE_SIZE)

	border_color = node_result.color if node_result else 'black'
	img = ImageOps.expand(img, border=5, fill=border_color)

	x, y = pos
	w, h = img.width, img.height
	extent = (x - w, x + w, y - h, y + h)
	plt.imshow(img, extent=extent, alpha=1)
	return SizeTuple(w, h)


def draw_with_networkx(graph: DiGraphEx, walk_log: Macro.WalkLog, nodes_pos: {}):
	"""	Matplotlib render: 	reliable, but does not support rectangle nodes """

	node_sizes = [300.0] * len(graph.nodes)
	img_nodes = graph.nodes_of_class(Actions.ImageRelatedAction)
	for node in img_nodes:
		img_shape = try_draw_node_image(node, nodes_pos[node], walk_log.node_results.get(node, None))
		if img_shape:
			node_sizes[img_nodes[node]] = max(img_shape.w, img_shape.h) * 50

	# TODO improve
	text_nodes = {}
	for n in graph.nodes_of_class(Actions.KeyPress):
		text_nodes[n] = n.info(short=True)
	for n in graph.nodes_of_class(Actions.Exit):
		text_nodes[n] = n.info(short=True)

	nx.draw_networkx_labels(graph, labels=text_nodes, pos=nodes_pos)

	# nx.draw_networkx_nodes(graph, pos, node_size=node_sizes)
	# TODO improve
	nx.draw_networkx_edges(graph,
						   nodes_pos,
						   edgelist=walk_log.unvisited_edges,
						   edge_color='black',
						   width=1,
						   arrows=True,
						   node_size=node_sizes)
	nx.draw_networkx_edges(graph,
						   nodes_pos,
						   edgelist=walk_log.visited_edges,
						   edge_color='g',
						   width=5,
						   arrows=True,
						   node_size=node_sizes)

	plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
	plt.show()


def draw_with_graphviz(graph: DiGraphEx, walk_log: Macro.WalkLog, nodes_pos: {}):
	""" Supposed to draw high quality edges """

	# TODO common routine for both draw
	node_sizes = [300.0] * len(graph.nodes)
	img_nodes = graph.nodes_of_class(Actions.ImageRelatedAction)
	for node in img_nodes:
		img_shape = try_draw_node_image(node, nodes_pos[node], walk_log.node_results.get(node, None))
		if img_shape:
			node_sizes[img_nodes[node]] = max(img_shape.w, img_shape.h) * 50
			graph.nodes[node]['shape'] = 'box'
			graph.nodes[node]['fixedsize'] = True
			graph.nodes[node]['width'] = img_shape[0]
			graph.nodes[node]['height'] = img_shape[1]

	agraph = nx.nx_agraph.to_agraph(graph)
	for node, position in nodes_pos.items():
		agraph.node_attr(node)['pos'] = f"{position[0]},{position[1]}"

	# TODO expected to work?
	# graph.graph['size'] = '10,10'
	agraph = nx.nx_agraph.to_agraph(graph)
	agraph.graph_attr['size'] = '10,10'
	agraph.graph_attr['dpi'] = '100'

	img = agraph.draw(prog='neato', format='png')
	# cv2.imshow(macro.description, img)
	cv2.imshow("macro.description", img)

	img_bytes = agraph.draw(prog='neato', format='png')
	nparr = np.frombuffer(img_bytes, np.uint8)
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	debug_show_images([img])

	# walk_log.unvizited_edges
	# walk_log.vizited_edges
	# nx.nx_agraph.view_pygraphviz()


def estimate_graph_layout(graph):
	graph.graph['rankdir'] = 'LR'
	graph.graph['ratio'] = 3 / 4

	# graph.graph['size'] = "1,1"
	# graph.graph['dpi'] = "0.1"
	# graph.graph['bb'] = "0,0,100,100"

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

	draw_with_networkx(graph, macro.walk_log, nodes_pos)
	# draw_with_graphviz(graph, macro.walk_log,  nodes_pos)

