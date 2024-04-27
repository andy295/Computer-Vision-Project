from data_manipulation import *

# todo add description
class CSVModel:

    def __init__(self, data, header=None):

        self._description = {}

        self._time = [] # seconds
        self._rotations = {}
        self._positions = {}

        self.initialize(data, header)

    # It initializes the data object.
    def initialize(self, data, header=None):

        if header is not None:
            self.initializeDescription(header)

        outerKey, dataDict = data  # Unpack the tuple into key and value
        parts = outerKey.split(KEY_SEPARATOR)
        for i, part in enumerate(parts):

            if i == TYPE:
                self._description['Type'] = part.replace(SPACE_REPLACEMENT, ' ')
            elif i == NAME:
                self._description['Name'] = part.replace(SPACE_REPLACEMENT, ' ')
            elif i == ID:
                self._description['ID'] = part.replace(SPACE_REPLACEMENT, ' ')

        for middleKey, value in dataDict.items():

            if middleKey == TIME:
                self._time = value[TIME_SHORT]
            elif middleKey == ROTATION:
                self._rotations = value
            elif middleKey == POSITION:
                self._positions = value

    # It initializes the description of the experiment.
    def initializeDescription(self, data):

        self._description = dict(data[HEADER_SHORT])

    # It provides a convenient way to quickly view the relevant information
    # about the configuration of the model.
    def info(self):

        print(f"Model info:")

        for key, value in self._description.items():
            print(f"\t{key.replace(SPACE_REPLACEMENT, ' ')}: {value}")

        print(f"\n\tTime number of elements: {len(self._time)}")

        print(f"\n\tRotations number of elements: {len(self._rotations)}")
        for key, value in self._rotations.items():
            print(f"\t{key.replace(SPACE_REPLACEMENT, ' ')}: {len(value)}")

        print(f"\n\tPositions number of elements: {len(self._positions)}")
        for key, value in self._positions.items():
            print(f"\t{key.replace(SPACE_REPLACEMENT, ' ')}: {len(value)}")

# todo add description
class BVHModel:

    def __init__(self, data):

        self._animation = None
        self._names = None
        self._frameTime = None

        self.initialize(data)

    # It initializes the data object.
    def initialize(self, data):

        for key, value in data.items():

            if key == ANIMATION:
                self._animation = value
            elif key == NAMES:
                self._names = value
            elif key == TIME:
                self._frameTime = value

    # It provides a convenient way to quickly view the relevant information
    # about the configuration of the model.
    def info(self):

            print(f"Model info:")

            print(f"\n\tNames number of elements: {len(self._names)}")
            print(f"\n\tFrame time: {self._frameTime}")

# todo add description
class C3DModel:

    def __init__(self, data, header=None):

        self._description = {}

        self._time = [] # seconds
        self._rotations = {}
        self._positions = {}

# todo add description
def createModels(filePath=None, data=None):

    if data is None or filePath is None:
        print(f'Error: Invalid data or file path\n')
        return None

    models = []

    _, fExt = os.path.splitext(filePath)
    if fExt == EXTENSIONS[Extension.csv]:

        for item in data.items():
            key, value = item  # Unpack the tuple into key and value
            if key != HEADER:
                model = CSVModel(item, header=data[HEADER])
                models.append(model)

    elif fExt == EXTENSIONS[Extension.bvh]:
        model = BVHModel(data)
        models.append(model)

    elif fExt == EXTENSIONS[Extension.c3d]:
        data = extractDataC3D(data)

    else:
        print(f'Error: Invalid file extension: {fExt}\n')
        return None

    return models if len(models) > 0 else None
