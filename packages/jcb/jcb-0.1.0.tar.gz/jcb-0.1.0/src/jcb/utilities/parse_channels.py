# --------------------------------------------------------------------------------------------------


def parse_channels(channels):

    """Parses a string containing numbers and ranges into a list of integers.

    This function takes a string input that can contain individual numbers and/or ranges of numbers
    separated by commas. For each part of the string, it determines whether the part is a single
    number or a range. Ranges are indicated by a  dash ('-') between two numbers and are inclusive
    of both end numbers. The function returns a list of integers including all the individual
    numbers and the numbers within any ranges specified.

    Args:
        channels (str): A string containing numbers and/or ranges of numbers. Individual
        numbers are represented as is, and ranges are represented by two numbers separated by a
        dash ('-'), inclusive of both numbers. The parts of the string (individual numbers or
        ranges) are separated by commas.

    Returns:
        list of int: A list of integers parsed from the input string. This includes all the
        individual numbers and all the numbers within the specified ranges in the input string.

    Examples:
        >>> parse_channels("1,2,5-7")
        [1, 2, 5, 6, 7]

        >>> parse_channels("3-5,7,9-11")
        [3, 4, 5, 7, 9, 10, 11]

        >>> parse_channels("10")
        [10]
    """

    # If the incoming channels is a list, process it and return it.
    if isinstance(channels, list):

        # If anything in the list contains strings covert them to integers
        for i, channel in enumerate(channels):
            if isinstance(channel, str):
                channels[i] = int(channel)

        return channels

    # If the incoming channels is a single integer, process it and return it.
    if isinstance(channels, int):
        return [channels]

    # If the incoming channels is empty string return empty list
    if channels == '':
        return []

    # Split the input string by commas
    parts = channels.split(',')
    result_list = []

    for part in parts:
        # Check if the part is a range
        if '-' in part:
            start, end = map(int, part.split('-'))
            # Use range to generate numbers in the range, inclusive of the end
            result_list.extend(range(start, end + 1))
        else:
            # Convert the part to an integer and add to the result list
            result_list.append(int(part))

    return result_list


# --------------------------------------------------------------------------------------------------


def parse_channels_set(channels):

    return set(parse_channels(channels))


# --------------------------------------------------------------------------------------------------
