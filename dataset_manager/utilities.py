import cv2
import os
import glob
import random
import shutil
import time
from dataset_manager.gui import *

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

def AnnotationInfoFile(dataset_directory, mode, files=None):
    if mode == "add":
        with open(os.path.join(dataset_directory, INFO_DIR, "out_for_annotation.dat"), 'a') as info_file:
            for file_name in files:
                print("Working")
                info_file.write(file_name + "\n")
            return None
    elif mode == "read":
        with open(os.path.join(dataset_directory, INFO_DIR, "out_for_annotation.dat"), 'r') as info_file:
            return set(x.rstrip('\n') for x in info_file.readlines())
    else:
        print("[ERROR] Unknown Option {}".format(mode))

def GetFileName(path):
    head, name = os.path.split(path)
    return name

def ExtractBatch(dataset_directory):
    head, dataset_name = os.path.split(dataset_directory)
    batch_size = int(input("Batch Size = "))
    train_or_test = str(input("train or test ? [train/test] "))

    if train_or_test in ['train', 'test']:
        destination_dir = os.path.join(DestinationPicker(directory="/"),
         "{}_{}_{}_{}_AB".format(dataset_name, batch_size, train_or_test, time.strftime("%Y%m%d-%H%M%S")))

        source_dir = os.path.join(dataset_directory, train_or_test, "unannotated")
        all_files = set(map(GetFileName, glob.glob(os.path.join(source_dir, "*.jpg"))))
        available_for_annotation =  list(all_files - AnnotationInfoFile(dataset_directory, "read"))
        batch_files = list(map(GetFileName, available_for_annotation[0:min(len(available_for_annotation), batch_size)]))
        
        AnnotationInfoFile(dataset_directory, "add", batch_files)
        os.mkdir(destination_dir)

        for file_name in batch_files:
            source_file = os.path.join(source_dir, file_name)
            destination_file = os.path.join(destination_dir, file_name)
            shutil.copy(source_file, destination_file )
        
    else:
        print("[ERROR] Invalid option {}".format(train_or_test))

def MergeBatch():
    pass