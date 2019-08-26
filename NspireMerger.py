#!/usr/bin/python
import sys, os, glob
from pathlib import Path
from PIL import Image

def print_help():
    print("Usage: Nspiremerger --target ? --out ? --root ? --in ? ? ?")
    exit()

def little_endian(number, byte_width):
    escape_string = ""
    for byte in range(0, byte_width):
        escape_string += f"\\{(number>>(byte*8))&255}"
    return escape_string

def image_to_string(image_file):
    im = Image.open(image_file).convert('RGBA')
    data = im.load()

    image_string = little_endian(im.size[0], 4) + little_endian(im.size[1], 4) #width, height
    image_string += little_endian(0, 1) + little_endian(0, 1) + little_endian(0, 2) #alignment, flags, padding
    image_string += little_endian(im.size[0]*2, 4)
    image_string += little_endian(16, 2) + little_endian(1, 2) #bits per pixels, planes per bit

    for y in range(im.size[1]):
        for x in range(im.size[0]):
            pixel = data[x, y]
            r, g, b = int((pixel[0]/255)*31), int((pixel[1]/255)*31), int((pixel[2]/255)*31)
            a = int(pixel[3] == 255)
            total = b + (g<<5) + (r<<10) + (a<<15)
            image_string += little_endian(total, 2)

    return image_string


def get_image_name(path):
    return os.path.split(path)[1].split(".")[-2]

def collect_resources(root, target):
    if target != "luna":
        return []
    header = "----- GENERATED ASSETS -----"
    resources = ["-" * len(header), header]

    resources.append("_R = {}")
    resources.append("_R.IMG = {}")
    for file in glob.glob(root + "/res/IMG/*.png"):
        image_str = image_to_string(file)
        resources.append(f"_R.IMG.{get_image_name(file)} = '{image_str}'")
    
    resources.append(header)
    resources.append("-"*len(header))
    return resources

def merge_input_files(input_globs):
    merge_result = []
    for input_glob in input_globs:
        for file_name in glob.glob(input_glob):
            header = f"----- '{file_name}' -----"
            merge_result.append("-" * len(header))
            merge_result.append(header)

            print(file_name)
            merge_result.append(Path(file_name).read_text())

            merge_result.append(header)
            merge_result.append("-"*len(header))
    if len(merge_result) == 0:
        print("Error: No input files found")
        print_help()
    return merge_result

def print_to_file(resources, contents, outfile):
    output = open(outfile, "w")
    for resource in resources:
        output.write(resource+'\n')
    output.write("\n\n\n")
    for content in contents:
        output.write(content+'\n')
    output.close()

def get_argument(tag, default, after):
    if not tag in sys.argv:
        return default
    index = sys.argv.index(tag) + 1
    if after:
        return sys.argv[index:]
    return sys.argv[index]

try:
    if __name__ == "__main__":
        outfile = get_argument("--out", "out.lua", False)
        root = get_argument("--root", "./", False)
        target = get_argument("--target", "luna", False)
        input_file_globs = get_argument("--in", ["*.lua", "src/*.lua"], True)

        if not Path(root).is_dir():
            print(f"Error: project directory: {root} not found")
            print_help()
        if target=="luna" and not Path(root + "/res"):
            print(f"Error: resources directory: {root}/res not found")
            print_help()
        
        resources = collect_resources(root, target)
        merged_file = merge_input_files(input_file_globs)
        print_to_file(resources, merged_file, outfile)
        print("Success.")
        print("Wrote to file:", outfile)
except IndexError:
    print_help()