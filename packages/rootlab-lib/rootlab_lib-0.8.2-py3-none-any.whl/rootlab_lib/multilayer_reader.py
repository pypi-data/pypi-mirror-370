import serial
import matplotlib.pyplot as plt
import time
import os
from typing import List, Tuple
import random
import matplotlib.animation as animation
import statistics


class _MockSerial:
    """Simulates a basic serial.Serial interface."""

    def __init__(self, delay=0.1):
        self.delay = delay

    def readline(self):
        time.sleep(self.delay)
        return f"{random.uniform(0, 5):.3f}\n".encode()


def gather_data(
    port: str,
    name: str,
    baudrate: str = 9600,
    output_file_dir: str = "./data/Multilayer-Raw",
    output_image_dir: str = "./data/Multilayer-Series",
    output_image_ext: str = "png",
    mock: bool = False,
    relative: float = None,
    title: str = "Resistance vs. Time",
    time_unit: str = "s",
    resistance_unit: str = "Ohm",
    thresh: int = 1000,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    tick_param_font_size: int = 15,
    legend: bool = True,
    legend_loc: str = "upper right",
    top_label: str = "Top",
    top_color: str = "red",
    middle_label: str = "Middle",
    middle_color: str = "green",
    bottom_label: str = "Bottom",
    bottom_color: str = "blue",
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
) -> Tuple[List[float], List[float], str]:
    """
    Reads and plots serial data in real-time, and saves to a timestamped .txt file.

    Args:
        port (str): Serial port (e.g., 'COM3').
        name (str): Descriptive name used in output filename. You need not include the file extension
        baudrate (int, optional): Baud rate for serial communication. Defaults to '9600'
        output_file_dir (str, optional): Directory to save the output file. Defaults to '.', the current directory
        output_image_dir (str, optional): Directory to save the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): Extension to use for the output image. You need not include the period. Defaults to 'png'
        mock (bool, optional): Indicates whether or not serial data should be simulated
        relative (float, optional): Indicates whether to plot read resistance or relative resistance (read / reference value). Defaults to None
        title (str, optional): The title to use for the plot. Defaults to 'Resistance vs. Time'
        time_unit (str, optional): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})". Defaults to "s"
        resistance_unit (str, optional): The unit to use for the y-axis. This will be formatted as "Resistance ({resistance_unit})". Defaults to "Ohm"
        thresh (int, optional): The number of readings gathered before the plot updates
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the plot legend, if enabled. Defaults to 20.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to True.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        top_label (str, optional): The label to use for the top layer. Defaults to 'Top'.
        top_color (str, optional): The color to use for the top layer. Defaults to 'red'.
        middle_label (str, optional): The label to use for the top layer. Defaults to 'Middle'.
        middle_color (str, optional): The color to use for the top layer. Defaults to 'green'.
        bottom_label (str, optional): The label to use for the top layer. Defaults to 'Bottom'.
        bottom_color (str, optional): The color to use for the top layer. Defaults to 'blue'.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).

    Returns:
        Tuple[List[float], List[float], List[float], List[float], str]: (R1_series, R2_series, R3_series, time_series, output_file_path)
    """
    ser = _MockSerial(0.1) if mock else serial.Serial(port=port, baudrate=baudrate)
    curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
    base_name = f"{curr_date}_{name}_{curr_time}"

    os.makedirs(output_file_dir, exist_ok=True)
    text_path = os.path.join(output_file_dir, f"{base_name}.txt")
    os.makedirs(output_image_dir, exist_ok=True)
    image_path = os.path.join(output_image_dir, f"{base_name}.{output_image_ext}")

    print(f"Recording to: {os.path.abspath(text_path)}")

    R1, R2, R3, t = [], [], [], []
    t0 = time.time()

    fig, ax = plt.subplots(figsize=figsize)
    # ax.set_ylim(1000, 50000)
    ax.set_xlabel(f"Time ({time_unit})", fontsize=axis_font_size)
    ax.set_ylabel(f"Resistance ({resistance_unit})", fontsize=axis_font_size)
    ax.set_title(title, fontsize=title_font_size)
    if grid:
        ax.grid(True)
    ax.tick_params(labelsize=tick_param_font_size)

    (line1,) = ax.plot([], [], label=bottom_label, color=bottom_color)
    (line2,) = ax.plot([], [], label=middle_label, color=middle_color)
    (line3,) = ax.plot([], [], label=top_label, color=top_color)
    if legend:
        ax.legend(fontsize=legend_font_size, loc=legend_loc)

    f = open(text_path, "w")

    def update(frame):
        try:
            raw = ser.readline().decode().strip().split(",")
            if len(raw) != 3:
                return

            r1, r2, r3 = float(raw[0]), float(raw[1]), float(raw[2])
            timestamp = time.time() - t0

            R1.append(r1)
            R2.append(r2)
            R3.append(r3)
            t.append(timestamp)

            f.write(f"{r1},{r2},{r3},{timestamp:.3f}\n")
            f.flush()

            # Limit to max_points
            R1_trim = R1[-thresh:]
            R2_trim = R2[-thresh:]
            R3_trim = R3[-thresh:]
            t_trim = t[-thresh:]

            # Bring values into reference resistance range
            if relative is not None:
                R1_trim = [res1 / relative for res1 in R1_trim]
                R2_trim = [res2 / relative for res2 in R2_trim]
                R3_trim = [res3 / relative for res3 in R3_trim]

            line1.set_data(t_trim, R1_trim)
            line2.set_data(t_trim, R2_trim)
            line3.set_data(t_trim, R3_trim)

            ax.relim()
            ax.autoscale_view()
        except Exception as e:
            print(f"Error in update: {e}")

    ani = animation.FuncAnimation(fig, update, interval=50, cache_frame_data=False)
    plt.tick_params(labelsize=tick_param_font_size)
    plt.tight_layout()

    try:
        plt.show()
    except KeyboardInterrupt:
        print("Interrupted by user.")

    print("Closing...")
    f.close()
    fig.savefig(image_path)
    print(f"Plot saved to {image_path}")
    return R1, R2, R3, t, text_path


def plot(
    file: str,
    output_file: str,
    title: str,
    time_unit: str = "s",
    resistance_unit: str = "Ohm",
    output_image_dir: str = "./data/Multilayer-Series",
    output_image_extension: str = "png",
    timestamp: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    legend_font_size: int = 20,
    tick_param_font_size: int = 15,
    legend: bool = True,
    legend_loc: str = "upper right",
    top_label: str = "Top",
    top_color: str = "red",
    middle_label: str = "Middle",
    middle_color: str = "green",
    bottom_label: str = "Bottom",
    bottom_color: str = "blue",
    grid: bool = False,
    figsize: Tuple[int, int] = (12, 9),
) -> None:
    """Creates a plot of the voltage data against time. Can overwrite any plot or file of the same name. Only use for recovery.

    Args:
        file (str): The file with raw data formatted as {r1},{r2},{r3},{time}, where r1 is the top and r3 is the bottom
        output_file (str): The output file to save the plot to. You need not specify the file extension
        title (str): The title to use for the plot
        time_unit (str, optional): The unit to use for the x-axis. This will be formatted as "Time ({time_unit})". Defaults to "s"
        resistance_unit (str, optional): The unit to use for the y-axis. This will be formatted as "Resistance ({resistance_unit})". Defaults to "Ohm"
        output_image_dir (str, optional): The directory to automatically save the output to. Defaults to "./data/Multilayer-Series".
        output_image_extension (str, optional): The file extension to use with the output file. Do not include the period. Defaults to "png"
        timestamp (bool, optional): Whether to include the data and time with the saved image to prevent overwriting previously saved plots. Defaults to False.
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        legend_font_size (int, optional): The fontsize to use for the plot legend, if enabled. Defaults to 20.
        tick_param_font_size (int, optional): The fontsize to use for the plot's ticks. Defaults to 15.
        legend (bool, optional): Whether to show a legend on the final plot. Defaults to True.
        legend_loc (str, optional): The location of the legend. Defaults to "upper right".
        top_label (str, optional): The label to use for the top layer. Defaults to 'Top'.
        top_color (str, optional): The color to use for the top layer. Defaults to 'red'.
        middle_label (str, optional): The label to use for the top layer. Defaults to 'Middle'.
        middle_color (str, optional): The color to use for the top layer. Defaults to 'green'.
        bottom_label (str, optional): The label to use for the top layer. Defaults to 'Bottom'.
        bottom_color (str, optional): The color to use for the top layer. Defaults to 'blue'.
        grid (bool, optional): Determines whether or not to show a gray grid on the plot. Defaults to False.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).
    """
    # Prepare series
    time_data = []
    resistance_top = []
    resistance_middle = []
    resistance_bottom = []

    with open(file, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(",")
            if len(parts) != 4:
                continue  # Skip malformed lines
            try:
                r1, r2, r3, t = map(float, parts)
                resistance_top.append(r1)
                resistance_middle.append(r2)
                resistance_bottom.append(r3)
                time_data.append(t)
            except ValueError:
                continue  # Skip lines that fail to parse

    # Plot the data
    plt.figure(figsize=figsize)
    plt.plot(time_data, resistance_top, label=top_label, color=top_color)
    plt.plot(time_data, resistance_middle, label=middle_label, color=middle_color)
    plt.plot(time_data, resistance_bottom, label=bottom_label, color=bottom_color)

    plt.title(title, fontsize=title_font_size)
    if grid:
        plt.grid(True)
    plt.xlabel(f"Time ({time_unit})", fontsize=axis_font_size)
    plt.ylabel(f"Resistance ({resistance_unit})", fontsize=axis_font_size)
    plt.tick_params(labelsize=tick_param_font_size)
    if legend:
        plt.legend(fontsize=legend_font_size, loc=legend_loc)
    plt.tight_layout()

    output_path = f"{output_file}_SERIES"
    if timestamp:
        curr_date, curr_time = time.strftime("%y-%m-%d"), time.strftime("%H-%M-%S")
        output_path = f"{curr_date}_{output_path}_{curr_time}"
    os.makedirs(output_image_dir, exist_ok=True)
    full_output_path = os.path.join(
        output_image_dir, f"{output_path}.{output_image_extension}"
    )
    print(f"Saving {os.path.abspath(full_output_path)}")
    print(f"\tCurrent File: {os.path.basename(full_output_path)}")
    plt.savefig(full_output_path)
    plt.show()


def analyze(
    file: str,
    output_file: str,
) -> List[Tuple[float]]:
    """Reads the resistance data from the file and writes statistics about each channel to the output file

    Args:
        file (str): The file with raw data formatted as {r1},{r2},{r3},{time}, where r1 is the top and r3 is the bottom. The time slot is not read and is hence optional
        output_file (str): The output file to save the data to

    Returns:
        List[Tuple[float]]: (mean, median, std, minim, maxim) for each layer, where List[0] is layer 1 and List[2] is layer 3
    """
    resistance_top = []
    resistance_middle = []
    resistance_bottom = []

    with open(file, "r") as f:
        for line in f.readlines():
            parts = line.strip().split(",")
            if len(parts) != 3 and len(parts) != 4:
                continue  # Skip malformed lines
            try:
                r1 = float(parts[0])
                r2 = float(parts[1])
                r3 = float(parts[2])
                resistance_top.append(r1)
                resistance_middle.append(r2)
                resistance_bottom.append(r3)
            except ValueError:
                continue  # Skip lines that fail to parse

    with open(output_file, "w") as f:
        res = [resistance_top, resistance_middle, resistance_bottom]
        names = ["Top Resistor", "Middle Resistor", "Bottom Resistor"]

        results = []

        for r, n in zip(res, names):
            f.write(f"{n}\n")
            mean = statistics.mean(r)
            median = statistics.median(r)
            std = "NaN"
            try:
                std = statistics.stdev(r)
            except:
                std = "NaN"
            minim = min(r)
            maxim = max(r)
            f.write(
                f"  {mean = }\n  {median = }\n  {std = }\n  {minim = }\n  {maxim = }\n\n"
            )
            results.append((mean, median, std, minim, maxim))

            print(f"{n}")
            print(
                f"  {mean = }\n  {median = }\n  {std = }\n  {minim = }\n  {maxim = }\n"
            )


if __name__ == "__main__":
    out_dir = "../../test_files/"
    file = "../../test_files/25-07-01_Resistance-INITIAL_15-21-19.txt"

    plot(file, out_dir + "what", "Test")
    analyze(file, out_dir + "who.txt")
