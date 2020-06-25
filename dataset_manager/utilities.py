import cv2
import os
import glob
import random
import shutil

ANNOTATED_DIR = "annotated"
UNANNOTATED_DIR = "unannotated"
TEST_DIR = "test"
TEMP_DIR = "temp"
TRAIN_DIR = "train"
INFO_DIR = "info"

def WriteInfoFile(dataset_directory, dataset_info):
    file_path = os.path.join(dataset_directory, INFO_DIR, "dataset_info.dat")
    with open(file_path, "w") as info_file:
        for key, value in dataset_info.items():
            info_file.write("{}={}\n".format(key, value))

def ReadInfoFile(dataset_directory):
    file_path = os.path.join(dataset_directory, INFO_DIR, "dataset_info.dat")
    dataset_info = {}
    with open(file_path, 'r') as info_file:
        for line in info_file.readlines():
            key, value = line.rstrip("\n").split("=")
            if value.isnumeric():
                dataset_info[key] = int(value)
            else:
                dataset_info[key] = value
    return dataset_info

def NameVideo(dataset_name, dataset_directory):
    with open(os.path.join(dataset_directory, INFO_DIR, "videos.dat"), 'r') as video_records_file:
        lines = video_records_file.readlines()
        if lines == []:
            return "{}_vid_1".format(dataset_name)
        else:
            last_number = lines[-1].rstrip("\n").split("_")[-1]
            return "{}_vid_{}".format(dataset_name, last_number+1)

def WriteVideoRecord(dataset_directory, video_name):
    with open(os.path.join(dataset_directory, INFO_DIR, "videos.dat"), 'a') as video_records_file:
        video_records_file.write(video_name + "\n")

def ExtractVideo(video_path, dataset_directory, train_test_ratio=0.8, extract_ratio=None):
    VIDEO_PATH = video_path
    DATASET_DIR = dataset_directory
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    FRAME_COUNT = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    total_frames = int(input("Video has {} frames. Frames to extract = ".format(FRAME_COUNT)))
    SEEK_STEP = FRAME_COUNT // total_frames
    
    dataset_info = ReadInfoFile(dataset_directory)
    video_name = NameVideo(dataset_info["dataset_name"], dataset_directory)
    
    count = 1
    while True:
	    video_left, frame = cap.read()
	    if not video_left:
		    break
	    cv2.imwrite(os.path.join(DATASET_DIR, TEMP_DIR, "{}_{}.jpg".format(video_name, count)), frame)
	    print("Frame {:>10} written, {:>10} left".format(str(count), str(total_frames - count)))
	    POS_FRAMES = cap.get(cv2.CAP_PROP_POS_FRAMES)
	    cap.set(cv2.CAP_PROP_POS_FRAMES, POS_FRAMES + SEEK_STEP)
	    count+=1

    files = glob.glob(os.path.join(dataset_directory, TEMP_DIR, "*.jpg"))
    print("Ratio ", total_frames * train_test_ratio)
    train_files = random.sample(files, int(total_frames * train_test_ratio))
    dataset_info["train_frames_unannotated"] += len(train_files)
    for train_file in train_files:
        head, file_name = os.path.split(train_file)
        shutil.move(train_file, os.path.join(dataset_directory, TRAIN_DIR, UNANNOTATED_DIR, file_name))

    test_files = glob.glob(os.path.join(dataset_directory, TEMP_DIR, "*.jpg"))
    dataset_info["test_frames_unannotated"] += len(test_files)
    for test_file in test_files:
        head, file_name = os.path.split(test_file)
        shutil.move(test_file, os.path.join(dataset_directory, TEST_DIR, UNANNOTATED_DIR, file_name))
    
    dataset_info["total_frames"]+= dataset_info["train_frames_unannotated"] + dataset_info["test_frames_unannotated"]
    dataset_info["videos_used"]+=1
    WriteInfoFile(dataset_directory, dataset_info)
    WriteVideoRecord(dataset_directory, video_name)
    print("Done Extracting")
