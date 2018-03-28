from modules.aux_fn import *
import copy
import scipy
# from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans

def run_dual_clustering_on_node_range(data, r, nclusters, nclusters_final, final_centroids=None):
    """
     Run dual clustering on specified node range.
     The data from a node is an array of arrays
    (for each day there is an array of 24 values).
    The clusters are calculated separately for each node and added to the cluster array.
    Then, there is another clustering on this cluster array which returns
    the final clusters for all the network (consumer types in the network)
    :param r:
    :param nclusters:
    :param nclusters_final:
    :return:
    """

    centroid_vect = []
    raw_data_vect = []

    if r is None:
        r = list(range(0, len(data)))

    print("node range: ", r)

    # run clustering for each node and save clusters into array
    for node_id in r:
        res = run_clustering_on_node_id(data, node_id, nclusters)
        centroid_vect.append(res)

    centroid_vect = get_array_of_arrays(centroid_vect)
    raw_data_vect = get_array_of_arrays(raw_data_vect)

    n_clusters_total = len(centroid_vect)
    centroids_np = np.array(centroid_vect)

    # run clustering again for the previous clusters
    res = get_centroids(centroids_np, nclusters_final, final_centroids)
    centroids_np = np.array(res)

    return centroids_np


def get_centroids(data, n_clusters=8, init=None):
    if n_clusters is not None:
        if init is not None:
            kmeans = KMeans(n_clusters=n_clusters, init=init)
        else:
            kmeans = KMeans(n_clusters=n_clusters)
    else:
        n_clusters_range = range(2, 10)
        max_silhouette_avg = [0] * len(n_clusters_range)
        # data = np.array(data)
        for (i, k) in enumerate(n_clusters_range):
            kmeans = KMeans(n_clusters=k)
            a = kmeans.fit_predict(data)
            # print(data.shape)
            # print(a)
            # The silhouette_score gives the average value for all the samples.
            # This gives a perspective into the density and separation of the formed
            # clusters
            silhouette_avg = silhouette_score(data, a)
            # print("For n_clusters =", k,
            #       "The average silhouette_score is :", silhouette_avg)
            max_silhouette_avg[i] = silhouette_avg

        n_clusters = n_clusters_range[max_silhouette_avg.index(max(max_silhouette_avg))]
        kmeans = KMeans(n_clusters=n_clusters)
    a = kmeans.fit(data)
    centroids = a.cluster_centers_
    return centroids

def run_clustering_on_node_id(data, node_id, nclusters, partial_sample_until_id=None, add_deviation_value=None):
    """
    Run clustering on specified node. The data from the node is an array of arrays
    (for each day there is an array of 24 values)
    The result is the consumer behaviour over the analyzed time frame
    :param node_id:
    :param nclusters:
    :return:
    """

    data = copy.deepcopy(data[node_id]["series"])
    if partial_sample_until_id is not None:
        data = data[0:partial_sample_until_id]
        if add_deviation_value is not None:
            data[partial_sample_until_id] += add_deviation_value

    if nclusters is not None and nclusters > len(data):
        print("node " + str(node_id) + "nclusters > len(data): " + str(nclusters) + "," + str(len(data)))
        return [], None, data
    res = get_centroids(data, nclusters)
    centroids = res
    nc = len(centroids)
    centroids_np = np.array(centroids)

    return centroids_np


def run_clustering_for_each_node_and_concat(data, r, nclusters):
    """
    Run clustering on specified node range. The data from a node is an array of arrays
    (for each day there is an array of 24 values). The clusters are calculated
    separately for each node and added to the cluster array (various consumer
    behaviours in the network)
    :param start:
    :param end:
    :param nclusters:
    :return:
    """
    centroid_vect = []
    raw_data_vect = []

    if r is None:
        r = list(range(0, len(data)))

    # run clustering for each node and save clusters into array
    for node_id in r:
        res = run_clustering_on_node_id(node_id, nclusters)
        centroid_vect.append(res)

    centroid_vect = get_array_of_arrays(centroid_vect)

    centroids_np = np.array(centroid_vect)
    return centroids_np


def run_clustering_for_all_nodes_at_once(data, r, nclusters, n_data=None):
    """
    Run clustering on specified node. The data from the node is an array of arrays
    (for each day there is an array of 24 values)
    The result is the consumer behaviour over the analyzed time frame
    :param n_data: the number of samples to be used from the data
    :param node_id:
    :param nclusters:
    :return:
    """

    if r is None:
        r = list(range(0, len(data)))

    res_data = []
    for id in r:
        for (i, s) in enumerate(data[id]["series"]):
            if n_data is not None:
                if i < n_data:
                    res_data.append(s)
            else:
                res_data.append(s)

    res_data = np.array(res_data)
    res = get_centroids(res_data, nclusters)
    centroids = res
    centroids_np = np.array(centroids)

    return centroids_np