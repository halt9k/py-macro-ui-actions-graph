import networkx as nx


class DiGraphEx(nx.DiGraph):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	# must be in a separate file because it damages inspection
	def roots(self):
		return [n for n, d in super().in_degree if d == 0]

	def leaves(self):
		return [n for n, d in super().out_degree if d == 0]
