from I_O import *
from models import *
from plotter import *

# The Experiment class represents an experiment with datasets and models.
# It provides functionality to initialize and manage an experiment.

# Class attributes:
# todo add description

class Experiment():

  def __init__(self, operation=NEW, inFile='', outPath='',
               saveData=False, savePath='', verbose=INFO):

    self._status = False
    self._operation = operation

    self._inFile = inFile
    self._outPath = outPath

    self._saveData = saveData
    self._savePath = savePath

    self._verbose = verbose

    self._description = {}

    self._models = []

    self.initialize()

  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, s):
    print(f'Error: Invalid operation, experiment status cannot be manually modified\n')

  @property
  def operation(self):
    return self._operation

  @operation.setter
  def operation(self, o):
    print(f'Error: Invalid operation, experiment operation cannot be manually modified\n')

  @property
  def inFile(self):
    return self._inFile

  @inFile.setter
  def inFile(self, file):
    print(f'Error: Invalid operation, experiment input file cannot be manually modified\n')

  @property
  def outPath(self):
    return self._outPath

  @outPath.setter
  def outPath(self, path):
    print(f'Error: Invalid operation, experiment output directory cannot be manually modified\n')

  @property
  def verbose(self):
    return self._outPath

  @verbose.setter
  def verbose(self, val):
    print(f'Error: Invalid operation, experiment verbose mode cannot be manually modified\n')

  @property
  def description(self):
    return self._description

  @description.setter
  def description(self):
    print(f'Error: Invalid operation, experiment description cannot be manually modified\n')

  @property
  def models(self):
    return self._models

  @models.setter
  def models(self):
    print(f'Error: Invalid operation, experiment models cannot be manually modified\n')

  @property
  def saveData(self):
    return self._saveData

  @saveData.setter
  def saveData(self, save):
    if save != self._saveData:
      self._saveData = save

    return self._saveData

  @property
  def savePath(self):
    return self._savePath

  @savePath.setter
  def savePath(self, path):
    if emptyString(path):
      print(f'Error: Given save directory is invalid: {path}\n')
      return False
    else:
      self._savePath = path

    return True

  def abort(self):
    self.__erase()
    print(f'Experiment aborted')

  # It initializes the experiment and performs necessary operations
  # based on the specified parameters.
  def initialize(self):

    print(f'Initializing the experiment\n')
    if self.checkData():
        self._status = True

    if self._status:
      print(f'Experiment correctly initialized\n')
    else:
      self.abort()

  # It initializes the description of the experiment.
  def initializeDescription(self, data):

    self._description = dict(data[HEADER][HEADER_SHORT])

  # It verifies various aspects of the input data:
  #   - input file
  #   - output path
  #   - save path
  # to ensure that they are valid and exist.
  def checkData(self):
    if emptyString(self._inFile):
      print(f'Error: Invalid or empty input file: {self._inFile}\n')
      return False

    if not os.path.isfile(self._inFile):
      print(f'Error: Invalid input file: {self._inFile}\n')
      return False

    fName, fExt = os.path.splitext(self._inFile)
    fExt = fExt.lower()
    if fExt not in INPUT_EXTENSIONS:
      print(f'Error: Invalid input file extension: {fExt}\n')
      return False    

    if not emptyString(self._outPath):
      if not os.path.isdir(self._outPath):
        print(f'Error: Invalid output path: {self._outPath}\n')
        return False
    else:
      # it can be made dependent on the type of the operation
      if self._verbose >= INFO:
        print(f'Info: Output path empty\n')

    if self._saveData:
      if not emptyString(self._savePath):
        if not os.path.isdir(self._savePath):
          print(f'Error: Invalid save path: {self._savePath}\n')
          return False
      else:
        print(f'Error: Invalid or empty save path:{self._savePath} \n')
        return False

    return True

  # It resets all the attributes of the Experiment class,
  # clearing any previous state and preparing it for a new experiment.
  def __erase(self):

    self._status = False
    self._operation = NEW

    self._inFile = ''
    self._outPath = ''

    self._saveData = False
    self._savePath = ''

    self._verbose = INFO

    self._description = {}

    self._models = []

  # It is responsible for importing data from a specified input file.
  def importData(self):

    fName = os.path.basename(self._inFile)
    print(f'Importing data data from {fName} file\n')

    data = readData(self._inFile)

    if data is not None:
      print(f'Data correctly imported\n')
    else:
      print(f'Error: Something wrong reading the data\n')

    return data

  # It is responsible for formatting data and creating models.
  # It involves some preprocessing of the data.
  def prepareData(self, data):

    print(f'Preparing data\n')

    self._models = createModels(self._inFile, data)

    print(f'Model(s) correctly prepared\n')

  def plotData(self, models=None):

    print(f'Plotting data\n')

    if models is None:
      plotModels(self._inFile, self._models)
    else:  
      plotModels(self._inFile, models)

  # It ensures the sequential execution of the experiment steps and provides
  # a convenient way to run the entire experiment with a single method call.
  def run(self):
    if self._operation == NEW:
      data = self.importData()

      if data is not None:
        self.prepareData(data)

        if len(self._models) > 0:
          # for model in self._models:
          #   modelsList = []
          #   modelsList.append(model)

          #   newModel = linearRegression(model)
          #   modelsList.append(newModel)

          #   self.plotData(modelsList)

          self.plotData()

          return True

      return True

    if data is None:
      self.abort()

    return False

  # It provides a convenient way to quickly view the relevant information about
  # the experiment configuration and current state.
  def info(self):
    print(f"Experiment info:")
    print(f"\tStatus: {self._status}")
    print(f"\tOperation: {self._operation}")
    print(f"\tInput file: {self._inFile}")
    print(f"\tOutput directory path: {self._outPath}")
    print(f"\tSave experiment: {'True' if self._saveData else 'False'}")
    print(f"\tSave directory path: {self._savePath}")
    print(f"\tVerbose level: {self._verbose}\n")

    for key, value in self._description.items():
      print(f"\t{key.replace(SPACE_REPLACEMENT, ' ')}: {value}")

    for model in self._models:
      print()
      model.info()
