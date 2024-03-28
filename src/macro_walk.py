import time
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from functools import cached_property

import pyautogui

from helpers.pygraphviz import DiGraphEx
from macro_actions import Action, MacroAbort


class Macro:
	class NodeResults:
		@dataclass(init=True)
		class NodeResult:
			text: str
			color: str

		PASS = NodeResult('pass', 'green')
		END = NodeResult('end', 'red')
		MIXED = NodeResult('mixed', 'purple')

	class WalkLog:
		def __init__(self, graph: DiGraphEx):
			self.graph = graph

		visited_edges = {}
		node_results = {}

		@cached_property
		def unvisited_edges(self):
			return [e for e in self.graph.edges if e not in self.visited_edges]

	def __init__(self, description: str, actions_graph):
		self.description = description
		self.actions_graph = DiGraphEx(actions_graph)

		self.walk_log: Optional[Macro.WalkLog] = None

	def update_node_walk_result(self, node, result: bool):
		print(f'{result}: {node}')
		res = self.NodeResults.PASS if result else self.NodeResults.END

		log = self.walk_log.node_results
		if node not in log:
			log[node] = res
		elif log[node] != res:
			log[node] = self.NodeResults.MIXED

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

			self.walk_log.visited_edges[node, next_node] = True
			if self.walk_at_node(next_node):
				return

	def run_macro(self):
		self.walk_log = self.WalkLog(self.actions_graph)

		print(self.description)
		graph = self.actions_graph

		node: Action
		extra_entry_nodes = [n for n in graph.nodes if n.is_extra_entry_node]

		try:
			for node in graph.roots() + extra_entry_nodes:
				self.walk_at_node(node)
		except MacroAbort:
			return
