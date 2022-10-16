import numpy as np
import pyzed.sl as sl
import getopt
import cv2
import os
import glob
import sys

# from python.utilities import *


# This was built by Sherlock
def usage():
    print('svo_export.py -a -v -f <file_path> -o <output_name>')
    print('-a or --all\t: Use this if you want video, png sequences and depth sequences')
    print('-v or --video\t: Use this if you only want the video')
    print('-f or --file\t: File path of the svo file to export')
    print('-o or --output\t: Output names for the mp4 and obj files')
    print('-d or --folder\t: Folder path full of svo files that need to be exported')


def progress_bar(percent_done, bar_length=50):
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %f%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()


def export(file, output_name, video_only):
    # Make directory to put the video, depth image sequences and SBS pngs
    if not video_only:
        video_path = "{0}/".format(output_name)
        png_path = video_path + "png_sequences/"
        depth_path = video_path + "depth_sequences/"

    try:
        if not video_only:
            os.makedirs(video_path)
            os.makedirs(png_path)
            os.makedirs(depth_path)
    except OSError as e:
        print('Creation of directories failed')
        print(e)
        exit()
    else:
        print('Directories created')

    # set the input type as from file
    input_type = sl.InputType()
    input_type.set_from_svo_file(file)
    # initialise the camera parameters
    init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False)
    init.depth_mode = sl.DEPTH_MODE.ULTRA
    init.coordinate_units = sl.UNIT.MILLIMETER

    # initialise the camera
    cam = sl.Camera()
    status = cam.open(init)

    # camera parameters mismatch
    if status != sl.ERROR_CODE.SUCCESS:
        print('Cam.Open failed')
        print(repr(status))
        exit()

    frame_size = cam.get_camera_information().camera_resolution
    height = frame_size.height
    width = frame_size.width
    width_sbs = width * 2
    # prepare side by side container
    svo_image_sbs_rgba = np.zeros((height, width_sbs, 4), dtype=np.uint8)

    # prepare left, right and depth containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_image = sl.Mat()

    video_writer = cv2.VideoWriter('{0}.avi'.format(output_name),
                                   cv2.VideoWriter_fourcc('M', '4', 'S', '2'),
                                   cam.get_camera_information().camera_fps, (width_sbs, height))

    if not video_writer.isOpened():
        sys.stdout.write("OpenCV video writer cannot be opened. Please check .avi file path and write "
                         "permissions\n")
        cam.close()
        exit(-1)

    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.FILL

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO to AVI Use Ctrl-C to interrupt conversion.\n")
    nb_frames = cam.get_svo_number_of_frames()

    while True:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:
            svo_position = cam.get_svo_position()

            cam.retrieve_image(left_image, sl.VIEW.LEFT)
            cam.retrieve_image(right_image, sl.VIEW.RIGHT)
            if not video_only:
                cam.retrieve_measure(depth_image, sl.MEASURE.DEPTH)

            svo_image_sbs_rgba[0:height, 0:width, :] = left_image.get_data()
            svo_image_sbs_rgba[0:, width:, :] = right_image.get_data()

            ocv_image_sbs_rgb = cv2.cvtColor(svo_image_sbs_rgba, cv2.COLOR_RGBA2RGB)

            video_writer.write(ocv_image_sbs_rgb)
            if not video_only:
                cv2.imwrite(depth_path + '{0}-{1}.png'.format(output_name, svo_position),
                            depth_image.get_data().astype(np.uint16))
                cv2.imwrite(png_path + '{0}-{1}.png'.format(output_name, svo_position), ocv_image_sbs_rgb)

            progress_bar((svo_position + 1) / nb_frames * 100, 30)

            if svo_position >= (nb_frames - 1):  # end of SVO
                sys.stdout.write("\nSVO end has been reached. Exiting.")
                break

    video_writer.release()
    cam.close()


def main(argv):
    file = ""
    output_name = ""
    folder_flag = False
    video_only = False
    folder_path = ""
    try:
        opts, args = getopt.getopt(argv, "hvad:f:o:", ["help=", "video", "all", "folder=", "file=", "output="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ('-v', '--video'):
            video_only = True
        elif opt in ('-a', '-all'):
            video_only = False
        elif opt in ('-d', '--folder'):
            folder_flag = True
            folder_path = arg
        elif opt in ('-f', '--file'):
            file = arg
        elif opt in ('-o', '--output'):
            output_name = arg
        else:
            print('Unrecognised option')
            usage()
            exit()

    # output deduction system
    # TODO: Fix output deduction system
    if not folder_flag and output_name == "":
        print('Deducing the output based on the file name')
        try:
            output_name = file.split('.')[0]
        except:
            print("Provided file does not have an extension")
            usage()
            sys.exit()
        print('Deduced output name: {0}'.format(file.split('.')[0]))
        acceptable_flag = False
        while not acceptable_flag:
            print('Is this acceptable? (y/n)')
            acceptable = input().lower()

            if acceptable in ('n', 'no'):
                print('Exiting, use the -o flag to define the name of the output')
                usage()
                sys.exit(2)
            elif acceptable in ('y', 'yes'):
                print('Using deduced output folder: {0}'.format(output_name))
                acceptable_flag = True
            else:
                acceptable_flag = False

    # folder input logic
    if folder_flag:
        if not folder_path.endswith('/'):
            folder_path += '/'
        # fetches all svos in the folder
        file = glob.glob(folder_path + "*.svo", recursive=False)
        # filters the name of the file and then sends it off to export
        for path in file:
            mod_path = ""
            if path.startswith(".\\"):
                mod_path = path.removeprefix('.\\')
            mod_path = mod_path.removesuffix('.svo')
            export(path, mod_path, video_only)
    else:
        export(file, output_name, video_only)


if __name__ == '__main__':
    main(sys.argv[1:])