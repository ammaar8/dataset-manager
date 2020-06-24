from tkinter import filedialog
from tkinter import *

def FilePicker(directory):
	root = Tk()
	root.filename =  filedialog.askopenfilename(initialdir = directory ,title = "Select file",filetypes = (("Video Files", ["*.mp4", "*.avi"]), ("All Files","*.*")))
	filename = root.filename
	root.destroy()
	return filename
