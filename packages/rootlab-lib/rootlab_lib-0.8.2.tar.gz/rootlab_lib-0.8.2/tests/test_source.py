import rootlab_lib.source_meter_analysis as source_meter_analysis


def test_single():
    test_filepath = "../test_data/data2.csv"
    test_filepath = source_meter_analysis.extract_readings_to_resistance_series(
        test_filepath, "data/converted"
    )
    output_name = "data2_SOURCE-METER"
    source_meter_analysis.analyze(test_filepath, output_name, "../test_files/")


def test_many():
    files = [
        "../test_data/source_conv1.csv",
        "../test_data/source_conv2.csv",
        "../test_data/source_conv3.csv",
    ]

    converted = []

    for file in files:
        out = source_meter_analysis.voltage_readings_to_resistance_series(
            file, "data/converted"
        )
        converted.append(out)

    source_meter_analysis.analyze_concat(
        converted,
        "Concat-Files",
        "data/SourceMeter",
        title="Concatenated Damage 2 Data (First 2 Periods)",
        log_scale_y=True,
        mark_lines=True,
        switch_label_line_colors=["red", "blue", "green"],
    )


if __name__ == "__main__":
    # test_single()
    test_many()
