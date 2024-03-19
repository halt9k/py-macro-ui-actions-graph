from abc import ABC
from typing import Type

import networkx as nx
import pyautogui

from actions import Action, MacroAbort


class DiGraphEx(nx.DiGraph):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def roots(self):
		return [v for v, d in self.in_degree if d == 0]

	def leaves(self):
		return [v for v, d in self.out_degree if d == 0]


class Macro(ABC):
	description: str
	actions_graph: DiGraphEx
	result_record: {}
	roots: []
	leaves: []


# TODO add fail callbackk switch?
def try_run_action(action: Action) -> bool:
	assert action.attempts > 0
	pyautogui.sleep(action.start_delay)

	delay = action.attempts_timeout / action.attempts
	for _ in range(action.attempts):
		if action.on_run():
			return True
		pyautogui.sleep(delay)
	return False


def try_walk_from_node(graph: nx.DiGraph, node: Action, prev_node: Action or None, result_record: {}):
	def run_node_action(n):
		# TODO proper callbacking sheduler
		# if n.block_parallel_run:
		return try_run_action(n)

	if run_node_action(node):
		result_record[prev_node, node] = True
		print(f'pass: {node}')
	else:
		print(f'end : {node}')
		result_record[prev_node, node] = False
		return

	for next_node in graph.successors(node):
		try_walk_from_node(graph, next_node, node, result_record)


def try_walk_actions_graph(macro: Type[Macro]):
	# reminder: can be optimized not to take again screenshots when no timeout expected
	macro.result_record = {}

	print(macro.description)
	graph = macro.actions_graph

	node: Action
	extra_entry_nodes = [n for n in graph.nodes if n.is_extra_entry_node]

	try:
		for node in graph.roots() + extra_entry_nodes:
			try_walk_from_node(graph, node, None, macro.result_record)
	except MacroAbort:
		return
