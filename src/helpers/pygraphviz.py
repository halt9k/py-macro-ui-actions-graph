from functools import lru_cache

import networkx as nx

from macro_actions import Action


class DiGraphEx(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @lru_cache(maxsize=10, typed=True)
    def indexed_nodes(self, filter_draw_type: Action.DrawMode = None) -> {}:
        """ Dict output here is nessesary for compartability with plot lib, also gives index in node array """

        if filter_draw_type:
            return {n: i for i, n in enumerate(self.nodes) if n.draw_mode == filter_draw_type}
        else:
            return {n: i for i, n in enumerate(self.nodes)}

    # must be in a separate file because it damages inspection
    def roots(self):
        return [n for n, d in super().in_degree if d == 0]

    def leaves(self):
        return [n for n, d in super().out_degree if d == 0]
