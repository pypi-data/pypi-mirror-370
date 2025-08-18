"""Core rechunking algorithm stuff."""
# import copy
from typing import List, Optional, Sequence, Tuple, Iterator, Generator
import numpy as np
import itertools
# from time import time
from math import prod, lcm, ceil
from collections import Counter, deque
from collections.abc import Callable
from itertools import count
from bisect import bisect

########################################################
### Parameters

composite_numbers = (1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720, 840, 1260, 1680, 2520, 5040, 7560, 10080, 15120, 20160, 25200, 27720, 45360, 50400, 55440, 83160, 110880, 166320, 221760, 277200, 332640, 498960, 554400, 665280, 720720, 1081080, 1441440, 2162160)

########################################################
### Functions


def guess_chunk_shape(shape: Tuple[int, ...], itemsize: int, target_chunk_size: int = 2**21) -> Tuple[int, ...]:
    """
    Guess an appropriate chunk layout for a dataset, given its shape and
    the size of each element in bytes.  Will allocate chunks only as large
    as target_chunk_size. Chunks will be assigned to the highest composite number within the target_chunk_size. Using composite numbers will benefit the rehunking process as there is a very high likelihood that the least common multiple of two composite numbers will be significantly lower than the product of those two numbers.

    Parameters
    ----------
    shape: tuple of ints
        Shape of the array.
    itemsize: int
        The byte size of the data type. It must be a numpy bytes size: 1, 2, 4, or 8
    target_chunk_size: int
        The maximum size per chunk in bytes.

    Returns
    -------
    tuple of ints
        shape of the chunk
    """
    ndims = len(shape)

    if ndims > 0:

        if not all(isinstance(v, int) for v in shape):
            raise TypeError('All values in the shape must be ints.')

        chunks = np.array(shape, dtype='=f8')
        if not np.all(np.isfinite(chunks)):
            raise ValueError("Illegal value in chunk tuple")

        idx = 0
        while True:
            chunk_bytes = prod(chunks)*itemsize

            if (chunk_bytes < target_chunk_size or \
             abs(chunk_bytes - target_chunk_size)/target_chunk_size < 0.5):
                break

            if prod(chunks) == 1:
                break

            chunks[idx%ndims] = ceil(chunks[idx%ndims] / 2.0)
            idx += 1

        return tuple(composite_numbers[bisect(composite_numbers, int(x)) - 1] for x in chunks)
    else:
        return None


def get_slice_min_max(read_slices, write_slices):
    """
    Function to get the max start position and the min stop position.
    """
    slices = tuple(slice(max(rs.start, ws.start), min(rs.stop, ws.stop)) for rs, ws in zip(read_slices, write_slices))

    return slices


def chunk_range(
    chunk_start: Tuple[int, ...], chunk_stop: Tuple[int, ...], chunk_step: Tuple[int, ...], include_partial_chunks=True, clip_ends=True,
) -> Iterator[Tuple[slice, ...]]:
    """
    Generator like the Python range function, but for multiple dimensions and it returns tuples of slices.

    Parameters
    ----------
    chunk_start: tuple of int
        The start positions of the chunks.
    chunk_stop: tuple of int
        The stop positions of the chunks.
    chunk_step: tuple of int
        The chunking step.
    include_partial_chunks: bool
        Should partial chunks be included? True by default.
    clip_ends: bool
        Only applies when include_partial_chunks == True. Should the chunks be clipped to the overall extents? True by default.

    Returns
    -------
    Generator with tuples of slices
    """
    if not isinstance(chunk_start, tuple):
        chunk_start = tuple(0 for i in range(len(chunk_stop)))

    if include_partial_chunks:
        start_ranges = [cs * (sc//cs) for cs, sc in zip(chunk_step, chunk_start)]
    else:
        start_ranges = [cs * (((sc - 1)//cs) + 1) for cs, sc in zip(chunk_step, chunk_start)]

    ranges = [range(sr, ec, cs) for ec, cs, sr in zip(chunk_stop, chunk_step, start_ranges)]

    for indices in itertools.product(*ranges):
        # print(indices)
        inside = True
        res = []
        for i, ec, cs, sc in zip(indices, chunk_stop, chunk_step, chunk_start):
            stop = i + cs
            if stop > ec:
                if clip_ends:
                    stop = ec
                inside = False

            start = i
            if start < sc:
                if clip_ends:
                    start = sc
                inside = False

            res.append(slice(start, stop))

        if inside or include_partial_chunks:
            yield tuple(res)


def calc_ideal_read_chunk_shape(source_chunk_shape, target_chunk_shape):
    """
    Calculates the minimum ideal read chunk shape between a source and target.
    """
    return tuple(lcm(i, s) for i, s in zip(source_chunk_shape, target_chunk_shape))


def calc_ideal_read_chunk_mem(ideal_read_chunk_shape, itemsize):
    """
    Calculates the minimum ideal read chunk memory between a source and target.
    """
    return int(prod(ideal_read_chunk_shape) * itemsize)


def calc_source_read_chunk_shape(source_chunk_shape, target_chunk_shape, itemsize, max_mem):
    """
    Calculates the optimum read chunk shape given a maximum amount of available memory.

    Parameters
    ----------
    source_chunk_shape: tuple of int
        The source chunk shape
    target_chunk_shape: tuple of int
        The target chunk shape
    itemsize: int
        The byte length of the data type.
    max_mem: int
        The max allocated memory to perform the chunking operation in bytes.

    Returns
    -------
    optimal chunk shape: tuple of ints
    """
    max_cells = max_mem // itemsize
    source_len = len(source_chunk_shape)
    target_len = len(target_chunk_shape)

    if source_len != target_len:
        raise ValueError('The source_chunk_shape and target_chunk_shape do not have the same number of dims.')

    tot_source = prod(source_chunk_shape)
    if tot_source >= max_cells:
        return source_chunk_shape

    new_chunks = list(calc_ideal_read_chunk_shape(source_chunk_shape, target_chunk_shape))

    ## Max mem
    tot_target = prod(new_chunks)
    pos = 0
    while tot_target > max_cells:
        prod_chunk = new_chunks[pos]
        source_chunk = source_chunk_shape[pos]
        if prod_chunk > source_chunk:
            new_chunks[pos] = prod_chunk - source_chunk

        tot_target = prod(new_chunks)

        if tot_target == tot_source:
            return source_chunk_shape
        else:
            if pos + 1 == source_len:
                pos = 0
            else:
                pos += 1

    ## Min mem
    n_chunks_write = tuple(s//target_chunk_shape[i] for i, s in enumerate(new_chunks))
    for i in range(len(new_chunks)):
        while True:
            n_chunk_write = n_chunks_write[i]
            prod_chunk = new_chunks[i]
            source_chunk = source_chunk_shape[i]
            target_chunk = target_chunk_shape[i]
            new_chunk = prod_chunk - source_chunk
            if new_chunk//target_chunk == n_chunk_write:
                new_chunks[i] = new_chunk
            else:
                break

    return tuple(new_chunks)


def calc_n_chunks_per_read(source_chunk_shape, source_read_chunk_shape):
    """

    """
    return prod(tuple(nc//sc for nc, sc in zip(source_read_chunk_shape, source_chunk_shape)))


def calc_n_chunks(shape, chunk_shape):
    """

    """
    chunk_start = tuple(0 for i in range(len(shape)))
    chunk_iter = chunk_range(chunk_start, shape, chunk_shape)

    counter = count()
    deque(zip(chunk_iter, counter), maxlen=0)

    return next(counter)


def calc_n_reads_simple(shape, source_chunk_shape, target_chunk_shape):
    """
    Brute force chunking read count. Every target chunk must iterate over every associated source chunk. This should be considered the maximum number of reads between a source and target (most inefficient). The number of writes is the total number of chunks in the target.

    Parameters
    ----------
    shape: tuple of ints
        The shape of the source dataset, which will also be the shape of the target dataset.
    dtype: np.dtype
        The numpy data type of the source/target.
    source_chunk_shape: tuple of ints
        The chunk_shape of the source.
    target_chunk_shape: tuple of ints
        The chunk_shape of the target.

    Returns
    -------
    int
        Count of the number of reads
    """
    chunk_start = tuple(0 for i in range(len(shape)))
    read_counter = count()

    for write_chunk in chunk_range(chunk_start, shape, target_chunk_shape):
        write_chunk_start = tuple(rc.start for rc in write_chunk)
        write_chunk_stop = tuple(rc.stop for rc in write_chunk)
        for chunk_slice in chunk_range(write_chunk_start, write_chunk_stop, source_chunk_shape):
            next(read_counter)

    return next(read_counter)


def calc_n_reads_rechunker(shape: Tuple[int, ...], itemsize: int,  source_chunk_shape: Tuple[int, ...], target_chunk_shape: Tuple[int, ...], max_mem: int, sel=None) -> Tuple[int, int]:
    """
    This function calculates the total number of reads (aand writes) using the more optimized rechunking algorithm. It optimises the rechunking by using an in-memory numpy ndarray with a size defined by the max_mem provided by the user.

    Parameters
    ----------
    source: array-like
        The source function to read the dataset/array. The function must have a single parameter input as a tuple of slices to retrieve an array chunk of data.
    shape: tuple of ints
        The shape of the source dataset, which will also be the shape of the target dataset.
    itemsize: int
        The byte length of the data type.
    source_chunk_shape: tuple of ints
        The chunk_shape of the source.
    target_chunk_shape: tuple of ints
        The chunk_shape of the target.
    max_mem: int
        The max allocated memory to perform the chunking operation in bytes.
    sel: tuple of slices
        A subset selection of the source in the form of a tuple of slices. The starts and stops must be within the shape of the source.

    Returns
    -------
    tuple
        number of reads, number of writes
    """
    ## Calc the optimum read_chunk_shape
    source_read_chunk_shape = calc_source_read_chunk_shape(source_chunk_shape, target_chunk_shape, itemsize, max_mem)

    ## Calc ideal read chunking shape
    ideal_read_chunk_shape = calc_ideal_read_chunk_shape(source_chunk_shape, target_chunk_shape)

    chunk_start = tuple(0 for i in range(len(shape)))

    if sel is None:
        target_shape = shape
    else:
        # Checks
        for s, sh in zip(sel, shape):
            if s.start < 0 or s.stop > sh:
                raise ValueError('The selection must be a subset of the source.')

        target_shape = tuple(s.stop - s.start for s in sel)

    ## Counters
    read_counter = count()
    write_counter = count()
    # write_counter2 = count()

    ## If the read chunking is set to the ideal chunking case, then use the simple implementation. Otherwise, use the more complicated one.
    if source_read_chunk_shape == ideal_read_chunk_shape:
        read_chunk_iter = chunk_range(chunk_start, target_shape, source_read_chunk_shape)
        for read_chunk_grp in read_chunk_iter:
            read_chunk_grp_start = tuple(s.start for s in read_chunk_grp)
            read_chunk_grp_stop = tuple(s.stop for s in read_chunk_grp)
            for read_chunk in chunk_range(read_chunk_grp_start, read_chunk_grp_stop, source_chunk_shape):
                next(read_counter)

            for write_chunk1 in chunk_range(read_chunk_grp_start, read_chunk_grp_stop, target_chunk_shape):
                next(write_counter)

    else:
        writen_chunks = set() # Need to keep track of the bulk writes

        write_chunk_iter = chunk_range(chunk_start, target_shape, target_chunk_shape)

        for write_chunk in write_chunk_iter:
            write_chunk_start = tuple(s.start for s in write_chunk)
            if write_chunk_start not in writen_chunks:
                write_chunk_stop = tuple(s.stop for s in write_chunk)

                read_chunk_start = tuple(rc * (wc//rc) for wc, rc in zip(write_chunk_start, source_chunk_shape))
                read_chunk_stop = tuple(min(max(rcs + rc, wc), sh) for rcs, rc, wc, sh in zip(read_chunk_start, source_read_chunk_shape, write_chunk_stop, shape))
                read_chunks_iter = chunk_range(read_chunk_start, read_chunk_stop, source_chunk_shape, True, False)

                if all(stop - start <= rcs for start, stop, rcs in zip(read_chunk_start, read_chunk_stop, source_read_chunk_shape)):
                    for read_chunk in read_chunks_iter:
                        next(read_counter)

                    is_end_chunk = any(wc.stop == ts for wc, ts in zip(write_chunk, target_shape))
                    for write_chunk1 in chunk_range(write_chunk_start, read_chunk_stop, target_chunk_shape, include_partial_chunks=is_end_chunk, clip_ends=False):
                        write_chunk2 = tuple(slice(wc.start, min(wc.stop, s)) for wc, s in zip(write_chunk1, target_shape))
                        if all(all((wc.stop - wcs <= src, wc.start < wc.stop)) for wcs, wc, src in zip(read_chunk_start, write_chunk2, source_read_chunk_shape)):
                            write_chunk1_start = tuple(s.start for s in write_chunk2)
                            if write_chunk1_start not in writen_chunks:
                                next(write_counter)

                                writen_chunks.add(write_chunk1_start)
                else:
                    for read_chunk in read_chunks_iter:
                        next(read_counter)

                    next(write_counter)

                    writen_chunks.add(write_chunk_start)

    return next(read_counter), next(write_counter)


def rechunker(source: Callable, shape: Tuple[int, ...], dtype: np.dtype, itemsize: int, source_chunk_shape: Tuple[int, ...], target_chunk_shape: Tuple[int, ...], max_mem: int, sel=None) -> Iterator[Tuple[Tuple[slice, ...], np.ndarray]]:
    """
    This function takes a source dataset function with a specific chunk_shape and returns a generator that converts to a new chunk_shape. It optimises the rechunking by using an in-memory numpy ndarray with a size defined by the max_mem provided by the user.

    Parameters
    ----------
    source: array-like
        The source function to read the dataset/array. The function must have a single parameter input as a tuple of slices to retrieve an array chunk of data.
    shape: tuple of ints
        The shape of the source dataset, which will also be the shape of the target dataset unless sel is passed.
    dtype: np.dtype
        The numpy data type of the source/target.
    itemsize: int
        The byte length of the data type.
    source_chunk_shape: tuple of ints
        The chunk_shape of the source.
    target_chunk_shape: tuple of ints
        The chunk_shape of the target.
    max_mem: int
        The max allocated memory to perform the chunking operation in bytes. This will only be as large as necessary for an optimum size chunk for the rechunking.
    sel: tuple of slices
        A subset selection of the source in the form of a tuple of slices. The starts and stops must be within the shape of the source.

    Returns
    -------
    Generator
        tuple of the target slices to the np.ndarray of data
    """
    ## Calc the optimum read_chunk_shape
    source_read_chunk_shape = calc_source_read_chunk_shape(source_chunk_shape, target_chunk_shape, itemsize, max_mem)

    mem_arr1 = np.zeros(source_read_chunk_shape, dtype=dtype)

    ## Calc ideal read chunking shape
    ideal_read_chunk_shape = calc_ideal_read_chunk_shape(source_chunk_shape, target_chunk_shape)

    chunk_start = tuple(0 for i in range(len(shape)))

    if sel is None:
        chunk_read_offset = chunk_start
        target_shape = shape
    else:
        # Checks
        for s, sh in zip(sel, shape):
            if s.start < 0 or s.stop > sh:
                raise ValueError('The selection must be a subset of the source.')

        chunk_read_offset = tuple(s.start for s in sel)
        target_shape = tuple(s.stop - s.start for s in sel)

    # target = np.zeros(target_shape, dtype=dtype)

    ## If the read chunking is set to the ideal chunking case, then use the simple implementation. Otherwise, use the more complicated one.
    if source_read_chunk_shape == ideal_read_chunk_shape:
        read_chunk_iter = chunk_range(chunk_start, target_shape, source_read_chunk_shape)
        for read_chunk_grp in read_chunk_iter:
            read_chunk_grp_start = tuple(s.start for s in read_chunk_grp)
            read_chunk_grp_stop = tuple(s.stop for s in read_chunk_grp)
            for read_chunk in chunk_range(read_chunk_grp_start, read_chunk_grp_stop, source_chunk_shape):
                offset_slices = tuple(slice(rc.start - wcs, rc.stop - wcs) for wcs, rc in zip(read_chunk_grp_start, read_chunk))
                read_chunk1 = tuple(slice(rc.start + cro, rc.stop + cro) for rc, cro in zip(read_chunk, chunk_read_offset))
                mem_arr1[offset_slices] = source(read_chunk1)

            for write_chunk1 in chunk_range(read_chunk_grp_start, read_chunk_grp_stop, target_chunk_shape):
                offset_slices = tuple(slice(wc.start - wcs, wc.stop - wcs) for wcs, wc in zip(read_chunk_grp_start, write_chunk1))

                # target[write_chunk1] = mem_arr1[offset_slices]

                yield write_chunk1, mem_arr1[offset_slices]

    else:
        writen_chunks = set() # Need to keep track of the bulk writes

        write_chunk_iter = chunk_range(chunk_start, target_shape, target_chunk_shape)

        for write_chunk in write_chunk_iter:
            write_chunk_start = tuple(s.start for s in write_chunk)
            if write_chunk_start not in writen_chunks:
                write_chunk_stop = tuple(s.stop for s in write_chunk)

                read_chunk_start = tuple(rc * (wc//rc) for wc, rc in zip(write_chunk_start, source_chunk_shape))
                read_chunk_stop = tuple(min(max(rcs + rc, wc), sh) for rcs, rc, wc, sh in zip(read_chunk_start, source_read_chunk_shape, write_chunk_stop, shape))
                read_chunks_iter = chunk_range(read_chunk_start, read_chunk_stop, source_chunk_shape, True, False)

                if all(stop - start <= rcs for start, stop, rcs in zip(read_chunk_start, read_chunk_stop, source_read_chunk_shape)):
                    for read_chunk in read_chunks_iter:
                        read_chunk1 = tuple(slice(rc.start + cro, min(rc.stop + cro, s)) for rc, cro, s in zip(read_chunk, chunk_read_offset, shape))
                        offset_slices = tuple(slice(rc.start - rcs - rco, rc.stop - rcs - rco) for rcs, rco, rc in zip(read_chunk_start, chunk_read_offset, read_chunk1))

                        mem_arr1[offset_slices] = source(read_chunk1)

                    is_end_chunk = any(wc.stop == ts for wc, ts in zip(write_chunk, target_shape))
                    for write_chunk1 in chunk_range(write_chunk_start, read_chunk_stop, target_chunk_shape, include_partial_chunks=is_end_chunk, clip_ends=False):
                        write_chunk2 = tuple(slice(wc.start, min(wc.stop, s)) for wc, s in zip(write_chunk1, target_shape))
                        if all(all((wc.stop - wcs <= src, wc.start < wc.stop)) for wcs, wc, src in zip(read_chunk_start, write_chunk2, source_read_chunk_shape)):
                            write_chunk1_start = tuple(s.start for s in write_chunk2)
                            if write_chunk1_start not in writen_chunks:
                                offset_slices = tuple(slice(wc.start - rcs, wc.stop - rcs) for rcs, wc in zip(read_chunk_start, write_chunk2))
                                # print(write_chunk1, offset_slices)

                                # target[write_chunk2] = mem_arr1[offset_slices]

                                yield write_chunk2, mem_arr1[offset_slices]

                                writen_chunks.add(write_chunk1_start)
                                # if write_chunk1_start == (14, 5):
                                #     raise ValueError()
                else:
                    mem_read_chunk_slice = tuple(slice(0, wc.stop - wc.start) for wc in write_chunk)
                    # for read_chunk in chunk_range(write_chunk_start, write_chunk_stop, source_chunk_shape, True, False):
                    for read_chunk in read_chunks_iter:
                        read_chunk1 = tuple(slice(rc.start + cro, rc.stop + cro) for rc, cro in zip(read_chunk, chunk_read_offset))
                        clip_read_chunk = get_slice_min_max(read_chunk, write_chunk)
                        read_slice = tuple(slice(cc.start - rc.start, cc.stop - rc.start) for cc, rc in zip(clip_read_chunk, read_chunk))
                        write_slice = tuple(slice(cc.start - rc.start, cc.stop - rc.start) for cc, rc in zip(clip_read_chunk, write_chunk))

                        # print(read_chunk, read_slice, write_slice)
                        mem_arr1[write_slice] = source(read_chunk1)[read_slice]

                    # target[write_chunk] = mem_arr1[mem_read_chunk_slice]

                    yield write_chunk, mem_arr1[mem_read_chunk_slice]

                    writen_chunks.add(write_chunk_start)




























































