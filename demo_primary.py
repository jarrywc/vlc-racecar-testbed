from threading import Thread
import queue
import heapq
import threading

print_queue = queue.Queue()

#  Statuses Published to refresh Terminal dashboard

lidar_pub = queue.Queue()
transmit_pub = queue.Queue()
zed_pub = queue.Queue()

published = queue.Queue()

published.put({'lidar': 'ready'})
published.put({'transmit': 'waiting'})
published.put({'zed': 'end'})
published.put({'main': 'killall'})


# If the


def print_q(q=Queue()):
    while True:
        p = q.get()
        print(f'Print {p}')
        time.sleep(1)
        q.task_done()


class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._count = 0
        self._cv = threading.Condition()

    def put(self, item, priority):
        with self._cv:
            heapq.heappush(self._queue, (-priority, self._count, item))
            self._count += 1
            self._cv.notify()

    def get(self):
        with self._cv:
            while len(self._queue) == 0:
                self._cv.wait()

# The priority queue lets high priority state changes to make it to the front

# For example {'main': 'killall'} could be set to high priority
