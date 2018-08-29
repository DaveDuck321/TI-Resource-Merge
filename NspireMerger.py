#!/usr/bin/python
import sys, os, glob
from pathlib import Path
from PIL import Image

#Functions
def ConvertImageToString(image):
    return "Placeholder"

def GetImageName(path):
    return os.path.split(path)[1].split(".")[0]


#Main body
if len(sys.argv) == 1:
    print("Error: No build directory given")

rootPath = Path(sys.argv[1])
if not rootPath.is_dir():
    print("Error: build directory: "+sys.argv[1]+" not found")
    exit()

stringsToAppend = []
resPath = Path(sys.argv[1] + "/res")
if resPath.is_dir():
    print("res directory found")
    stringsToAppend.append("_R={}")
    stringsToAppend.append("_R.IMG = {}")
    for file in glob.glob(sys.argv[1] + "/res/IMG/*.png"):
        image = Image.open(file).load()
        imageString = ConvertImageToString(image)
        stringsToAppend.append("_R.IMG."+GetImageName(file) + '="'+ imageString +'"')
else:
    print("res directory not found")

files = []
for arg in sys.argv[2:]:
    files.append(arg)

if len(files)==0:
    print("Error: No lua scripts given")
    exit()

for file in files:
    file = open(file, "r")
    stringsToAppend.append(file.read())

outFile = open(sys.argv[1]+"/out.lua", "w")
for string in stringsToAppend:
    outFile.write(string+"\n")
print("Success")