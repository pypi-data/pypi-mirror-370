"""The main plotting suite for analyzing data provided by the arduino."""

from typing import List, Tuple, Union
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy import stats
import numpy as np
import os
from rootlab_lib.plateau_processing import (
    average_voltage_analysis,
    find_plateaus,
    read_timed_voltage_data,
    multilayer_read_timed_voltage_data,
)

# Default values to use thresholds, plateau lengths, and gap lengths
RECOMMENDED_THRESHOLD = 0.05
RECOMMENDED_MIN_PLATEAU_LENGTH = 25
RECOMMENDED_MIN_GAP_LENGTH = 0.01

# ===== Helper Methods for the plotting suite, should be interacted with the main functions at the bottom of this file =====


def _plot_voltage_series(
    time_data: List[float],
    voltage_data: List[float],
    output_file: str,
    output_file_extension: str,
    title: str,
    time_unit: str,
    voltage_unit: str,
    axis_font_size: int,
    title_font_size: int,
    legend_font_size: int,
    tick_param_font_size: int,
    legend: bool,
    legend_loc: str,
    line_label: str,
    grid: bool,
    figsize: Tuple[int, int],
    line_color: str = None,
) -> None:
    """Creates a plot of the voltage data against time

    Args:
        time_data (List[float]): The time data from the file
        voltage_data (List[float]): The voltage data from the file
        output_file (str): The output file to save the plot to. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title to use for the plot.
        time_unit (str): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})".
        voltage_unit (str): The unit to use for the y-axis. This will be formatted as "Voltage ({voltage_unit})".
        axis_font_size (int): The fontsize to use for the plot's axes.
        title_font_size (int): The fontsize to use for the plot title.
        legend_font_size (int): The fontsize to use for the plot legend, if enabled.
        tick_param_font_size (int): The fontsize to use for the plot's ticks.
        legend (bool): Whether to show a legend on the final plot.
        legend_loc (str): The location of the legend.
        line_label (str): The label to use for the plotted line.
        grid (bool): Determines whether or not to show a gray grid on the plot.
        figsize (Tuple[int, int]): The figsize to use for the figure.
        line_color (str, optional): The color to use for the plotted line. If None, uses the default color cycle. Defaults to None.

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """
    plt.figure(figsize=figsize)
    if line_color is not None:
        plt.plot(time_data, voltage_data, label=line_label, color=line_color)
    else:
        plt.plot(time_data, voltage_data, label=line_label)
    plt.title(title, fontsize=title_font_size)
    if legend:
        plt.legend(fontsize=legend_font_size, loc=legend_loc)
    if grid:
        plt.grid(True)
    plt.xlabel(f"Time ({time_unit})", fontsize=axis_font_size)
    plt.ylabel(f"Voltage ({voltage_unit})", fontsize=axis_font_size)
    plt.tick_params(labelsize=tick_param_font_size, width=2, length=7)
    plt.tight_layout()
    output_file = f"{output_file}_SERIES.{output_file_extension}"
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


def _plot_voltage_series_plateaus(
    time_data: List[float],
    voltage_data: List[float],
    plateaus: List[Tuple],
    output_file: str,
    output_file_extension: str,
    title: str,
    time_unit: str,
    voltage_unit: str,
    legend: bool,
    axis_font_size: int,
    title_font_size: int,
    legend_font_size: int,
    tick_param_font_size: int,
    legend_loc: str,
    line_label: str,
    grid: bool,
    figsize: Tuple[int, int],
    avg_plateau_line_color: str,
    avg_plateau_point_color: str,
    line_color: str = None,
) -> List[float]:
    """Creates a plot of the voltage data and highlights and extracts the average values.

    Args:
        time_data (List[float]): The time data from the file
        voltage_data (List[float]): The voltage data from the file
        plateaus (List[Tuple]): The plateaus calculated and determined through analysis
        output_file (str): The output file to save the plot to. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title to use for the plot.
        time_unit (str): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})".
        voltage_unit (str): The unit to use for the y-axis. This will be formatted as "Voltage ({voltage_unit})".
        legend (bool): Determines whether or not to show the legend. Defaults to False for readability.
        axis_font_size (int): The fontsize to use for the plot's axes.
        title_font_size (int): The fontsize to use for the plot title.
        legend_font_size (int): The fontsize to use for the plot legend, if enabled.
        tick_param_font_size (int): The fontsize to use for the plot's ticks.
        legend_loc (str): The location of the legend.
        line_label (str): The label to use for the plotted line.
        grid (bool): Determines whether or not to show a gray grid on the plot.
        figsize (Tuple[int, int]): The figsize to use for the figure.
        line_color (str, optional): The color to use for the plotted line. If None, uses the default color cycle. Defaults to None.

    Returns:
        List[float]: The list of the extracted average values from each plateau
    """
    # plot the original series
    plt.figure(figsize=figsize)
    if line_color is not None:
        plt.plot(time_data, voltage_data, label=line_label, color=line_color)
    else:
        plt.plot(time_data, voltage_data, label=line_label)

    # plot each plateau as a scatter, including the average at the average time
    v_avg = []
    for average, start, end in plateaus:
        v_avg.append(average)

        # find the values in each plateau using the start and end
        voltage_values = voltage_data[start:end]
        time_values = time_data[start:end]
        average_time = (time_data[start] + time_data[end - 1]) / 2

        # plot the time and voltage values in the range and add the (avg_time, avg) point
        plt.plot(
            time_values,
            voltage_values,
            label=f"Plateau: {average_time:.2f}s, Avg: {average:.2f}V",
            color=avg_plateau_line_color,
        )
        plt.scatter(average_time, average, color=avg_plateau_point_color, zorder=5)

    # format the plot for readers convenience
    plt.title(title, fontsize=title_font_size)
    if legend:
        plt.legend(fontsize=legend_font_size, loc=legend_loc)
    if grid:
        plt.grid(True)
    plt.xlabel(f"Time ({time_unit})", fontsize=axis_font_size)
    plt.ylabel(f"Voltage ({voltage_unit})", fontsize=axis_font_size)
    plt.tick_params(labelsize=tick_param_font_size, width=2, length=7)
    plt.tight_layout()

    # show the plot and return the average voltages
    output_file = f"{output_file}_SERIES-plats.{output_file_extension}"
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()

    return v_avg


def _plot_voltage_heatmap(
    V_avg_map: np.ndarray,
    output_file: str,
    output_file_extension: str,
    title: str,
    x_axis_unit: str,
    y_axis_unit: str,
    cbar_voltage_unit: str,
    axis_font_size: int,
    title_font_size: int,
    tick_param_font_size: int,
    figsize: Tuple[int, int],
) -> None:
    """Plots an analysis of the data as a heatmap

    Args:
        V_avg_map (np.ndarray): The average voltages
        output_file (str): The output file to save the plot. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title of the plot to show.
        x_axis_unit (str): The unit to use for the x-axis. This will be formatted as "Position ({x_axis_unit})".
        y_axis_unit (str): The unit to use for the y-axis. This will be formatted as "Position ({y_axis_unit})".
        cbar_voltage_unit (str): The unit to use for the colorbar. This will be formatted as "Voltage ({cbar_voltage_unit})".
        axis_font_size (int): The fontsize to use for the plot's axes and colorbar.
        title_font_size (int): The fontsize to use for the plot title.
        tick_param_font_size (int): The fontsize to use for the plot's ticks.
    """
    # Add the data to the figure
    plt.figure(figsize=figsize)
    plt.imshow(V_avg_map, vmin=0, vmax=5, cmap="viridis")
    plt.xticks(tuple(i for i in range(0, 7)))

    # Plot the voltage series with labeled axes and colors for presentation
    plt.xlabel(f"Position ({x_axis_unit})", fontsize=axis_font_size)
    plt.ylabel(f"Position ({y_axis_unit})", fontsize=axis_font_size)
    plt.title(title, fontsize=title_font_size)
    cbar = plt.colorbar()
    cbar.set_label(f"Voltage ({cbar_voltage_unit})", fontsize=axis_font_size)
    cbar.ax.tick_params(labelsize=tick_param_font_size)
    plt.tick_params(labelsize=tick_param_font_size, width=3, length=7)
    plt.tight_layout()
    output_file = f"{output_file}_HEATMAP.{output_file_extension}"
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


def _plot_voltage_regression(
    pos: np.ndarray,
    V_avg_column: np.ndarray,
    V_std_column: np.ndarray,
    output_file: str,
    output_file_extension: str,
    title: str,
    intercept: bool,
    point_color: str,
    line_color: str,
    legend: bool,
    legend_loc: str,
    x_axis_unit: str,
    y_axis_unit: str,
    axis_font_size: int,
    title_font_size: int,
    tick_param_font_size: int,
    legend_font_size: int,
) -> None:
    """Plots an analysis of the data as a heatmap

    Args:
        pos (np.ndarray): The x-axis positions of the voltages to display on the regression and to use in the regression analysis
        V_avg_column (np.ndarray): The y-axis positions of the voltages to display
        V_std_column (np.ndarray): The standard deviation of of each voltage reading, to be used in error bar plotting
        output_file (str): The output file to save the plot to. You need not specify the file extension
        output_file_extension (str): The file extension to use with the output file
        title (str): The title of the plot to show
        intercept (bool): Determines if the y-intercept should be variable and not fixed at (0,0)
        point_color (str): The color to use for the voltage points and their error bars (extracted plateaus).
        line_color (str): The color to use for the fitted line.
        legend (bool): Whether to display the legend which contains the line of best fit equation and R^2.
        legend_loc (str): The location to place the legend, if enabled.
        x_axis_unit (str): The unit to use for the x axis (position).
        y_axis_unit (str): The unit to use for the y axis (voltage).
        axis_font_size (int): The fontsize to use for the plot's axes.
        title_font_size (int): The fontsize to use for the plot's title.
        tick_param_font_size (int): The fontsize to use for the plot's ticks.
        legend_font_size (int): The fontsize to use for the plot's legend, if enabled.
    """
    # Plot the average data for statistical analysis
    pos_full = np.array([0.0, 0.25, 0.75, 1.25, 1.75, 2.25, 3.0], dtype=float)
    plt.title(title, fontsize=title_font_size)
    plt.xlabel(f"Position ({x_axis_unit})", fontsize=axis_font_size)
    plt.ylabel(f"Voltage ({y_axis_unit})", fontsize=axis_font_size)
    plt.tick_params(labelsize=tick_param_font_size, width=2, length=7)
    plt.ylim((-0.9, 5.1))
    plt.xlim((-0.1, 3.1))
    plt.errorbar(
        pos,
        V_avg_column,
        yerr=V_std_column,
        linestyle="None",
        marker="o",
        color=point_color,
    )
    if intercept:
        res = stats.linregress(pos, V_avg_column)
        plt.plot(
            pos_full,
            res[0] * pos_full + res[1],
            line_color,
            label="V = %.2f x + %.2f\nR$^2$= %.4f" % (res[0], res[1], res[2] ** 2),
        )
    else:
        res = np.polyfit(pos, V_avg_column, 1, w=np.ones_like(pos), full=True)
        slope = res[0][0]
        residuals = res[1][0] if len(res[1]) > 0 else 0
        r2 = 1 - (residuals / np.sum((V_avg_column - np.mean(V_avg_column)) ** 2))
        plt.plot(
            pos_full,
            slope * pos_full,
            line_color,
            label="V = %.2f x\nR$^2$= %.4f" % (slope, r2),
        )
    if legend:
        plt.legend(loc=legend_loc, frameon=False, fontsize=legend_font_size)
    plt.tight_layout()
    output_file = (
        f"{output_file}_REGRESSION-intercept.{output_file_extension}"
        if intercept
        else f"{output_file}_REGRESSION.{output_file_extension}"
    )
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


# ===== The main functions for the user to interface with =====


def heatmap(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    title: str = "Heatmap",
    prepend_zero: bool = False,
    output_dir: str = "./data/Heatmaps",
    output_image_extension: str = "png",
    x_axis_unit: str = "0.5 cm",
    y_axis_unit: str = "0.5 cm",
    cbar_voltage_unit: str = "V",
    axis_font_size: int = 25,
    title_font_size: int = 30,
    tick_param_font_size: int = 15,
    figsize: Tuple[int, int] = (12, 9),
) -> None:
    """Creates a heatmap out of given data

    Args:
        filepath (str): The file to use formatted as [time_series, voltage]
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        title (str, optional): The title to use for the map. Defaults to 'Heatmap'.
        prepend_zero (bool, optional): Determines if the plateaus should have 0 added to the start of the list. Defaults to False.
        output_dir (str, optional): The directory to save the image to. Defaults to "./data/Heatmaps", relative to the current directory
        output_image_extension (str, optional): Specifies the image type to save the generated graph as. Do not include the dot. Defaults to png
        x_axis_unit (str): The unit to use for the x-axis. This will be formatted as "Position ({x_axis_unit})". Defaults to "0.5 cm"
        y_axis_unit (str): The unit to use for the y-axis. This will be formatted as "Position ({y_axis_unit})". Defaults to "0.5 cm"
        cbar_voltage_unit (str): The unit to use for the colorbar. This will be formatted as "Voltage ({cbar_voltage_unit})". Defaults to "V"
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
    """
    v_averages = [
        v_avg
        for v_avg, _, _ in find_plateaus(
            read_timed_voltage_data(filepath)[1],
            threshold,
            min_plateau_length,
            min_gap_length,
        )
    ]
    if prepend_zero:
        v_averages = [0] + v_averages
    print(f"{v_averages}\n Number of Plateaus: {len(v_averages)}")
    basename = os.path.basename(filepath)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")
    _plot_voltage_heatmap(
        average_voltage_analysis(v_averages)[1],
        output_file,
        output_image_extension,
        title,
        x_axis_unit,
        y_axis_unit,
        cbar_voltage_unit,
        axis_font_size,
        title_font_size,
        tick_param_font_size,
        figsize,
    )


def regression(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    title: str = "Regression Model",
    prepend_zero: bool = False,
    intercept: bool = False,
    output_dir: str = "./data/Regression",
    output_image_extension: str = "png",
    point_color: str = "black",
    line_color: str = "red",
    legend: bool = True,
    legend_loc: str = "upper left",
    position_unit: str = "cm",
    voltage_unit: str = "V",
    axis_font_size: int = 25,
    title_font_size: int = 30,
    tick_param_font_size: int = 15,
    legend_font_size: int = 20,
    normalize: bool = True,
) -> None:
    """Creates a linear regression out of given data

    Args:
        filepath (str): The file to use formatted as [time_series, voltage]
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        title (str, optional): The title to use for the plot. Defaults to 'Regression Model'.
        prepend_zero (bool, optional): Determines if the plateaus should have 0 added to the start of the list. Defaults to False.
        intercept (bool, optional): Determines if the y-intercept should be variable and not fixed at (0,0). Defaults to False.
        output_dir (str, optional): The directory to save the image to. Defaults to "./data/Regression", relative to the current directory
        output_image_extension (str, optional): Specifies the image type to save the generated graph as. Do not include the dot. Defaults to png
        point_color (str, optional): The color to use for the voltage points and their error bars (extracted plateaus). Defaults to 'black'.
        line_color (str, optional): The color to use for the fitted line. Defaults to 'red'.
        legend (bool, optional): Whether to display the legend which contains the line of best fit equation and R^2. Defaults to True.
        legend_loc (str, optional): The location to place the legend, if enabled. Defaults to 'upper left'.
        position_unit (str, optional): The unit to use for the x axis (position). Defaults to 'cm'.
        voltage_unit (str, optional): The unit to use for the y axis (voltage). Defaults to 'V'.
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot's title. Defaults to 30.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        legend_font_size (int, optional): The fontsize to use for the plot's legend, if enabled. Defaults to 20.
        normalize (bool, optional): Determines whether or not to shift the voltages to start at 0. It does not make sense to have this and the 'intercept' arg True at the same time. Defaults to True
    """
    data = read_timed_voltage_data(filepath)
    v_averages = [
        v_avg
        for v_avg, _, _ in find_plateaus(
            data[1], threshold, min_plateau_length, min_gap_length
        )
    ]
    if normalize:
        minim = min(v_averages)
        v_averages = [v - minim for v in v_averages]
    if prepend_zero:
        v_averages = [0] + v_averages
    pos, _, V_avg_column, V_std_column = average_voltage_analysis(v_averages)
    basename = os.path.basename(filepath)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")
    _plot_voltage_regression(
        pos,
        V_avg_column,
        V_std_column,
        output_file,
        output_image_extension,
        title,
        intercept,
        point_color,
        line_color,
        legend,
        legend_loc,
        position_unit,
        voltage_unit,
        axis_font_size,
        title_font_size,
        tick_param_font_size,
        legend_font_size,
    )


def series(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    title_default: str = "Voltage Series",
    title_plateaus: str = "Voltage Series with Plateaus",
    plateaus: bool = False,
    legend: bool = False,
    output_series_dir: str = "./data/Series",
    output_plats_dir: str = "./data/Plats",
    output_image_extension: str = "png",
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    tick_param_font_size: int = 15,
    legend_loc: str = "upper right",
    time_unit: str = "s",
    voltage_unit: str = "V",
    line_label: str = "Voltage",
    line_color: str = "black",
    plateau_line_marker_color: str = "red",
    plateau_point_marker_color: str = "blue",
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
) -> None:
    """Creates the voltage series out of given data

    Args:
        filepath (str): The file to use formatted as [time_series, voltage]
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        title_default (str, optional): The title to use for the map. Defaults to 'Voltage Series'.
        title_plateaus (str, optional): The title to use for the map. Defaults to 'Voltage Series with Plateaus'.
        plateaus (bool, optional): Determines if the plateaus should be plotted on the graph. Defaults to False.
        legend (bool, optional): Determines whether or not to show the legend. Defaults to False for readability.
        output_series_dir (str, optional): The directory to save the image to if the plateau flag is false. Defaults to '.', relative to the current directory
        output_plats_dir (str, optional): The directory to save the image to if the plateau flag is true. Defaults to './data/Plats', relative to the current directory
        output_image_extension (str, optional): Specifies the image type to save the generated graph as. Do not include the dot. Defaults to png
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the plot legend, if enabled. Defaults to 20.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to True.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        time_unit (str): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})". Defaults to "s"
        voltage_unit (str): The unit to use for the y-axis. This will be formatted as "Voltage ({voltage_unit})". Defaults to "V".
        line_label (str, optional): The label to use for the plotted line. Defaults to 'Resistance'.
        line_color (str, optional): The color to use for the plotted line. Defaults to 'black'.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
    """
    data = read_timed_voltage_data(filepath)
    plats = find_plateaus(data[1], threshold, min_plateau_length, min_gap_length)
    basename = os.path.basename(filepath)

    output_dir = output_plats_dir if plateaus else output_series_dir
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")

    if plateaus:
        _plot_voltage_series_plateaus(
            data[0],
            data[1],
            plats,
            output_file,
            output_image_extension,
            title_plateaus,
            time_unit,
            voltage_unit,
            legend,
            axis_font_size,
            title_font_size,
            legend_font_size,
            tick_param_font_size,
            legend_loc,
            line_label,
            grid,
            figsize,
            plateau_line_marker_color,
            plateau_point_marker_color,
            line_color,
        )
    else:
        _plot_voltage_series(
            data[0],
            data[1],
            output_file,
            output_image_extension,
            title=title_default,
            time_unit=time_unit,
            voltage_unit=voltage_unit,
            axis_font_size=axis_font_size,
            title_font_size=title_font_size,
            legend_font_size=legend_font_size,
            tick_param_font_size=tick_param_font_size,
            legend=legend,
            legend_loc=legend_loc,
            line_label=line_label,
            grid=grid,
            figsize=figsize,
            line_color=line_color,
        )


def suite(
    filename: str,
    generic_plot_title: str,
    port: str = "COM3",
    read_serial: bool = True,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    normalize_regression: bool = True,
    prepend_zero_to_plateaus: bool = False,
) -> str:
    """The simplist way to gather and plot data for single analog channel reading

    Args:
        filename (str): The name to use in a timestamped file if gthering data (read_serial is True), or the full filepath to plot (read_serial is False)
        generic_plot_title (str): The title to use on all generated plots.
        port (str, optional): The port to read serial data from. Defaults to 'COM3'.
        read_serial (bool, optional): Whether or not to gather_data from the Arduino connected to the specified serial port. Defaults to True.
        threshold (float, optional): The minimum voltage to be considered for a plateau. Defaults to 0.05
        min_plateau_length (float, optional): The minimum length of a plateau to be logged. Defaults to 25
        min_gap_length (float, optional): The minimum voltage drop to break a plateau. Defaults to 0.01
        normalize_regression (bool, optional): Whether or not to normalize the linear regression generated such that the first voltage average is at 0V. Defaults to True.
        prepend_zero_to_plateaus (bool, optional): Whether or not to prepend a reading of 0V to extracted plateaus, useful for very slightly malformed data. Defaults to False.

    Returns:
        str: _description_
    """
    from .serial_reader import gather_data

    file = (
        gather_data(port, filename, title=generic_plot_title)
        if read_serial
        else filename
    )
    series(
        file,
        threshold,
        min_plateau_length,
        min_gap_length,
        plateaus=True,
        title_default=generic_plot_title,
        title_plateaus=generic_plot_title,
    )
    regression(
        file,
        threshold,
        min_plateau_length,
        min_gap_length,
        generic_plot_title,
        normalize=normalize_regression,
        prepend_zero=prepend_zero_to_plateaus,
    )
    heatmap(
        file,
        threshold,
        min_plateau_length,
        min_gap_length,
        generic_plot_title,
        prepend_zero=prepend_zero_to_plateaus,
    )


# === MULTILAYER ===
# ========================================================================= CONSTRUCTION ZONE BEYOND THIS POINT ===============================================================================================


def _plot_analog_pin_data(
    filepath: str,
    pin: Union[int, str],
    title: str = None,
    output_dir: str = "./data/Series",
    output_image_extension: str = "png",
) -> None:
    basename = os.path.basename(filepath)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(
        output_dir, f"{os.path.splitext(basename)[0]}.{output_image_extension}"
    )

    label = ""
    # decode pin user input
    if pin == 0 or (isinstance(pin, str) and pin.lower() in ["a0", "0"]):
        pin = 0
        label += "A0"
    elif pin == 1 or (isinstance(pin, str) and pin.lower() in ["a1", "1"]):
        pin = 1
        label += "A1"
    elif pin == 2 or (isinstance(pin, str) and pin.lower() in ["a2", "2"]):
        pin = 2
        label += "A2"

    label_top = label + " Top"
    label_bot = label + " Bottom"

    ((Vtop, Vbot), (vb1, vt1), (vb2, vt2), (t1, t2)) = (
        multilayer_read_timed_voltage_data(filepath)
    )

    m = {
        # (level (top/bottom), pin (a0,1,2))
        (0, 0): Vbot,
        (0, 1): vb1,
        (0, 2): vb2,
        (1, 0): Vtop,
        (1, 1): vt1,
        (1, 2): vt2,
    }
    user_input_bot = (0, pin)
    user_input_top = (1, pin)
    if user_input_bot not in m or user_input_top not in m:
        raise ValueError("You shouldn't be here")
    v_plot_bot = m[user_input_bot]
    v_plot_top = m[user_input_top]

    if title is None:
        title = "Analog Pin " + label + " Time Series"

    plt.figure(figsize=(8, 6))
    plt.tick_params(labelsize=25, width=2, length=7)
    plt.plot(t1, v_plot_bot, color="r", label=label_bot)
    plt.plot(t2, v_plot_top, color="k", label=label_top)
    plt.title(title)
    plt.xlabel("Time (s)", fontsize=20)
    plt.ylabel("Voltage (V)", fontsize=20)
    plt.tight_layout()
    plt.ylim(0, 5)
    plt.legend()
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


def _plot_original_voltage_pos_series(
    filepath: str,
    layer: Union[int, str] = None,
    title: str = "Voltage Series",
    plateaus: bool = False,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH - 5,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
    legend: bool = False,
    output_series_dir: str = "./data/Series",
    output_plats_dir: str = "./data/Plats",
    output_image_extension: str = "png",
) -> None:
    basename = os.path.basename(filepath)
    output_dir = output_plats_dir if plateaus else output_series_dir
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.splitext(basename)[0]}")

    ((Vtop, Vbot), (_, _), (vb2, vt2), (t1, t2)) = multilayer_read_timed_voltage_data(
        filepath
    )
    plateaus_t = find_plateaus(vt2, threshold, min_plateau_length, min_gap_length)
    plateaus_b = find_plateaus(vb2, threshold, min_plateau_length, min_gap_length)

    plt.figure(figsize=(8, 6))
    plt.tick_params(labelsize=25, width=2, length=7)
    ok = False
    if (
        layer is None
        or layer == 0
        or (isinstance(layer, str) and layer.lower() in ["bottom", "b", "bot", "lower"])
    ):
        plt.plot(range(len(Vbot)), vb2, color="blue", label="Voltage Series Bottom")
        output_file += "_Bottom"
        if plateaus:
            vavg = []
            avg_time = []
            for average, start, end in plateaus_t:
                time_values = range(start, end + 1)
                voltage_values = [vt2[i] for i in time_values]
                average_time = (t2[start] + t2[end]) / 2
                average_interval = (start + end) / 2
                plt.plot(
                    time_values,
                    voltage_values,
                    label=f"Plateau {average_time:.2f}s, Avg: {average:.2f}V",
                    color="magenta",
                    zorder=5,
                )
                plt.scatter(average_interval, average, color="k", zorder=5)
                vavg.append(average)
                avg_time.append(average_time)
        ok = True
    if (
        layer is None
        or layer == 1
        or (isinstance(layer, str) and layer.lower() in ["top", "t", "upper"])
    ):
        plt.plot(range(len(Vtop)), vt2, color="orange", label="Voltage Series Top")
        output_file += "_Top"
        if plateaus:
            vavgb = []
            avg_timeb = []
            for average, start, end in plateaus_b:
                time_values = range(start, end + 1)
                voltage_values = [vb2[i] for i in time_values]
                average_time = (t2[start] + t2[end]) / 2
                average_interval = (start + end) / 2
                plt.plot(
                    time_values,
                    voltage_values,
                    label=f"Plateau {average_time:.2f}s, Avg: {average:.2f}V",
                    color="red",
                )
                plt.scatter(average_interval, average, color="k", zorder=5)
                vavgb.append(average)
                avg_timeb.append(average_time)
        ok = True
    if not ok:
        raise ValueError("Layer must be either None, 0, or 1")

    output_file = (
        f"{output_file}_SERIES{"-plats" if plateaus else ""}.{output_image_extension}"
    )

    plt.title(title)
    plt.xlabel("Time (s)", fontsize=25)
    plt.ylabel("Position (cm)", fontsize=25)
    if legend:
        plt.legend()
    plt.tight_layout()
    print(f"Saving {os.path.abspath(output_file)}")
    print(f"\tCurrent File: {os.path.basename(output_file)}")
    plt.savefig(output_file)
    plt.show()


def _plot_inferred_positions(
    filepath: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH - 5,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
):
    ((Vtop, Vbot), (_, _), (vb2, vt2), (t1, t2)) = multilayer_read_timed_voltage_data(
        filepath
    )
    plateaus_t = find_plateaus(vt2, threshold, min_plateau_length, min_gap_length)
    plateaus_b = find_plateaus(vb2, threshold, min_plateau_length, min_gap_length)

    vavg = np.asarray([average for average, _, _ in plateaus_t])
    vavgb = np.asarray([average for average, _, _ in plateaus_b])

    avg_time, avg_timeb = [], []
    for _, start, end in plateaus_t:
        average_time = (t2[start] + t2[end]) / 2
        avg_time.append(average_time)

    for _, start, end in plateaus_b:
        average_time = (t2[start] + t2[end]) / 2
        avg_timeb.append(average_time)

    pos_x = vavg / 1.66
    pos_y = vavgb / 1.66

    print(pos_y)

    pos_x_real = np.asarray([1.5, 1.5, 1.5, 1.5, 1.5])
    pos_y_real = np.asarray([2.5, 2.0, 1.5, 1.0, 0.5])

    error_x = pos_x - pos_x_real
    error_y = pos_y - pos_y_real

    # dif_sq = np.sqrt((pos_x - pos_x_real) ** 2 + (pos_y - pos_y_real) ** 2) * 10  # mm
    # print("difference squared:")
    # print(dif_sq)
    # print("mean difference squared:")
    # print(np.mean(dif_sq))

    plt.figure(figsize=(8, 6))
    plt.tick_params(labelsize=25, width=2, length=7)
    plt.scatter(
        pos_x, pos_y, c=range(len(pos_x)), s=50, marker="s", label="Inferred Position"
    )
    plt.scatter(
        pos_x_real, pos_y_real, c=range(len(pos_x)), s=50, label="Actual Position"
    )
    plt.scatter(pos_x_real, pos_y_real, c=range(len(pos_x)), s=50, alpha=0.25)
    plt.xlabel("Actual Position (cm)", fontsize=25)
    plt.ylabel("Inferred Position(cm)", fontsize=25)
    plt.legend(loc="upper right", frameon=False, fontsize=15)
    plt.xlim(-0.25, 3.75)
    plt.ylim(0, 3.5)
    # plt.grid(True)
    plt.show()


# TODO
def multilayer_voltage_analysis(
    filename: str,
    V_to_check: str,
    threshold: float = RECOMMENDED_THRESHOLD,
    min_plateau_length: float = RECOMMENDED_MIN_PLATEAU_LENGTH - 5,
    min_gap_length: float = RECOMMENDED_MIN_GAP_LENGTH,
) -> Tuple[np.ndarray]:
    """Calculates the average and std dev of the voltage values from the experiment

    Args:
        filename (str): A file with comma separated voltage and time data
        V_to_check (str): Whether to analyze the top or bottom

    Returns:
        Tuple[np.ndarray]: Returns analysis output as (pos, V_avg_map, V_avg_column, V_std_column).
    """
    ((Vtop, Vbot), (vb1, vt1), (vb2, vt2), (t1, t2)) = (
        multilayer_read_timed_voltage_data(filename)
    )
    voltage_data = []
    if V_to_check == "T":
        voltage_data = Vtop
    elif V_to_check == "B":
        voltage_data = Vbot
    else:
        raise ValueError("V_to_check must be either T or B, cannot analyze volt data")

    plateaus_t = find_plateaus(vt2, threshold, min_plateau_length, min_gap_length)
    plateaus_b = find_plateaus(vb2, threshold, min_plateau_length, min_gap_length)

    num_plateaus_t = len(plateaus_t)
    num_plateaus_b = len(plateaus_b)
    print("Number of plateaus:", num_plateaus_t)
    print("Number of plateaus b:", num_plateaus_b)

    average_values = [plateau[0] for plateau in plateaus_b]
    print("Average values for each plateau:", average_values)
