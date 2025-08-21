import os
import logging
from pi2py2 import ImageDataType, Pi2  # pylint: disable=E0401


_logger = logging.getLogger(__name__)


class HTVol:
    """Half-tomo volume"""

    def __init__(self, args, volName):

        self.pi = Pi2()

        dt = {
            "float32": "float32",
            "32bits": "uint32",
            "16bits": "uint16",
            "8bits": "uint8",
        }

        self.volName = os.path.join(args.base_dir, args.vol_dir, volName)
        infoFile = os.path.join(args.base_dir, args.vol_dir, (volName + ".info"))
        self.info = self.get_vol_info(infoFile)
        self.slices = int(self.info["NUM_Z"])
        self.rows = int(self.info["NUM_Y"])
        self.cols = int(self.info["NUM_X"])
        self.voxelSize = float(self.info["voxelSize"])
        self.vmin = float(self.info["ValMin"])
        self.vmax = float(self.info["ValMax"])
        self.byteorder = self.info["BYTEORDER"].strip()

        self.dimensions = [self.cols, self.rows, self.slices]

        self.fromType = "float32"
        if args.bitdepth is None:
            args.bitdepth = self.fromType

        self.toType = dt[args.bitdepth]

        if args.vrange is not None:
            self.tomin = args.vrange[0]
            self.tomax = args.vrange[1]
        else:
            self.tomin = self.vmin
            self.tomax = self.vmax

        self.rescaleTo = args.voxelsize
        if self.rescaleTo is not None:
            self.zoom = self.voxelSize / (float(self.rescaleTo) / 1000.0)
        else:
            self.zoom = 1

        strbits = args.bitdepth

        self.modified = False

        self.x = round(self.cols * self.zoom)
        self.y = round(self.rows * self.zoom)
        self.z = round(self.slices * self.zoom)

        self.shape = str(self.y) + "x" + str(self.x) + "x" + str(self.z)

        self.savePath = os.path.join(args.base_dir, "volraw/")
        self.saveFile = self.volName.replace(".vol", strbits).split("/")[-1]
        if self.zoom != 1:
            self.saveFile += "_rescaled_" + str(self.rescaleTo) + "nm"
        self.saveFileName = self.saveFile + "_" + self.shape + ".raw"

    def get_vol_info(self, infoFile):
        """
        Get the information contained with the .vol.info file.

        Arguments:
        infoFile: The name of the info file as a string.

        Returns:
        A dictionary with the property name as the KEY and its value as the VALUE.
        """

        info = {}
        with open(infoFile) as f:
            for line in f.readlines():
                try:
                    key, value = line.replace(" ", "").replace("\n", "").split("=")
                    info[key] = value
                except Exception:
                    continue

        return info

    def check_raw(self):
        """
        Check if a processed image corresponding to selected options already exists or not.

        Arguments:
        None

        Returns:
        True or False
        """

        infoFileName = os.path.join(self.savePath, self.saveFileName) + ".info"
        if os.path.isfile(
            os.path.join(self.savePath, self.saveFileName)
        ) and os.path.isfile(infoFileName):
            raw_info = self.get_vol_info(infoFileName)

            raw_vmin = int(float(raw_info["ValMin"]))
            raw_vmax = int(float(raw_info["ValMax"]))

            if raw_vmin == int(self.tomin) and raw_vmax == int(self.tomax):
                _logger.info(
                    os.path.join(self.savePath, self.saveFileName)
                    + " already exists. Skipping."
                )
                return True

        return False

    def read_vol(self):
        """
        Opens a .vol volume as a pi2 image.

        Arguments:
        None

        Returns:

        """

        _logger.info("Reading volume " + self.volName)
        self.volfloat = self.pi.read(self.volName)

    def create_vol(self, dtype):
        """
        Create a new pi2 image of specified datatype and dimensions.

        Arguments:
        dtype: Desired datatype.

        Returns:
        vol: Empty pi2 image.
        """

        if dtype == "float32":
            vol = self.pi.newimage(ImageDataType.FLOAT32, self.y, self.x, self.z)
        elif dtype == "uint32":
            vol = self.pi.newimage(ImageDataType.UINT32, self.y, self.x, self.z)
        elif dtype == "uint16":
            vol = self.pi.newimage(ImageDataType.UINT16, self.y, self.x, self.z)
        elif dtype == "uint8":
            vol = self.pi.newimage(ImageDataType.UINT8, self.y, self.x, self.z)
        else:
            raise NotImplementedError

        return vol

    def bit_conversion(self):
        """
        Convert volume from original datatype to new datatype with specified range.

        Arguments:
        None

        Returns:

        """

        intbits = {"uint32": 32, "uint16": 16, "uint8": 8}
        _logger.info("Converting to " + str(intbits[self.toType]) + " bits.")

        self.vmax = self.tomax
        self.vmin = self.tomin
        self.vmin -= 1 / (
            2 ** intbits[self.toType] - 1
        )  # Zero-valued pixels (eg. pixels outside the reconstructed cylinder) should retain their zero-value after the conversion

        vrange = self.vmax - self.vmin

        self.pi.replace(self.volfloat, 0, self.vmin)
        self.pi.subtract(self.volfloat, self.vmin)
        self.pi.divide(self.volfloat, vrange)
        self.pi.max(self.volfloat, 0)
        self.pi.min(self.volfloat, 1)
        self.pi.multiply(self.volfloat, (2 ** intbits[self.toType] - 1))

        if self.toType == "uint32":
            self.pi.convert(self.volfloat, ImageDataType.UINT32)
        elif self.toType == "uint16":
            self.pi.convert(self.volfloat, ImageDataType.UINT16)
        elif self.toType == "uint8":
            self.pi.convert(self.volfloat, ImageDataType.UINT8)

        self.modified = True

    def rescale(self):
        """
        Rescale (modify the dimensions of) the volume.

        Arguments:
        None

        Returns:

        """

        _logger.info("Rescaling to " + str(self.rescaleTo) + " nm pixel/voxel size.")
        tmp = self.create_vol(self.toType)
        self.pi.scale(self.volfloat, tmp, [0, 0, 0], False, "Nearest")
        self.volfloat.set_data(tmp.get_data())
        del tmp
        self.modified = True

    def write_to_raw(self):
        """
        Save the processed volume in the raw format.

        Arguments:
        None

        Returns:

        """

        _logger.info("Writing to " + os.path.join(self.savePath, self.saveFileName))

        self.pi.writeraw(self.volfloat, os.path.join(self.savePath, self.saveFile))
        self.write_raw_info()

    def write_raw_info(self):
        """
        Write a .raw.info file containing the parameters of the processed volume.

        Arguments:
        None

        Returns:

        """

        dims = self.volfloat.get_dimensions()
        infoFile = (
            self.savePath
            + self.saveFile
            + "_"
            + str(dims[0])
            + "x"
            + str(dims[1])
            + "x"
            + str(dims[2])
            + ".raw.info"
        )

        with open(infoFile, "w") as f:
            f.write("NUM_X = " + str(dims[0]) + "\n")
            f.write("NUM_Y = " + str(dims[1]) + "\n")
            f.write("NUM_Z = " + str(dims[2]) + "\n")
            f.write("voxelSize = " + str(self.voxelSize / self.zoom) + "\n")
            f.write("BYTEORDER = " + str(self.byteorder) + "\n")
            f.write("ValMin = " + str(self.tomin) + "\n")
            f.write("ValMax = " + str(self.tomax) + "\n")

    def process_vol(self):
        """
        Calls the functions required to process the volume prior to stitching.

        Arguments:
        None

        Returns:
        The full path to the processed volume.
        """

        raw_exists = self.check_raw()

        if not raw_exists:
            self.read_vol()

            if self.toType != "float32":
                self.bit_conversion()

            if self.zoom != 1:
                self.rescale()

            if self.modified:
                self.write_to_raw()
            else:
                return self.volName

        return os.path.join(self.savePath + self.saveFileName)
