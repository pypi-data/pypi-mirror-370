# coding: utf-8

"""
stitch_settings_from_ID16a_ht.py:

This script is dedicated to holotomographic data acquired on the beamline ID16A at the ESRF, and is used to generate a stitch settings file to be used as input to nr_stitcher.py.
The stitch settings file is generated based on the template default_stitch_settings.py provided with nr_stitcher, with parameters mofdified based on user-selected options.
After adding the NRStitcher directory to the path, this script should be run from the directory where the generated stitch settings file is to be saved.

"""

import argparse
import glob
import os
import shutil
import sys
import logging
from pathlib import Path

# import from pi2 / NRstitcher -> see https://github.com/arttumiettinen/pi2/blob/master/python_scripts/default_stitch_settings.py
from default_stitch_settings import write_stitch_settings  # pylint: disable=E0401
from nrstitcher_utils.core.h5_settings import H5Settings
from nrstitcher_utils.core.ht_vol import HTVol
from nrstitcher_utils.core import utils
from nrstitcher_utils.resources import get_config_file

_logger = logging.getLogger(__name__)


def main():

    def get_h5file(h5_folder):
        """
        Gets the name of the h5 file associated with the experiment base directory.

        Arguments:
        None

        Returns:
        Name of the h5 file as a string.
        """

        h5_filename = glob.glob(h5_folder + "/*.h5")[0]

        return h5_filename

    argv = sys.argv[1:]
    argparser = argparse.ArgumentParser(
        description="Creates input file for nr_stitcher.py program from id16a holotomography scan settings."
    )
    argparser.add_argument(
        "--base_dir",
        type=str,
        help="Required. Base directory containing sub-directories for individual scans and reconstructed volumes.",
    )
    argparser.add_argument(
        "--vol_dir",
        type=str,
        default="volfloat/",
        help="Required. Sub-directory containing reconstructed volumes.",
    )
    argparser.add_argument(
        "--volumes",
        nargs="*",
        type=str,
        action="store",
        default="*.raw",
        help="Required. Names (separated by a space) of reconstructed volumes to be stitched, or, if there are many volumes a single input with regular expressions can be used e.g., sample_*.raw.",
    )
    argparser.add_argument(
        "--distances",
        nargs="*",
        type=int,
        action="store",
        default=None,
        help="Optional. Integers (separated by a space) corresponding to distances used in holotomographic acquisition. Default is [1 2 3 4].",
    )
    argparser.add_argument(
        "--bitdepth",
        default=None,
        type=str,
        help='Optional. Bit depth of output .raw volumes if conversion is required. Default is none, no conversion will be performed. Options are "pyhst" (32-bit float), "8bits", "16bits" and "32bits" (int).',
    )
    argparser.add_argument(
        "--voxelsize",
        default=None,
        type=str,
        help="Optional. Give desired voxel size (in nm) if volumes are to be rescaled (same value applies to all volumes).",
    )
    argparser.add_argument(
        "--vrange",
        default=None,
        nargs=2,
        type=int,
        help="Optional. Minimum and maximum greyscale values. If not given they will be automatically calculated. Values are applied to all volumes",
    )
    argparser.add_argument(
        "-b",
        "--binning",
        default=1,
        type=int,
        help="Optional. Binning that is to be applied before stitching. Recommended for optimising the stitch settings. Default is 1 (no binning).",
    )
    argparser.add_argument(
        "-n",
        "--name",
        default="stitched",
        type=str,
        help='Sample name. Default is "stitched".',
    )
    argparser.add_argument(
        "-o",
        "--output",
        default="stitch_settings.txt",
        type=str,
        help='Optional. Name of stitch_settings file. Default is "stitch_settings.txt". Will be saved in the current working directory.',
    )
    argparser.add_argument(
        "--debug",
        type=bool,
        default=False,
        help='Optional. Name of stitch_settings file. Default is "stitch_settings.txt". Will be saved in the current working directory.',
    )

    args = argparser.parse_args(argv)
    if args.distances is None:
        args.distances = [1, 2, 3, 4]
    args.distances.sort()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    # Get volumes from command line input
    if len(args.volumes) > 1:
        # Do this if entire name of individual volumes given
        volNames = args.volumes
        floatVols = [os.path.join(args.base_dir, args.vol_dir) + x for x in volNames]
    else:
        # Do this if script is to take all volumes containing the given strings, can contain wildcards
        floatVols = sorted(
            glob.glob(os.path.join(args.base_dir, args.vol_dir) + args.volumes[0])
        )
        _logger.debug(f"floatVols: {floatVols}")
        volNames = [os.path.basename(x) for x in floatVols]

    rawVols = []

    for volName in volNames:
        # Process the float volumes (convert to raw if not already done)
        vol = HTVol(args, volName)
        rawVol = vol.process_vol()
        rawVols.append(rawVol)

    floatInfoFiles = [vol + ".info" for vol in floatVols]
    rawInfoFiles = [vol + ".info" for vol in rawVols]

    line_to_write = ""

    for i, vol in enumerate(rawVols):

        # Read the .info files for the .raw and original .vol volumes
        rawInfo = utils.get_vol_info(rawInfoFiles[i])
        floatInfo = utils.get_vol_info(floatInfoFiles[i])

        # Dimensions in number of pixels of the volumes
        Xdim = float(rawInfo["NUM_X"])
        Ydim = float(rawInfo["NUM_Y"])
        Zdim = float(rawInfo["NUM_Z"])

        # Assume standard image size pf 3216 x 3216 x 3216 px^3
        Xdim_ref = 3216
        Ydim_ref = 3216
        Zdim_ref = 3216

        # Get scan settings from .h5 file (the one from the experiment, containing all the scans)
        settings_folder = Path(args.base_dir).parent
        _logger.info(f"try to get settings from {settings_folder}")
        # try to read the setting from the proposal file (like ls "ls2892-id16a.h5")
        settings_file = get_h5file(str(settings_folder))
        first_dist = args.distances[0]
        scan_settings = H5Settings(settings_file, vol, scan_suffix=f"_{first_dist}_")
        motor_positions = scan_settings.get_motor_positions()
        tomo_params = scan_settings.get_tomo_parameters()

        sx = motor_positions["sx"]
        sz = motor_positions["sz"]
        su = motor_positions["su"]
        sv = motor_positions["sv"]
        sax, say = utils.get_sax_say(su, sv)

        sx0 = tomo_params["sx0"]

        orig_vox_size = (
            float(floatInfo["voxelSize"]) / 1000.0
        )  # Voxel size stored in um, convert to mm
        vox_size = (
            float(rawInfo["voxelSize"]) / 1000.0
        )  # Voxel size stored in um, convert to mm

        Z = sz
        Y = -sax
        X = -say

        # Magnification factor
        zoom = orig_vox_size / vox_size

        # When zoom != 1, ie., correct for downward slope of beam
        dX = utils.get_delta_sx(sx, sx0, zoom)
        dZ = utils.get_delta_sz(tomo_params["energy"], dX)

        Z += dZ

        # Positions in units of pixels with correction in case tiles do not have the same number of pixels
        Z = round(Z / vox_size + (Zdim_ref - Zdim) / 2.0)
        Y = round(Y / vox_size + (Ydim_ref - Ydim) / 2.0)
        X = round(X / vox_size + (Xdim_ref - Xdim) / 2.0)

        logging.info(f"positions (in px): {X}, {Y}, {Z}")

        path = vol
        line = f"{path} = {X}, {Y}, {Z}"
        line_to_write += line + "\n"

    # Write the stitch settings file and copy slurm_config file to local directory
    write_stitch_settings(
        args.name,
        args.binning,
        line_to_write,
        point_spacing=100,
        coarse_block_radius=50,
        coarse_binning=2,
        cluster_name="SLURM",
    )
    # note: write_stitch_settings always write settings to stitch_settings.txt
    os.rename("./stitch_settings.txt", "./" + args.output)
    if not os.path.isfile("./slurm_config.txt"):
        shutil.copyfile(
            get_config_file("slurm_config_id16a.txt"),
            "./slurm_config.txt",
        )


if __name__ == "__main__":
    main()
