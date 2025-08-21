from enum import Enum, unique


@unique
class Instruments(Enum):
    # Values are determined using scan of the fist byte of data
    EK60 = "EK60"
    EK80 = "EK80"


# @unique
class Constants(Enum):
    TILE_SIZE = 512

    # Average https://noaa-wcsd-zarr-pds.s3.us-east-1.amazonaws.com/level_2/Henry_B._Bigelow/HB0902/EK60/HB0902.zarr/time/927
    # chunk size is ~1.3 kB, HB0902 cruise takes ~30 seconds to load all time/lat/lon dataset
    # NOTE: larger value here will speed up the TurfJS download of dataset in the UI
    # Problem interpolating the dataset: cannot reshape array of size 65536 into shape...
    SPATIOTEMPORAL_CHUNK_SIZE = int(2**16) - 1024  # e.g. int(2**14)
    # TODO: create test for SPATIOTEMPORAL_CHUNK_SIZE with requirement!

    LEVEL_0 = "raw"
    LEVEL_1 = "level_1"  # from bucket path
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"

    EK60 = "EK60"  # TODO: use for "instrument"
    EK80 = "EK80"
    # INSTRUMENT = EK60 | EK80


class Coordinates(Enum):
    """
    Should try to specify
        dtype
        units
        long_name — most readable description of variable
        standard_name — name in lowercase and snake_case
    """

    PROJECT_NAME = "echofish"

    DEPTH = "depth"
    DEPTH_DTYPE = "float32"
    DEPTH_UNITS = "m"  # TODO: Pint? <https://pint.readthedocs.io/en/stable/>
    DEPTH_LONG_NAME = "Depth below surface"
    DEPTH_STANDARD_NAME = "depth"

    TIME = "time"
    TIME_DTYPE = "float64"
    # Note: units and calendar are used downstream by Xarray
    TIME_UNITS = "seconds since 1970-01-01 00:00:00"
    TIME_LONG_NAME = "Timestamp of each ping"
    TIME_STANDARD_NAME = "time"
    TIME_CALENDAR = "proleptic_gregorian"
    # TODO: create test for reading out timestamps in Xarray

    FREQUENCY = "frequency"
    FREQUENCY_DTYPE = "uint"
    FREQUENCY_UNITS = "Hz"
    FREQUENCY_LONG_NAME = "Transducer frequency"
    FREQUENCY_STANDARD_NAME = "sound_frequency"

    LATITUDE = "latitude"
    LATITUDE_DTYPE = "float32"
    LATITUDE_UNITS = "degrees_north"
    LATITUDE_LONG_NAME = "Latitude"
    LATITUDE_STANDARD_NAME = "latitude"

    LONGITUDE = "longitude"
    LONGITUDE_DTYPE = "float32"
    LONGITUDE_UNITS = "degrees_east"
    LONGITUDE_LONG_NAME = "Longitude"
    LONGITUDE_STANDARD_NAME = "longitude"

    BOTTOM = "bottom"
    BOTTOM_DTYPE = "float32"
    BOTTOM_UNITS = "m"
    BOTTOM_LONG_NAME = "Detected sea floor depth"
    BOTTOM_STANDARD_NAME = "bottom"

    SPEED = "speed"
    SPEED_DTYPE = "float32"
    SPEED_UNITS = "Knots"
    SPEED_LONG_NAME = "Nautical miles per hour"
    SPEED_STANDARD_NAME = "speed"

    SV = "Sv"
    SV_DTYPE = "float32"  # int64
    SV_UNITS = "dB"
    SV_LONG_NAME = "Volume backscattering strength (Sv re 1 m-1)"
    SV_STANDARD_NAME = "volume_backscattering_strength"


class BatchShape(Enum):
    """
    The tensor shape of a machine learning sample.
    """

    DEPTH = 2
    TIME = 3
    FREQUENCY = 4
    BATCH_SIZE = 5
