import time
from dataclasses import dataclass

import pyautogui

from macro_actions import Action, MacroAbort
from helpers.pygraphviz import DiGraphEx


class NodeResults:
	@dataclass(init=True, frozen=True)
	class Result:
		text: str
		color: str

	PASS = Result('pass', 'green')
	END = Result('end', 'red')
	MIXED = Result('mixed', 'purple')


class Macro:
	def __init__(self, description: str, actions_graph):
		self.description = description
		self.actions_graph = DiGraphEx(actions_graph)

		self.nodes_run_result = {}
		self.walked_edges = {}
		self.roots: []
		self.leaves: []

	def update_node_walk_result(self, node, result: bool):
		print(f'{result}: {node}')
		res = NodeResults.PASS if result else NodeResults.END

		if node not in self.nodes_run_result:
			self.nodes_run_result[node] = res
		elif self.nodes_run_result[node] != res:
			self.nodes_run_result[node] = NodeResults.MIXED

	def walk_at_node(self, node: Action):
		assert node.max_attempts > 0

		result = node.run()
		self.update_node_walk_result(node, result)
		if result:
			self.walk_edges_from_node(node)
		return result

	def walk_edges_from_node(self, node: Action):
		"""
		Complex routine here because it's possible that no nodes are avaliable instantly
		and only some (yet unknown which) will be avaliable after delay
		"""
		next_nodes = self.actions_graph.successors(node)

		# delay, node
		schedule = []
		for next_node in next_nodes:
			if next_node.block_parallel_run:
				schedule.append([next_node.start_delay, next_node])
				continue

			for attempt in range(0, next_node.max_attempts):
				schedule.append([next_node.attempts_interval * attempt + next_node.start_delay, next_node])

		start_time = time.time()
		for need_delay, next_node in sorted(schedule, key=lambda p: p[0]):
			time_passed = time.time() - start_time
			time_left = need_delay - time_passed
			if time_left > 0:
				pyautogui.sleep(time_left)

			self.walked_edges[node, next_node] = True
			if self.walk_at_node(next_node):
				return

	def run_macro(self):
		# reminder: can be optimized not to take again screenshots when no timeout expected
		self.nodes_run_result = {}

		print(self.description)
		graph = self.actions_graph

		node: Action
		extra_entry_nodes = [n for n in graph.nodes if n.is_extra_entry_node]

		try:
			for node in graph.roots() + extra_entry_nodes:
				self.walk_at_node(node)
		except MacroAbort:
			return
