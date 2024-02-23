from typing import Type

import networkx as nx

from actions import Action
from helpers.os_helpers import run_in_thread
from abc import ABC


class Macro(ABC):
    # this is just a draft, proper inheritance is worse here
    description: str
    actions_graph: nx.DiGraph
    result_record: dict


def try_walk_from_node(graph: nx.DiGraph, node: Action, prev_node: Action or None, result_record: {}):
    def run_node_action(n):
        return run_in_thread(n.run) if n.parallel_run else n.run()

    if run_node_action(node):
        result_record[prev_node, node] = True
        print(f'ok: {node}')
    else:
        print(f'failed: {node}')
        result_record[prev_node, node] = False
        return

    for next_node in graph.successors(node):
        try_walk_from_node(graph, next_node, node, result_record)


def try_walk_actions_graph(macro: Type[Macro]):
    # can be optimized not to take again screenshots on failed click steps
    macro.result_record = {}

    print(macro.description)
    graph = macro.actions_graph

    node: Action
    entry_nodes = [node for node in graph.nodes if graph.in_degree(node) == 0 or node.extra_entry_node]
    for node in entry_nodes:
        try_walk_from_node(graph, node, None, macro.result_record)
