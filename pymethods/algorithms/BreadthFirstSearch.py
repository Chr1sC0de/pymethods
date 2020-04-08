from ..utils import LockedDescriptor
from queue import Queue
from tqdm import tqdm
from typing import Iterable


class BreadthFirstSearch:

    adjacency_list = LockedDescriptor('_adjacency_list')

    def __init__(
            self, adjacency_list: Iterable[Iterable], properties=None,
            show_progress=False) -> None:
        self._adjacency_list = adjacency_list
        self.properties = properties
        self.traversal_dict = {i: False for i in range(len(adjacency_list))}
        self.show_progress = not show_progress
        self.reset_progress_bar()

    def __len__(self):
        if not hasattr(self, '_len'):
            self._len = len(self.traversal_dict)
        return self._len

    def __call__(
            self, start_vertex=0, end_vertices=None, n_progress_checks=10):
        self.n_progress_checks = n_progress_checks
        self.traversal_dict[start_vertex] = True
        self.current_vertex = start_vertex
        self.VertexQueue = Queue()
        self.VertexQueue.put(self.current_vertex)
        self._internal_counter = 0
        if hasattr(self, 'pre_bfs'):
            self.pre_bfs()

        while not self.VertexQueue.empty():
            self.query_current_vertex()
            for self.queried_edge_vertex in self.queried_vertex_edges:
                if hasattr(self, 'pre_edge_check'):
                    self.pre_edge_check()
                if not self.traversal_dict[self.queried_edge_vertex]:
                    self.traversal_dict[self.queried_edge_vertex] = True
                    self.VertexQueue.put(self.queried_edge_vertex)
                    if hasattr(self, 'on_unvisited_edge'):
                        self.on_unvisited_edge()
                    self._internal_counter += 1
                if hasattr(self, 'post_edge_check'):
                    self.post_edge_check()
            self.step_progress_bar()
        self.step_progress_bar()
        self.clean()

    def query_current_vertex(self):
        if hasattr(self, 'pre_vertex_query'):
            self.pre_vertex_query()
        self.queried_vertex = self.VertexQueue.get()
        self.queried_vertex_edges = self.adjacency_list[self.queried_vertex]
        if hasattr(self, 'post_vertex_query'):
            self.post_vertex_query()

    def step_progress_bar(self):
        check_1 = \
            self._internal_counter % (len(self)//self.n_progress_checks) == 0
        check_2 = self._internal_counter == (len(self)-1)

        if any([check_1, check_2]):
            self.n_complete = sum(self.traversal_dict.values())
            self.progress_bar.update(self.n_complete - self.last_steps)
            self.last_steps = self.n_complete

    def reset_progress_bar(self):
        self.progress_bar = tqdm(
            total=len(self.traversal_dict), disable=self.show_progress)
        self.last_steps = 0

    def clean(self):
        call_varialbles = [
            'current_vertex', 'VertexQueue', 'queried_vertex',
            'queried_vertex_edges', 'queried_edge_vertex', 'n_complete',
            'n_progress_checks'
        ]
        for var in call_varialbles:
            try:
                delattr(self, var)
            except:
                print('%s does not exist'%var)