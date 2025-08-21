"""A multi-producer, multi-consumer closable queue."""

import threading
from collections import deque
from time import monotonic as time


class Empty(Exception):
    "Exception raised by Queue.get(block=0)/get_nowait()."


class Full(Exception):
    "Exception raised by Queue.put(block=0)/put_nowait()."


class Closed(Exception):
    """Exception to indicate that the ClosableQueue is closed."""



class ClosableQueue:
    """Create a queue object with a given maximum size.

    If maxsize is <= 0, the queue size is infinite.

    This adds an extra behavior where a producer can `close` the queue,
    to indicate that no new items will be added. Semantics:
      `get`: When a queue is closed, `get` calls will succeed until the queue is empty,
             at which point further get calls will raise `Closed`. All pending `get`,
             which happens when the queue is already empty, will be pre-empted and raise `Closed`.

      `put`: When a queue is closed, `put` calls raise `Closed`. All pending `put`
             will be pre-empted and also raise `Closed`.

    NOTE: This implementation is inspired by the stdlib implementation.
    The code has been adapted to handle the semantics of the `close`.
    Reference: https://github.com/python/cpython/blob/3.8/Lib/queue.py
    """

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)

        # mutex must be held whenever the queue is mutating.  All methods
        # that acquire mutex must release it before returning.  mutex
        # is shared between the three conditions, so acquiring and
        # releasing the conditions also acquires and releases mutex.
        self.mutex = threading.Lock()

        # Notify not_empty whenever an item is added to the queue; a
        # thread waiting to get is notified then.
        self.not_empty = threading.Condition(self.mutex)

        # Notify not_full whenever an item is removed from the queue;
        # a thread waiting to put is notified then.
        self.not_full = threading.Condition(self.mutex)

        # Notify all_tasks_done whenever the number of unfinished tasks
        # drops to zero; thread waiting to join() is notified to resume
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

        self._is_closed = False

    def task_done(self):
        """Indicate that a formerly enqueued task is complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).

        Raises a ValueError if called more times than there were items
        placed in the queue.
        """
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    msg = "task_done() called too many times"
                    raise ValueError(msg)
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self):
        """Blocks until all items in the Queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()

    def qsize(self):
        """Return the approximate size of the queue (not reliable!)."""
        with self.mutex:
            return self._qsize()

    def put(self, item, block=True, timeout=None):
        """Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        """
        with self.not_full:
            if self._is_closed:
                msg = "Cannot add to a closed queue."
                raise Closed(msg)

            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize and not self._is_closed:
                        self.not_full.wait()
                elif timeout < 0:
                    msg = "'timeout' must be a non-negative number"
                    raise ValueError(msg)
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize and not self._is_closed:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)

            # Handle the case where we are done waiting because the
            # queue is closed.
            if self._is_closed:
                msg = "Cannot add to a closed queue."
                raise Closed(msg)

            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        with self.not_empty:
            # Handle the case where the queue is closed and already empty.
            # We should not have to wait.
            if not self._qsize() and self._is_closed:
                msg = "Cannot get from a closed queue with no items."
                raise Closed(msg)

            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize() and not self._is_closed:
                    self.not_empty.wait()
            elif timeout < 0:
                msg = "'timeout' must be a non-negative number"
                raise ValueError(msg)
            else:
                endtime = time() + timeout
                while not self._qsize() and not self._is_closed:
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)

            # Handle the case where we are done waiting because the
            # queue is closed.
            if self._is_closed and not self._qsize():
                msg = "Cannot get from a closed queue with no items."
                raise Closed(msg)

            item = self._get()
            self.not_full.notify()
            return item

    def put_nowait(self, item):
        """Put an item into the queue without blocking.

        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.
        """
        return self.put(item, block=False)

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.

        Only get an item if one is immediately available. Otherwise
        raise the Empty exception.
        """
        return self.get(block=False)

    def close(self) -> None:
        with self.mutex:
            if self._is_closed:
                msg = "Cannot `close` an already closed queue."
                raise Closed(msg)
            self._is_closed = True

        # We need to notify waiters that this queue is closed.
        with self.not_empty:
            self.not_empty.notify_all()

        # We need to notify waiters that this queue is closed.
        with self.not_full:
            self.not_full.notify_all()

    def is_closed(self) -> bool:
        with self.mutex:
            return self._is_closed

    # Override these methods to implement other queue organizations
    # (e.g. stack or priority queue).
    # These will only be called with appropriate locks held

    # Initialize the queue representation
    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        return len(self.queue)

    # Put a new item in the queue
    def _put(self, item):
        self.queue.append(item)

    # Get an item from the queue
    def _get(self):
        return self.queue.popleft()
