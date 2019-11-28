import ctypes
import enum
import warnings

import numpy as np

from astropy import units as u

class ASICamera:
    """ZWO ASI Camera class."""

    def __init__(self, library_path, camera_index=0):
        self._CDLL = ctypes.CDLL(library_path)
        self._camera_index = camera_index

        self._info = self.get_camera_property(self._camera_index)
        self._camera_ID = self.info['camera_ID']

        error_code = self._CDLL.ASIOpenCamera(self._camera_ID)
        if error_code != ErroCode.SUCCESS:
            msg = "Couldn't open camera: {}".format(error_code)
            warnings.warn(msg)
            raise RuntimeError(msg)

        result = self._CDLL.ASIInitCamera(self._camera_ID)
        if error_code != ErroCode.SUCCESS:
            msg = "Couldn't init camera: {}".format(result)
            warnings.warn(msg)
            raise RuntimeError(msg)

    def get_camera_property(self, camera_index):
        """ Get properties of the camera with given index """
        camera_info = CameraInfo()
        error_code = self._CDLL.ASIGetCameraProperty(ctypes.byref(camera_info), camera_index)
        if error_code != ErrorCode.SUCCESS:
            msg = "Error getting camera properties: {}".format(error_code)
            warnings.warn(msg)
            raise RuntimeError(msg)

        pythonic_info = self._parse_info(camera_info)
        return pythonic_info

    def _call_function(self, function_name, camera_ID, *args):
        """ Utility function for calling the SDK functions that return ErrorCode """
        function = getattr(self._CDLL, function_name)
        error_code = function(ctypes.c_int(camera_ID), *args)
        if error_code != ErrorCode.SUCCESS:
            msg = "Error calling {}: {}".format(function_name, ErrorCode(error_code).name)
            warnings.warn(msg)
            raise RuntimeError(msg)

    def _parse_info(self, camera_info):
        """ Utility function to parse CameraInfo Structures into something more Pythonic """
        pythonic_info = {'name': camera_info.name.decode(),
                         'camera_ID': int(camera_info.camera_ID),
                         'max_height': camera_info.max_height * u.pixel,
                         'max_width': camera_info.max_width * u.pixel,
                         'is_color_camera': bool(camera_info.is_color_camera),
                         'bayer_pattern': BayerPattern(camera_info.bayer_pattern).name,
                         'supported_bins': self._parse_bins(camera_info.supported_bins),
                         'supported_video_format': self._parse_formats(
                             camera_info.supported_video_format),
                         'pixel_size': camera_info.pixel_size * u.um,
                         'has_mechanical_shutter': bool(camera_info.has_mechanical_shutter),
                         'has_ST4_port': bool(camera_info.has_ST4_port),
                         'has_cooler': bool(camera_info.has_cooler),
                         'is_USB3_host': bool(camera_info.is_USB3_host),
                         'is_USB3_camera': bool(camera_info.is_USB3_camera),
                         'e_per_adu': camera_info.e_per_adu * u.electron / u.adu,
                         'bit_depth': camera_info.bit_depth * u.bit,
                         'is_trigger_camera': bool(camera_info.is_trigger_camera)}
        return pythonic_info


@enum.unique
class ErrorCode(enum.IntEnum):
    """ Error codes """
    SUCCESS = 0
    INVALID_INDEX = 1  # No camera connected or index value out of boundary
    INVALID_ID = 2
    INVALID_CONTROL_TYPE = 3
    CAMERA_CLOSED = 4  # Camera didn't open
    CAMERA_REMOVED = 5  # Failed to fine the camera, maybe it was removed
    INVALID_PATH = 6  # Cannot find the path of the file
    INVALID_FILEFORMAT = 7
    INVALID_SIZE = 8  # Wrong video format size
    INVALID_IMGTYPE = 9  # Unsupported image format
    OUTOF_BOUNDARY = 10  # The startpos is out of boundary
    TIMEOUT = 11
    INVALID_SEQUENCE = 12  # Stop capture first
    BUFFER_TOO_SMALL = 13
    VIDEO_MODE_ACTIVE = 14
    EXPOSURE_IN_PROGRESS = 15
    GENERAL_ERROR = 16  # General error, e.g. value is out of valid range
    INVALID_MODE = 17  # The current mode is wrong
    END = 18


class CameraInfo(ctypes.Structure):
    """ Camera info structure """
    _fields_ = [('name', ctypes.c_char * 64),
                ('camera_ID', ctypes.c_int),
                ('max_height', ctypes.c_long),
                ('max_width', ctypes.c_long),
                ('is_color_camera', ctypes.c_int),
                ('bayer_pattern', ctypes.c_int),
                ('supported_bins', ctypes.c_int * 16),  # e.g. (1,2,4,8,0,...) means 1x, 2x, 4x, 8x
                ('supported_video_format', ctypes.c_int * 8),  # ImgTypes, terminates with END
                ('pixel_size', ctypes.c_double),  # in microns
                ('has_mechanical_shutter', ctypes.c_int),
                ('has_ST4_port', ctypes.c_int),
                ('has_cooler', ctypes.c_int),
                ('is_USB3_host', ctypes.c_int),
                ('is_USB3_camera', ctypes.c_int),
                ('e_per_adu', ctypes.c_float),
                ('bit_depth', ctypes.c_int),
                ('is_trigger_camera', ctypes.c_int),
                ('unused', ctypes.c_char * 16)]
