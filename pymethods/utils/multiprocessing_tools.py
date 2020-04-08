from typing import Iterable, Callable
import numpy as np
from time import time


def time_func(func, *args, **kwargs):
    start = time()
    outputs = func(*args, **kwargs)
    end = time()
    return (end-start, outputs)


def chunk_iterable(
        indexable: Iterable, num_chunk: int, callbacks=None) -> list:
    """chunk_iterable

    For some iterable generate num_chunk, approximately even number of chunks

    Args:
        iterable (Iterable): an iterable to be chunked
        num_chunk (int): total number of chunks to generate
        callbacks (Iterable[Callable]): an iterable containing callable methods
            which take two arguments (indexed, indexable). These callbacks
            operate over these indexable values and outputs the values
            of the current chunk

    Returns:
        list: a list of lists of chunks from the iterabel
    """

    try:
        indexable[0]
    except ValueError:
        indexable = list(indexable)
    len_indexable = len(indexable)
    avg_len = len_indexable // num_chunk
    out = []
    for i in range(num_chunk):
            k = i * avg_len
            if i < (num_chunk-1):
                append_item = indexable[k:(k+avg_len)]       
            else:
                append_item = indexable[k:]

            if callbacks is not None:
                for callback in callbacks:
                    append_item = callback(append_item, indexable)

            out.append(append_item)

    total_enumerated = 0
    for item in out:
        total_enumerated += len(item)
    assert total_enumerated == len_indexable, \
        "Something went wrong, sum of all chunked\
            items is shorter than total items"
    return out


def enumerate_chunk(iterable: Iterable, num: int) -> list:
        chunked = chunk_iterable(iterable, num)
        return enumerate(chunked)


def sort_pair_list_and_extract_items(mp_list: list) -> list:
        """sort_and_extract_mp_list

        A list when enumerated and zipped has the form:
            [(key, item_1),..., (key, item_n)]
        This method sorts the input list by the
        key and extracts a list of the items.

        Args:
            mp_list (list): enumerated zipped list

        Returns:
            list: the sorted list of items
        """
        mp_list.sort(key=lambda x: x[0])
        output = []
        mp_list = [item[1] for item in mp_list]
        [output.extend(item) for item in mp_list]
        sorted_list = output
        return sorted_list
