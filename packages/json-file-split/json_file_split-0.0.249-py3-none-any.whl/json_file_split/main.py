import argparse, os
from loguru import logger
from json_file_split.split_libs.jsonl_split import split_by_number_of_buckets
from fsai_shared_funcs.string_helper import string_is_true_or_false


def app():

    parser = argparse.ArgumentParser(
        description="Split json and jsonl files into parts."
    )

    parser.add_argument(
        "-i",
        "--input_file_path",
        help="The path to the input json or jsonl file.",
        default="./tests/data/test.jsonl",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-s",
        "--save_to_dir",
        help="The directory to save the jsonl file.",
        required=True,
        default="/tmp/output/",
        type=str,
    )

    parser.add_argument(
        "-j",
        "--output_file_name",
        help="The name of the output jsonl file.",
        default="output.jsonl",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-sb",
        "--split_by",
        help="The method of splitting files: number_of_buckets, or size_of_buckets.",
        default="number_of_buckets",
        type=str,
    )

    parser.add_argument(
        "-bs",
        "--batch_size",
        help="The size of each batch.",
        default=10,
        required=True,
        type=int,
    )

    parser.add_argument(
        "-scf",
        "--save_count_file",
        help="Should a file with the count of files generated be saved.",
        default=False,
        required=False,
        type=string_is_true_or_false,
    )

    parser.add_argument(
        "-cfp",
        "--count_file_path",
        help="The file to save the count of files generated.",
        default="/tmp/count.txt",
        required=False,
        type=str,
    )

    args = vars(parser.parse_args())

    output_file_path = os.path.join(
        args["save_to_dir"],
        args["output_file_name"].lstrip(
            os.path.sep
        ),  # remove leading forward slash which causes join to think path is relative
    )

    logger.debug("Saving output file to: {}".format(output_file_path))

    # Create the directory structure
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    logger.info("Split By: {}".format(args["split_by"]))
    logger.info("Batch Size: {}".format(args["batch_size"]))
    logger.info("Input File Path: {}".format(args["input_file_path"]))
    logger.info("Output File Path: {}".format(output_file_path))

    # If the output file path is a jsonl file
    if output_file_path.endswith(".jsonl"):

        if args["split_by"] == "number_of_buckets":
            saved_files = split_by_number_of_buckets(
                args["batch_size"], args["input_file_path"], output_file_path
            )

        if args["split_by"] == "size_of_buckets":
            raise Exception("split_by size_of_buckets not implemented.")

        if args["save_count_file"] == True:
            with open(args["count_file_path"], "w") as f:
                cnt = len(saved_files)
                logger.debug(
                    "Save the count file path {} ({})".format(
                        args["count_file_path"], cnt
                    )
                )
                f.write(str(cnt))

        logger.info("Save {} files: {}".format(len(saved_files), saved_files))
