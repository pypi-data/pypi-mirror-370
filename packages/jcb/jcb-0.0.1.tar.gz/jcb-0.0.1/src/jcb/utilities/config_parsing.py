# --------------------------------------------------------------------------------------------------


from datetime import datetime, timedelta
import re

import jcb


# --------------------------------------------------------------------------------------------------


def datetime_from_conf(datetime_input):

    """
    Convert a datetime string in the format to a datetime object. The string can have any number of
    non-numeric characters in it. The function will strip all non-numeric characters and then pad
    with zeros if the string is less than 14 characters long. The string must be at least 8
    characters long to be a valid datetime string.

    Args:
        datetime_input (str or datetime object): The datetime string to convert.

    Returns:
        datetime: The datetime object.
    """

    # If the input is already a datetime object then return it
    if isinstance(datetime_input, datetime):
        return datetime_input

    # If not a string then abort
    jcb.abort_if(not isinstance(datetime_input, str),
                 f"The datetime \'{datetime_input}\' is not a string.")

    # A string that is less 8 characters long is not valid
    jcb.abort_if(len(datetime_input) < 8,
                 f"The datetime \'{datetime_input}\' must be at least 8 character (the length of "
                 "a date).")

    # Strip and non-numeric characters from the string and make at least 14 characters long
    datetime_string = re.sub('[^0-9]', '', datetime_input+'000000')[0:14]

    # Convert to datetime object
    return datetime.strptime(datetime_string, "%Y%m%d%H%M%S")


# --------------------------------------------------------------------------------------------------


def check_duration_ordered(iso_duration):

    """
    Check if iso_duration characters is in correct order. The function will return True if the \
    characters in the iso_duration are in the correct order. The function is case sensitive.

    Args:
        iso_duration (str): The iso_duration characters to check.

    Returns:
        bool: True if the iso_duration is in correct order, False otherwise.
    """

    # Reference string for the correct order of the characters
    reference = "PYMWDTHMS"

    # Strip non alpha characters from the string
    iso_duration_letters = re.sub('[^a-zA-Z]', '', iso_duration)

    # Check that letters in the ios duration string are in the correct order
    search_start = 0
    for char in iso_duration_letters:
        # Try to find the current character in the reference string, starting from search_start
        found_pos = reference.find(char, search_start)
        if found_pos == -1:
            # Character not found in the reference string, order is not preserved
            return False
        else:
            # Move search_start to the position after the found character
            search_start = found_pos + 1
    # All characters found in order, return True
    return True


# --------------------------------------------------------------------------------------------------


def duration_from_conf(iso_duration_input):

    """
    Convert an ISO 8601 duration string to a timedelta object. The string must be at least 2
    characters long to be a valid duration string.

    Args:
        iso_duration_input (str or timedelta object): The ISO duration string to convert.

    Returns:
        timedelta: The timedelta object.
    """

    # If the input is already a timedelta object then return it
    if isinstance(iso_duration_input, timedelta):
        return iso_duration_input

    # If not a string then abort
    jcb.abort_if(not isinstance(iso_duration_input, str),
                 f"The ISO duration \'{iso_duration_input}\' is not a string.")

    # Strip non alpha characters from the string
    jcb.abort_if(len(iso_duration_input) < 2,
                 f"The ISO duration \'{iso_duration_input}\' must be at least 2 characters long.")

    # Format is P[n]Y[n]M[n]W[n]DT[n]H[n]M[n]S. Use regex to extract the values
    pattern = r'P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    pattern_compile = re.compile(pattern)
    years, months, weeks, days, hours, minutes, seconds = \
        pattern_compile.match(iso_duration_input).groups()

    # Assert that years and months are None
    jcb.abort_if(years is not None or months is not None,
                 f"The ISO duration \'{iso_duration_input}\' must not have years or months. This "
                 "is not supported by the timedelta class in the Python standard.")

    # Create the timedelta object
    return timedelta(weeks=int(weeks or 0),
                     days=int(days or 0),
                     hours=int(hours or 0),
                     minutes=int(minutes or 0),
                     seconds=int(seconds or 0))


# --------------------------------------------------------------------------------------------------
