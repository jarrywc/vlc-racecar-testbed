import time


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}',
          sep='', end='',
          flush=True)
    # Print New Line on Complete
    if iteration == total:
        print()


# A List of Items
items = list(range(0, 57))
l = len(items)
line = ["( | )", "( / )", "( - )", '( \\ )']
line2 = ["( ' )", "(- )", "( , )", '( -)']
line3 = ["( ': )", "(-: )", "(,: )", "( ; )","( :,)", '( :-)', "( :')"]
line4 = ["(<  )", "( ^ )", "(  >)", "( v )"]
recording_progress = '3m 2s'

# Initial call to print 0% progress
printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
for i, item in enumerate(items):
    position = i % len(line4)
    time.sleep(0.1)
    # Update Progress Bar
    printProgressBar(i + 1, l, prefix=f'Tx:',
                     suffix=f' |_ZED: Recording {recording_progress}_| Lidar: Scanning {line4[position]} |_ Some Lots of '
                            f'words will go here _| ', length=20)


def print_experiment_stream(tx_step, txm_length, recording_progress, lidar_status):
    line = ["( ' )", "(- )", "( , )", '( -)', 'hidden']
    adj_position = tx_step % 4  # 4 makes the 5th element hidden Or len(line)
    #
    if lidar_status is not None:
        lidar_print = lidar_status
    else: lidar_print = line[adj_position]

    printProgressBar(tx_step + 1, txm_length, prefix=f'Tx:',
                     suffix=f' |_ZED: Recording {recording_progress}_| Lidar: Scanning {lidar_print} |_ Some Lots of '
                            f'words will go here _| ', length=20)
