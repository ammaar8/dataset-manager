#!/usr/bin/env python3
import os
import shutil
import cv2
from dataset_manager.gui import *
from dataset_manager.utilities import *

PARENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATASETS_DIR = os.path.join(PARENT_DIR, "datasets")
DATASET_INDEX_FILE = os.path.join(DATASETS_DIR, "dataset_index.dat")
CURRENT_DIR = None

if not os.path.isdir(DATASETS_DIR):
    os.mkdir(DATASETS_DIR)
    with open(DATASET_INDEX_FILE, 'w') as _:
        pass

def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator

@rename("Print Dataset Index")
def print_dataset_index():
    print("-" * 32)
    print("|{:^30}|".format("Dataset Index"))
    print("-" * 32)
    with open(DATASET_INDEX_FILE, 'r') as index_file:
        lines = enumerate(index_file.read().splitlines(), start=1)
        for option, name in lines:
            print("|{:>3}. {:<25}|".format(option, name))
    print("-" * 32)

@rename("Create New Dataset")
def create_new_dataset():
    already_exists = True
    dataset_name = input("Enter Dataset Name [without spaces]: ")
    
    with open(DATASET_INDEX_FILE, 'r') as index_file:
        if str(dataset_name)+"\n" in index_file.readlines():
            print("[ERROR] Dataset {} already exists!".format(dataset_name))
        else:
            already_exists = False

    if not already_exists:
        try:
            dataset_dir = os.path.join(DATASETS_DIR, dataset_name)

            os.mkdir(dataset_dir)
            os.makedirs(dataset_dir + "/info")
            os.makedirs(dataset_dir + "/temp")
            os.makedirs(dataset_dir + "/test/annotated")
            os.makedirs(dataset_dir + "/test/unannotated")
            os.makedirs(dataset_dir + "/train/annotated")
            os.makedirs(dataset_dir + "/train/unannotated")

            dataset_info_file_template = {
                "dataset_name": dataset_name,
                "videos_used": 0,
                "total_frames" : 0,
                "train_test_ratio" : 0.8,
                "train_frames_annotated" : 0,
                "train_frames_unannotated" : 0,
                "test_frames_annotated" : 0,
                "test_frames_unannotated" : 0
            }
            with open(dataset_dir + "/info/dataset_info.dat", 'a') as dataset_info_file:
                for key, value in dataset_info_file_template.items():
                    dataset_info_file.write("{}={}\n".format(key, value))
            with open(dataset_dir + "/info/videos.dat", 'w') as _:
                pass
            with open(dataset_dir + "/info/train_for_annotation.dat", 'w') as _:
                pass
            with open(dataset_dir + "/info/test_for_annotation.dat", 'w') as _:
                pass
            with open(DATASET_INDEX_FILE, 'a') as index_file:
                index_file.write(dataset_name + "\n")
            print("Dataset {} created!".format(dataset_name))
        except:
            print("[Error] creating dataset {} failed!".format(dataset_name))

@rename("Delete Dataset")
def delete_dataset():
    dataset_name = input("Name of dataset to delete: ")
    try:
        dataset_dir = os.path.join(DATASETS_DIR, dataset_name)
        if os.path.isdir(dataset_dir):
            command = input("Are you sure you want to delete {}? [y/n] ".format(dataset_name))
            if command == 'y':
                shutil.rmtree(dataset_dir)
                index = open(DATASET_INDEX_FILE).readlines()
                with open(DATASET_INDEX_FILE, 'w') as index_file:
                    for line in index:
                        if line == dataset_name+"\n":
                            continue
                        index_file.write(line)
                print("Dataset {} deleted successfully!".format(dataset_name))
            else:
                print("Delete operation cancelled.")
        else:
            print("Dataset {} does not exist!".format(dataset_name))
    except Exception as e:
        print(e)

@rename("Add Video")
def add_video():
    head, tail = os.path.split(PARENT_DIR)
    video_path = FilePicker(head)
    # TODO - Add incorrect dir handling
    ExtractVideo(video_path, CURRENT_DIR)

@rename("Delete Video")
def delete_video():
    pass

@rename("Add Annotated")
def add_annotated():
    MergeBatch(CURRENT_DIR)

@rename("Extract Batch")
def extract_batch():
    ExtractBatch(CURRENT_DIR)

@rename("Go Back")
def go_back():
    pass

@rename("Print Dataset Info")
def print_dataset_info():
    dataset_info = ReadInfoFile(CURRENT_DIR)
    print("-" * 48)
    print("|{:^30}|{:^15}|".format("Parameter", "Value"))
    print("-" * 48)
    for key, value in dataset_info.items():
        print("|{:<30}|{:>15}|".format(key, value))
    print("-" * 48)

@rename("Open Dataset")
def open_dataset():
    global CURRENT_DIR
    dataset_name = input("Name of Dataset to open: ")
    if os.path.isdir(os.path.join(DATASETS_DIR, dataset_name)):
        CURRENT_DIR = os.path.join(DATASETS_DIR, dataset_name)
        menu = {
            "0": go_back,
            "1": add_video,
            "2": delete_video,
            "3": add_annotated,
            "4": extract_batch,
            "5": print_dataset_info,
        }
        while True:
            for key, value in menu.items():
                print("{}. {}".format(key, value.__name__))
            option = input("What do you want to do? > ")
            if option == "0":
                break
            if option in menu.keys():
                menu[option]()
        CURRENT_DIR = None
    else:
        print("[ERROR]Database {} does not exist".format(dataset_name))

def Quit():
    quit()

menu = {
    "1": print_dataset_index,
    "2": create_new_dataset,
    "3": delete_dataset,
    "4": open_dataset,
    "5": Quit
    }

def main():
    while True:
        print("Dataset Manager.")
        for key, value in menu.items():
            print("{}. {}".format(key, value.__name__))
        option = input("What do you want to do? > ")
        if option in menu.keys():
            menu[option]()
    
if __name__ == "__main__":
    main()