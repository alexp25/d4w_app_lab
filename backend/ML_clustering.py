import csv
import json

import numpy as np
import time

from data_class import DataClass
import scipy
# from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans

import numpy as np
import math
import random

from math import sqrt

from os import listdir
from os.path import isfile, join

import copy

import itertools


import matplotlib.pylab as plt




from modules.data.constants import Constants
from modules import aux_fn as ml
from modules.dynamic_clustering import ClusteringClass
dcluster = ClusteringClass()
dcluster2 = ClusteringClass()


class ML_clustering:
    def __init__(self, use_scikit=True):
        self.dc = DataClass()
        self.data = []
        self.node_data = []
        self.assignments_series = []
        self.min_final = None
        self.max_final = None
        self.files = []
        self.n_nodes = 0

        self.n_series_disp = 10
        # self.i_run = int(self.n_nodes/2)
        self.i_run2 = 1
        # self.use_previous_cluster_data = False
        self.centroids = None
        self.final_centroids = None
        self.final_clusters = None
        self.clusters = []
        self.node_centroids = []

        self.partial_sample_index = 0
        self.use_scikit = use_scikit

    def set_lib(self, use_scikit):
        self.use_scikit = use_scikit

    def init(self):
        self.final_centroids = None
        self.centroids = None
        self.read_data()

        # self.assign_class_to_nodes()

    def assign_class_to_nodes(self):
        print("machine learning: assign class to nodes")
        assignment_index = 0
        node_id = 0
        for node in self.node_data:
            cluster = 0
            # get average cluster index for node

            n_series_node = len(self.data[node_id]["series"])

            # get the assignments for the time series corresponding to the node
            node_assignments = [None] * n_series_node
            for i in range(n_series_node):
                # cluster += self.assignments_series[assignment_index]["cluster"]
                if assignment_index < len(self.assignments_series):
                    node_assignments[i] = self.assignments_series[assignment_index]["cluster"]
                    assignment_index += 1

            # node["class"] = int(cluster/n_series_node)
            # get class with max number of occurences in list
            node["class"] = max(node_assignments, key=node_assignments.count)

            node["demand"] = int(self.clusters[node["class"]]["avg_demand"])
            node["priority"] = int(self.clusters[node["class"]]["priority"])

            # print(node)
            node_id += 1
        return self.node_data

    def get_info(self, node_id=None):
        if node_id is None:
            info = {
                "n_nodes": len(self.node_data),
                "nodes": self.node_data
            }
        else:
            info = self.node_data[node_id]
        return info



    def read_data(self, folder="sensors"):
        """
            read data from files
            each file has the data for a measurement node
            over a time frame of n days, for every hour
        :return:
        """
        self.data = []
        self.node_data = []
        print(folder)

        self.files = [f for f in listdir("data/"+folder) if isfile(join("data/"+folder, f))]
        print(self.files)
        self.n_nodes = len(self.files)

        for i, f in enumerate(self.files[0:self.n_nodes]):
            # print(str(i) + ". reading: " + f)
            fdata = self.dc.read_data(join("data/"+folder+"/", f))
            data = copy.copy(fdata)
            self.data.append(data)
            node = Constants.NODE_MODEL
            node["id"] = i
            self.node_data.append(copy.deepcopy(node))

        # print('first')
        # print(self.data[0])
        # print('second')
        # print(self.data[1])

    def get_raw_data(self, node=0):
        t_start = time.time()
        # self.read_data()
        data = self.data[node]
        imax = data["series"].shape[0]
        imax_all = 0

        for i in range(len(data)):
            data_array = data["series"][i]
            imax_all += data_array.shape[0]

        # print('imax: ' + str(imax))
        t_end = time.time()
        min = int(np.min(data["series"]))
        max = int(np.max(data["series"]))
        dt = t_end - t_start
        info = {
                "description": "Raw data",
                "details": {
                    "node": node,
                    "n_series": imax,
                    "n_nodes": len(data),
                    "n_series_total": imax_all,
                    "dt": int(dt*1000),
                    "min": min,
                    "max": max
                },
                "headers": np.ndarray.tolist(data["headers"]), "dt": dt, "lines": data["series"].shape[0],
                    "columns": data["series"].shape[1]}

        return (np.ndarray.tolist(data["series"][:self.n_series_disp]), info)

    def get_array_of_arrays(self, a):
        array = []
        for ag in a:
            for ag1 in ag:
                array.append(ag1)
        return array

    def get_display_data(self, d, global_scale=False):
        if d is not None:
            # centroids = d[0]
            # info = d[1]
            # return np.ndarray.tolist(centroids[:self.n_series_disp]), info

            ddata = d[0]
            info = d[1]
            start = len(ddata) - self.n_series_disp - 1
            if start < 0:
                start = 0
            end = len(ddata)
            # start = 0
            # end = len(ddata)
            # if end > self.n_series_disp - 1:
            #     end = self.n_series_disp - 1

            ddata = ddata[start:end]

            if global_scale and self.min_final is not None:
                # print("use global scale")
                min = self.min_final
                max = self.max_final
            else:
                min = int(np.min(ddata))
                max = int(np.max(ddata))

            info["details"]["min"] = min
            info["details"]["max"] = max
            return np.ndarray.tolist(ddata), info
        else:
            return None

    def get_centroids(self, data, n_clusters=8, init=None):
        if self.use_scikit:
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
            return centroids, a
        else:
            if n_clusters is None:
                n_clusters = 3
            dcluster.reinit(data, n_clusters)
            # dcluster.add_new_data(data, n_clusters)
            centroids, a = dcluster.k_means_clust_dynamic()
            # print(centroids)
            return centroids, a

    def get_assignments(self, a, data):
        if self.use_scikit:
            return a.predict(data)
        else:
            return a

    def assign_sample_to_cluster(self, node_id, sample_id):
        data = self.data[node_id]["series"]
        data1 = data[sample_id]
        data1 = [data1]
        assignments = self.get_assignments(self.final_clusters, data1)
        return assignments[0]

    def assign_partial_sample_to_cluster(self, node_id, sample_id, init=False):
        data = list(self.data[node_id]["series"][sample_id])

        if init:
            self.partial_sample_index = 0

        index = self.partial_sample_index

        min_dist = 0
        min_index = 0
        for (i, c) in enumerate(self.final_centroids):
            d = ml.euclid_dist(data[0: index], c[0: index])
            if i == 0:
                min_dist = d
            else:
                if d < min_dist:
                    min_dist = d
                    min_index = i


        partial_time_series = [0] * len(data)
        partial_time_series[0: index] = data[0: index]

        assignment = min_index

        if self.partial_sample_index < len(data) - 1:
            self.partial_sample_index += 1
        else:
            self.partial_sample_index = 0

        # # get assignments of time series to the final clusters
        partial_time_series = np.array(partial_time_series)
        return assignment, partial_time_series

    def assign_partial_sample_to_cluster_default(self, node_id, sample_id, init=False):
        data = list(self.data[node_id]["series"][sample_id])

        if init:
            self.partial_sample_index = 0

        data1 = [0] * len(data)
        partial_time_series = [0] * len(data)
        # print(data1)
        cluster_mean = list(np.mean(self.final_centroids, axis=0))
        # print(cluster_mean)
        # print(data)
        for i in range(0, len(data)):
            if i <= self.partial_sample_index:
                data1[i] = data[i]
                partial_time_series[i] = data[i]
            elif i > self.partial_sample_index:
                data1[i] = cluster_mean[i]

        assignments = self.get_assignments(self.final_clusters, [data1])

        if self.partial_sample_index < len(data1) - 1:
            self.partial_sample_index += 1
        else:
            self.partial_sample_index = 0

        # # get assignments of time series to the final clusters
        partial_time_series = np.array(partial_time_series)
        return assignments[0], partial_time_series

    def run_clustering_on_partial_sample(self, node_id, sample_id, init=False):
        assignment, partial_time_series = self.assign_partial_sample_to_cluster(node_id, sample_id, init)
        min = int(np.min(partial_time_series))
        max = int(np.max(partial_time_series))
        info = {
            "description": "Partial node data loading vs global clusters",
            "headers": ["new sample"],
            "dt": 0,
            "details": {
                "node_id": node_id,
                "node_sample": sample_id,
                "assignment": int(assignment),
                "min": min,
                "max": max
            },
            "assignments": None}

        # print(partial_time_series)
        partial_time_series = [list(partial_time_series)]
        for (i, c) in enumerate(self.final_centroids):
            partial_time_series.append(list(c))
            info["headers"].append("cluster " + str(i))

        partial_time_series = np.array(partial_time_series)
        return partial_time_series, info

    def update_node_clusters_with_partial_sample(self, node_id, sample_id, init=False):
        data = self.node_centroids[node_id]["centroids"]
        info = {
            "description": "Node clusters loading vs global clusters",
            "headers": ["data"],
            "dt": 0,
            "details": {
                "node_id": node_id,
                "node_sample": sample_id,
                "min": 0,
                "max": 0
            },
            "assignments": None}

        # print(partial_time_series)
        # partial_time_series = [list(partial_time_series)]
        # for (i, c) in enumerate(self.final_centroids):
        #     partial_time_series.append(list(c))
        #     info["headers"].append("cluster " + str(i))
        #
        # partial_time_series = np.array(partial_time_series)
        return data, info


    def run_clustering_on_node_id(self, node_id, nclusters, partial_sample_until_id=None, add_deviation_value=None):
        """
        Run clustering on specified node. The data from the node is an array of arrays
        (for each day there is an array of 24 values)
        The result is the consumer behaviour over the analyzed time frame
        :param node_id:
        :param nclusters:
        :return:
        """
        t_start = time.time()
        # print(self.data)
        data = copy.deepcopy(self.data[node_id]["series"])
        if partial_sample_until_id is not None:
            data = data[0:partial_sample_until_id]
            if add_deviation_value is not None:
                data[partial_sample_until_id]+=add_deviation_value

        if nclusters is not None and nclusters > len(data):
            print("node " + str(node_id) + "nclusters > len(data): " + str(nclusters) + "," + str(len(data)))
            return [], None, data
        res = self.get_centroids(data, nclusters)
        centroids = res[0]
        nc = len(centroids)
        centroids_np = np.array(centroids)
        desc = "Clusters from all data (single clustering)"
        # assign each time series to a cluster
        assignments = []

        headers = []
        for i in range(len(centroids_np)):
            headers.append("cluster " + str(i))

        # the assignments of the data series to the clusters
        assignments_series = [None] * len(assignments)
        for (i, a) in enumerate(assignments):
            assignments_series[i] = {
                "series": i,
                "cluster": int(assignments[i])
            }

        t_end = time.time()
        dt = t_end - t_start
        min = int(np.min(centroids_np))
        max = int(np.max(centroids_np))

        append = True
        for n in self.node_centroids:
            if n["id"] == node_id:
                n["centroids"] = centroids_np
                append = False
                break

        if append:
            self.node_centroids.append({
                "id": node_id,
                "centroids": centroids_np
            })

        info = {
                "description": desc, "headers": headers,
                "dt": t_end - t_start,
                "details": {
                    "node": node_id,
                    "new_node": node_id,
                    "n_clusters": nc,
                    "n_nodes": len(self.data),
                    "dt": int(dt * 1000),
                    "min": min,
                    "max": max
                },
                "assignments": assignments_series}

        return centroids_np, info, data

    def run_clustering_on_node_range(self, r, nclusters):
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
        t_start = time.time()
        centroid_vect = []
        raw_data_vect = []

        if r is None:
            r = list(range(0, len(self.data)))

        # run clustering for each node and save clusters into array
        for node_id in r:
            res = self.run_clustering_on_node_id(node_id, nclusters)
            centroid_vect.append(res[0])
            raw_data_vect.append(res[2])


        centroid_vect = self.get_array_of_arrays(centroid_vect)

        # raw_data_vect = self.get_array_of_arrays(raw_data_vect)
        centroids_np = np.array(centroid_vect)

        headers = []
        for i in range(len(centroids_np)):
            headers.append("cluster " + str(i))

        t_end = time.time()
        dt = t_end - t_start


        min = int(np.min(centroids_np))
        max = int(np.max(centroids_np))
        info = {
                "description": "Clusters from node range (single clustering)", "headers": headers,
                "dt": t_end - t_start,
                "details": {
                    "node_range": r,
                    "n_clusters": len(centroids_np),
                    "n_nodes": len(self.data),
                    "dt": int(dt * 1000),
                    "min": min,
                    "max": max
                },
                "assignments": None}

        return centroids_np, info



    def run_single_clustering_on_node_range(self, r, nclusters, n_data=None):
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
            r = list(range(0, len(self.data)))

        t_start = time.time()
        # print(self.data)
        # data = self.data[node_id]["series"]
        # data = [[series for series in node_series["series"]] for node_series in self.data]
        # data = np.array(data)
        # print(data.shape)
        # data = np.array([])
        data = []
        for id in r:
            for (i, s) in enumerate(self.data[id]["series"]):
                if n_data is not None:
                    if i < n_data:
                        data.append(s)
                else:
                    data.append(s)
        data = np.array(data)


        # print(self.data[0]["series"])
        # print(data)
        res = self.get_centroids(data, nclusters)
        centroids = res[0]
        nc = len(centroids)
        centroids_np = np.array(centroids)
        desc = "Clusters from all data from all nodes (single clustering)"
        # assign each time series to a cluster
        assignments = []

        headers = []
        for i in range(len(centroids_np)):
            headers.append("cluster " + str(i))

        # the assignments of the data series to the clusters
        assignments_series = [None] * len(assignments)
        for (i, a) in enumerate(assignments):
            assignments_series[i] = {
                "series": i,
                "cluster": int(assignments[i])
            }

        t_end = time.time()
        dt = t_end - t_start
        min = int(np.min(centroids_np))
        max = int(np.max(centroids_np))

        info = {
                "description": desc, "headers": headers,
                "dt": t_end - t_start,
                "details": {
                    "n_clusters": nc,
                    "n_nodes": len(self.data),
                    "dt": int(dt * 1000),
                    "min": min,
                    "max": max
                },
                "assignments": assignments_series}

        return centroids_np, info, data

    def run_dual_clustering_on_node_range(self, r, nclusters, nclusters_final):
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

        t_start = time.time()
        centroid_vect = []
        raw_data_vect = []

        if r is None:
            r = list(range(0, len(self.data)))

        print("node range: ", r)

        # run clustering for each node and save clusters into array
        for node_id in r:
            res = self.run_clustering_on_node_id(node_id, nclusters)
            centroid_vect.append(res[0])
            raw_data_vect.append(res[2])

        centroid_vect = self.get_array_of_arrays(centroid_vect)
        raw_data_vect = self.get_array_of_arrays(raw_data_vect)

        n_clusters_total = len(centroid_vect)
        centroids_np = np.array(centroid_vect)

        # run clustering again for the previous clusters
        res = self.get_centroids(centroids_np, nclusters_final, self.final_centroids)
        centroids = res[0]
        self.final_centroids = res[0]
        self.final_clusters = res[1]
        nc = len(centroids)
        centroids_np = np.array(centroids)

        # get assignments of time series to the final clusters

        assignments = self.get_assignments(res[1], raw_data_vect)

        n = len(centroids_np)
        headers = [None] * n
        self.clusters = []
        demands = []
        for i in range(n):
            headers[i] = "cluster " + str(i)
            cluster = Constants.CLUSTER_MODEL
            cluster["id"] = assignments[i]
            avg_demand = np.average(centroids_np[i])
            cluster["avg_demand"] = avg_demand
            demands.append(avg_demand)
            cluster["centroid"] = centroids_np[i]
            self.clusters.append(copy.deepcopy(cluster))

        demands = np.array(demands)
        temp = demands.argsort()
        ranks = np.empty_like(temp)
        ranks[temp] = np.arange(len(demands))

        for i in range(n):
            self.clusters[i]["priority"] = ranks[i]

        # print(self.clusters)
        # the assignments of the data series to the clusters
        self.assignments_series = [None] * len(assignments)
        for (i, a) in enumerate(assignments):
            self.assignments_series[i] = {
                "series": i,
                "cluster": int(a)
            }

        t_end = time.time()
        dt = t_end - t_start
        min = int(np.min(centroids_np))
        max = int(np.max(centroids_np))

        self.min_final = min
        self.max_final = max

        info = {
                "description": "Clusters from node range (dual clustering)", "headers": headers,
                "dt": t_end - t_start,
                "details": {
                    "node_range": r,
                    "n_clusters": nc,
                    "n_nodes": len(self.data),
                    "dt": int(dt * 1000),
                    "min": min,
                    "max": max
                },
                "assignments": self.assignments_series}

        return centroids_np, info


    def reinit(self):
        self.final_centroids = None
        self.final_clusters = None

def run_dual_clustering(plot=True):
    """
    dual clustering
    """
    machine_learning.set_lib(True)

    # res_dual = machine_learning.run_dual_clustering_on_node_range(None, None, 3)
    n_clusters = 3

    ncn = 3
    print("start")
    res_dual = machine_learning.run_dual_clustering_on_node_range(None, ncn, n_clusters)
    res_dual = res_dual[0]

    if plot:
        for ts in res_dual:
            plt.plot(ts)
        plt.gca().set_title("dual clustering")
        plt.xlabel("time (h)")
        plt.ylabel("flow")

        plt.show()
    return res_dual


def run_single_clustering(plot=True):
    # machine_learning.read_data("simulated")
    machine_learning.read_data("simulated_leak_ramp_each_day_diff")
    machine_learning.set_lib(True)

    n_clusters = 3

    print("start")
    res_single = machine_learning.run_single_clustering_on_node_range(None, n_clusters)
    print("done")
    res_single = res_single[0]

    if plot:
        for ts in res_single:
            plt.plot(ts)
        plt.gca().set_title("single clustering")
        plt.xlabel("time (h)")
        plt.ylabel("flow")

        plt.show()
    return res_single

def run_single_clustering_combined(plot=True):
    machine_learning.read_data("simulated_leak_ramp_each_day_dynamic_diff")

    n_clusters = 3

    print("start")
    res_single = machine_learning.run_clustering_on_node_range(None, n_clusters)
    print("done")
    res_single = res_single[0]
    print(res_single.shape)
    if plot:
        for ts in res_single:
            plt.plot(ts)
        plt.gca().set_title("single clustering combined")
        plt.xlabel("time (h)")
        plt.ylabel("flow")

        plt.show()


    return res_single


def compare_node_data():
    machine_learning.read_data("simulated")

    machine_learning.read_data("simulated_leak_step_day1")
    # def get_centroids(self, data, n_clusters=8, init=None):
    #     if self.use_scikit:


def compare_data_sets():
    # machine_learning = ML_clustering(use_scikit=False)
    dual = True

    machine_learning.read_data("simulated")

    if dual:
        res_1 = run_dual_clustering(False)
    else:
        res_1 = run_single_clustering_combined(False)

    machine_learning.reinit()

    machine_learning.read_data("simulated_leak_step_day1")

    if dual:
        res_2 = run_dual_clustering(False)
    else:
        res_2 = run_single_clustering_combined(False)

    machine_learning.reinit()

    comp_euclid_dist, comp_avg, comp_array = ml.get_comp(res_1, res_2)
    # print(comp_array)


    for ts in res_1:
        plt.plot(ts)
    plt.gca().set_title("cluster 1")
    plt.xlabel("time (h)")
    plt.ylabel("flow")

    plt.figure()

    for ts in res_2:
        plt.plot(ts)
    plt.gca().set_title("cluster 2")
    plt.xlabel("time (h)")
    plt.ylabel("flow")

    plt.figure()

    for ts in comp_array:
        plt.plot(ts)
    plt.gca().set_title("cluster difference")
    plt.xlabel("time (h)")
    plt.ylabel("flow")

    plt.show()

if __name__ == "__main__":
    print("machine learning test")
    machine_learning = ML_clustering(use_scikit=False)
    # machine_learning.read_data()

    # compare_data_sets()

    run_single_clustering_combined(True)
    # run_single_clustering(True)


