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
