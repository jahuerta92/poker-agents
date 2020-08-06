import os

import pandas as pd
import numpy as np

from sklearn.feature_selection import VarianceThreshold

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import Birch, DBSCAN
from sklearn.cluster import KMeans, MiniBatchKMeans, MeanShift
from sklearn.cluster import OPTICS, SpectralClustering

from sklearn.preprocessing import MinMaxScaler

from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score

from sklearn.random_projection import SparseRandomProjection

from datetime import datetime

from features import FEATURES

CUSTOM = list(FEATURES.keys()) + ['TOTAL_RAKE']#, 'GAMES_PER_STEP']

MAX_CORR = 0.99
MIN_STD = 0.001
N_FEATURES = 15

RESULTS = 'results'
CLUSTER_RANGE = range(2, 5)
METHODS = {'agglomerative_clustering': AgglomerativeClustering,
           'birch': Birch,
           'kmeans': KMeans,
           'minibatch_kmeans': MiniBatchKMeans,
           'spectral_clustering': SpectralClustering}

CONTROL_REAL = {'etilEnipS', 'frimija26', 'LACHATATATA', 'Cocochamelle', 'Ryujin', 'D0ntCryBB', 'BTCto1M', 'Cesar Polska', 'rorro29', 'Hari86'}
CONTROL_BOTS = {'kelly59242'}#, 'Juju75002', 'renaud220', 'Zizou2885', 'patouf97320', 'Titeuf0713', 'titi84330', 'volpi84120'}

methods = {'{}_c{}'.format(k, i): alg(n_clusters=i) for k, alg in METHODS.items() for i in CLUSTER_RANGE}

methods.update({'mean_shift': MeanShift(),
                'optics': OPTICS()})
#methods.update({'dbscan_e{}'.format(i): DBSCAN(eps=i/10) for i in range(1, 10, 1)})

metrics = {'silhouette_score': silhouette_score,
           'davies_bouldin_score': davies_bouldin_score,
           'calinski_harabasz_score': calinski_harabasz_score}

clusters = {k: [] for k in methods.keys()}

metric_measures = pd.DataFrame(columns=list(methods.keys()), index=list(metrics.keys()))

data = pd.read_csv('player_processed.csv', index_col=0).dropna(how="all")


scaler = MinMaxScaler()
selector = VarianceThreshold(MIN_STD)
reductor = SparseRandomProjection(N_FEATURES, random_state=1)

data_scaled = pd.DataFrame(scaler.fit_transform(data),
                           columns=data.columns,
                           index=data.index)
data_scaled.fillna(0, inplace=True)
data_selected = selector.fit_transform(data_scaled)
data_selected = pd.DataFrame(data_selected,
                             columns=selector.transform(data_scaled.columns.values.reshape(-1, 1).T).flatten(),
                             index=data.index)
corr_matrix = data_selected.corr().abs()
upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
to_drop = [column for column in upper.columns if any(upper[column] > MAX_CORR)]

data_selected.drop(data_scaled[to_drop], axis=1, inplace=True)
if N_FEATURES == 0:
    data_reduced = data_selected
else:
    data_reduced = reductor.fit_transform(data_selected)

print(data_selected.columns)


for method, alg in methods.items():
    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    print('[{}] Running algorithm: {}'.format(now, method))
    cls = alg.fit_predict(data_reduced)
    clusters[method] = cls
    for metric, func in metrics.items():
        metric_measures.loc[metric, method] = func(data_reduced, cls)

clusters = pd.DataFrame(clusters, index=data.index)
clusters['suspected_bot'] = -1
clusters.loc[CONTROL_REAL, 'suspected_bot'] = 0
clusters.loc[CONTROL_BOTS, 'suspected_bot'] = 1

clusters.sort_values('suspected_bot', ascending=False).to_csv(os.path.join(RESULTS, 'clusters.csv'))
metric_measures.transpose().to_csv(os.path.join(RESULTS, 'cluster_metrics.csv'))