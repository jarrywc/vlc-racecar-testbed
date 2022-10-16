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
    print("You've pressed Ctrl+C!")
    logging.info("Program ending")
    sys.stdout.flush()
    sys.exit(0)


def create_transmission(bitstream, times_to_multiply):
    return bitstream * times_to_multiply  # multiplies it by the number of times to be repeated


def transmit(transmission_bits, lock, sync):
    total_bits = len(transmission_bits)
    counter = 0
    print("Transmit about to Try")
    try:
        m = LED_S(0x70, 0x73, 1)
        time.sleep(10)
        print("Matrix open")

        # Check for others to be ready
        ready = False
        timeout = 200 # Timeout after 200 seconds
        while not ready:
            lock.acquire()
            sync.update(5)
            if sync.ready or timeout == 0:
                ready = True
            lock.release()
            time.sleep(1)
            timeout = timeout-1
        try:
            if ready:
                for bit in tqdm(transmission_bits, desc='Main Rear LED transmitting at {}hz:'.format(frequency), position=0,
                                leave=True, ascii=False):
                    m.transfer_bit(bit, counter)
                    counter += 1
                    time.sleep(1 / frequency)
            else:
                print("Didn't get ready in time")
        finally:
            m.cleanup()
    finally:
        sys.exit()


def usage():
    print('transmitter_randombits_repeat.py -s <define_static_state> -r <length_of_random_bitstream> -f '
          '<frequency_to_transmit> -t <number_of_times>')
    print('-f or --frequency\t: Frequency to transmit at')
    print('-r or --random\t: Flag to set random bit transmission followed by the size of the bitstream')
    print('-t or --times\t: Number of times the random bitstream is to be repeated')
    print('-s or --state\t: Set the permanent state of the LED. This flag takes precedence so include only for LED '
          'ON/OFF experiment')
    print('-b or --bitfile for seconds\t: Set the target file for bits to be transmitted')


def seconds_2bit_size(seconds, frequency):
    return seconds * frequency


def transmit_main(argv, lock, sync):
    global output_pin, frequency, state_flag, perma_state, random_flag, random_size, \
        times, bitfile, file_import, bitstream, duration
    if len(argv) == 1:
        print('Using default values of: Output Pin = Board 12, Frequency = 30 Hz')
    try:
        opts, args = getopt.getopt(argv, "hps:r:f:t:b:", ["state=", "random=", "frequency=", "times=", "bitfile="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
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
    print("A")
    if state_flag:
        # GPIO.setmode(GPIO.TEGRA)
        print("B")
        # GPIO.setup(output_pin, GPIO.OUT, initial=perma_state)
        # GPIO.output(output_pin, perma_state)
        print('Output set to permanent state: {0}'.format(perma_state))
        # GPIO.cleanup(output_pin)
    elif random_flag:
        print("C")
        # logging config
        # ToDo: Change the filename here if in the future our datasets change
        logging.basicConfig(
            filename='DataLog/TXDATA/transmitter_{0}Hz_{1}_cycles-{2}_bits.log'.format(frequency, times, random_size),
            level=logging.INFO, format='%(asctime)s %(message)s')
        random_bits = generate_random_bitstream(random_size)
        print("D")
        logging.info("Generated bitstream: {0}".format(random_bits))
        print("E")
        transmission = create_transmission(random_bits, times)
        f = open('DataLog/TXDATA/raw_bitsream_{0}Hz_{1}_cycles-{2}_bits.txt'.format(frequency, times, random_size),
                 "w+")
        print("F")
        f.write(transmission)
        print("G")
        logging.info("Starting Transmission")
        print("Transmit Start")
        transmit(transmission, lock, sync)
        print("Transmit End")
        logging.info("Transmisssion Ended")
        GPIO.output(output_pin, GPIO.LOW)
    elif file_import:
        try:
            f = open(bitfile_dir+bitfile, "+r")
            bitstream = f.read()
            transmit(bitstream, lock, sync)
        except OSError:
            print(f'File "{bitfile}" could not be found or opened')
        except KeyboardInterrupt:
            print('Keyboard interrupt, exiting')
        finally:

            usage()
            sys.exit(0)
    else:
        print('No flags set, exiting')

        usage()
        sys.exit(0)


if __name__ == '__main__':
    transmit_main(sys.argv[1:])
