import rootlab_lib.vkx150_analysis as vkx150_analysis

file1_in = "../test_data/Height_Ex1.csv"
file1_out = "Height_Ex1"
file2_in = "../test_data/Height_Ex2.csv"
file2_out = "Height_Ex2"
comparison_out = "Height1_vs_Height2"
out_dir = "../test_files"


def test_single_heightmap():
    vkx150_analysis.heightmap(file1_in, file1_out, out_dir)


def test_compare_heightmaps():
    vkx150_analysis.compare_heightmaps(
        [file1_in],
        comparison_out,
        out_dir,
        # individual_colorbars=False,
        title="",
    )


if __name__ == "__main__":
    # test_single_heightmap()
    test_compare_heightmaps()
    pass
