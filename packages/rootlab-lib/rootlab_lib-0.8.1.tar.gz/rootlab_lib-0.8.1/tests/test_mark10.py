import rootlab_lib.mark10_analysis as mark10_analysis


def single():
    time, force = mark10_analysis.parse_log_file("../test_data/sample_mark10.log")
    mark10_analysis.plot_single_stress_strain_from_extracted(
        time,
        force,
        0.3,
        3,
        10,
        500,
        "sample_mark10",
        plot_modulus_line=True,
        mark_yield_point_as_max=True,
        strain_to_percent=True,
        x_label="Tensile Strain (%)",
        legend=True,
    )


# single()


def multiple():
    files = [
        "../test_data/mark10_1.log",
        "../test_data/mark10_2.log",
        "../test_data/mark10_3.log",
        "../test_data/mark10_4.log",
    ]

    mark10_analysis.plot_multiple_stress_strains(
        files,
        [0.3, 0.3, 0.3, 0.3],
        [3, 3, 3, 3],
        10,
        500,
        "sample_mark10",
    )


multiple()
