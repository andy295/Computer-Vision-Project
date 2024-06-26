# Class used only to rise and handle user-defined exceptions
class CustomException(Exception):
    pass

# Function to check if a given string is empty or consists only of
# whitespace characters.
def emptyString(string):
  if string != None and not isinstance(string, str):
    print(f'provided input is not a string')
    return True

  if not (string and string.strip()):
    return True

  return False

# Function that splits the input string into words using split()
# then iterates over each word, extracting the first character of each wordusing
# finally, it joins these first letters together into a single string.
def extractFirstLetters(string):
    # Split the string into words
    words = string.split()

    # Extract the first letter of each word
    first_letters = [word[0] for word in words]

    # Join the first letters into a single string
    result = ''.join(first_letters)

    return result

# Function to safely convert user input to an integer
def getIntegerInput(text):
    while True:
        value = input(text)
        try:
            # Attempt to convert the input to an integer
            value = int(value)
            return value
        except ValueError:
            # If conversion fails, inform the user and prompt again
            print('Invalid input. Please enter a valid integer.\n')
