import cv2
import string
import pandas as pd
import matplotlib.pyplot as plt
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

        option = 1
        while True:
            text = f'Models that can be filtered:\n'
            text += f'0. Exit\n'
            text += f'1. All\n'
            for idx, model in enumerate(data):
                text += f'{idx+2}. {model.getName()}\n'

            text += f'Please select the model to filter:'
            option = getIntegerInput(text)        
            if option == 0:
                # exit the loop and end the program
                break

            elif option == 1:

                for model in data:
                    print(f'Filtering data for model: {model.getName()}')
                    linearRegression(model)
                    kalmanFilter(model)
                    print(f'Data correctly filtered\n')

                break

            elif option > 1 and option < len(data) + 2:

                for idx, model in enumerate(data):
                    if option == idx + 2:
                        print(f'Filtering data for model: {model.getName()}')
                        linearRegression(model)
                        kalmanFilter(model)
                        print(f'Data correctly filtered\n')

                exit = f'Would you like to filter another model?\n'
                exit += f'0 to No\n'
                exit += f'Any integer to Yes\n'
                exit += f'Make your choice: '
                exit = getIntegerInput(exit)
                if exit == 0:
                    # exit the loop and end the program
                    break
            else:
                print(f'Invalid input, try again.')

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

    model = sourceModel.deepcopy()

    # input data
    data = {
        TIME_SHORT: model.time,
        X: model.positions[X],
        Y: model.positions[Y],
        Z: model.positions[Z]
    }

    # convert to pandas DataFrame
    df = pd.DataFrame(data)

    # perform linear regression for each coordinate
    for coord in [X, Y, Z]:
        linearRegressionPredict(df, coord)

    # copy the data back to the model
    model.rlPositions[X] = df[X]
    model.rlPositions[Y] = df[Y]
    model.rlPositions[Z] = df[Z]

    # plot the results
    plotData("Regression Line", sourceModel.positions, model.rlPositions)

# Function to compute the Kalman filter to estimate missing values
def kalmanFilter(sourceModel):
    
    model = sourceModel.deepcopy()

    # input data
    data = {
        TIME_SHORT: model.time,
        X: model.positions[X],
        Y: model.positions[Y],
        Z: model.positions[Z]
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
    model.kfPositions[X] = df_estimated[X]
    model.kfPositions[Y] = df_estimated[Y]
    model.kfPositions[Z] = df_estimated[Z]

    # plot the results
    plotData("Kalman Filter", sourceModel.positions, model.kfPositions)

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
