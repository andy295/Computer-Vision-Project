import os
import sys
import cv2
import copy
import platform
import numpy as np

from enum import IntEnum

from utils import *

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
    bvh = 10
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
    '.bvh',
    '.c3d'
    )

# allowed extenSions for input files
INPUT_EXTENSIONS = (
    '.csv',
    '.bvh',
    '.c3d'
    )

# FILES NAMES
RIGID_BODY = 'rigidbody'
SKELETON = 'skeleton'
ANIMATION = 'animation'
MARKER = 'marker'

CSV_LIST = [RIGID_BODY + EXTENSIONS[Extension.csv], SKELETON + EXTENSIONS[Extension.csv]]
OTHER_LIST = [ANIMATION + EXTENSIONS[Extension.bvh], MARKER + EXTENSIONS[Extension.c3d]]
FPS_LIST = ['60fps', '360fps']

#TYPE OF FILTERING
KALMAN_FILTER = 'kfPositions'
SPLINE_INTERPOLATION = 'splPositions'

# PATHS
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(ROOT_PATH, f'Data')
SAVE_PATH = os.path.join(ROOT_PATH, f'Saved')

# used for testing purposes
SRC_FILE = RIGID_BODY + EXTENSIONS[Extension.csv]
SRC_PATH = os.path.join(DATA_PATH, SRC_FILE)

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

IGNORE_DATA = ['Marker'] # columns to be ignored

# BVH STRUCTURE
BHV_DIR = "bvh_reader"
ANIMATION = 'animation'
NAMES = 'names'

# C3D STRUCTURE
C3D_ANALOG = 'analog'
C3D_SCALE_FACTOR = 'scale_factor'
C3D_ERR_EST = 'err_est' # estimated error
C3D_CAMERA_NR = 'camera' # number of cameras that registered the point
C3D_POINT_RATE = 'point_rate'

# DATA STRUCTURE
HEADER = 'header'
HEADER_SHORT = 'h'

TIME = 'time'
TIME_SHORT = 't'

ROTATION = 'rotation'
POSITION = 'position'

POINT = 'point'
FRAME = 'frame'

X = 'x'
Y = 'y'
Z = 'z'
W = 'w'

TYPE = 0
NAME = 1
ID = 2

KEY_SEPARATOR = '-'
SPACE_REPLACEMENT = '_'

# MODALITIES
NONE = 'n'
PLOT_CHART = False

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
TEST = 1

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
