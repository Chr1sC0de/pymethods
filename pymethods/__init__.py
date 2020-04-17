import multiprocessing as _mp
import CGALMethods
available_cpus = _mp.cpu_count()
from . import math
from . import utils
from . import algorithms
from . import multiprocess
from . import arrays
from . import parse
from . import pyplot
from . import construct
from . import templates

__all__ = [
    'math', 'utils', 'arrays', 'parse', 'pyplot', 'algorithms',
    'multiprocess', 'construct'
]
