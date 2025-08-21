# coding: utf-8

"""
This script will clean output scories from the stiching.
nr-stitcher is creating several temporary files that are useless to the user.

This is the conversion of the `rm_stitch_temps.sh` scipt. It was simpler to embed it as a python script / application
"""

import argparse
import os
import sys
from fnmatch import fnmatch
import logging
import shutil

_logger = logging.getLogger(__name__)


def main():

    argv = sys.argv[1:]
    argparser = argparse.ArgumentParser(
        description="Creates input file for nr_stitcher.py program from id16a holotomography scan settings."
    )
    argparser.add_argument(
        "output_dir",
        type=str,
        help="Output directory. Will be the current working directory if not provided.",
        default=".",
        nargs="?",
    )

    args = argparser.parse_args(argv)
    if not os.path.exists(args.output_dir):
        raise ValueError(f"{args.output_dir} doesn't exists")

    FILE_PATTERNS_TO_REMOVE = (
        "*_refpoints.txt",
        "*_refpoints_settings.txt",
        "*_transformation.txt",
        "*_gof_*.raw",
        "*_defpoints_*.raw",
        "*_world_to_local_shifts_*.raw",
        "*_index.txt",
        "*_done.tif",
        "*_mosaic_settings.txt",
        "*_transformations_settings.txt",
        "*_position_settings.txt",
    )

    FOLDER_PATTERN_TO_REMOVE = ("slurm-io-files",)

    def remove_if_match(file_path):
        for pattern in FILE_PATTERNS_TO_REMOVE:
            if fnmatch(file_name, pattern):
                try:
                    os.remove(file_name)
                except Exception as e:
                    _logger.error(f"Fail to remove {file_path}. Error is {e}")
                return

        for pattern in FOLDER_PATTERN_TO_REMOVE:
            if fnmatch(file_name, pattern):
                try:
                    shutil.rmtree(file_name)
                except Exception as e:
                    _logger.error(f"Fail to remove {file_path}. Error is {e}")
                return

    for file_name in os.listdir(args.output_dir):
        file_path = os.path.join(args.output_dir, file_name)
        assert os.path.exists(file_path)
        remove_if_match(file_path=file_path)


if __name__ == "__main__":
    main()
