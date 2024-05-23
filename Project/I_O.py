import csv
import c3d # if library not found: pip install c3d

from global_constants import *
from data_manipulation import *
from utils import *

# Function to handle directory-related checks and validation based on
# the specified mode and path parameters.
# It returns True if the checks pass and False if any errors or
# invalid conditions are encountered.
def checkDir(mode=None, path=None):

  if mode == None:
    print(f"Error: Invalid selected operation\n")
    return False

  if emptyString(path):
    print(f"Error: Invalid path: {path}\n")
    return False

  if mode == SAVE:
    if not os.path.isdir(path):
      os.makedirs(path)

    True if os.path.isdir(path) else False

  elif mode == LOAD:
    if not os.path.isdir(path):
      print(f"Error: Specified path doesn't exist, impossible to load data\n")
      return False

    if os.listdir(path) == []:
      print(f"Error: {path} doens't contain any file\n")
      return False

  return True

# Function to handle various checks and validations related to files, based
# on the specified mode and file path parameters.
# It returns True if the checks pass, returns the new file path in
# case of saving mode, and returns False if any errors or invalid
# conditions are encountered.
def checkFile(mode=None, filePath=None):

  if mode == None:
    print(f"Error: Invalid selected operation\n")
    return False

  if emptyString(filePath):
    print(f"Error: Invalid file: {filePath}\n")
    return False

  if os.path.exists(filePath):
    if os.path.isfile(filePath):

      if mode == SAVE:
        found = False

        for i in range(2, 11):
          newFilePath, extention = os.path.splitext(filePath)

          if i > 2:
            newFilePath, _ = newFilePath.rsplit('_', 1)

          newFilePath += (f'_{i}')
          filePath = newFilePath + extention

          if VERBOSE >= WARNING:
            print(f"extention: {extention}")
            print(f"newPathFile: {newFilePath}")
            print(f"filePath: {filePath}")

          if not os.path.exists(filePath):
            found = True
            break

        if not found:
          print(f"Error: Impossible to create file: {filePath}, and save data\n")
          return False

        return filePath

      elif mode == LOAD:
        return True

    else:
      print(f"Error: Passed string isn't a file: {filePath}")
      print(f"Impossible to save/load data\n")
      return False

  elif mode == SAVE:
    return True
  else:
    print(f"Error: File doesn't exist: {filePath}, impossible to load data\n")
    return False

  return True

# Function for reading data from different file types
# based on the specified file type.
# It returns the imported data if successful
# or None if unsuccessful.
def readData(filePath=None):

  res = checkFile(mode=LOAD, filePath=filePath)
  if isinstance(res, bool) and not res:
    return None

  _, fExt = os.path.splitext(filePath)

  data = None
  if fExt == EXTENSIONS[Extension.csv]:
    print(f'CSV file reading')
    data = readCSV(filePath)

  elif fExt == EXTENSIONS[Extension.bvh]:
    print(f'BVH file reading')
    data = readBVH(filePath)

  elif fExt == EXTENSIONS[Extension.c3d]:
    print(f'C3D file reading')
    data = readC3D(filePath)

  else:
    print(f'Error: Invalid file extension: {fExt}\n')

  return data

# Function to read the CSV file at the specified location and returns
# the data as a list of lines.
# If the file exists, can be read, and contains any lines,
# the data list is returned.
# If the CSV file is empty or cannot be read, None is returned.
def readCSV(filePath):

  data = []
  try:

    with open(filePath, READ) as f:
      for line in csv.reader(f):
        data.append(line)

      if data is not None:
        data = extractDataCSV(data)
        # print('tipo: ', type(data))
        # print(len(data))

  except Exception as e:
    print(f'Error: Impossible to read CSV file - {e}\n')
    return None

  # if VERBOSE >= DEBUG:
  #   for line in data:
  #     print(f'{line}')

  return data if len(data) > 0 else None

# Function to reads data from a BVH (Biovision Hierarchy) file located
# at the given file path.
# It is a function wrapper around the read_bvh() function provided by
# an external library.
# The returned data are organized into a dictionary.
# This last is returned if the reading process is successful.
# If an error occurs during the reading process, None is returned.
def readBVH(filePath):

  data = {}
  try:

    animation, names, frameTime = read_bvh(file_name=filePath)

    data[ANIMATION] = animation
    data[NAMES] = names
    data[TIME] = frameTime

  except Exception as e:
    print(f'Error: Impossible to read BVH file - {e}\n')
    return None

  # for key, value in data.items():
  #     print("Key:", key)
  #     print("Type of Value:", type(value))

  return data

# Function to read data from a C3D (Coordinate 3D) file
# located at the given filePath.
# It returns the data dictionary if at least one frame
# was successfully read, otherwise it returns None.
#  If an error occurs during the process returns None.
def readC3D(filePath):

  data = None
  try:

    with open(filePath, READ_B) as f:
        dataReader = c3d.Reader(f)

        data = extractDataC3D(dataReader)

  except Exception as e:
    print(f'Error: {e}')
    return None

  return data
