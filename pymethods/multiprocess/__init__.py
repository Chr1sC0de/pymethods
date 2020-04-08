import multiprocessing as mp
import typing as tp
try:
    from pymethods import utils as ut
    from pymethods import available_cpus
except:
    from .. import utils as ut
    from .. import available_cpus
import numpy as np
from functools import partial
from . import ssh

def _maintain_np_shape(indexed, indexable):
    if ut.len_shape(indexable) > ut.len_shape(indexed):
        return indexed[None, :]
    return indexed


chunk_np_ndarray = partial(
    ut.chunk_iterable, callbacks=(_maintain_np_shape,)
)


class NumpyMulti:

    def __init__(self, arg_dict: dict, n_processors='max') -> None:
        if ut.is_string(n_processors):
            if n_processors in 'max':
                self.n_processors = available_cpus
            else:
                raise ValueError(f'{n_processors} can either be max or int')
        else:
            assert ut.is_int(n_processors),\
                ValueError(f'{n_processors} can either be max or int')
            self.n_processors = n_processors
        self.mp_queue = mp.Queue()
        self.processes = []
        self.arg_dict = arg_dict

    def run(self, *args, **kwargs):
        zipped_and_decomposed_list = self.decompose_arrays()

        for idx, args in zipped_and_decomposed_list:
            self.processes.append(
                mp.Process(
                    target=self.worker, args=(self.mp_queue, idx, *args))
            )
        self.start_all_processes()
        while 1:
            while not self.mp_queue.empty():
                self.reconstruct_arrays()
            running = any(
                [p.is_alive() for p in self.processes]
            )
            if not running:
                break
        self.join_all_processes()

    def reconstruct_arrays(self):
        if not hasattr(self, 'reconstructed'):
            self.reconstructed = np.zeros((self.n_processors, 1, self.arg_dict['a'].shape[-1]))
        #overwrite this method
        idx, output = self.mp_queue.get()
        self.reconstructed[idx] = output

    def decompose_arrays(self):
        decomposeable_list = []
        for key, val in self.arg_dict.items():
            chunked = chunk_np_ndarray(
                val, self.n_processors
            )
            decomposeable_list.append(chunked)
        zipped_dict = list(enumerate(
            list(zip(*decomposeable_list))
        ))
        return zipped_dict

    @staticmethod
    def worker(mp_q, idx, *args):
        mp_q.put((idx, sum(args)))

    @staticmethod
    def process(*args):
        return sum(args)

    def append_process(self, *, args: tp.Iterable):
        self.processes.append(
            mp.Process(target=self.worker, args=args)
        )

    def start_all_processes(self):
        [p.start() for p in self.processes]

    def join_all_processes(self):
        [p.join() for p in self.processes]


if __name__ == "__main__":
    a, b, c = np.zeros((3, 20, 10)) + 1.0

    argdict = dict(
        a=a, b=b, c=c
    )

    numpymult = NumpyMulti(
        arg_dict=argdict
    )
    numpymult.run()