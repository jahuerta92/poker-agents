import os
import pickle
import tsfel
import re

import pandas as pd
import numpy as np
import scipy as sp

from datetime import datetime


DATASET_DIR = './dataset'
STANDARD_RANGE = [0, 0.3, 0.6, 1, 3, 6, 10, 30, 60, 100, 300, 600, 1000, 3000, 6000]
COLS_ROI = ['ROI_{}'.format(n) for n in STANDARD_RANGE] + ['ROI_Other']
COLS_RAKE = ['RAKE_{}'.format(n) for n in STANDARD_RANGE] + ['RAKE_Other']
COLS_GAMES = ['GAMES_{}'.format(n) for n in STANDARD_RANGE] + ['GAMES_Other']

CFG = tsfel.get_features_by_domain()
TSFEL_COLS = ['{}'.format(n) for n in tsfel.time_series_features_extractor(CFG, np.random.rand(10), fs=1).columns]
COLS_GAIN = ['GAIN_{}'.format(n[2:]) for n in TSFEL_COLS]
COLS_GPD = ['GAIN_{}'.format(n[2:]) for n in TSFEL_COLS]

COIN_FINDER = re.compile(r'[^\d.]+')

files = [f for f in os.walk(DATASET_DIR)][0][2]


def diff(ts):
    return [t_1 - t_0 for t_0, t_1 in zip(ts[:-1], ts[1:])]


def safe_division(n, d):
    return n / d if d else 0


def approximate(games, roi, rake, game_value, standardized_range):
    standard_dict = {k: [] for k in standardized_range}
    roi_dict = {k: -1 for k in standardized_range}
    games_dict = {k: -1 for k in standardized_range}
    rake_dict = {k: -1 for k in standardized_range}
    roi_dict['Other'] = -1
    rake_dict['Other'] = -1
    games_dict['Other'] = -1

    if game_value[-1] == 'Other':
        other_g, other_roi, other_rake = games[-1], roi[-1], rake[-1]
        games, roi, rake = games[:-1], roi[:-1], rake[:-1]
        game_value = game_value[:-1]

        roi_dict['Other'] = other_roi
        rake_dict['Other'] = other_rake
        games_dict['Other'] = other_g

    game_value = [float(COIN_FINDER.sub('', v)) for v in game_value]

    for g, ro, ra, v in zip(games, roi, rake, game_value):
        k = min(standardized_range, key=lambda x: abs(x - v))
        standard_dict[k].append((g, ro, ra))
    for k, v in standard_dict.items():
        if v:
            g_0 = 0
            avg_ro = 0
            avg_ra = 0
            for g, ro, ra in v:
                if ro is None:
                    ro = 0
                g_0 += g
                avg_ro += ro * g
                avg_ra += ra * g
            avg_ro /= g_0
            avg_ra /= g_0
            roi_dict[k] = avg_ro
            rake_dict[k] = avg_ra
            games_dict[k] = g_0

    return roi_dict, rake_dict, games_dict


def get_stats(pi, file):
    player_name = file[:-4]

    gain = [float(i) for i in pi['gain_series']['gain']]
    n_games = pi['gain_series']['n_games']
    dates = [datetime.fromtimestamp(t / 1000) for t in pi['gain_series']['date']]
    date_diff = diff(dates)
    games_diff = diff(n_games)
    games_per_day = [safe_division(g, d.days * 86400 + d.seconds) * 86400 for g, d in zip(games_diff, date_diff)]

    features_gain = tsfel.time_series_features_extractor(CFG, gain, fs=1, verbose=0)[TSFEL_COLS]
    features_gain.columns = COLS_GAIN
    features_gain.index = [player_name]

    features_gpd = tsfel.time_series_features_extractor(CFG, games_per_day, fs=1, verbose=0)[TSFEL_COLS]
    features_gpd.columns = COLS_GPD
    features_gpd.index = [player_name]

    roi, rake, games = approximate(pi['rake_series']['n_games'],
                                   pi['rake_series']['roi'],
                                   pi['rake_series']['rake'],
                                   pi['rake_series']['game_value'],
                                   STANDARD_RANGE)

    features_roi = pd.DataFrame(roi, index=[player_name])
    features_roi.columns = COLS_ROI
    features_rake = pd.DataFrame(rake, index=[player_name])
    features_rake.columns = COLS_RAKE
    features_games = pd.DataFrame(games, index=[player_name])
    features_games.columns = COLS_GAMES

    return pd.concat([features_gain, features_gpd, features_roi, features_rake, features_games], axis=1)


player_set = pd.DataFrame(columns=COLS_GAIN + COLS_GPD + COLS_ROI + COLS_RAKE + COLS_GAMES)
max_players = len(files)

for i, ff in enumerate(files):
    with open(os.path.join(DATASET_DIR, ff), 'rb') as f:
        player_info = pickle.load(f)
        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        progress = '{}/{} {:.2f}%'.format(i+1, max_players, (i+1) * 100 / max_players)

        try:
            row = get_stats(player_info, ff)
            player_set = player_set.append(row)
            print('[{}] (Progress: {}) --- Player from file {} added'.format(now, progress, ff))
        except:
            print('[{}] (Progress: {}) --- Ignored file {} on failure'.format(now, progress, ff))


player_set.to_csv('player_processed.csv')
