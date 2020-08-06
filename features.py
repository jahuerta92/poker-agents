from tslearn.clustering import TimeSeriesKMeans, silhouette_score
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from tslearn.utils import to_time_series, to_time_series_dataset
from tslearn.metrics import dtw

import pathos.multiprocessing as mp
import numpy as np
import pandas as pd


def median_diff(series):
    x = np.diff(series)
    x = np.median(x)
    return x


def losses(series):
    x = np.diff(series)
    x = np.where(x > 0, 0, x)
    nz = np.count_nonzero(x)
    x = np.sum(x) / nz
    return x


def loss_ratio(series):
    x = np.diff(series)
    x = np.where(x > 0, 0, x)
    x = np.count_nonzero(x) / len(series)
    return x


def negative_turning_point_ratio(series):
    x = np.diff(series)
    x = np.sum(x[1:] * x[:-1] < 0) / len(series)
    return x


def max_win(series):
    x = np.diff(series)
    x = np.max(x)
    return x


FEATURES = {'gain median diff': median_diff,
            'avg losses': losses,
            'loss ratio': loss_ratio,
            'gain negative turning point ratio': negative_turning_point_ratio,
            'max win ammount': max_win}


def extract_features(player, player_name):
    gain = player['gain_series']['gain']

    row = dict()
    for k, fn in FEATURES.items():
        row[k] = fn(gain)

    return pd.DataFrame(row,
                        columns=list(FEATURES.keys()),
                        index=[player_name])


def get_distance_matrix(numpy_array):
    sc = TimeSeriesScalerMeanVariance()
    X_s = sc.fit_transform(to_time_series_dataset(numpy_array))

    size = len(X_s)

    idx = [(i, j) for i in range(0, size) for j in range(i + 1, size)]

    def calc_dtw(my_idx):
        i, j = my_idx
        return dtw(X_s[i], X_s[j])

    with mp.Pool(mp.cpu_count()-1) as p:
        distances = p.map(calc_dtw, idx)

    dm = np.zeros(shape=(size, size))
    for (i, j), v in zip(idx, distances):
        dm[i, j] = v
        dm[j, i] = v

    return dm
