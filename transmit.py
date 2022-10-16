from datetime import *
from tqdm.auto import tqdm
# import Jetson.GPIO as GPIO
import signal
import sys
import time
import logging, getopt, random
from time import ctime
from led_sync import LED_S


# output_pin = "SOC_GPIO54"  # Board Pin 12
frequency = 50  # effectively a 50Hz transmission rate
# variables for random bit transmission
random_flag = False
random_size = 500
times = 1
# variables for perma state transmission
state_flag = False
# perma_state = GPIO.LOW
file_import = True
duration = 120  # 120 secs = 2 minutes
bitfile = f'raw_bitsream_duration_{duration}'
bitfile_dir = 'DataLog/TXDATA/'
bitstream = ''


def interrupt_handler(sig, frame):
    # print_queue.put("You've pressed Ctrl+C!")
    logging.info("Program ending")
    sys.stdout.flush()
    sys.exit(0)


def create_transmission(bitstream, times_to_multiply):
    return bitstream * times_to_multiply  # multiplies it by the number of times to be repeated


def transmit(transmission_bits, ready, end, lidar, zed, print_queue):
    total_bits = len(transmission_bits)
    counter = 0
    print_queue.put("Transmit about to Try")
    try:
        m = LED_S(0x70, 0x73, 1)
        print_queue.put("LED Matrix opening...")
        preset = False
        for second in range (1, 10):
            if not preset:
                if lidar.is_set() and zed.is_set():
                    print_queue.put('Preconditions Met.')
                    preset = True
            time.sleep(1)
        # Since Matrix is ready, LEDs can Transmit!!, set event
        if preset:
            ready.set()
            print_queue.put('Transmit ready event set')
        else:
            return KeyboardInterrupt
        try:
            for bit in tqdm(transmission_bits, desc='Main Rear LED transmitting at {}hz:'.format(frequency), position=0,
                            leave=True, ascii=False):
                m.transfer_bit(bit, counter)
                counter += 1
                time.sleep(1 / frequency)
        except KeyboardInterrupt:
            print_queue.put('Transmit - Keyboard Interrupt')
        finally:
            end.set()
            m.cleanup()
            print_queue.put(f'End: {end.is_set()}')
    except KeyboardInterrupt:
        print_queue('Stopped')
    finally:
        sys.exit()


def usage(printer):
    print_queue.put('transmitter_randombits_repeat.py -s <define_static_state> -r <length_of_random_bitstream> -f '
          '<frequency_to_transmit> -t <number_of_times>')
    print_queue.put('-f or --frequency\t: Frequency to transmit at')
    print_queue.put('-r or --random\t: Flag to set random bit transmission followed by the size of the bitstream')
    print_queue.put('-t or --times\t: Number of times the random bitstream is to be repeated')
    print_queue.put('-s or --state\t: Set the permanent state of the LED. This flag takes precedence so include only for LED '
          'ON/OFF experiment')
    print_queue.put('-b or --bitfile for seconds\t: Set the target file for bits to be transmitted')


def seconds_2bit_size(seconds, frequency):
    return seconds * frequency


def transmit_main(argv, ready, end, lidar, zed, print_queue):
    global output_pin, frequency, state_flag, perma_state, random_flag, random_size, \
        times, bitfile, file_import, bitstream, duration
    if len(argv) == 1:
        print_queue.put('Using default values of: Output Pin = Board 12, Frequency = 30 Hz')
    try:
        opts, args = getopt.getopt(argv, "hps:r:f:t:b:", ["state=", "random=", "frequency=", "times=", "bitfile="])
    except getopt.GetoptError:
        usage(print_queue)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage(print_queue)
            sys.exit()
        elif opt == '-p':
            file_import = True
            randomdc_flag = False
            bitfile = f'raw_bitsream_duration_{duration}.txt'
        elif opt in ('-s', '--state'):
            state_flag = True
            perma_state = get_perma_state(arg)
        elif opt in ('-f', '--freq'):
            frequency = int(arg)
        elif opt in ('-r', '--random'):
            random_flag = True
            random_size = int(arg)
        elif opt in ('-t', '--times'):
            times = int(arg)
        elif opt in ('-d', '--duration'):
            duration = opt
        elif opt in ('-b', '--bitfile'):
            file_import = True
            random_flag = False
            bitfile = opt

    signal.signal(signal.SIGINT, interrupt_handler)
    print_queue.put("A")
    if state_flag:
        # GPIO.setmode(GPIO.TEGRA)
        print_queue.put("B")
        # GPIO.setup(output_pin, GPIO.OUT, initial=perma_state)
        # GPIO.output(output_pin, perma_state)
        print_queue.put('Output set to permanent state: {0}'.format(perma_state))
        # GPIO.cleanup(output_pin)
    elif random_flag:
        print_queue.put("C")
        # logging config
        # ToDo: Change the filename here if in the future our datasets change
        logging.basicConfig(
            filename='DataLog/TXDATA/transmitter_{0}Hz_{1}_cycles-{2}_bits.log'.format(frequency, times, random_size),
            level=logging.INFO, format='%(asctime)s %(message)s')
        random_bits = generate_random_bitstream(random_size)
        print_queue.put("D")
        logging.info("Generated bitstream: {0}".format(random_bits))
        print_queue.put("E")
        transmission = create_transmission(random_bits, times)
        f = open('DataLog/TXDATA/raw_bitsream_{0}Hz_{1}_cycles-{2}_bits.txt'.format(frequency, times, random_size),
                 "w+")
        print_queue.put("F")
        f.write(transmission)
        print_queue.put("G")
        logging.info("Starting Transmission")
        print_queue.put("Transmit Start")
        transmit(transmission, ready, end, lidar, zed, print_queue)
        print_queue.put("Transmit End")
        logging.info("Transmisssion Ended")
        GPIO.output(output_pin, GPIO.LOW)
    elif file_import:
        try:
            f = open(bitfile_dir+bitfile, "+r")
            bitstream = f.read()
            transmit(bitstream, ready, end, lidar, zed, print_queue)
        except OSError:
            print_queue.put(f'File "{bitfile}" could not be found or opened')
        except KeyboardInterrupt:
            print_queue.put('Keyboard interrupt, exiting')
        finally:
            # usage(printer)
            sys.exit(0)
    else:
        print_queue.put('No flags set, exiting')
        usage(print_queue)
        sys.exit(0)


