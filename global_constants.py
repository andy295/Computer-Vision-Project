import os
import csv

from enum import IntEnum

# FILE EXTENSIONS
class Extension(IntEnum):
    none = 0
    mat = 1
    csv = 2
    png = 3
    txt = 4
    jpg = 5
    pt = 6
    json = 7
    pkl = 8
    zip = 9
    bhv = 10
    c3d = 11

EXTENSIONS = (
    '',
    '.mat',
    '.csv',
    '.png',
    '.txt',
    '.jpg',
    '.pt',
    '.json',
    '.pkl',
    '.zip',
    '.bhv',
    '.c3d'
    )

# allowed extenSions for input files
INPUT_EXTENSIONS = (
    '.csv',
    '.bhv',
    '.c3d'
    )

# FILES NAMES
SRC_FILE = 'ProvaRigidBody'
# SRC_FILE = 'test'

# PATHS
SRC_PATH = 'Data/60fps'
INPUT_FILE = os.path.join(SRC_PATH, SRC_FILE + EXTENSIONS[Extension.csv])

# CSV STRUCTURE
# the application is thought to work with CVS data version 1.23
# any other version is not supported
CSV_VERSION = '1.23'

CSV_HEADER_FILE_ROW = 0 # file header row start number
CSV_HEADER_FILE_LEN = 1 # file header dimension
CSV_VERSION_COLUMN = 1 # file header column number for version info
CSV_HEADER_DATA_ROW = 2 # data header row start number
CSV_HEADER_DATA_LEN = 5 # data header dimension
CSV_DATA_COLUMN = 2 # data column start number

# DATA STRUCTURE
HEADER = 'Header'
HEADER_SHORT = 'H'

TIME = 'Time'
TIME_SHORT = 'T'

ROTATION = 'Rotation'
POSITION = 'Position'

TYPE = 0
NAME = 1
ID = 2

KEY_SEPARATOR = '-'
SPACE_REPLACEMENT = '_'

# MODALITIES
NONE = 'n'

# I/O
READ = 'r'
READ_B = 'rb'
WRITE = 'w'
WRITE_B = 'wb'
APPEND = 'a'
COPY = 'cp'
COMPRESS = 'cmp'
EXPAND = 'exp'
SAVE = 's'
LOAD = 'l'

# EXPERIMENT OPERATIONS
NEW = 0

# just for developing purposes
NOTHING = -1

# EXPERIMENT PHASES
ALL = 'all'
IMPORT = 'imp'

# LOGGING
# verbose type
OFF = 0
STANDARD = 1
INFO = 2
WARNING = 3
DEBUG = 4

VERBOSE = DEBUG
DECIMAL_DIGITS = 2
