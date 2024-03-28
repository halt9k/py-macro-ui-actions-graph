from functools import lru_cache
from typing import Optional, Type, Union

import networkx as nx


from macro_actions import Action


class DiGraphEx(nx.DiGraph):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@lru_cache(maxsize=10, typed=True)
	def nodes_of_class(self, filter_class: Type[Action] = None) -> {}:
		""" Dict output here is nessesary for compartability with plot lib, also gives index in node array """
		filtered = {}
		for i, n in enumerate(super().nodes):
			if filter_class:
				if isinstance(n, filter_class):
					filtered[n] = i
			else:
				filtered[n] = i
		return filtered
		# return {n for n in super().nodes if isinstance(n, filter_class)}

	# must be in a separate file because it damages inspection
	def roots(self):
		return [n for n, d in super().in_degree if d == 0]

	def leaves(self):
		return [n for n, d in super().out_degree if d == 0]
