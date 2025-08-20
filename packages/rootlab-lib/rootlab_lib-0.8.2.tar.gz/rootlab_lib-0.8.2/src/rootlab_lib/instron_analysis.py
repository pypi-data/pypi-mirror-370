"""An extremely basic and minimal interface for working with data from the instron tensile tester"""

import os
from typing import List, Tuple
import matplotlib.pyplot as plt
import csv
import time


def _read_numeric_data(
    filepath: str, flag: str = "(s),(mm),(N),(%),(MPa),(N/tex)"
) -> Tuple[
    List[float], List[float], List[float], List[float], List[float], List[float]
]:
    """Reads the data produced by the Instron

    Args:
        filepath (str): The path to the csv file output from the Instron's analysis software
        flag (str, optional): The text to look for to indicate data should be read on the next pass. Defaults to '(s),(mm),(N),(%),(MPa),(N/tex)'

    Returns:
        Tuple[List[float], List[float], List[float], List[float], List[float], List[float],]:
            Time, Extension, Load, Tensile strain (Extension), Tensile stress, Tenacity
    """
    with open(filepath, "r") as f:
        reader = csv.reader(f.readlines())
        read_flag = False

        result = [[], [], [], [], [], []]
        for row in reader:
            if read_flag:
                for i, val in enumerate(row):
                    result[i].append(float(val))
            if ",".join(row) == flag:
                read_flag = True

    return tuple(list(col) for col in result)


def single_stress_strain(
    filepath: str,
    title: str = "Stress-Strain Curve",
    x_label: str = "Tensile Strain (%)",
    y_label: str = "Tensile Stress (MPa)",
    label: str = "Specimen",
    legend: bool = False,
    legend_loc: str = "upper right",
    output_image_dir: str = "./data/Instron",
    output_image_ext: str = "png",
    timestamp: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    color: str = None,
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
) -> None:
    """Plots a single stress strain curve and saves the image generated

    Args:
        filepath (str): The path to the file with the Instron readings
        title (str, optional): The title to use for the plot. Defaults to "Stress-Strain Curve".
        x_label (str, optional): The x-axis label to use for the plot. Defaults to "Tensile Strain (%)".
        y_label (str, optional): The y-axis label to use for the plot. Defaults to "Tensile Stress (MPa)".
        label (str, optional): The legend label to use, if legend is enabled, for the line. Defaults to "Specimen".
        legend (bool, optional): Determines whether or not a legend will be shown. Defaults to False.
        legend_loc (str, optional): The location to show the legend, if toggled on. Defaults to "upper right".
        output_image_dir (str, optional): The directory to store the image generated. Defaults to "./data/Instron".
        output_image_ext (str, optional): The extension to use on the image. Do not include the 'dot'. Defaults to "png".
        timestamp (bool, optional): Determines whether or not to include a timestamp on the image output file. Thi si useful for iterations where you want to prevent overwriting data. Defaults to False.
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the legend, if toggled on. Defaults to 20.
        color (str, optional): The color to use for each plot. If None, uses the default color. Defaults to None.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
    """
    data = _read_numeric_data(filepath)

    name = os.path.splitext(os.path.basename(filepath))[0]
    if timestamp:
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        name = f"{curr_date}_{name}_{curr_time}"
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{name}.{output_image_ext}")

    plt.figure(figsize=figsize)
    if color is not None:
        plt.plot(data[3], data[4], label=label, color=color)
    else:
        plt.plot(data[3], data[4], label=label)
    plt.title(title, fontsize=title_font_size)
    plt.xlabel(x_label, fontsize=axis_font_size)
    plt.ylabel(y_label, fontsize=axis_font_size)
    if legend:
        plt.legend(fontsize=legend_font_size, loc=legend_loc)
    if grid:
        plt.grid(True)
    plt.tight_layout()
    print(f"Saving {os.path.abspath(image_path)}")
    print(f"\tCurrent File: {os.path.basename(image_path)}")
    plt.savefig(image_path)
    plt.show()


def plot_multiple_stress_strain(
    filepaths: List[str],
    output_filename: str,
    labels: List[str] = [],
    title: str = "Stress-Strain Curves",
    x_label: str = "Tensile Strain (%)",
    y_label: str = "Tensile Stress (MPa)",
    legend: bool = True,
    legend_loc: str = "upper right",
    output_image_dir: str = "./data/Instron",
    output_image_ext: str = "png",
    timestamp: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    colors: List[str] = None,
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
) -> None:
    """Plots multiple stress strain curves on the same plot

    Args:
        filepaths (List[str]): A list of filepaths with data to render
        output_filename (str): The desired name of the output file. You need not specify the extension or include timestamp data. See input `timestamp`
        labels (List[str], optional): The labels for the legend if turned on. Will pad to a numbered list of `Specimen #`. Defaults to [].
        title (str, optional): The title to use for the final plot. Defaults to "Stress-Strain Curve".
        x_label (str, optional): The x-axis label to use. Defaults to "Tensile Strain (%)".
        y_label (str, optional): The y-axis label to use. Defaults to "Tensile Stress (MPa)".
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to True.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        output_image_dir (str, optional): The directory to automatically save the image to. Defaults to "./data/Instron".
        output_image_ext (str, optional): The extension to use for the generated and saved image. Defaults to "png".
        timestamp (bool, optional): Whether to include the data and time with the saved image to prevent overwriting previously saved plots. Defaults to False.
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the legend, if toggled on. Defaults to 20.
        colors (List[str], optional): The colors to use for each plot. Must provide enough colors for every plot. If None, uses default colors. Defaults to None.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
    """
    # format the image path
    if timestamp:
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        output_filename = f"{curr_date}_{output_filename}_{curr_time}"
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{output_filename}.{output_image_ext}")

    # Determine color usage
    use_usr_colors = False
    num_files = len(filepaths)
    if colors is not None and num_files != len(colors):
        raise ValueError("Arg: 'colors' must be exactly as long as arg: 'filepaths'")
    elif colors is not None:
        use_usr_colors = True

    # Right pad labels to match number of filepaths
    idx = len(labels) + 1
    while num_files > len(labels):
        labels.append(f"Specimen {idx}")
        idx += 1

    # collect all of the data
    datum = []
    for filepath in filepaths:
        data = _read_numeric_data(filepath)
        datum.append([data[3], data[4]])

    plt.figure(figsize=figsize)
    for i in range(len(datum)):
        if use_usr_colors:
            plt.plot(*datum[i], label=labels[i], color=colors[i])
        else:
            plt.plot(*datum[i], label=labels[i])
    plt.title(title, fontsize=title_font_size)
    plt.xlabel(x_label, fontsize=axis_font_size)
    plt.ylabel(y_label, fontsize=axis_font_size)
    if legend:
        plt.legend(fontsize=legend_font_size, loc=legend_loc)
    if grid:
        plt.grid(True)
    plt.tight_layout()
    print(f"Saving {os.path.abspath(image_path)}")
    print(f"\tCurrent File: {os.path.basename(image_path)}")
    plt.savefig(image_path)
    plt.show()
