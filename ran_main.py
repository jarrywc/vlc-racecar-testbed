import transmit, lidar, zed
from transmit import transmit_main
from lidar import lidar_main
from zed import zed_main
import threading, sys
from threading import Thread
from queue import Queue
from multi_tool import Sync, Experiment

print_queue = Queue()


def print_q(q=Queue()):
    while True:
        p = q.get()
        print(f'Print {p}')
        time.sleep(1)
        q.task_done()


def main(argv):
    global print_queue
    sync = Sync(9)
    lock = threading.Lock()
    experiment = Experiment(threading)
    transmit_ready = threading.Event()
    zed_ready = threading.Event()
    lidar_ready = threading.Event()
    transmit_end = threading.Event()

    # pq = threading.Thread(target=print_q(print_queue))
    transmit = threading.Thread(target=transmit_main(sys.argv[1:], transmit_ready, transmit_end, lidar_ready, zed_ready, print_queue ))
    print(f'Thread Transmit: {transmit.is_alive}')
    lidar = threading.Thread(target=lidar_main( transmit_ready, transmit_end, lidar_ready, print_queue ))
    print(f'Thread Lidar: {lidar.is_alive}')
    zed = threading.Thread(target=zed_main(transmit_ready, transmit_end, zed_ready, print_queue ))
    print(f'Thread ZED: {zed.is_alive}')

    transmit.setDaemon(True)
    lidar.setDaemon(True)
    zed.setDaemon(True)
    # pq.setDaemon(True)

    lidar.start()
    transmit.start()

    zed.start()
    # pq.start()

    print_q(print_queue)

    transmit.join()
    lidar.join()
    zed.join()
    # pq.join()
    if transmit.is_alive:
        print('Transmit alive')
    if lidar.is_alive:
        print('Lidar alive')
    if zed.is_alive:
        print('ZED alive')


if __name__ == '__main__':
    main(sys.argv[1:])
