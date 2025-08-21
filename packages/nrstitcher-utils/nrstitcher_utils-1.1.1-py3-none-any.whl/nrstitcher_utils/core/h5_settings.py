import h5py
from itertools import compress
import logging

_logger = logging.getLogger(__name__)


class H5Settings:

    def __init__(self, h5_filename, volume_name, scan_suffix):
        self.filename = h5_filename
        self.file = h5py.File(self.filename, "r")
        self.keys = list(self.file.keys())

        mask = [x.endswith(scan_suffix) for x in self.keys]
        entry_list = list(compress(self.keys, mask))

        found = False

        for entry in entry_list:
            prefix = entry.split(" ")[-1].replace(scan_suffix, "")
            if prefix in volume_name:
                self.root = self.file[entry]
                _logger.info(f"will treat volume {volume_name}")
                found = True

        if found is False:
            for entry in entry_list:
                tmp = entry.split(" ")[-1]
                prefix = "".join(tmp.rsplit(scan_suffix, 1))

                if prefix in volume_name:
                    self.root = self.file[entry]
                    _logger.info(f"will treat volume {volume_name}")

    def toList(self, group):
        """
        Write h5 file entries to a list.

        Arguments:
        group: Required group in h5 file

        Returns:
        items: names of datasets
        data: values in datasets
        """

        # Names
        items = []
        for item in group.items():
            items.append(str(item[0]))

        data = []
        for item in group.values():
            # Data is saved as a string with spaces between values. Split on spaces to get the values as strings.
            raw_data = item[()].astype(str).split(" ")
            # Remove null strings
            filtered_data = list(filter(None, raw_data))
            data.append(filtered_data)

        return items, data

    def get_motor_positions(self):
        """
        Get the parameters saved under sample/positioners in the experiment .h5 file.

        Arguments:
        None

        Returns:
        motor_positions_dict: Dictionary containing the positioner names as KEYS and their positions as VALUES
        """

        motor_info = self.root["sample"]["positioners"]
        h5_items, h5_data = self.toList(motor_info)
        names = h5_data[0]  # List of motor names as strings
        values = [float(x) for x in h5_data[1]]  # List of motor positions as floats
        # Create dictionary of motor positions
        motor_positions_dict = {}
        for idx, key in enumerate(names):
            motor_positions_dict[key] = values[idx]

        return motor_positions_dict

    def get_tomo_parameters(self):
        """
        Get the parameters saved under the heading "TOMO" in the experiment .h5 file.

        Arguments:
        None

        Returns:
        tomo_parameters_dict: Dictionary containing the parameter names as KEYS and their values as VALUES
        """

        h5_items, h5_data = self.toList(self.root["TOMO"])
        tomo_parameters_dict = {}
        for idx, key in enumerate(h5_items):
            if key != "FTOMO_PAR":
                tomo_parameters_dict[key] = float(h5_data[idx][0])

        return tomo_parameters_dict
