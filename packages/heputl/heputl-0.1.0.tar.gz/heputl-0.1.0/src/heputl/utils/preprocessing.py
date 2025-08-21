import numpy as np

# two sided percentile clip
def is_outlier_percentile(points, percentile=99.9):
    diff = (100 - percentile) / 2.0
    minval, maxval = np.percentile(points, [diff, 100 - diff])
    return (points < minval) | (points > maxval)

# clip only the tail outliers
def is_outlier_percentile_tail(points, percentile=99.5):
    maxval = np.percentile(points,percentile)
    return points > maxval


def clip_outlier(data, percentile=99.9, one_sided=False):
    if one_sided:
        idx = is_outlier_percentile_tail(data,percentile)
    else:
        idx = is_outlier_percentile(data,percentile)
    return data[~idx]

