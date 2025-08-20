import rootlab_lib.voltage_analysis as voltage_analysis
import rootlab_lib.serial_reader as serial_reader


# Tests the serial port reader using a mock instance
def test_reader_mock():
    out_dir = "../test_files/"
    serial_reader.gather_data(
        0, "test", output_file_dir=out_dir, output_image_dir=out_dir, mock=True
    )


# These are the values used as defaults for the series, heatmap, and regression functions
threshold = voltage_analysis.RECOMMENDED_THRESHOLD
min_plateau_length = voltage_analysis.RECOMMENDED_MIN_PLATEAU_LENGTH
min_gap_length = voltage_analysis.RECOMMENDED_MIN_GAP_LENGTH


# Tests the
def test_plot_suite():
    filepath = "../test_data/data1.txt"
    out_dir = "../test_files/"

    voltage_analysis.series(
        filepath,
        output_plats_dir=out_dir,
        output_series_dir=out_dir,
        title_default="Test Data",
        title_plateaus="Test Data",
    )
    voltage_analysis.series(
        filepath,
        output_plats_dir=out_dir,
        output_series_dir=out_dir,
        title_default="Test Data",
        title_plateaus="Test Data",
        plateaus=True,
    )
    pass
    voltage_analysis.heatmap(filepath, output_dir=out_dir, title="Test Data")
    voltage_analysis.regression(filepath, output_dir=out_dir, title="Test Data")
    voltage_analysis.regression(
        filepath, output_dir=out_dir, title="Test Data", intercept=True
    )


def test_weird():
    filepath = "../test_data/weird_behavior.txt"
    out_dir = "../test_files/"

    voltage_analysis.series(
        filepath,
        output_plats_dir=out_dir,
        output_series_dir=out_dir,
        title_default="Weird Behaving Data",
        title_plateaus="Weird Behaving Data",
    )
    voltage_analysis.series(
        filepath,
        output_plats_dir=out_dir,
        output_series_dir=out_dir,
        title_default="Weird Behaving Data",
        title_plateaus="Weird Behaving Data",
        plateaus=True,
        threshold=0.2,
    )
    pass
    voltage_analysis.heatmap(
        filepath, output_dir=out_dir, title="Weird Behaving Data", threshold=0.2
    )
    voltage_analysis.regression(
        filepath, output_dir=out_dir, title="Weird Behaving Data", threshold=0.2
    )
    voltage_analysis.regression(
        filepath,
        output_dir=out_dir,
        title="Weird Behaving Data",
        intercept=True,
        threshold=0.2,
    )


if __name__ == "__main__":
    # test_reader_mock()
    # test_plot_suite()
    test_weird()
    pass
