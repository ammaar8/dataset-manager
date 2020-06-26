from tkinter import filedialog
from tkinter import *

def DestinationPicker(directory):
	root = Tk()
	root.dirname =  filedialog.askdirectory(initialdir = directory)
	dirname = root.dirname
	root.destroy()
	return dirname

def FilePicker(directory):
	root = Tk()
	root.filename =  filedialog.askopenfilename(initialdir = directory ,title = "Select file",filetypes = (("Video Files", ["*.mp4", "*.avi"]), ("All Files","*.*")))
	filename = root.filename
	root.destroy()
	return filename

def DirectoryPicker(directory):
	root = Tk()
	root.dirname =  filedialog.askdirectory(initialdir = directory)
	dirname = root.dirname
	root.destroy()
	return dirname