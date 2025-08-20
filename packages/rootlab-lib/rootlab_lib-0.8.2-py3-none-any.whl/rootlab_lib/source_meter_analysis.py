"""The main way to interact with data outputted by the source meter in lab."""

import pandas as pd
from typing import Tuple, List
import time as t
import os
import csv
import matplotlib.pyplot as plt
from itertools import cycle


def voltage_readings_to_resistance_series(
    input_filepath: str,
    output_dir: str = "./converted",
) -> str:
    """Converts the voltage data in a file to resistance series data and writes it out to a file of a similar name.

    Args:
        input_filepath (str): The filepath of the original file with the
        output_dir (str, optional): The directory to store the output file. Defaults to "."

    Returns:
        str: The filepath of the output file
    """
    if not os.path.isfile(input_filepath):
        raise FileNotFoundError(f"Input file not found: {input_filepath}")

    # Set output directory to input's dir if not provided
    os.makedirs(output_dir, exist_ok=True)

    # Parse CSV and isolate voltage + time data
    two_col_rows = []
    rest_rows = []
    switch_found = False

    with open(input_filepath, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not switch_found and len(row) == 2:
                two_col_rows.append(row)
            else:
                switch_found = True
                rest_rows.append(row)

    headers = rest_rows[0]
    df = pd.DataFrame(rest_rows[1:], columns=headers)

    voltage_col = "Reading"
    amperage_col = "Value"
    time_col = "Relative Time"

    df[voltage_col] = pd.to_numeric(df[voltage_col], errors="coerce")
    df[amperage_col] = pd.to_numeric(df[amperage_col], errors="coerce")
    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
    df.dropna(subset=[voltage_col, amperage_col, time_col], inplace=True)

    df["Resistance"] = df[voltage_col] / df[amperage_col]

    # Create output .txt file with format time,resistance
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    base = os.path.basename(input_filepath).rsplit(".", 1)[0]
    output_filename = f"{curr_date}_{base}_resistance_{curr_time}.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w") as out:
        for _, row in df.iterrows():
            out.write(f"{row[time_col]},{row['Resistance']}\n")

    return output_path


def extract_readings_to_resistance_series(
    input_filepath: str,
    output_dir: str | None,
) -> str:
    """Extracts data in a file to resistance series data and writes it out to a file of a similar name.

    Args:
        input_filepath (str): The filepath of the original file with the
        output_dir (str | None): The directory to store the output file. If this is None, then the directory of the input is preserved

    Returns:
        str: The filepath of the output file
    """
    if not os.path.isfile(input_filepath):
        raise FileNotFoundError(f"Input file not found: {input_filepath}")

    # Set output directory to input's dir if not provided
    if output_dir is None:
        output_dir = os.path.dirname(input_filepath)
    os.makedirs(output_dir, exist_ok=True)

    # Parse CSV and isolate voltage + time data
    two_col_rows = []
    rest_rows = []
    switch_found = False

    with open(input_filepath, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not switch_found and len(row) == 2:
                two_col_rows.append(row)
            else:
                switch_found = True
                rest_rows.append(row)

    headers = rest_rows[0]
    df = pd.DataFrame(rest_rows[1:], columns=headers)

    resistance_col = "Reading"
    time_col = "Relative Time"

    df[resistance_col] = pd.to_numeric(df[resistance_col], errors="coerce")
    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
    df.dropna(subset=[resistance_col, time_col], inplace=True)

    df["Resistance"] = df[resistance_col]

    # Create output .txt file with format time,resistance
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    base = os.path.basename(input_filepath).rsplit(".", 1)[0]
    output_filename = f"{curr_date}_{base}_resistance_{curr_time}.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w") as out:
        for _, row in df.iterrows():
            out.write(f"{row[time_col]},{row['Resistance']}\n")

    return output_path


def _read_time_resistance_data(filepath: str) -> Tuple[List[float], List[float]]:
    """Extracts time and resistance data from a text file formatted as 'time,resistance' on each line.

    Args:
        filepath (str): Path to the formatted data file

    Returns:
        Tuple[List[float], List[float]]: Lists of time values and resistance values
    """
    time_vals = []
    resistance_vals = []

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    with open(filepath, "r") as f:
        for line in f:
            try:
                t_str, r_str = line.strip().split(",")
                time_vals.append(float(t_str))
                resistance_vals.append(float(r_str))
            except ValueError:
                continue  # skip malformed lines

    return time_vals, resistance_vals


def analyze(
    input_filepath: str,
    output_name: str,
    output_dir: str = "./data/SourceMeter",
    output_image_ext: str = "png",
    title: str = "Source Meter Readings",
    readings_unit: str = "Ohms",
    time_unit: str = "s",
    write_out: bool = False,
    log_scale_x: bool = False,
    log_scale_y: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    tick_param_font_size: int = 15,
    legend: bool = False,
    legend_loc: str = "upper right",
    line_label: str = "Resistance",
    line_color: str = "black",
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
) -> Tuple[List[float], List[float], str]:
    """
    Writes and plots source meter resistance readings vs time and saves a .png of the data. Expects the data to be formatted with lines of (time, resistance)

    Args:
        input_filepath (str): The name of the input file with the data to be read. This should be a txt file.
        output_name (str): Descriptive name used in output filename. The current date and time will be combined with this. Do not include the extension or path
        output_dir (str, optional): The path to be used for the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): The image extension to be used for the output image. You need not include the period. Defaults to 'png'
        title (str, optional): The title of the plot. Defaults to 'Source Meter Readings'
        readings_unit (str, optional): The unit of the readings outputted. Defaults to 'Ohms'
        time_unit (str, optional): The unit of the time values reported. Defaults to seconds
        write_out (bool, optional): Determines whether or not to write the (time, resistance) data out to a file. Defaults to false
        log_scale_x (bool, optional): If True, uses logarithmic scale for x-axis. Defaults to False
        log_scale_y (bool, optional): If True, uses logarithmic scale for y-axis. Defaults to False
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the plot legend, if enabled. Defaults to 20.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to False.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        line_label (str, optional): The label to use for the plotted line. Defaults to 'Resistance'.
        line_color (str, optional): The color to use for the plotted line. Defaults to 'black'.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
    Returns:
        Tuple(List[float], List[float], str): (time_series, resistance_series, data_filepath_out) where data_filepath_out is a txt file of [time, data]
    """
    if not os.path.isfile(input_filepath):
        print("Error: Input filepath is not a valid file")
        return

    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)

    output_data = f"{curr_date}_{output_name}_{curr_time}.txt"
    output_data_path = os.path.join(output_dir, output_data)

    try:
        time_series, resistance_series = _read_time_resistance_data(input_filepath)

        if len(time_series) != len(resistance_series):
            raise ValueError("Time and resistance series are not the same length.")

        if write_out:
            with open(output_data_path, "w") as f:
                for i in range(len(time_series)):
                    f.write(f"{time_series[i]},{resistance_series[i]}\n")
            print(f"Saving {os.path.abspath(output_data_path)}")

        plt.figure(figsize=figsize)
        plt.plot(time_series, resistance_series, label=line_label, color=line_color)
        plt.title(title, fontsize=title_font_size)
        plt.xlabel(f"Time ({time_unit})", fontsize=axis_font_size)
        plt.ylabel(f"Readings ({readings_unit})", fontsize=axis_font_size)
        plt.tick_params(labelsize=tick_param_font_size)
        if legend:
            plt.legend(fontsize=legend_font_size, loc=legend_loc)
        if grid:
            plt.grid(True)

        if log_scale_x:
            plt.xscale("log")
        if log_scale_y:
            plt.yscale("log")

        plt.tight_layout()
        plt.savefig(output_img_path)
        print(f"Saving {os.path.abspath(output_img_path)}")
        print(f"\tCurrent File: {os.path.basename(output_img_path)}")
        plt.show()

        return (time_series, resistance_series, output_data_path)

    except Exception as e:
        print(f"Fatal error analyzing data: {e}")
        return


def analyze_concat(
    input_filepaths: List[str],
    output_name: str,
    output_dir: str = "./data/SourceMeter",
    output_image_ext: str = "png",
    title: str = "Concatenated Source Meter Readings",
    readings_unit: str = "Ohms",
    time_unit: str = "s",
    write_out: bool = False,
    log_scale_x: bool = False,
    log_scale_y: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    tick_param_font_size: int = 15,
    legend: bool = True,
    legend_loc: str = "upper right",
    line_label: str = "Resistance",
    line_color: str = "black",
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
    mark_lines: bool = False,
    mark_shapes: bool = False,
    switch_labels: List[str] = None,
    switch_label_line_colors: List[str] = None,
    switch_label_shape_color: str = "red",
) -> Tuple[List[float], List[float], str]:
    """
    Reads and appends resistance vs time data from multiple files, resets time to start at 0, and plots it as one continuous curve.
    Each dataset is shifted linearly in time to maintain continuity across concatenation.

    Args:
        input_filepaths (List[str]): List of filepaths to txt files, each formatted as 'time,resistance' on each line
        output_name (str): Descriptive name used in the output filename. The current date and time will be combined with this
        output_dir (str, optional): Directory for output image and optionally data file. Defaults to current directory
        output_image_ext (str, optional): Image format extension (e.g. 'png', 'svg'). Defaults to 'png'
        title (str, optional): Title of the plot. Defaults to 'Concatenated Source Meter Readings'
        readings_unit (str, optional): Y-axis unit label. Defaults to 'Ohms'
        time_unit (str, optional): X-axis unit label. Defaults to 'seconds'
        write_out (bool, optional): If True, saves concatenated time/resistance data to a .txt file. Defaults to False
        log_scale_x (bool, optional): If True, uses logarithmic scale for x-axis. Defaults to False
        log_scale_y (bool, optional): If True, uses logarithmic scale for y-axis. Defaults to False
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the plot legend, if enabled. Defaults to 20.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to True.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        line_label (str, optional): The label to use for the plotted line. Defaults to 'Resistance'.
        line_color (str, optional): The color to use for the plotted line. Defaults to 'black'.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
        mark_lines (bool, optional): Whether to place vertical line markers at the transition points between files. This takes priority over mark_shapes. Defaults to False.
        mark_shapes (bool, optional): Whether to place shape markers at the transition points between files. Defaults to False.
        switch_labels (List[str], optional): Labels to place for each switch point. Pads with File Numbers. Defaults to None
        switch_label_line_colors (List[str], optional): The colors to use for the line markers at each file switch, if enabled. If None, will follow the default color cycle. Defaults to None.
        switch_label_shape_color (str, optional): The color to use for the shape markers at each file switch, if enabled. Defaults to 'red'.
    Returns:
        Tuple[List[float], List[float], str]: (concatenated_time_series, concatenated_resistance_series, data_filepath_out)
    """
    all_times = []
    all_resistances = []
    switch_times = []
    time_offset = 0.0

    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)

    output_data = f"{curr_date}_{output_name}_{curr_time}.txt"
    output_data_path = os.path.join(output_dir, output_data)

    for i, filepath in enumerate(input_filepaths):
        try:
            times, resistances = _read_time_resistance_data(filepath)

            if len(times) != len(resistances):
                print(f"Warning: Skipping file due to mismatch in length - {filepath}")
                continue

            # Normalize time to start from 0 and shift by offset
            if times:
                times = [t + time_offset for t in times]
                time_offset = times[-1] + (
                    times[1] - times[0] if len(times) > 1 else 1.0
                )
                if mark_lines or mark_shapes and i < len(input_filepaths) - 1:
                    switch_times.append(times[-1])

            all_times.extend(times)
            all_resistances.extend(resistances)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue

    if write_out:
        with open(output_data_path, "w") as f:
            for t_val, r_val in zip(all_times, all_resistances):
                f.write(f"{t_val},{r_val}\n")
        print(f"Saving concatenated data: {os.path.abspath(output_data_path)}")

    # Plot
    plt.figure(figsize=figsize)
    plt.plot(all_times, all_resistances, label=line_label, color=line_color)
    plt.title(title, fontsize=title_font_size)
    plt.xlabel(f"Time ({time_unit})", fontsize=axis_font_size)
    plt.ylabel(f"Readings ({readings_unit})", fontsize=axis_font_size)
    plt.tick_params(labelsize=tick_param_font_size)

    if mark_lines:
        color_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])
        if not switch_label_line_colors:
            switch_label_line_colors = [next(color_cycle) for _ in input_filepaths]
        elif len(switch_label_line_colors) < len(input_filepaths):
            # Pad with cyclic fallback colors
            switch_label_line_colors += [
                next(color_cycle)
                for _ in range(len(input_filepaths) - len(switch_label_line_colors))
            ]

        first_label = switch_labels[0] if switch_labels else "File 1"
        plt.axvline(
            x=0, linestyle="--", color=switch_label_line_colors[0], label=first_label
        )

        for idx, switch_time in enumerate(switch_times):
            if idx == len(switch_times) - 1:
                break
            label = switch_labels[idx + 1] if switch_labels else f"File {idx + 2}"
            plt.axvline(
                x=switch_time,
                linestyle="--",
                color=switch_label_line_colors[idx + 1],
                label=label,
            )
    elif mark_shapes:
        # Define a list of distinct marker styles
        marker_styles = ["o", "s", "D", "^", "v", "<", ">", "p", "H", "*", "X"]
        used_labels = set()

        switch_points = [0] + switch_times
        label_list = (
            switch_labels
            if switch_labels
            else [f"File {i+1}" for i in range(len(switch_points))]
        )

        for i, switch_time in enumerate(switch_points):
            idx = next((j for j, t in enumerate(all_times) if t >= switch_time), -1)
            if idx != -1:
                time_val = all_times[idx]
                resistance_val = all_resistances[idx]

                marker = marker_styles[i % len(marker_styles)]
                label = label_list[i]

                # Slight vertical offset
                plt.scatter(
                    time_val,
                    resistance_val * 1.3,
                    color=switch_label_shape_color,
                    marker=marker,
                    s=50,
                    label=label if label not in used_labels else None,
                )
                used_labels.add(label)
    if legend:
        plt.legend(fontsize=legend_font_size, loc=legend_loc)
    if grid:
        plt.grid(True)

    if log_scale_x:
        plt.xscale("log")
    if log_scale_y:
        plt.yscale("log")

    plt.tight_layout()
    plt.savefig(output_img_path)
    print(f"Saving plot: {os.path.abspath(output_img_path)}")
    print(f"\tCurrent File: {os.path.basename(output_img_path)}")
    plt.show()

    return all_times, all_resistances, output_data_path if write_out else ""
