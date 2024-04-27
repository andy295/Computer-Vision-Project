from global_constants import *
from utils import *

# Function for exporting and formatting data based on the given file path and data.
# It validates the input, determines the appropriate data extraction function
# based on the file extension, extracts the data, and returns it if successful,
# or None if there is an error.
def formatData(filePath=None, data=None):

    if data is None or filePath is None:
        print(f'Error: Invalid data or file path\n')
        return None

    _, fExt = os.path.splitext(filePath)
    if fExt == EXTENSIONS[Extension.csv]:
        data = extractDataCSV(data)
        
    elif fExt == EXTENSIONS[Extension.bvh]:
        # to read the data from a BVH file, we are using and external library
        # which reads and provides the data in a structured way
        # we can directly return the data
        return data

    elif fExt == EXTENSIONS[Extension.c3d]:
        data = extractDataC3D(data)

    else:
        print(f'Error: Invalid file extension: {fExt}\n')
        return None

    return data

# Function extracting and processing data from a pre-acquired CSV file.
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
                    middleKey += tmpStr

                else:
                    innerKey = row[CSV_HEADER_DATA_LEN-1] if row[CSV_HEADER_DATA_LEN-1] != '' else extractFirstLetters(row[CSV_HEADER_DATA_LEN-2])
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

        # for outerKey in sorted(dataDict.keys()):
        #     print(outerKey + ':')
        #     middleDict = dataDict[outerKey]
        #     for middleKey in sorted(middleDict.keys()):
        #         print('\t' + middleKey + ':')
        #         innerDict = middleDict[middleKey]
        #         for innerKey in sorted(innerDict.keys()):
        #             print('\t\t' + innerKey + ':', innerDict[innerKey])

    except Exception as e:
        print(f'Error: Impossible to extract data from CSV file - {e}\n')
        dataDict = None

    return dataDict

# todo add description
def extractDataC3D(data):
    return None
