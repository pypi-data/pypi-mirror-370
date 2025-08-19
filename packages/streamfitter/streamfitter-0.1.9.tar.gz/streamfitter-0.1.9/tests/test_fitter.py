from pytest import approx

from streamfitter.fitter import RunningStats


def test_running_stats():
    values = [
        1.488873677,
        1.559985294,
        1.67092815,
        1.605115185,
        1.622028945,
        1.469919296,
        1.408920926,
        1.649979198,
        1.504577736,
        1.563891939,
    ]

    running_stats = RunningStats()
    for value in values:
        running_stats.add(value)

    print(running_stats.stddev(), running_stats.mean(), running_stats.num_values(), running_stats.variance())

    assert running_stats.num_values() == 10
    assert running_stats.stddev() == approx(0.085021756)
    assert running_stats.variance() == approx(0.007228699)
    assert running_stats.mean() == approx(1.554422035)
    assert running_stats.stderr_variance() == approx(0.003407641)
    assert running_stats.stderr_stddev() == approx(0.02003982)
