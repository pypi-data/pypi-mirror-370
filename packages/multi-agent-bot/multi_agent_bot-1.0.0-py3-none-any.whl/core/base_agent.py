from typing import Any, Dict, Callable, Literal
from langgraph.graph import StateGraph
from langgraph.types import Command


class Agent:
    def __init__(
        self, state_type: Any, nodes: Dict[str, Callable[..., Command[Literal]]]
    ):
        self._state_type = state_type
        self._nodes = nodes
        self._compiled_graph = None

    def build_graph(self):
        if len({k.lower() for k in self._nodes}) != len(self._nodes):
            raise RuntimeError("Duplicated node names detected (case-insensitive).")

        graph = StateGraph(self._state_type)
        for name, fn in self._nodes.items():
            setattr(self, name, fn)
            graph.add_node(name, fn)
        graph.set_entry_point("supervisor")
        self._compiled_graph = graph.compile()
        return self._compiled_graph

    def __call__(self):
        if self._compiled_graph is None:
            return self.build_graph()
        return self._compiled_graph

    def invoke(self, state, **kwargs):
        if self._compiled_graph is None:
            self._compiled_graph = self.build_graph()
        # Set recursion limit to prevent infinite loops
        config = kwargs.get('config', {})
        if 'recursion_limit' not in config:
            config['recursion_limit'] = 50
        kwargs['config'] = config
        return self._compiled_graph.invoke(state, **kwargs)

    def stream(self, state, metadata=None):
        if self._compiled_graph is None:
            self._compiled_graph = self.build_graph()
        return self._compiled_graph.stream(state, metadata)
