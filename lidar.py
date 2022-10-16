import csv
import os, sys, signal
from math import cos, sin, pi, floor
from adafruit_rplidar import RPLidar
import time
from time import ctime, sleep
from datetime import datetime
from car_config import Config
import logging

# from multi_tool import Experiment

config_file = Config().dict

# Setup the RPLidar
PORT_NAME = '/dev/ttyUSB0' # config_file['lidar_port']
t = ctime()
output_csv = None
output = 'DataLog/RXDATA/Lidar/'


def current_time():
    newcur = ctime().split()[:]
    return '-'.join(str(x) for x in newcur)


def write_file():
    global output, output_csv
    output_csv = output + current_time() + '.csv'
    # write_csv_row('angle, distance, time')
    with open(output_csv, 'w+') as f:
        f.write('angle, distance, time\n')


def interrupt_handler(sig, frame, lidar):
    print_queue.put("Lidar shutting down...")
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    sys.stdout.flush()
    sys.exit(0)


# change to a Log file!


def lidar_main(ready, end, lidar_ready, print_queue):
    global output_csv
    try:
        write_file()
    except FileNotFoundError:
        print_queue.put(f'Lidar File Issue: {FileNotFoundError}')

    print_queue.put("Starting LIDAR>>>")
    lidar = RPLidar(None, PORT_NAME, baudrate=256000)
    info = None
    for i in range(1, 10):
        info = lidar.info
        if info is not None:
            print_queue.put(info)
            print_queue.put("Initiated scanning>>>")
            break
        else:
            print_queue.put(f'Attempting lidar... {i}sec elapsed')
        sleep(1)

    signal.signal(signal.SIGINT, interrupt_handler, lidar)
    # logging.basicConfig(filename="Datalog/Receiver/lidar_data_{}.log".format(time), level = logging.INFO)
    max_distance = 0
    try:
        filesize_timeout = 400
        # Set the flag so lidar is ready
        e = lidar_ready.set()
        print_queue.put(f'Lidar ready event set {e}')
        # Check for others to be ready
        start = False
        timeout = 200  # Timeout after 200 seconds
        done = False
        while timeout > 0 or ready:
            print_queue.put(f'Lidar checks Transmit, status: {ready}')
            start = ready.wait(5)
            timeout = timeout - 5
        check_end_cycle = 0
        if start:
            try:
                for scan in lidar.iter_scans():
                    for (_, angle, distance) in scan:
                        time.sleep(1 / 100)
                        check_end_cycle = 1 + check_end_cycle
                        if check_end_cycle % 200 == 0:
                            if end.is_set():
                                return 0
                        timedata = datetime.now().strftime('%H:%M:%S.%f')
                        with open(output_csv, 'a+') as f:
                            f.write(f'{angle}, {distance}, {timedata}\n')

            except KeyboardInterrupt or end.is_set():
                print_queue.put('Lidar signaled to end thread')
            finally:
                lidar.stop()
                lidar.stop_motor()
                lidar.disconnect()
                sys.stdout.flush()
                logging.info("Stop scanning")
                sys.exit(0)
        else:
            print_queue.put('lidar main timeout')
    except KeyboardInterrupt:
        print_queue.put('Keyboard interrupt')
    except RPLidarException:
        print_queue.put(f'Lidar: {RPLidarException}')
    finally:
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        sys.stdout.flush()
        logging.info("Stop scanning")
        sys.exit(0)
