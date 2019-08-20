#!/usr/bin/python
import sys, os, glob
from pathlib import Path
from PIL import Image

def print_help():
    print("Usage: Nspiremerger <output file> <project root dir> <lua file globs>...")
    exit()

def image_to_string(image):
    return "Placeholder"

def get_image_name(path):
    return os.path.split(path)[1].split(".")[-2]

def collect_resources(root):
    header = "----- GENERATED ASSETS -----"
    resources = ["-" * len(header), header]

    resources.append("_R = {}")
    resources.append("_R.IMG = {}")
    for file in glob.glob(root + "/res/IMG/*.png"):
        image = Image.open(file).load()
        image_str = image_to_string(image)
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

            merge_result.append(Path(file_name).read_text())

            merge_result.append(header)
            merge_result.append("-"*len(header))
    if len(merge_result) == 0:
        raise Exception("Error: No input files found")
    return merge_result

def print_to_file(resources, contents, outfile):
    output = open(outfile, "w")
    for resource in resources:
        output.write(resource+'\n')
    output.write("\n\n\n")
    for content in contents:
        output.write(content+'\n')
    output.close()

try:
    if __name__ == "__main__":
        outfile = sys.argv[1]
        root = sys.argv[2]
        input_file_globs = sys.argv[3:]

        if not Path(root).is_dir():
            raise Exception(f"Error: project directory: {root} not found")
        if not Path(root + "/res"):
            raise Exception(f"Error: resources directory: {root}/res not found")
        
        resources = collect_resources(root)
        merged_file = merge_input_files(input_file_globs)
        print_to_file(resources, merged_file, outfile)
        print("Success.")
        print("Wrote to file:", outfile)
except IndexError:
    print_help()