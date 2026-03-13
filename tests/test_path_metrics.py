from draftnet.trajectories.path_metrics import path_error


def test_path_error_zero_for_identical_paths():
    path = [[0.0, 1.0], [2.0, 3.0]]
    assert path_error(path, path) == 0.0
