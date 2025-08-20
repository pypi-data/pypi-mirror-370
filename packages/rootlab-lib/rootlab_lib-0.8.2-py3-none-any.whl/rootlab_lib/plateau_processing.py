"""A backend file for data processing. This should only be used by the user for debugging purposes."""

from typing import List, Tuple
import numpy as np


def read_timed_voltage_data(filename: str) -> Tuple[List[float], List[float]]:
    """Reads time and voltage data from specified file

    Args:
        filename (str): A file with comma separated time and voltage data

    Returns:
        Tuple[List[float], List[float]]: (time_series, voltage_series)
    """
    time_series, voltage_series = [], []
    with open(filename, "r") as file:
        for line in file.readlines():
            line = line.strip("\n").split(",")
            time_series.append(float(line[0]))
            voltage_series.append(float(line[1]))
    return (time_series, voltage_series)


def multilayer_read_timed_voltage_data(
    filename: str,
) -> Tuple[
    Tuple[List[float], List[float]],
    Tuple[List[float], List[float]],
    Tuple[List[float], List[float]],
    Tuple[List[float], List[float]],
]:
    """Reads time and voltage data from specified file

    Args:
        filename (str): A file with comma separated voltage and time data

    Returns:
        Tuple[Tuple[List[float]]]: ((Vtop, Vbot), (vb1, vt1), (vb2, vt2), (t1, t2))
    """
    Vtop, Vbot = [], []
    vb1, vt1 = [], []
    vb2, vt2 = [], []
    t1, t2 = [], []
    with open(filename, "r") as file:
        for line in file.readlines():
            line = line.strip("\n").split(",")
            if line[4] == "B":
                Vbot.append(float(line[0]))
                vb1.append(float(line[1]))
                vb2.append(float(line[2]))
                t1.append(float(line[3]))
            if line[4] == "T":
                Vtop.append(float(line[0]))
                vt1.append(float(line[1]))
                vt2.append(float(line[2]))
                t2.append(float(line[3]))
    return ((Vtop, Vbot), (vb1, vt1), (vb2, vt2), (t1, t2))


def find_plateaus(
    voltage_data: List[float],
    threshold: float,
    min_plateau_length: float,
    min_gap_length: float,
) -> List[Tuple]:
    """Identifies the voltage plateaus in a given data set

    Args:
        voltage_data (List[float]): An array of voltage data
        threshold (float): The minimum voltage to be considered for a plateau
        min_plateau_length (float): The minimum length of a plateau to be logged
        min_gap_length (float): The minimum voltage drop to break a plateau

    Returns:
        List[Tuple]: A list containing information about each found plateau as (avg v, start i, end i)
    """
    # set the array to return and the initial values for plateau analysis
    plateaus = []
    plateau_start = None
    plateau_sum = plateau_length = 0

    # loop through the entire voltage data
    for i, voltage in enumerate(voltage_data):
        # check if the current voltage exceeds the set threshold
        if voltage > threshold:
            if plateau_start is None:
                plateau_start = i
            # increment the sum and length of the plateau
            plateau_sum += voltage
            plateau_length += 1
        # only enter if the voltage is too low and a plateau has been entered
        elif plateau_start is not None:
            # check if the plateau meets the minimum length set
            if plateau_length >= min_plateau_length:
                # calculate the avg value of the plateau and add it to the list
                plateau_avg = plateau_sum / plateau_length
                plateaus.append((plateau_avg, plateau_start, i - 1))
            # reset the values set for plateau analysis
            plateau_start = None
            plateau_sum = plateau_length = 0

        # check if the distance between current and prev point is sufficiently large
        big_enough = voltage < min_gap_length and voltage_data[i - 1] > min_gap_length
        if i > 0 and big_enough and plateau_start is not None:
            # check if the plateau meets the minimum length set
            if plateau_length >= min_plateau_length:
                # calculate the avg value of the plateau and add it to the list
                plateau_avg = plateau_sum / plateau_length
                plateaus.append((plateau_avg, plateau_start, i - 1))
            # reset the values set for plateau analysis
            plateau_start = None
            plateau_sum = plateau_length = 0

    return plateaus


def plateau_analysis(
    plateaus: List[Tuple],
    std_out: bool = False,
) -> Tuple[int, List[float]]:
    """Returns the number of plateaus and all of the average plateau values

    Args:
        plateaus (List[Tuple]): The plateau data with avg values in the first column
        std_out (bool): Determines whether or not to print the results

    Returns:
        Tuple[int, List[float]]: The results formatted as (number of plateaus, avg_values)
    """
    num_plateaus = len(plateaus)
    avg_values = [plateau[0] for plateau in plateaus]
    if std_out:
        print("Number of plateaus:", num_plateaus)
        print("Average values for each plateau:", avg_values)
    return (num_plateaus, avg_values)


def average_voltage_analysis(
    v_avg: List[float], V_to_check: str = "T"
) -> Tuple[np.ndarray]:
    """Calculates the average and std dev of the voltage values from the experiment

    Args:
        v_avg (List[float]): The average voltage data

    Raises:
        ValueError: If V_to_check is not T or B

    Returns:
        Tuple[np.ndarray]: Returns analysis output as (pos, V_avg_map, V_avg_column, V_std_column).
    """
    # check if the v to check is valid
    # Create an average map, column, and an std column for the data
    V_avg_map = np.zeros([5, 7], dtype=float)
    V_avg_column = np.zeros([7], dtype=float)
    V_std_column = np.zeros([7], dtype=float)

    # establish the arrays to use (predetermined)
    T_arr = [0.0, 0.5, 1.0, 1.5, 2, 2.5, 3]
    B_arr = [2.5, 2, 1.5, 1, 0.5]
    pos = np.array(T_arr if V_to_check == "T" else B_arr, dtype=float)

    # extract values from v_avg
    V_avg_map[:, 0], _ = v_avg[0], v_avg.pop(0)
    V_avg_map[:, -1], _ = v_avg[-1], v_avg.pop(-1)

    count = 0
    for i in range(5):
        for j in range(5):
            V_avg_map[
                i if V_to_check == "T" else j, j + 1 if V_to_check == "T" else i
            ] = v_avg[count]
            count += 1
    if V_to_check == "B":
        V_avg_map = np.rot90(V_avg_map)

    # Calculate mean and std values
    for i in range(7):
        if V_to_check == "T":
            V_avg_column[i] = np.mean(V_avg_map[:, i])
            V_std_column[i] = np.std(V_avg_map[:, i])
        elif V_to_check == "B":
            V_avg_column[i] = np.mean(V_avg_map[i, :])
            V_std_column[i] = np.std(V_avg_map[i, :])
    return (pos, V_avg_map, V_avg_column, V_std_column)
