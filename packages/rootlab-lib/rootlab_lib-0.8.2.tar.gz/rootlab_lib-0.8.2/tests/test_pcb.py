import rootlab_lib.serial_reader as serial_reader
import rootlab_lib.voltage_analysis as voltage_analysis


def test_gather():
    out_dir = "../test_files/"
    serial_reader.gather_pcb_data(
        "COM3",
        "test",
        output_file_dir=out_dir,
        output_image_dir=out_dir,
    )


def test_plot():
    out_dir = "../test_files/"
    # _plot_analog_pin_data("../test_data/data5.txt", 2, output_dir=out_dir)
    # voltage_analysis._plot_original_voltage_pos_series("../test_data/data_ours.txt", plateaus=True, layer=0, output_series_dir=out_dir, output_plats_dir=out_dir, min_plateau_length=3)
    voltage_analysis._plot_inferred_positions("../test_data/data_his2.txt", threshold=3)


if __name__ == "__main__":
    # test_gather()
    # test_plot()
    serial_reader.gather_pcb_data(
        "COM3",
        "data_what",
        output_file_dir="../test_data",
        output_image_dir="../test_files",
    )
