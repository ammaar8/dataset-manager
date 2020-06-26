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

def AnnotationInfoFile(dataset_directory, mode, train_or_test=None, files=None):
    if mode == "add":
        with open(os.path.join(dataset_directory, INFO_DIR, "{}_for_annotation.dat".format(train_or_test)), 'a') as info_file:
            for file_name in files:
                info_file.write(file_name + "\n")
            return None
    elif mode == "read":
        with open(os.path.join(dataset_directory, INFO_DIR, "{}_for_annotation.dat".format(train_or_test)), 'r') as info_file:
            return set(x.rstrip('\n') for x in info_file.readlines())
    elif mode == "update":
        with open(os.path.join(dataset_directory, INFO_DIR, "{}_for_annotation.dat".format(train_or_test)), 'w') as info_file:
            for file_name in files:
                info_file.write(file_name + "\n")
            return None
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
        available_for_annotation =  list(all_files - AnnotationInfoFile(dataset_directory, "read", train_or_test))
        batch_files = list(map(GetFileName, available_for_annotation[0:min(len(available_for_annotation), batch_size)]))
        
        AnnotationInfoFile(dataset_directory, "add", train_or_test=train_or_test, files=batch_files)
        os.mkdir(destination_dir)

        for file_name in batch_files:
            source_file = os.path.join(source_dir, file_name)
            destination_file = os.path.join(destination_dir, file_name)
            shutil.copy(source_file, destination_file )
        
    else:
        print("[ERROR] Invalid option {}".format(train_or_test))

def MergeBatch(dataset_directory):
    # TODO Duplicate Handling
    source_dir = DirectoryPicker("/")

    # TODO get type [train/test]
    train_or_test = input("Dataset type = [train/test] ")
    if train_or_test not in ["train", "test"]:
        print("[ERROR] Unknown dataset type : {}".format(train_or_test))
        return None
    
    text_files = glob.glob(os.path.join(source_dir, "*.txt"))
    text_files = [os.path.split(x)[1] for x in text_files]
    text_files_names = [x.split('.')[0] for x in text_files]
    
    image_files = glob.glob(os.path.join(source_dir, "*.jpg"))
    image_files = [os.path.split(x)[1] for x in image_files]
    image_files_names = [x.split('.')[0] for x in text_files]

    files_for_annotation = AnnotationInfoFile(dataset_directory, "read", train_or_test)
    files_for_annotation_names = [x.split('.')[0] for x in files_for_annotation]
    #print("[TXT]", text_files_names)
    #print("[IMG]", image_files_names)
    #print("[ANN]", files_for_annotation_names)
    files_to_move = []
    files_not_recognized = []
    
    for text_file in text_files_names:
        if text_file in files_for_annotation_names:
            files_to_move.append(text_file)
        else:
            files_not_recognized.append(text_file)

    destination_dir = os.path.join(dataset_directory, train_or_test, ANNOTATED_DIR)
    for file_to_move in files_to_move:
        src_dir_txt = os.path.join(source_dir, file_to_move+".txt")
        dest_dir_txt = os.path.join(destination_dir, file_to_move+".txt")
        src_dir_img = os.path.join(dataset_directory, train_or_test, UNANNOTATED_DIR, file_to_move+".jpg")
        dest_dir_img = os.path.join(destination_dir, file_to_move+".jpg")
        shutil.copy(src_dir_txt, dest_dir_txt)
        shutil.copy(src_dir_img, dest_dir_img)

    files_left_for_annotation = [x for x in files_to_move if x not in files_for_annotation_names]
    files_left_for_annotation = [x+".jpg" for x in files_left_for_annotation]
    AnnotationInfoFile(dataset_directory, "update", train_or_test, files=files_left_for_annotation)
    # TODO Update Database Info Annotated Count
    dataset_info = ReadInfoFile(dataset_directory) 
    dataset_info["{}_frames_annotated".format(train_or_test)] += len(files_to_move)
    dataset_info["{}_frames_unannotated".format(train_or_test)] -= len(files_to_move)
    WriteInfoFile(dataset_directory, dataset_info)
    print("[INFO] All done")