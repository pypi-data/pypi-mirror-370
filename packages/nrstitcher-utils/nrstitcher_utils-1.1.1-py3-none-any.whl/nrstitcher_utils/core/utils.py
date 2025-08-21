"""generic utils function"""

import numpy as np


def get_sax_say(su, sv):
    """
    Calculate the sax and say values from the su and sv positions.

    Arguments:
    su: Position of motor su, read from experiment .h5 file
    sv: Position of motor sv, read from experiment .h5 file

    Returns:
    sax: Position of virtual motor sax
    say: Position of virtual motor say
    """

    a = 21.5 * np.pi / 180.0

    sax = -np.sin(a) * su + np.cos(a) * sv
    say = np.cos(a) * su + np.sin(a) * sv

    return sax, say


def get_delta_sx(sx, sx0, zoom):
    """
    Find the shift in sx which would be required to magnify (or demagnify) an image by a given factor.
    This is particularly useful for finding sx and corresponding sy and sz values for a rescaled image.
    the equation has been deduced from ...

    Arguments:
    sx: The position of motor sx read from the h5 file for the original image
    sx0: The fixed sx0 value (depends on beam energy), read from the experiment .h5 file
    zoom: The magnification factor

    Returns:
    delta_sx: The shift in sx to be applied
    """

    sx_ = (sx - sx0) * (1.0 / zoom) + sx0

    delta_sx = sx_ - sx

    return delta_sx


def get_delta_sy(energy, delta_sx):
    """
    Find the shift in sy which is required to correct for the slope of the beam when moving sx.
    The angle values were obtained from the beamline macros.
    Check with Peter Cloetens for eventual updates to these values.
    The values were last updated in the beamline macros on 31/10/2020 and were up to date as of 21/06/2023.
    Currently not used in _main_, but has been written in case it is required in future updates.

    Arguments:
    energy: Beam energy in keV
    delta_sx: The shift, or translation to be performed with sx

    Returns:
    delta_sy: shift in sy which corresponds to the given shift in sx
    """

    if int(energy) == 17:
        angle = 28.866
    else:
        angle = 15.871

    delta_sy = -delta_sx * angle / 1000

    return delta_sy


def get_delta_sz(energy, delta_sx):
    """
    Find the shift in sz which is required to correct for the slope of the beam when moving sx.
    The angle values were obtained from the beamline macros.
    Check with Peter Cloetens for eventual updates to these values.
    The values were last updated in the beamline macros on 31/10/2020 and were up to date as of 21/06/2023.

    Arguments:
    energy: Beam energy in keV
    delta_sx: The shift, or translation to be performed with sx

    Returns:
    delta_sz: shift in sz which corresponds to the given shift in sx
    """

    if int(energy) == 17:
        angle = 29.389
    else:
        angle = 15.415

    delta_sz = -delta_sx * angle / 1000

    return delta_sz


def motorpos_to_pixels(value, voxel_size):
    # Converts motor position in mm to pixels
    return round(value / voxel_size)


def get_vol_info(infoFile):
    """
    Extracts information from .info file.

    Arguments:
    infoFile: The name and path of the .info files to be read

    Returns:
    info: Dictionary containing the contents of the file,
    where the left column, or parameter name is the KEY and the right column is the VALUE
    """

    info = {}
    with open(infoFile) as f:
        for line in f.readlines():
            try:
                key, value = line.replace(" ", "").split("=")
                info[key] = value
            except Exception:
                continue

    return info
