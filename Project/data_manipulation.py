import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev, CubicSpline
from sklearn.linear_model import LinearRegression

from global_constants import *

def filterData(filePath, data):

    if data is None or filePath is None:
        print(f'Error: Invalid data or file path\n')
        return None

    fName = os.path.basename(filePath)
    fName, fExt = os.path.splitext(fName)

    # only data extracted from rigidbody.csv file can be filtered
    if fExt == EXTENSIONS[Extension.csv] and fName == RIGID_BODY:
        splineInterpolation(data)
        for model in data:
            print(f'Filtering data for model: {model.getName()}')
            linearRegression(model)
            kalmanFilter(model)
            print(f'Data correctly filtered\n')


# Function to prepare data by separating into training and test sets
def linearRegressionPrepareData(df, column):

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

    XTrain, yTrain, XTest, testIndex = linearRegressionPrepareData(df, column)

    model = LinearRegression()
    model.fit(XTrain, yTrain)

    predictions = model.predict(XTest)

    # fill the missing values with predictions
    df.loc[testIndex, column] = predictions

# Function to compute the linear regression to estimate missing values
def linearRegression(sourceModel):

    # input data
    data = {
        TIME_SHORT: sourceModel.time,
        X: sourceModel.positions[X],
        Y: sourceModel.positions[Y],
        Z: sourceModel.positions[Z]
    }

    # convert to pandas DataFrame
    df = pd.DataFrame(data)

    # perform linear regression for each coordinate
    for coord in [X, Y, Z]:
        linearRegressionPredict(df, coord)

    # copy the data back to the original model
    sourceModel.rlPositions[X] = df[X].to_list()
    sourceModel.rlPositions[Y] = df[Y].to_list()
    sourceModel.rlPositions[Z] = df[Z].to_list()

    if PLOT_CHART:
        # plot the results
        plotData("Regression Line", sourceModel.positions, sourceModel.rlPositions)

def initKalmanFilter(dt=5, vel=1, acc=1, processNoiseStD=0.1, measurementNoiseStD=0.001):
    # time step, we are assuming it constant for simplicity
    dtTo2 = 0.5 * dt**2

    # instantiate and initialize the Kalman filter
    kalman = cv2.KalmanFilter(9, 3)
    kalman.measurementMatrix = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0]], np.float32)

    kalman.transitionMatrix = np.array([
        [1, 0, 0, vel*dt, 0, 0, acc*dtTo2, 0, 0],
        [0, 1, 0, 0, vel*dt, 0, 0, acc*dtTo2, 0],
        [0, 0, 1, 0, 0, vel*dt, 0, 0, acc*dtTo2],
        [0, 0, 0, 1, 0, 0, vel*dt, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, vel*dt, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, vel*dt],
        [0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1]], np.float32)

    kalman.processNoiseCov = np.eye(9, dtype=np.float32) * processNoiseStD

    kalman.measurementNoiseCov = np.eye(3, dtype=np.float32) * measurementNoiseStD

    return kalman

# Function to compute the Kalman filter to estimate missing values
def kalmanFilter(sourceModel):

    # input data
    data = {
        TIME_SHORT: sourceModel.time,
        X: sourceModel.positions[X],
        Y: sourceModel.positions[Y],
        Z: sourceModel.positions[Z]
    }

    # convert to pandas DataFrame
    df = pd.DataFrame(data)

    # time step, we are assuming it constant for simplicity
    dt = df[TIME_SHORT].diff().mean()
    kalman = initKalmanFilter(dt)

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

    # copy the data back to the original model
    sourceModel.kfPositions[X] = df_estimated[X].to_list()
    sourceModel.kfPositions[Y] = df_estimated[Y].to_list()
    sourceModel.kfPositions[Z] = df_estimated[Z].to_list()

    if PLOT_CHART:
        # plot the results
        plotData("Kalman Filter", sourceModel.positions, sourceModel.kfPositions)

# data is a list of model, i.e. a list of markers
def splineInterpolation(data):

    markerList = []
    # obtaining a list of list of positions in time
    for model in data:
        tempList = list(zip(model.positions[X], model.positions[Y], model.positions[Z]))
        markerList.append(tempList)
    markerList = np.array(markerList)
    
    # Number of markers
    num_markers, _, _ = markerList.shape

    # Identify time entries with missing values
    missing_indices = np.where((markerList == (0, 0, 0)).all(axis=0).all(axis=1))[0]
    available_indices = np.where(~(markerList == (0, 0, 0)).all(axis=0).all(axis=1))[0]
    
    # Function to interpolate and fill missing values for each marker
    def interpolate_and_fill(markerList, missing_indices, available_indices):
        filledMarkerList = np.copy(markerList)
        t = available_indices  # Time points for available data
        
        for marker in range(num_markers):
            for i in range(3):  # For x, y, z
                values = markerList[marker, available_indices, i]
                cs = CubicSpline(t, values)
                filled_values = cs(missing_indices)
                filledMarkerList[marker, missing_indices, i] = filled_values
                
        return filledMarkerList
    
    # Fill the missing data
    filledMarkerList = interpolate_and_fill(markerList, missing_indices, available_indices)
    for i, model in enumerate(data):
            xList, yList, zList = zip(*filledMarkerList[i])
            model.splPositions[X] = xList
            model.splPositions[Y] = yList
            model.splPositions[Z] = zList
            
    if PLOT_CHART:   
        # plot the results for each marker
        for i, model in enumerate(data):
            plotData("Spline interpolation for marker %d" % i, model.positions, model.splPositions)


def plotData(operation, firstDataPoints, secondDataPoints=None):

    # extract data
    X1 = np.array(firstDataPoints[X])
    Y1 = np.array(firstDataPoints[Y])
    Z1 = np.array(firstDataPoints[Z])

    if secondDataPoints is not None:
        X2 = np.array(secondDataPoints[X])
        Y2 = np.array(secondDataPoints[Y])
        Z2 = np.array(secondDataPoints[Z])

    # plot the results in 3D on two separate charts
    fig = plt.figure(figsize=(14, 6))

    # plot for original data
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    ax1.scatter(X1, Y1, Z1, c='r', label='Original Data')
    ax1.set_xlabel(X)
    ax1.set_ylabel(Y)
    ax1.set_zlabel(Z)
    ax1.set_title('Original Data')

    if secondDataPoints is not None:
        # plot for new data
        ax2 = fig.add_subplot(1, 2, 2, projection='3d')
        ax2.scatter(X2, Y2, Z2, c='b', label=f'{operation} Data')
        ax2.set_xlabel(X)
        ax2.set_ylabel(Y)
        ax2.set_zlabel(Z)
        ax2.set_title(f'{operation} Data')

    plt.tight_layout()
    plt.show()
