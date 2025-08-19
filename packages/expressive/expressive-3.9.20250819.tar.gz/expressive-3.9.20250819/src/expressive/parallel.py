""" Copyright 2025 Russell Fordyce

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
from threading import Thread
from queue import Queue
from queue import Empty as EmptyQueueException

import numpy

from .config import DTYPES_FILLER_HINT
from .messaging import warn

JOB_THREAD_EXIT = None


def worker_count_from_cores():
    """ the simple count of cores in a system isn't sufficient to determine the correct
        number of threads, instead, the number of worker cores that can be accessed is a
        far better metric - see official docs
         - https://docs.python.org/3/library/multiprocessing.html#multiprocessing.cpu_count
         - https://docs.python.org/3/library/os.html#os.cpu_count
        NOTE under py3.13+ CPython interpreter is killed on startup if PYTHON_CPU_COUNT or -X arg <=0

        additionally, while it's possible to have more process cores than system cores when a
        user simply sets it to be that way, such a case is probably wrong
          % python3.13 -c 'import os ; print(os.process_cpu_count())'
          12
          % PYTHON_CPU_COUNT=1000000 python3.13 -c 'import os ; print(os.process_cpu_count())'
          1000000
        instead, prefer to directly set ParallelRunner threadcount

        FUTURE consider if this should work with the `numba.set_num_threads()` system for prange too
          does it make sense to use upstream or to try and upstream this function?
    """
    cores_system  = os.cpu_count()  # total system cores count (2*physical cores in basically all amd64 systems)

    try:  # directly accept NUMBA_NUM_THREADS env
        workers = cores_process = int(os.environ["NUMBA_NUM_THREADS"])
        if workers < 1:  # definitely an integer if accepted
            raise OSError(f"NUMBA_NUM_THREADS must be int>=1 if set, but got {workers}")
    except KeyError:
        try:  # go ahead and try 3.13+ way to override `os.process_cpu_count()`
            cores_process = int(os.environ["PYTHON_CPU_COUNT"])
        except KeyError:
            cores_process = os.process_cpu_count() if sys.version_info[:2] >= (3, 13) else len(os.sched_getaffinity(0))
        if cores_process >= cores_system:
            # NOTE == case is normal, while > case is almost-certainly an env error
            workers = max(cores_system - 1, 1)  # prefer to reserve 1 core for system overhead
        else:  # cores_process < cores_system
            workers = cores_process

    if workers < 1:  # shouldn't be possible under py3.13, but might be earlier by setting PYTHON_CPU_COUNT=0
        raise OSError(f"impossible worker count detected: {workers}")
    if cores_system == 1 or cores_process == 1 or cores_process > cores_system:
        warn(
            f"possibly a bad environment: cores_system={cores_system} cores_process={cores_process} "
            f"set env NUMBA_NUM_THREADS before running or dynamically call "
            f"expressive.parallel.parallel_runner.update(threadcount=threadcount) to update the "
            f"threadcount to a reasonable value - using {workers} cores for now"
        )

    return workers


def data_slices(length, count):
    blocksize = length // count + 1
    pos_head = 0
    while pos_head < length:
        pos_next = min(pos_head + blocksize, length)  # don't overrun!
        yield pos_head, pos_next  # NOTE end is noninclusive
        pos_head = pos_next


def worker_parallel(Q_jobs, Q_error):
    """ Thread worker which consumes jobs from Queue """
    while True:  # run forever until program exit (daemon thread) or `ParallelRunner.stop()`
        job = Q_jobs.get()  # blocks, but daemon threads are still killed at program exit
        try:
            if job is JOB_THREAD_EXIT:
                return  # stop called: exit and wait for .join()
            fn, data, (start, end) = job  # just unpack 'em for now
            fn(**data, _offset_start=start, _offset_end=end)
        except Exception as ex:
            Q_error.put(ex)  # save the Exception for caller
        finally:  # always mark job as completed
            Q_jobs.task_done()


class ParallelRunner:
    """ parallel runner object class (should only be one instance, but not enforced) """

    def __init__(self, threadcount="auto"):
        self._set_threadcount(threadcount)
        self._Q_jobs  = Queue()
        self._Q_error = Queue()
        self.threads = []  # unfilled until .start() called to fill and start thread pool
        self._started = False  # wait until an instance is built to create threadpool

    def _set_threadcount(self, threadcount):
        if threadcount == "auto":
            threadcount = worker_count_from_cores()
        elif not isinstance(threadcount, int) or threadcount < 1:
            raise ValueError(f"threadcount must be int>=1, but got {repr(threadcount)}")
        self._threadcount = threadcount

    def start(self):
        """ create and start internal thread pool
            multiple calls will be ignored (only a single instance should exist)
            ideally starting the threads during build avoids adding the start overhead to the runtime
        """
        if not self._started:
            for index in range(self._threadcount):
                t = Thread(target=worker_parallel, args=(self._Q_jobs, self._Q_error), daemon=True)
                self.threads.append(t)
                t.start()
            self._started = True
        return self

    def stop(self):
        """ quit threadpool
            pool must be re-started with .start() if this method is called
            this shouldn't be needed during normal use, but has testing benefits
        """
        # TODO consider adding lock, though really this itself shouldn't need to be threadsafe
        #   Queue instance has a lock (.mutex), but re-using it feels troublesome
        if not self._started:
            return
        self.wait()
        for _ in self.threads:  # exit all threads by passing them a None job
            self._Q_jobs.put(JOB_THREAD_EXIT)
        for t in self.threads:
            t.join()  # thread is now ended
        self.threads.clear()  # no more references exist
        self._started = False

    def wait(self):
        # NOTE unlike threads, `Queue.join()` doesn't close the instance, but only blocks until
        #   `.task_done()` is called for each task which has been added to it (atomic counter)
        self._Q_jobs.join()
        try:
            err = self._Q_error.get_nowait()
        except EmptyQueueException:
            return  # success: no errors from workers
        else:       # at least one worker thread raised an Exception
            raise RuntimeError(f"caught ({self._Q_error.qsize() + 1}) Exception(s) in threads: {repr(err)}") from err

    def update(self, threadcount=None):  # FUTURE opportunity to update other properties
        if threadcount is not None:
            self.stop()
            self._set_threadcount(threadcount)
        return self.start()

    def parallelize(self, E, fn, data, dtype_result, result_passed):
        """ main method when E is called with native_threadpool parallelization model
        """
        # FUTURE consider `numpy.array_split()`?
        #   https://numpy.org/doc/stable/reference/generated/numpy.array_split.html
        #   if splitting verify each `ref.base is None`
        #   https://numpy.org/doc/stable/user/basics.copies.html

        # MUST raise for passing the case
        #  - refers to result array
        #  - offset
        # specifically the result data could become modified out-of-order
        # leading to incorrect results
        # no fix feels likely and Numba should/must handle this case too (especially prange)
        # possibly there are hacks like massive unrolling or discovering some `x*0` exists
        # NOTE relies on _prepare et al. to assure data validity in advance
        #   should work be done there for this?

        # get offsets needed for data chunks
        name_result = next(iter(E._results))
        indexers = E._indexers
        # FIXME no effect without indexers, should they all be adapted when parallel_mode set?
        if len(indexers) != 1:
            raise RuntimeError(f"BUG: expected len(indexers)==1, but got {indexers}")
        _, (_start, _end) = next(iter(indexers.items()))  # surprisingly no need for name
        # if name_result in data and _offset_start != 0 and _offset_end != 0:
        if _start != 0 or _end != 0:
            # raise NotImplementedError(f"can't combine passing result array with indexers: {indexers}")
            raise NotImplementedError(f"non-zero indexers are disallowed (for now): {indexers}")

        # just pass the edges?
        # TODO can caller pass length? (from ._prepare()`?)
        # TODO use combined datalen function [ISSUE 176]
        datalen = 0
        for ref in data.values():
            if ref.ndim == 0:
                continue
            datalen = len(ref)  # NOTE doesn't consider shape yet
            break
        else:
            raise RuntimeError("BUG: couldn't determine data length")

        # actually create the result array if it wasn't passed
        # TODO probably always do this to enable function return to be `numba.void`
        if result_passed:
            arr_result = data[name_result]
        else:
            data = data.copy()  # shallow copy enables including new result array
            filler = DTYPES_FILLER_HINT[dtype_result]
            # FIXME needs to be shape aware (at least improve with full_like and/or raise for mixed shapes)
            arr_result = numpy.full(datalen, filler, dtype=dtype_result)
            data[name_result] = arr_result

        # slight overhead, but hopefully helps case where some thread(s) take twice as long
        # TODO surely there's some good research here
        buckets = self._threadcount * 3
        if buckets > datalen:
            buckets = max(datalen // 3, 1)  # must have at least 1 bucket
            warn(f"very little data passed datalen={datalen}, using buckets={buckets}")

        for data_slice in data_slices(datalen, buckets):
            # job = fn, data, data_slice, counter
            job = fn, data, data_slice
            self._Q_jobs.put_nowait(job)

        # wait for jobs to complete (result array filled)
        # NOTE raises for Exception in worker thread
        self.wait()

        return arr_result  # mirror original API


# FUTURE consider pool or single process for simplification to take place in
#   SymPy simplification may take excessively long or never complete
#   in which case the process can be terminated and building continue
#   with a less-simplified expr
# WORKERS_PARALLEL = {
#     "parallelizer": ParallelRunner(),
# }

# NOTE threads are not created until an Expressive().build() is called
#   using the native_threadpool parallelization model
parallel_runner = ParallelRunner()
