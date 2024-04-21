from global_constants import *
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

  _, fExt = os.path.splitext(filePath)

  data = None
  if fExt == EXTENSIONS[Extension.csv]:
    print(f'csv file start')
    data = readCSV(filePath)
    print(f'csv file end')
    
  elif fExt == EXTENSIONS[Extension.bhv]:
    print(f'bhv file start')
    data = readBHV(filePath)
    print(f'bhv file end')

  elif fExt == EXTENSIONS[Extension.c3d]:
    print(f'c3d file start')
    data = readC3D(filePath)
    print(f'c3d file end')

  else:
    print(f'Error: Invalid file extension: {fExt}\n')

  return data

# Function to load a CSV file at the specified path and returns
# the data as a list of lines.
# If the file exists, can be read, and contains any lines,
# the data list is returned.
# If the CSV file is empty or cannot be read, None is returned.
def readCSV(filePath):

  res = checkFile(mode=LOAD, filePath=filePath)
  if isinstance(res, bool) and not res:
    return None

  data = []
  with open(filePath, READ) as f:
    for line in csv.reader(f):
      data.append(line)

    # if VERBOSE >= DEBUG:
    #   for line in data:
    #     print(f'{line}')

  if len(data) > 0:
    return data
  else:
    return None

def readBHV(filePath):
  res = checkFile(mode=LOAD, filePath=filePath)
  if isinstance(res, bool) and not res:
    return None

    # if VERBOSE >= DEBUG:
    #   for line in data:
    #     print(f'{line}')

  return None

def readC3D(filePath):
  res = checkFile(mode=LOAD, filePath=filePath)
  if isinstance(res, bool) and not res:
    return None

    # if VERBOSE >= DEBUG:
    #   for line in data:
    #     print(f'{line}')

  return None