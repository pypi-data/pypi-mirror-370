# --------------------------------------------------------------------------------------------------


import copy
from datetime import datetime

import jcb


# --------------------------------------------------------------------------------------------------

"""
Function mapping for variable strategy. If the channel values vary over the window because a
chronicle happens during that window you need a strategy to choose the value. For example, for the
variables that determine if a channel is used or not, min is likely a sensible strategy.
This will ensure the channel is completely off for that window and no bad data can make it in.
If the variable is error it may be better to choose max as the strategy to ensure the maximum
needed error is chosen over the window. If other functions are needed in the future they can be
added here. In the YAML the user defined the strategy as a string so this dictionary provides a
map to the actual functions.
"""

function_map = {
    'min': min,
    'max': max,
}


# --------------------------------------------------------------------------------------------------


def add_to_evolving_observing_system(evolving_observing_system, datetime, channel_values):

    """
    Add the channel values to the evolving observing system. This function is used to add the
    channel values to the evolving observing system. The evolving observing system is a list of
    dictionaries where each dictionary has a datetime key and a channel_values key. The datetime key
    is a datetime object and the channel_values key is a dictionary where the keys are the channel
    names and the values are lists of the channel values.

    Args:
        evolving_observing_system (list): The evolving observing system.
        datetime (datetime): The datetime of the channel values.
        channel_values (dict): The channel values.

    Returns:
        None (None): Mutable evolving_observing_system is updated in place.
    """

    # Temporary dictionary
    temp_dict = {}
    temp_dict['datetime'] = copy.deepcopy(datetime)
    temp_dict['channel_values'] = copy.deepcopy(channel_values)

    # Append to the evolving observing system
    evolving_observing_system.append(temp_dict)


# --------------------------------------------------------------------------------------------------


def get_left_index(error_message, action_dates, insert_point):

    """
    Get the index of the nearest action date that is before or equal to the insert point. This
    function finds the index of the nearest action date that is before or equal to the insert point.
    If the insert point is before the first action date then None is returned.

    Args:
        action_dates (list): A list of action dates.
        insert_point (datetime): The insert point.

    Returns:
        int: The index of the nearest action date that is before or equal to the insert point.
    """

    # Abort if the insert point is before the first action date
    jcb.abort_if(insert_point < action_dates[0],
                 f"{error_message} The insert point is before the first action date.")

    # Find the index of the nearest action date that is before or equal to the insert point
    for index, action_date in enumerate(action_dates):
        if action_date <= insert_point:
            index_of_previous = index
        else:
            break

    return index_of_previous


# --------------------------------------------------------------------------------------------------


def process_satellite_chronicles(satellite_id, window_begin, window_final, chronicle_in):

    """
    Processes satellite data chronicles for a specified time window, applying various adjustments
    to the channel values based on the satellite's chronicle actions.

    This function iterates through a satellite's chronological data records, adjusting channel
    variables and values as dictated by the chronicles. It validates the chronicle structure,
    ensures chronological order, and applies adjustments or reverts as specified. The final output
    is a set of channel values adjusted according to the specified window and strategies.

    Args:
        window_begin (datetime): The beginning of the data assimilation window.
        window_final (datetime): The end of the data assimilation window.
        chronicle (dict): A dictionary containing the satellite's commissioning data, channel
                          values, variables, and a list of chronological actions (chronicles) that
                          include  adjustments or reverts of variables and values.

    Returns:
        dict: A dictionary of channel values processed according to the specified time window and
              the strategies chosen for variable adjustments.

    Raises:
        AbortException: If any of the preconditions are not met, such as if the first variable in
                        `channel_variables` is not 'simulated', if chronicles are not in
                        chronological order, or if there are any mismatches in the number of
                        variables and values for each channel.

    Note:
        The function assumes that the channel values and variables are properly structured
        in the input `chronicle` dictionary.
    """

    # Copy the incoming chronicle to avoid modifying the original
    # -----------------------------------------------------------
    chronicle = copy.deepcopy(chronicle_in)

    # Create a message to prepend any errors with
    # -------------------------------------------
    errors_message_pre = f"Error processing satellite chronicle for satellite {satellite_id}:"

    # Commissioned time for this platform
    # -----------------------------------
    commissioned = jcb.datetime_from_conf(chronicle['commissioned'])

    # Check for decommissioned time
    # -----------------------------
    decommissioned = chronicle.get('decommissioned', None)
    if decommissioned:
        decommissioned = jcb.datetime_from_conf(decommissioned)

        # Abort if window_final is after decommissioned
        jcb.abort_if(window_begin >= decommissioned,
                     f"{errors_message_pre} The beginning of the window falls after the "
                     "decommissioned date. This chronicle should not be used after the "
                     "decommissioned date.")

    # Initial channel values
    # ----------------------
    channel_values = chronicle.get('channel_values')

    # Variables that are described in the chronicle
    # ---------------------------------------------
    channel_variables = list(chronicle.get('channel_variables').keys())
    num_variables = len(channel_variables)

    # Abort if the first variable is not simulated
    jcb.abort_if(channel_variables[0] != 'simulated',
                 f"{errors_message_pre} The first variable in the channel_variables must be "
                 "\'simulated\'. This variable is used in a specific way.")

    # Convert the list of channel_variables_strategies to actual function references
    channel_variables_func = [function_map[op] for op in chronicle['channel_variables'].values()]

    # For each channel (keys of channel_values) check values matches number of variables
    for channel, values in channel_values.items():
        jcb.abort_if(not len(values) == num_variables,
                     f"{errors_message_pre} The number of values for channel \'{channel}\' is "
                     f"{len(values)}, which does not match the number of variables "
                     f"{num_variables}.")

    # Dictionary to hold the observing system as it evolves through the chronicles
    # ----------------------------------------------------------------------------
    evolving_observing_system = []

    # Store chronicle at the initial commissioned date
    add_to_evolving_observing_system(evolving_observing_system, commissioned, channel_values)

    # Get chronicles list
    # -------------------
    chronicles = chronicle.get('chronicles', [])

    # Validation checks on the chronicles
    # -----------------------------------

    # Check chronicles for chronological order and that they are unique
    action_dates = [jcb.datetime_from_conf(chronicle['action_date']) for chronicle in chronicles]
    jcb.abort_if(action_dates != sorted(action_dates),
                 f"{errors_message_pre} The chronicles are not in chronological order.")
    jcb.abort_if(len(action_dates) != len(set(action_dates)),
                 f"{errors_message_pre} The chronicles are not unique. Ensure no two chronicles "
                 "have the same date.")

    # Prepend the action dates with the commissioned date
    action_dates = [commissioned] + action_dates

    # Loop through the chronicles and at each time there will be a complete set of channel_values
    # with the values specified by the chronicle.
    # -------------------------------------------------------------------------------------------
    for chronicle in chronicles:

        # Chronicle action date
        ch_action_date = jcb.datetime_from_conf(chronicle['action_date'])
        ch_action_date_iso = datetime.isoformat(ch_action_date)

        # Update the error message prefix with the action date
        errors_message_pre_ad = "Error processing satellite chronicle with action date " + \
                                f"{ch_action_date_iso} for satellite {satellite_id}:"

        # If chronicle has channel_values key then simply update those channels
        if 'channel_values' in chronicle:

            # Check that the number of values provided for each channel matched the variables
            for channel, values in chronicle['channel_values'].items():
                jcb.abort_if(not len(values) == num_variables,
                             f"{errors_message_pre_ad} The number of values for channel {channel} "
                             f"does not have correct number of variables ({num_variables}).")

            # Update the channel values with those in the chronicle
            for channel, values in chronicle['channel_values'].items():
                channel_values[channel] = values

        # If chronicle has key adjust_variable_for_all_channels then update those variables for all
        # channels
        if 'adjust_variable_for_all_channels' in chronicle:
            variables = chronicle['adjust_variable_for_all_channels']['variables']
            values = chronicle['adjust_variable_for_all_channels']['values']
            for variable, value in zip(variables, values):
                for channel in channel_values.keys():
                    channel_values[channel][channel_variables.index(variable)] = value

        # If the chronicle has key revert_to_previous_chronicle
        if 'revert_to_previous_date_time' in chronicle:
            previous_datetime = jcb.datetime_from_conf(chronicle['revert_to_previous_date_time'])

            # Find the nearest previous datetime in the action_dates list (without going over)
            index_of_previous = get_left_index(errors_message_pre_ad, action_dates,
                                               previous_datetime)

            # Update the channel values to the previous chronicle (using evolving observing system)
            channel_values = copy.deepcopy(
                evolving_observing_system[index_of_previous]['channel_values'])

        # Add the values after the action to the evolving observing system
        add_to_evolving_observing_system(evolving_observing_system, ch_action_date, channel_values)

    # Now that the entire chronicle has been processed we can return the values to be used for
    # the window. If the window beginning and ending are both between the same action dates then the
    # values will be set to the earlier values. If the window straddles and action date then the
    # values have to be determined using the min/max strategy that the user wishes and has chosen
    # in the variables.

    # Ensure window_begin and window_final are datetime objects
    window_begin = jcb.datetime_from_conf(window_begin)
    window_final = jcb.datetime_from_conf(window_final)

    # Sanity check on the expected input values
    # -----------------------------------------
    jcb.abort_if(window_begin < commissioned,
                 f"{errors_message_pre} The window begin is before the commissioned date.")
    jcb.abort_if(window_final < commissioned,
                 f"{errors_message_pre} The window begin is before the commissioned date.")

    # Abort if the window final is not after window begin
    jcb.abort_if(window_final <= window_begin,
                 f"{errors_message_pre} The window final must be after the window begin.")

    # Find the index of the nearest actions_date that is before or equal to window begin
    index_of_begin = get_left_index(errors_message_pre, action_dates, window_begin)

    # Find the index of the nearest actions_date that is before or equal to window end
    index_of_final = get_left_index(errors_message_pre, action_dates, window_final)

    # Extract actual values at times before window and begin and final
    channel_values_a = copy.deepcopy(evolving_observing_system[index_of_begin]['channel_values'])
    channel_values_b = copy.deepcopy(evolving_observing_system[index_of_final]['channel_values'])

    # Loop over channels
    for channel in channel_values_a.keys():

        # Index loop over variables
        for variable_index in range(num_variables):

            # Use strategy to determine value for the window
            channel_values_a[channel][variable_index] = \
                channel_variables_func[variable_index](channel_values_a[channel][variable_index],
                                                       channel_values_b[channel][variable_index])

    # Return the channel variables and values
    return channel_variables, channel_values_a


# --------------------------------------------------------------------------------------------------
