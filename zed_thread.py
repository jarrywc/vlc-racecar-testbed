"""
    Multi cameras sample showing how to open multiple ZED in one program
"""

import pyzed.sl as sl
import cv2, csv
import numpy as np
import threading
import time
import signal
from time import ctime
import sys, getopt

zed_list = []
left_list = []
depth_list = []
timestamp_list = []
thread_list = []
stop_signal = False


class TimeHandler:
    def __init__(self):
        self.t_imu = sl.Timestamp()
        self.t_baro = sl.Timestamp()
        self.t_mag = sl.Timestamp()

    def new_data(self, sensor):
        if (isinstance(sensor, sl.IMUData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_imu.get_microseconds())
            if new_:
                self.t_imu = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.MagnetometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_mag.get_microseconds())
            if new_:
                self.t_mag = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.BarometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_baro.get_microseconds())
            if new_:
                self.t_baro = sensor.timestamp
            return new_


def signal_handler(signal, frame):
    global stop_signal
    stop_signal = True
    time.sleep(0.5)
    exit()


def current_time():
    newcur = ctime().split()[:]
    return '-'.join(str(x) for x in newcur)


def get_res_framerate (resolution_string: str, frame_rate: str):
    cleaned = resolution_string.lower()
    res = sl.RESOLUTION.VGA
    if cleaned in ('wvga', 'vga'):
        res = sl.RESOLUTION.VGA
    elif cleaned in ('hd'):
        res = sl.RESOLUTION.HD720
    elif cleaned in ('fullhd', 'fhd'):
        res = sl.RESOLUTION.HD1080
    elif cleaned in ('4k', '2k', '2.2k'):
        res = sl.RESOLUTION.HD2K
    else:
        print('Incorrect Resolution requested, use WVGA, HD, FULLHD, 4K')
        usage()
        exit()
    fps_request = int(frame_rate)
    rate = 100
    if fps_request not in (15, 30, 60, 100):
        print('Incorrect framerate requested, use 15, 30, 60, 100')
        usage()
        exit()
    elif fps_request == 15:
         rate = 15
    elif fps_request == 30 and res in (sl.RESOLUTION.VGA, sl.RESOLUTION.HD720, sl.RESOLUTION.HD1080):
        rate = 30
    elif fps_request == 60 and res in (sl.RESOLUTION.VGA, sl.RESOLUTION.HD720):
        rate = 60
    elif fps_request == 100 and res == sl.RESOLUTION.VGA:
        rate = 100
    else:
        print('Something incredible has happened, you have somehow broken everything')
        usage()
        exit()
    return res, rate


def grab_run(index):
    global stop_signal
    global zed_list
    global timestamp_list
    global left_list
    global depth_list
    global sensors_data
    ts_handler = TimeHandler()
    sensors_data = sl.SensorsData()
    runtime = sl.RuntimeParameters()
    with open("DataLog/RXDATA/IMU/DATA-{}.csv".format(current_time()), mode='w') as file_append_row:
        write_header = csv.writer(file_append_row, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        write_header.writerow(['Orientation',
                               'Acceleration',
                               'Angular Velocities',
                               'Magnetometer Magnetic Field',
                               'Barometer Atmospheric pressure'])
        while not stop_signal:
            err = zed_list[index].grab(runtime)
            if err == sl.ERROR_CODE.SUCCESS:
                zed_list[index].retrieve_image(left_list[index], sl.VIEW.LEFT)
                zed_list [index].retrieve_measure(depth_list[index], sl.MEASURE.DEPTH)
                timestamp_list[index] = zed_list[index].get_timestamp(sl.TIME_REFERENCE.CURRENT).data_ns
                # Get IMU Data
                if zed_list[index].get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS:
                    # Check if the data has been updated since the last time
                    # IMU is the sensor with the highest rate
                    if ts_handler.new_data(sensors_data.get_imu_data()):
                        quaternion = sensors_data.get_imu_data().get_pose().get_orientation().get()
                        # logging.info(" \t Orientation: [ Ox: {0}, Oy: {1}, Oz {2}, Ow: {3} ]".format(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))
                        orientation = 'Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}'.format(quaternion[0], quaternion[1],
                                                                                 quaternion[2], quaternion[3])
                        linear_acceleration = sensors_data.get_imu_data().get_linear_acceleration()
                        # logging.info(" \t Acceleration: [ {0} {1} {2} ] [m/sec^2]".format(linear_acceleration[0], linear_acceleration[1], linear_acceleration[2]
                        acceleration = '{0} {1} {2}'.format(linear_acceleration[0], linear_acceleration[1],
                                                            linear_acceleration[2])
                        angular_velocity = sensors_data.get_imu_data().get_angular_velocity()
                        # logging.info(" \t Angular Velocities: [ {0} {1} {2} ] [deg/sec]".format(angular_velocity[0], angular_velocity[1], angular_velocity[2]))
                        angular_v_text = '{0} {1} {2}'.format(angular_velocity[0], angular_velocity[1],
                                                              angular_velocity[2])

                    if ts_handler.new_data(sensors_data.get_magnetometer_data()):
                        magnetic_field_calibrated = sensors_data.get_magnetometer_data().get_magnetic_field_calibrated()
                        # logging.info(" - Magnetometer\n \t Magnetic Field: [ {0} {1} {2} ] [uT]".format(magnetic_field_calibrated[0], magnetic_field_calibrated[1], magnetic_field_calibrated[2]))
                        magnetometer = '{0} {1} {2}'.format(magnetic_field_calibrated[0], magnetic_field_calibrated[1],
                                                            magnetic_field_calibrated[2])
                    if ts_handler.new_data(sensors_data.get_barometer_data()):
                        magnetic_field_calibrated = sensors_data.get_barometer_data().pressure
                        # logging.info(" - Barometer\n \t Atmospheric pressure: {0} [hPa]".format(sensors_data.get_barometer_data().pressure))
                        barometer = '{0}'.format(sensors_data.get_barometer_data().pressure)
                write_header.writerow([orientation,
                                       acceleration,
                                       angular_v_text,
                                       magnetometer,
                                       barometer])
            time.sleep(0.01)  # 1ms
    zed_list[index].disable_recording()
    zed_list[index].close()
    print("End")


def zed_main(argv, lock, sync):
    global stop_signal
    global zed_list
    global left_list
    global depth_list
    global timestamp_list
    global thread_list

    # If CTRL-C, lets close up these threads:
    signal.signal(signal.SIGINT, signal_handler)

    # Some Defaults
    possible_res_string = "WVGA"
    possible_frame_string = "100"

    print("Running...")

    # Initializing params
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.VGA
    init.camera_fps = 100  # The framerate is lowered to avoid any USB3 bandwidth issues
    init.depth_mode = sl.DEPTH_MODE.ULTRA
    init.coordinate_units = sl.UNIT.MILLIMETER
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init.sdk_verbose = True

    # Get Opts
    try:
        opts, args = getopt.getopt(argv, "ho:r:f:", ["output=", "resolution=", "framerate="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(argv) == 0:
        print('Using default values of WVGA at 100fps and defualt output name of date time')

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ('-r', '--resolution'):
            possible_res_string = arg
        elif opt in ('-f', '--framerate'):
            possible_frame_string = arg
        elif opt in ('-o', '--output'):
            output_name = arg
        else:
            print('Unrecognised option')
            usage()
            exit()

    init.camera_resolution, init.camera_fps = get_res_framerate(possible_res_string, possible_frame_string)

    print('Resolution: {0}, Frame rate: {1}'.format(init.camera_resolution, init.camera_fps))

    # List, open & setup cameras
    name_list = []
    last_ts_list = []
    cameras = sl.Camera.get_device_list()
    index = 0
    path_output="DataLog/RXDATA/ZED/RECORDING-{}.svo".format(current_time())
    for cam in cameras:
        init.set_from_serial_number(cam.serial_number)
        name_list.append("ZED {}".format(cam.serial_number))
        print("Opening {}".format(name_list[index]))
        zed_list.append(sl.Camera())
        left_list.append(sl.Mat())
        depth_list.append(sl.Mat())
        timestamp_list.append(0)
        last_ts_list.append(0)
        # Camera actually opened
        status = zed_list[index].open(init)
        if status != sl.ERROR_CODE.SUCCESS:
            print(repr(status))
            zed_list[index].close()
        # Camera Record Params
        recording_param = sl.RecordingParameters(path_output, sl.SVO_COMPRESSION_MODE.H264)
        # Camera Recording Enabled
        err = zed_list[index].enable_recording(recording_param)
        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            exit(1)
        index = index + 1

    filesize_timeout = 400
    # Check for others to be ready
    ready = False
    timeout = 200  # Timeout after 200 seconds
    while not ready:
        lock.acquire()
        sync.update(5)
        if sync.ready or timeout == 0:
            ready = True
        lock.release()
        time.sleep(1)
        timeout = timeout - 1
    if ready:
        # Start camera threads
        for index in range(0, len(zed_list)):
            if zed_list[index].is_opened():
                thread_list.append(threading.Thread(target=grab_run, args=(index,)))
                thread_list[index].start()
        wait = True
        try:
            while wait:
                lock.acquire()
                if sync.finished or filesize_timeout:
                    wait = False
                lock.release()
                time.sleep()
                filesize_timeout = filesize_timeout-1

        except KeyboardInterrupt:
            sleep = False
        finally:
            # Stop the threads
            stop_signal = True
            time.sleep(5)
            for index in range(0, len(thread_list)):
                thread_list[index].join()
        print()
        print("\nFINISH")
    else:
        print('ZED Thread timeout')


if __name__ == "__main__":
    zed_main(sys.argv[1:])

