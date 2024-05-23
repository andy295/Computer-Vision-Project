import cv2
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from global_constants import *
from utils import *

# Function to extract and process data from a pre-acquired CSV file.
# It handles header extraction, version checking, time extraction, data processing,
# and error handling.
# Finally, it returns a dictionary containing the extracted data or None in case of errors.
def extractDataCSV(data):

    times = []
    dataDict = {HEADER: {HEADER_SHORT: {}}}

    # extract the header of the file and check if the version is compatible
    try:
        # the file is structured in a way that the even columns contain the 
        # description of the data, while the odd columns contain the data
        for row in data[:CSV_HEADER_FILE_LEN]:
            for i in range(0, len(row), 2):
                if row[i] != '':
                    key = row[i].replace(' ', SPACE_REPLACEMENT)
                    value = row[i + 1]

                    if (i+1) == CSV_VERSION_COLUMN and value != CSV_VERSION:
                        raise CustomException(f'Error: CSV file version {value} is not supported\n')

                    dataDict[HEADER][HEADER_SHORT][key] = value

        # remove the header of the file
        # we don't need it anymore
        for i in range(CSV_HEADER_DATA_ROW):
            del data[0]

        # save the information about the time
        # which will be common for all
        # in the csv file, the time is always the comlumn before the data
        # convert the string to float
        for row in data[CSV_HEADER_DATA_LEN:]:
            times.append(0 if row[CSV_DATA_COLUMN-1] == '' else float(row[CSV_DATA_COLUMN-1]))

        # transpose the data and remove the first two rows
        # we don't need them anymore
        data = list(zip(*data))
        for i in range(CSV_DATA_COLUMN):
            del data[0]

        # create a dictionary of dictionaries with the data
        # the first key is the combination of the first CSV_HEADER_DATA_LEN-1 elements
        # of the header; -1 because we want to use the last element of the header
        # as the key for the sub-dictionary
        for row in data:

            # CSV file can contain some data that we want to ignore
            # we can specify the type of data to ignore in the IGNORE_DATA list
            if row[TYPE] in IGNORE_DATA:
                continue

            outerKey = ''
            middleKey = ''
            innerKey = ''
            for i in range(CSV_HEADER_DATA_LEN):

                if i < CSV_HEADER_DATA_LEN-2:
                    tmpStr = row[i].replace(' ', SPACE_REPLACEMENT)
                    outerKey += tmpStr
                    outerKey = outerKey + KEY_SEPARATOR if i < CSV_HEADER_DATA_LEN-3 else outerKey

                elif i < CSV_HEADER_DATA_LEN-1:
                    tmpStr = row[i].replace(' ', SPACE_REPLACEMENT)
                    middleKey += tmpStr.lower()

                else:
                    innerKey = row[CSV_HEADER_DATA_LEN-1] if row[CSV_HEADER_DATA_LEN-1] != '' else extractFirstLetters(row[CSV_HEADER_DATA_LEN-2])
                    innerKey = innerKey.lower()
                    values = [float(x) if x != '' else float(0) for x in row[CSV_HEADER_DATA_LEN:]]

            if outerKey in dataDict:
                if middleKey in dataDict[outerKey]:
                    dataDict[outerKey][middleKey][innerKey] = values
                else:
                    dataDict[outerKey][middleKey] = {innerKey: values}
            else:
                dataDict[outerKey] = {middleKey: {innerKey: values}}

        # finally add to each middle dictionary the time
        for outerKey, middleDict in dataDict.items():
            if outerKey != HEADER:
                middleDict[TIME] = {TIME_SHORT: times}

        for outerKey in sorted(dataDict.keys()):
            print(outerKey + ':')
            middleDict = dataDict[outerKey]
            for middleKey in sorted(middleDict.keys()):
                print('\t' + middleKey + ':')
                innerDict = middleDict[middleKey]
                for innerKey in sorted(innerDict.keys()):
                    print('\t\t' + innerKey + ':')#, innerDict[innerKey][0:3])

    except Exception as e:
        print(f'Error: Impossible to extract data from CSV file - {e}\n')
        dataDict = None

    return dataDict

# Function to extract data from a C3D file using a provided dataReader
# capable of reading C3D files.
# It extracts point rate, scale factor, and frames data.
# If the extraction process is successful, it returns a dictionary containing the data.
# Otherwise, it returns None.
def extractDataC3D(dataReader):

    data = {C3D_POINT_RATE: 0, C3D_SCALE_FACTOR : 0, FRAME : {}}
    try:

        data[C3D_POINT_RATE] = dataReader.point_rate
        point_scale = abs(dataReader.point_scale)
        data[C3D_SCALE_FACTOR] = point_scale
        for i, points, analog in dataReader.read_frames():

            frameData = {}
            for (x, y, z, err_est, cam_nr), label in zip(points, 
                                        dataReader.point_labels):

                label = label.strip()
                frameData[label] = {
                    X : x * point_scale,
                    Y : y * point_scale,
                    Z : z * point_scale,
                    C3D_ERR_EST: err_est,
                    C3D_CAMERA_NR: cam_nr
                }

            data[FRAME][i] = frameData

    except Exception as e:
        print(f'Error: Impossible to extract data from C3D file - {e}')
        return None

    return data

# Function to prepare data by separating into training and test sets
def prepareData(df, column):

    # training data: drop rows where the target column is 0.0
    trainDF = df[df[column] != 0.0]
    XTrain = trainDF[TIME_SHORT].values.reshape(-1, 1)
    yTrain = trainDF[column].values

    # test data: rows where the target column is 0.0
    testDF = df[df[column] == 0.0]
    XTest = testDF[TIME_SHORT].values.reshape(-1, 1)

    return XTrain, yTrain, XTest, testDF.index

# Function to perform linear regression and predict missing values
def linearRegressionPredict(df, column):

    XTrain, yTrain, XTest, testIndex = prepareData(df, column)

    model = LinearRegression()
    model.fit(XTrain, yTrain)

    predictions = model.predict(XTest)

    # fill the missing values with predictions
    df.loc[testIndex, column] = predictions

# Function to compute the linear regression to estimate missing values
def linearRegression(sourceModel):

    model = sourceModel.deepcopy()

    # input data
    data = {
        TIME_SHORT: model._time,
        X: model._positions[X],
        Y: model._positions[Y],
        Z: model._positions[Z]
    }

    # convert to pandas DataFrame
    df = pd.DataFrame(data)

    # perform linear regression for each coordinate
    for coord in [X, Y, Z]:
        linearRegressionPredict(df, coord)

    # copy the data back to the model
    model._positions[X] = df[X]
    model._positions[Y] = df[Y]
    model._positions[Z] = df[Z]

    # plot the results
    plotData("Regression Line", sourceModel, model)

    return model

# Function to compute the Kalman filter to estimate missing values
def kalmanFilter(sourceModel):
    
    model = sourceModel.deepcopy()

    # input data
    data = {
        TIME_SHORT: model._time,
        X: model._positions[X],
        Y: model._positions[Y],
        Z: model._positions[Z]
    }

    # convert to pandas DataFrame
    df = pd.DataFrame(data)

    # time step, we are assuming it constant for simplicity
    dt = df[TIME_SHORT].diff().mean()
    dtTo2 = 0.5 * dt**2

    # instantiate and initialize the Kalman filter
    kalman = cv2.KalmanFilter(9, 3)
    kalman.measurementMatrix = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0]], np.float32)

    kalman.transitionMatrix = np.array([
        [1, 0, 0, dt, 0, 0, dtTo2, 0, 0],
        [0, 1, 0, 0, dt, 0, 0, dtTo2, 0],
        [0, 0, 1, 0, 0, dt, 0, 0, dtTo2],
        [0, 0, 0, 1, 0, 0, dt, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, dt, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, dt],
        [0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1]], np.float32)

    processNoiseStD = 0.1
    kalman.processNoiseCov = np.eye(9, dtype=np.float32) * processNoiseStD

    measurementNoiseStD = 0.001
    kalman.measurementNoiseCov = np.eye(3, dtype=np.float32) * measurementNoiseStD

    # prepare storage for estimated results
    estimatedCoords = np.zeros((len(df), 3), dtype=np.float32)

    for i, row in df.iterrows():
        if row[X] == 0.0 and row[Y] == 0.0 and row[Z] == 0.0:
            kalman.predict()
        else:
            measurement = np.array([row[X], row[Y], row[Z]], dtype=np.float32)
            kalman.predict()
            kalman.correct(measurement)

        estimatedCoords[i] = kalman.statePost[:3].flatten()

    # fill in the missing coordinates in the DataFrame
    df_estimated = df.copy()
    df_estimated[[X, Y, Z]] = estimatedCoords

    # copy the data back to the model
    model._positions[X] = df_estimated[X]
    model._positions[Y] = df_estimated[Y]
    model._positions[Z] = df_estimated[Z]

    # plot the results
    plotData("Kalman Filter", sourceModel, model)

    return model

def plotData(operation, first, second=None):

    # extract data
    X1 = np.array(first._positions[X])
    Y1 = np.array(first._positions[Y])
    Z1 = np.array(first._positions[Z])

    if second is not None:
        X2 = np.array(second._positions[X])
        Y2 = np.array(second._positions[Y])
        Z2 = np.array(second._positions[Z])

    # plot the results in 3D on two separate charts
    fig = plt.figure(figsize=(14, 6))

    # plot for original data
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax1.scatter(X1, Y1, Z1, c='r', label='Original Data')
    ax1.set_xlabel(X)
    ax1.set_ylabel(Y)
    ax1.set_zlabel(Z)
    ax1.set_title('Original Data')

    if second is not None:
        # plot for new data
        ax2 = fig.add_subplot(1, 2, 2, projection='3d')
        ax2.scatter(X2, Y2, Z2, c='b', label=f'{operation} Data')
        ax2.set_xlabel(X)
        ax2.set_ylabel(Y)
        ax2.set_zlabel(Z)
        ax2.set_title(f'{operation} Data')

    plt.tight_layout()
    plt.show()
