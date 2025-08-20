"""The main way to interact with data outputted by the source meter in lab."""

import numpy as np
from typing import Tuple, List
import time as t
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.gridspec as gridspec

import cv2
from scipy.ndimage import median_filter, gaussian_filter


def heightmap(
    input_filepath: str,
    output_name: str,
    output_dir: str = "./data/Heightmaps",
    output_image_ext: str = "png",
    reading_flag_name: str = "Height:",
    horizontal_axis_label: str = "",
    vertical_axis_label: str = "",
    title: str = "VK-x150 Height Heatmap",
    height_unit: str = "nm",
    iterations: int = 0,
    method: str = "none",
    flatten: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    figsize: Tuple[int, int] = (12, 9),
) -> List[List[float]]:
    """
    Writes and plots source meter resistance readings vs time and saves a .png of the data.

    Args:
        input_filepath (str): The name of the input file with the data to be read. This should be a csv file.
        output_name (str): Descriptive name used in output filename. The current date and time will be combined with this. Do not include the extension or path
        output_dir (str, optional): The path to be used for the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): The image extension to be used for the output image. You need not include the period. Defaults to 'png'
        reading_flag_name (str, optional): The string to watch for when the actual data is emitted. Defaults to 'Height:'
        horizontal_axis_label (str, optional): The string to use for the x-axis label. Defaults to an empty string
        vertical_axis_label (str, optional): The string to use for the y-axis label. Defaults to an empty string
        title (str, optional): The title of the plot. Defaults to 'VK-x150 Height Heatmap'
        height_unit (str, optional): The unit of the height values reported. Defaults to an "nm" (nanometers)
        iterations (int, optional): Determines how many iterations of normalization should occur. This is not lossless and is performance intensive. Cannot be negative (will be clamped to [0, inf]). Defaults to 0
        method (str, optional): Determines the iteration algorithm {"none", "gaussian", "median", "bilateral"}. Defaults to "none"
        flatten (bool, optional): Determines whether or not the program should attempt to correct tilt. This is experimental, use the analyzer software. Defaults to False
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        figsize (Tuple[int, int], optional): The figsize to use for the figure. Defaults to (12,9).

    Returns:
        List[List[float]]: (height_data)
    """
    assert method in {"none", "gaussian", "median", "bilateral"}

    # Prep the file system for reading and writing
    if not os.path.isfile(input_filepath):
        print("Error: Input filepath is not a valid file")
        return
    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)

    output_data = f"{curr_date}_{output_name}_{curr_time}.txt"
    output_data_path = os.path.join(output_dir, output_data)

    # Initialize the row vectors to hold the differently sized data
    garbage = []
    heights = []
    switch_found = False

    # open the csv file and read in the data until the row length changes
    with open(input_filepath, "r") as f1:
        try:
            reader = csv.reader(f1)
            switch_found = False
            for row in reader:
                if not switch_found:
                    if "".join(row).startswith(reading_flag_name):
                        switch_found = True
                    garbage.append(row)
                    continue  # skip this line and keep going
                # collect height data after the marker
                heights.append(row)
        except Exception as e:
            print(f"Fatal error reading input csv file: {e}")
            return

        try:
            for i, row in enumerate(heights):
                heights[i] = np.array(
                    [float(value) for value in row if value.strip() != ""],
                    dtype=np.float32,
                )

            # Get the minimum height and shift the map to be zero'd at that height
            min_height = np.amin(heights)
            for i, row in enumerate(heights):
                heights[i] = np.array(
                    [value - min_height for value in row], dtype=np.float32
                )

            height_matrix = np.array(heights, dtype=np.float32)

            if flatten:
                height_matrix = _correct_tilt(height_matrix)
            iterations = max(0, iterations)

            if method == "gaussian":
                for idx in range(iterations):
                    height_matrix = gaussian_filter(height_matrix, sigma=1.0)
                    print(
                        f"{method} iteration {idx + 1}: (min, max) = ({np.amin(height_matrix), np.amax(height_matrix)})"
                    )

            elif method == "median":
                for idx in range(iterations):
                    height_matrix = median_filter(height_matrix, size=3)
                    print(
                        f"{method} iteration {idx + 1}: (min, max) = ({np.amin(height_matrix), np.amax(height_matrix)})"
                    )

            elif method == "bilateral":
                prev_min_height = np.amin(height_matrix)
                prev_max_height = np.amax(height_matrix)
                height_matrix = cv2.normalize(
                    height_matrix, None, 0, 255, cv2.NORM_MINMAX
                )
                height_matrix = np.float32(height_matrix)
                for idx in range(iterations):
                    height_matrix = cv2.bilateralFilter(
                        height_matrix, d=5, sigmaColor=50, sigmaSpace=5
                    )
                    print(
                        f"{method} iteration {idx + 1}: (min, max) = ({np.amin(height_matrix), np.amax(height_matrix)})"
                    )
                height_matrix = cv2.normalize(
                    height_matrix,
                    None,
                    prev_min_height,
                    prev_max_height,
                    cv2.NORM_MINMAX,
                )
                height_matrix = np.float32(height_matrix)

            # Final normalization
            height_matrix -= np.amin(height_matrix)

            with open(output_data_path, "w") as f:
                print(f"Saving {os.path.abspath(output_data_path)}")
                for row in height_matrix:
                    for i, val in enumerate(row):
                        if i != len(row):
                            f.write(f"{val},")
                        else:
                            f.write(f"{val}")
                    f.write("\n")

            # Get the final min and max values for a correct cbar scale
            min_height = np.amin(height_matrix)
            max_height = np.amax(height_matrix)

            fig, ax = plt.subplots(figsize=figsize)
            im = ax.imshow(
                height_matrix, vmin=min_height, vmax=max_height, cmap="viridis"
            )

            # Labels and axis settings
            ax.set_title(title, fontsize=title_font_size, pad=20)
            ax.set_xlabel(horizontal_axis_label, fontsize=axis_font_size)
            ax.set_ylabel(vertical_axis_label, fontsize=axis_font_size)
            ax.set_xticks([])
            ax.set_yticks([])

            # Colorbar
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label(
                f"Height {f"({height_unit})" if height_unit != "" else ""}", fontsize=15
            )
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits(
                (-3, 3)
            )  # Use scientific notation outside this range
            formatter.set_useOffset(False)

            cbar.ax.yaxis.set_major_formatter(formatter)
            cbar.ax.tick_params(labelsize=15)

            plt.tight_layout()
            print(f"Saving {os.path.abspath(output_img_path)}")
            print(f"\tCurrent File: {os.path.basename(output_img_path)}")
            plt.savefig(output_img_path)
            plt.show()

            return ()
        except Exception as e:
            print(f"Fatal error plotting height data: {e}")
            return


def compare_heightmaps(
    input_filepaths: List[str],
    output_name: str,
    output_dir: str = ".",
    output_image_ext: str = "png",
    labels: List[str] = None,
    reading_flag_name: str = "Height:",
    horizontal_axis_label: str = "",
    vertical_axis_label: str = "",
    title: str = "Comparison of VK-x150 Height Heatmaps",
    height_unit: str = "nm",
    method: str = None,
    iterations: int = 0,
    flatten: bool = False,
    individual_colorbars: bool = False,
    axis_font_size: int = 25,
    title_font_size: int = 30,
    figsize: Tuple[int, int] = (12, 9),
) -> List[np.ndarray]:
    """
    Plots multiple heightmaps side-by-side with a shared colorbar.

    Args:
        input_filepaths (List[str]): List of paths to the height CSV files.
        output_name (str): Descriptive name used in output filename. The current date and time will be combined with this. Do not include the extension or path
        output_dir (str, optional): The path to be used for the output image. Defaults to '.', the current directory
        output_image_ext (str, optional): The image extension to be used for the output image. You need not include the period. Defaults to 'png'
        labels (List[str], optional): Titles for each subplot. Defaults to Map {idx}.
        reading_flag_name (str, optional): Marker in CSV indicating start of data. Defaults to "Height:".
        horizontal_axis_label (str, optional): Label for the x-axis. Defaults to "".
        vertical_axis_label (str, optional): Label for the y-axis. Defaults to "".
        title (str, optional): Title of the overall figure. Defaults to "Comparison of VK-x150 Height Heatmaps".
        height_unit (str, optional): Unit to append to the colorbar label. Defaults to "nm" (nanometers).
        method (str, optional): Asserts that this is one of {None, "none", "gaussian", "median", "bilateral"}. Defaults to None.
        iterations (int, optional): Number of smoothing iterations. Defaults to 0.
        flatten (bool, optional): Whether to apply tilt correction. This is experimental, use the analyzer software. Defaults to False.
        individual_colorbars (bool, optional): Whether to enforce a global colorbar or use individual ones per plot
        axis_font_size (int, optional): The fontsize to use for the plot's axes. Defaults to 25.
        title_font_size (int, optional): The fontsize to use for the plot title. Defaults to 30.
        figsize (Tuple[int, int], optional): Size of the figure. Defaults to (12, 9).

    Returns:
        List[np.ndarray]: List of processed height maps (as numpy arrays).
    """
    assert method in {None, "none", "gaussian", "median", "bilateral"}, "Invalid method"
    assert all(
        os.path.isfile(p) for p in input_filepaths
    ), "All input paths must be valid files"

    os.makedirs(output_dir, exist_ok=True)
    curr_date, curr_time = t.strftime("%y-%m-%d"), t.strftime("%H-%M-%S")
    output_img = f"{curr_date}_{output_name}_{curr_time}.{output_image_ext}"
    output_img_path = os.path.join(output_dir, output_img)

    height_matrices = []
    processed_filenames = []

    for filepath in input_filepaths:
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            heights = []
            switch_found = False
            for row in reader:
                if not switch_found:
                    if "".join(row).startswith(reading_flag_name):
                        switch_found = True
                    continue
                heights.append(row)

        heights_clean = []
        for row in heights:
            try:
                parsed = np.array(
                    [float(v) for v in row if v.strip() != ""], dtype=np.float32
                )
                heights_clean.append(parsed)
            except ValueError:
                continue

        min_height = np.amin(heights_clean)
        heights_zeroed = [row - min_height for row in heights_clean]
        height_matrix = np.array(heights_zeroed, dtype=np.float32)

        if flatten:
            height_matrix = _correct_tilt(height_matrix)

        iterations = max(0, iterations)

        if method == "gaussian":
            for _ in range(iterations):
                height_matrix = gaussian_filter(height_matrix, sigma=1.0)
        elif method == "median":
            for _ in range(iterations):
                height_matrix = median_filter(height_matrix, size=3)
        elif method == "bilateral":
            pre_min, pre_max = np.amin(height_matrix), np.amax(height_matrix)
            height_matrix = cv2.normalize(
                height_matrix, None, 0, 255, cv2.NORM_MINMAX
            ).astype(np.float32)
            for _ in range(iterations):
                height_matrix = cv2.bilateralFilter(
                    height_matrix, d=5, sigmaColor=50, sigmaSpace=5
                )
            height_matrix = cv2.normalize(
                height_matrix, None, pre_min, pre_max, cv2.NORM_MINMAX
            ).astype(np.float32)

        height_matrix -= np.amin(height_matrix)
        height_matrices.append(height_matrix)

        # Save processed matrix to file
        base = os.path.basename(filepath).rsplit(".", 1)[0]
        processed_name = f"{curr_date}_{base}_{curr_time}.txt"
        processed_path = os.path.join(output_dir, processed_name)
        processed_filenames.append(processed_path)
        with open(processed_path, "w") as f_out:
            for row in height_matrix:
                f_out.write(",".join(map(str, row)) + "\n")

    # Plotting
    n = len(height_matrices)
    fig_width = figsize[0] * n
    fig_height = figsize[1]
    fig, axes = plt.subplots(1, n, figsize=(fig_width, fig_height), dpi=100)

    # Always work with list of axes
    if n == 1:
        axes = [axes]

    global_min = min(np.amin(hm) for hm in height_matrices)
    global_max = max(np.amax(hm) for hm in height_matrices)

    # Plot each heatmap
    for i, (ax, hm) in enumerate(zip(axes, height_matrices)):
        vmin, vmax = (
            (np.amin(hm), np.amax(hm))
            if individual_colorbars
            else (global_min, global_max)
        )
        im = ax.imshow(hm, vmin=vmin, vmax=vmax, cmap="viridis")
        ax.set_title((labels[i] if labels else f"Map {i+1}"), fontsize=16)
        ax.set_xticks([])
        ax.set_yticks([])

        if individual_colorbars:
            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label(
                f"Height {f'({height_unit})' if height_unit else ''}", fontsize=20
            )
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-3, 3))
            formatter.set_useOffset(False)
            cbar.ax.yaxis.set_major_formatter(formatter)
            cbar.ax.tick_params(labelsize=10)

    # Shared colorbar if needed
    if not individual_colorbars:
        im = axes[-1].images[0]  # get last image, no extra plotting
        cbar = fig.colorbar(
            im, ax=axes, orientation="vertical", fraction=0.015, pad=0.02
        )
        cbar.set_label(
            f"Height {f'({height_unit})' if height_unit else ''}", fontsize=20
        )
        formatter = ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-3, 3))
        formatter.set_useOffset(False)
        cbar.ax.yaxis.set_major_formatter(formatter)
        cbar.ax.tick_params(labelsize=13)

    # Titles and layout
    fig.suptitle(title, fontsize=title_font_size, x=0.5, y=0.995)
    fig.supxlabel(horizontal_axis_label, fontsize=axis_font_size)
    fig.supylabel(vertical_axis_label, fontsize=axis_font_size)

    # Clean layout
    fig.subplots_adjust(left=0.01, right=0.95, top=0.92, bottom=0.08, wspace=0.05)

    print(f"Saving {os.path.abspath(output_img_path)}")
    print(f"\tCurrent File: {os.path.basename(output_img_path)}")
    plt.savefig(output_img_path, dpi=100)  # Save as-is with proper layout
    plt.show()

    return height_matrices


def _correct_tilt(height_matrix: np.ndarray) -> np.ndarray:
    """Corrects plane tilt. Lossless and imperfect, use VKX150 software when available! Developed with ChatGPT

    Args:
        height_matrix (np.ndarray): A matrix of height data

    Returns:
        np.ndarray: The corrected matrix of height data
    """
    rows, cols = height_matrix.shape
    X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
    Z = height_matrix

    # Flatten for least squares
    A = np.c_[X.ravel(), Y.ravel(), np.ones(X.size)]
    C, _, _, _ = np.linalg.lstsq(A, Z.ravel(), rcond=None)  # fit Z = ax + by + c
    plane = C[0] * X + C[1] * Y + C[2]

    # Subtract the plane from the data
    return Z - plane
