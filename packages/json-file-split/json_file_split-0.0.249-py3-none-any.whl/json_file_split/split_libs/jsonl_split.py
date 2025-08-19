import math
from beartype import beartype
from loguru import logger
import glob, subprocess, os


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


def split_by_size_of_buckets():
    raise Exception("split_by_size_of_buckets not implemented.")


import os
import glob


def empty_directory_tmp(dir_path: str):
    files = glob.glob(os.path.join(dir_path, "*"))
    for f in files:
        try:
            os.remove(f)
        except:
            pass


# @beartype
def split_by_number_of_buckets(
    number_of_buckets: int, input_file_path: str, output_file_path: str, start: int = 0
):
    output_dir_path = os.path.dirname(output_file_path)
    empty_directory_tmp(output_dir_path)

    num_lines = int(open(input_file_path).read().count("\n"))

    # number_of_buckets
    lines_per_file = int(round_up(num_lines / number_of_buckets))

    # Execute the split as a subprocess and ait
    p = subprocess.Popen(
        [
            "split",
            "-a",  # suffix-length
            "5",
            "-l",
            str(lines_per_file),
            input_file_path,
            "{}.".format(output_file_path),
        ]
    )
    p.wait()

    if p.returncode != 0:
        exit(p.returncode)

    output_file_dir = os.path.dirname(os.path.abspath(output_file_path))

    # Get all files in the output directory
    files = glob.glob(os.path.join(output_file_dir, "*.jsonl.*"))

    saved = []

    # For each file
    for counter, file in enumerate(files, start=start):

        # Get the full file path
        path = os.path.dirname(os.path.abspath(file))

        new_file_path = "{}/{}.jsonl".format(path, counter)

        # Rename the file
        os.rename(file, new_file_path)

        saved.append(new_file_path)

    return saved
