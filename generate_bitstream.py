import random, sys


def generate_random_bitstream(size):
    bitstream = ""
    for i in range(size):
        bitstream += str(random.randint(0, 1))
    return bitstream


def seconds_2bit_size(seconds, frequency):
    return seconds * frequency


def main(argv):
    print(f'{argv}')
    if len(argv) == 1:
        print(f'Generating Bitstream that will persist at 50Hz over {argv[0]} seconds')
        size = seconds_2bit_size(int(argv[0]), 50)
        bitstream = generate_random_bitstream(size)
        f = open(f'DataLog/TXDATA/raw_bitsream_duration_{argv[0]}.txt',
                 "w+")
        f.write(bitstream)
    else:
        print('No arg set')
        

if __name__ == '__main__':
    main(sys.argv[1:])
