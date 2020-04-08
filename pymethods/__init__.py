import multiprocessing as _mp
available_cpus = _mp.cpu_count()
from . import math
from . import utils
from . import algorithms
from . import multiprocess
from . import arrays
from . import parse
from . import pyplot
from . import construct

__all__ = [
    'math', 'utils', 'arrays', 'parse', 'pyplot', 'algorithms',
    'multiprocess', 'construct'
]
