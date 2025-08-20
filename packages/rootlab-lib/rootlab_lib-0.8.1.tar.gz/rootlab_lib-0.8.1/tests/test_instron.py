import rootlab_lib.instron_analysis as instron_analysis

avail_paths = [
    "../test_data/Instron1.csv",
    "../test_data/Instron2.csv",
    "../test_data/Instron3.csv",
    "../test_data/Instron4.csv",
    "../test_data/Instron5.csv",
]


def test_single():
    instron_analysis.single_stress_strain(avail_paths[0])


def test_many_no_labels():
    instron_analysis.plot_multiple_stress_strain(avail_paths, "Many-Test")


if __name__ == "__main__":
    test_many_no_labels()
