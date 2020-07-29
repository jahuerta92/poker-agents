import os

import pandas as pd
import numpy as np

from sklearn.feature_selection import VarianceThreshold

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import Birch, DBSCAN
from sklearn.cluster import KMeans, MeanShift
from sklearn.cluster import OPTICS, SpectralClustering

from sklearn.preprocessing import MinMaxScaler

from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score

from datetime import datetime

RESULTS = 'results'
CLUSTER_RANGE = range(2, 12, 2)
METHODS = {'agglomerative_clustering': AgglomerativeClustering,
           'birch': Birch,
           'kmeans': KMeans,
           'spectral_clustering': SpectralClustering}

methods = {'{}_c{}'.format(k, i): alg(n_clusters=i) for k, alg in METHODS.items() for i in CLUSTER_RANGE}

methods.update({'agglomerative_clustering': AgglomerativeClustering(),
                'dbscan': DBSCAN(),
                'mean_shift': MeanShift(),
                'optics': OPTICS()})

metrics = {'silhouette_score': silhouette_score,
           'davies_bouldin_score': davies_bouldin_score,
           'calinski_harabasz_score': calinski_harabasz_score}

clusters = {k: [] for k in methods.keys()}

metric_measures = pd.DataFrame(columns=list(methods.keys()), index=list(metrics.keys()))

data = pd.read_csv('player_processed.csv', index_col=0).dropna(how="all")

scaler = MinMaxScaler()
selector = VarianceThreshold()

data_scaled = scaler.fit_transform(data)
data_selected = selector.fit_transform(data_scaled)
where_are_NaNs = np.isnan(data_selected)
data_selected[where_are_NaNs] = 0

for method, alg in methods.items():
    now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    print('[{}] Running algorithm: {}'.format(now, method))
    cls = alg.fit_predict(data_selected)
    clusters[method] = cls
    for metric, func in metrics.items():
        metric_measures.loc[metric, method] = func(data_selected, cls)

pd.DataFrame(clusters, index=data.index).to_csv(os.path.join(RESULTS, 'clusters.csv'))
metric_measures.transpose().to_csv(os.path.join(RESULTS, 'cluster_metrics.csv'))