import csv
import json

import numpy as np
import time

from read_data import DataClass
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




import matplotlib.pylab as plt




from modules.data.constants import Constants
from modules import machine_learning_functions as ml
from modules.dynamic_clustering import ClusteringClass
dcluster = ClusteringClass()


class MachineLearningMain:
    def __init__(self, use_scikit=True):
        self.dc = DataClass()
        self.data = []
        self.node_data = []
        self.assignments_series = []
        self.min_final = None
        self.max_final = None
        self.files = [f for f in listdir("data/sensors") if isfile(join("data/sensors", f))]
        print(self.files)
        self.n_nodes = len(self.files)
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



    def read_data(self):
        """
            read data from files
            each file has the data for a measurement node
            over a time frame of n days, for every hour
        :return:
        """
        self.data = []
        self.node_data = []
        for i, f in enumerate(self.files[0:self.n_nodes]):
            # print(str(i) + ". reading: " + f)
            fdata = self.dc.read_data(join("data/sensors/", f))
            data = copy.copy(fdata)
            self.data.append(data)
            node = Constants.NODE_MODEL
            node["id"] = i
            self.node_data.append(copy.deepcopy(node))



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
        print("data:")
        print(data1)
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

    def run_clustering_on_node_id(self, node_id, nclusters):
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
        data = self.data[node_id]["series"]
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



    def run_single_clustering_on_node_range(self, r, nclusters):
        """
        Run clustering on specified node. The data from the node is an array of arrays
        (for each day there is an array of 24 values)
        The result is the consumer behaviour over the analyzed time frame
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
            for s in self.data[id]["series"]:
                data.append(s)
        data = np.array(data)
        print(data.shape)

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

    # def run_single_clustering_on_node_range(self, r, nclusters):
    #     """
    #     Run clustering on specified node range. The data from a node is an array of arrays
    #     (for each day there is an array of 24 values). The clusters are calculated
    #     separately for each node and added to the cluster array (various consumer
    #     behaviours in the network)
    #     :param start:
    #     :param end:
    #     :param nclusters:
    #     :return:
    #     """
    #     t_start = time.time()
    #     centroid_vect = []
    #     raw_data_vect = []
    #
    #     if r is None:
    #         r = list(range(0, len(self.data)))
    #
    #     # run clustering for each node and save clusters into array
    #     for node_id in r:
    #         res = self.run_clustering_on_node_id(node_id, nclusters)
    #         centroid_vect.append(res[0])
    #         raw_data_vect.append(res[2])
    #
    #     centroid_vect = self.get_array_of_arrays(centroid_vect)
    #     # raw_data_vect = self.get_array_of_arrays(raw_data_vect)
    #     centroids_np = np.array(centroid_vect)
    #
    #     headers = []
    #     for i in range(len(centroids_np)):
    #         headers.append("cluster " + str(i))
    #
    #     t_end = time.time()
    #     dt = t_end - t_start
    #     min = int(np.min(centroids_np))
    #     max = int(np.max(centroids_np))
    #     info = {
    #             "description": "Clusters from node range (single clustering)", "headers": headers,
    #             "dt": t_end - t_start,
    #             "details": {
    #                 "node_range": r,
    #                 "n_clusters": len(centroids_np),
    #                 "n_nodes": len(self.data),
    #                 "dt": int(dt * 1000),
    #                 "min": min,
    #                 "max": max
    #             },
    #             "assignments": None}
    #
    #     return centroids_np, info

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


    def run_clustering_twice(self, node=None):
        """
        NOTE: DEPRECATED
        node == None => run clustering for all nodes and then run clustering again on all clusters
        node > 0 => run clustering for the selected node
        :param plot:
        :return:
        :param node:
        :return:
        """
        t_start = time.time()
        nclusters = 2
        nclusters_final = 3
        centroids = []
        data = []
        desc = ""
        assignments = []
        data_array_for_all = []
        try:
            if node is None:
                # print("consumer nodes: " + str(len(self.data)))

                # for i in range(0, len(self.data)):
                for i in range(0, self.i_run2):
                    data_array = self.data[i]["series"]
                    # data_array_for_all.append([d.tolist() for d in data_array])
                    for data_array1 in data_array:
                        data_array_for_all.append(data_array1)
                    # data_array has multiple time series from the same consumer
                    len_data = len(data_array)
                    data_array1 = data_array
                    # data_array1 = data_array[0:int(len_data / 2)]
                    # if self.centroids is None:
                    #     kmeans = KMeans(n_clusters=nclusters)
                    # else:
                    #     kmeans = KMeans(n_clusters=nclusters, init=self.centroids[i])

                    kmeans = KMeans(n_clusters=nclusters)
                    # print kmeans
                    # Compute cluster centers and predict cluster index for each sample.
                    a = kmeans.fit(data_array1)
                    # print a.cluster_centers_
                    assignments = a.predict(data_array1)

                    centroid = a.cluster_centers_
                    # print(centroid)
                    centroids.append(centroid)

                self.centroids = centroids
                centroids_all = []
                for centroid_group in centroids:
                    for centroid in centroid_group:
                        centroids_all.append(centroid)

                n_clusters_total = len(centroids_all)
                centroids_np = centroids_all
                centroids_np = np.array(centroids_np)

                desc = "Final clusters (double clustering)"

                if self.final_centroids is None:
                    kmeans = KMeans(n_clusters=nclusters_final)
                else:
                    kmeans = KMeans(n_clusters=nclusters_final, init=self.final_centroids)
                # kmeans = KMeans(n_clusters=nclusters_final)
                # print kmeans
                # Compute cluster centers and predict cluster index for each sample.
                a = kmeans.fit(centroids_np)
                assignments = a.predict(data_array_for_all)
                self.final_centroids = a.cluster_centers_
                data = self.final_centroids

            else:
                desc = "Clusters from all data (single clustering)"
                data_array = self.data[node]["series"]
                kmeans = KMeans(n_clusters=nclusters_final)
                # print kmeans
                # Compute cluster centers and predict cluster index for each sample.
                a = kmeans.fit(data_array)
                # print a.cluster_centers_
                assignments = a.predict(data_array)
                centroids = a.cluster_centers_

                n_clusters_total = len(centroids)
                data = centroids

            headers = []
            for i in range(len(data)):
                headers.append("cluster " + str(i))

            assignments_series = [None] * len(assignments)
            for (i, a) in enumerate(assignments):
                assignments_series[i] = {
                    "series": i,
                    "cluster": int(assignments[i])
                }

            t_end = time.time()
            dt = t_end - t_start
            min = np.min(data)
            max = np.max(data)
            # print("min: " + str(np.min(data)))
            info = {
                    "description": desc, "headers": headers,
                    "dt": t_end - t_start,
                    "details": {
                        "node": node,
                        "new_node": self.i_run2,
                        "n_clusters": n_clusters_total,
                        "n_nodes": len(self.data),
                        "dt": int(dt*1000),
                        "min": min,
                        "max": max
                    },
                    "assignments": assignments_series}
        except:
            info = "failed"

        self.i_run2 += 1
        if self.i_run2 >= self.n_nodes:
            self.i_run2 = 1
        return np.ndarray.tolist(data[:self.n_series_disp]), info



def get_comp(a1, a2, get_diff=False):
    comp = [0] * len(a1)
    diff = [0] * len(a1)
    for icomp, ri in enumerate(a1):
        comp[icomp] = dcluster.euclid_dist(ri, a2[0])
        for rj in a2:
            dist = dcluster.euclid_dist(ri, rj)
            if dist < comp[icomp]:
                comp[icomp] = dist
                if get_diff:
                    diff[icomp] = ri - rj
    # for comp1 in comp:
    #     print(comp1)
    comp_avg = np.mean(comp)
    return comp, comp_avg, diff

def test_partial_whole(data, ls1=None):
    ls = len(data)
    if ls1 is None:
        ls1 = int(ls / 2)

    # test partial update with whole series
    dcluster.reinit(data[0:ls1], 2)
    res_partial_whole, a = dcluster.k_means_clust_dynamic()

    for i_data in range(ls + 1, ls):
        dcluster.add_new_data(data[i_data])
        res_partial_whole, a = dcluster.k_means_clust_dynamic()

    return res_partial_whole

def test_partial(data, ls1=None):
    ls = len(data)
    if ls1 is None:
        ls1 = int(ls / 2)
    # test partial update with partial series
    dcluster.reinit(data[0:ls1], 2)
    res_partial, a = dcluster.k_means_clust_dynamic()

    for i_data in range(ls1 + 1, ls):
        for i_sample in range(1, 24):
            dcluster.add_new_data(data[i_data])
            res_partial = dcluster.k_means_clust_dynamic_partial_update(i_sample)

    return res_partial

def test_full(data):
    dcluster.reinit(data, 2)
    res_standard, a = dcluster.k_means_clust_dynamic()
    return res_standard


def save_mat(mat, filename="mat.txt"):
    s = ""
    # print('\n'.join(str(aa) for aa in mat))
    for row in mat:
        if hasattr(row, "__len__"):
            # print(row)
            for col in row:
                # print(col)
                s += str(col) + "\t"
            s += "\n"
    print(s)

    with open(filename, "wt") as f:
        f.write(s)

def plot_from_matrix(m,colors=None):

    for (i, ts) in enumerate(m):
        if colors is not None and i < len(colors):
            plt.plot(ts, colors[i])
        else:
            plt.plot(ts)

def run_test_1():
    n_nodes = 21

    res_standard = []
    res_partial_whole = []
    res_partial = []
    comp_whole = 0
    comp_partial = 0

    lim1 = 2
    lim2 = 81
    n_test = lim2 - lim1

    comp_whole_vect = [0] * n_test
    comp_partial_vect = [0] * n_test
    comp_diff_vect = [0] * n_test

    for (i, k) in enumerate(range(lim1, lim2)):
        # for each test
        comp_whole_vect[k - lim1] = [0] * n_nodes
        comp_partial_vect[k - lim1] = [0] * n_nodes
        for i in range(n_nodes):
            # for each node
            print(str(k) + "." + str(i))
            # data = machine_learning.data[0]["series"].tolist()
            data = machine_learning.data[i]["series"]

            res_standard = test_full(data)
            # test partial update with whole series
            res_partial_whole = test_partial_whole(data, k)

            # test partial update with partial series
            res_partial = test_partial(data, k)

            # print("whole ts")
            x, comp_whole = get_comp(res_standard, res_partial_whole)
            comp_whole_vect[k - lim1][i] = comp_whole
            # print("partial ts")
            x, comp_partial = get_comp(res_standard, res_partial)
            comp_partial_vect[k - lim1][i] = comp_partial

        # all data from a test (for all nodes)
        t1 = comp_partial_vect[k - lim1]
        t2 = comp_whole_vect[k - lim1]
        comp_diff_vect[k - lim1] = [abs(j - i) for i, j in zip(t1, t2)]

    print(comp_whole_vect)
    print(comp_partial_vect)
    print(comp_diff_vect)
    # save_mat(comp_diff_vect)
    save_mat(comp_partial_vect, "mat_partial_comp.txt")
    save_mat(comp_whole_vect, "mat_whole_comp.txt")
    save_mat(comp_diff_vect, "mat_diff_comp.txt")

    plt.subplot(311)
    for ts in res_standard:
        plt.plot(ts)
    plt.gca().set_title("standard clustering")

    plt.subplot(312)
    for ts in res_partial_whole:
        plt.plot(ts)
    plt.gca().set_title("partial clustering with whole time series")
    plt.legend([comp_whole])

    plt.subplot(313)
    for ts in reversed(res_partial):
        plt.plot(ts)
    plt.legend([comp_partial])
    plt.gca().set_title("partial clustering with partial time series")

    plt.figure()

    ind = np.arange(n_nodes)
    t1_ind = int((lim2 + lim1) / 2 - lim1)
    print(t1_ind)

    width = 0.35  # the width of the bars
    plt.bar(ind, comp_partial_vect[t1_ind], width)
    plt.bar(ind + width, comp_whole_vect[t1_ind], width)

    ratio_c1 = [comp_partial_vect[t1_ind][i] / comp_whole_vect[t1_ind][i] for i in
                range(len(comp_partial_vect[t1_ind]))]
    print(ratio_c1)
    print(np.mean(ratio_c1))

    plt.legend(["method, avg: " + str(np.mean(comp_partial_vect[t1_ind])),
                "control, avg: " + str(np.mean(comp_whole_vect[t1_ind]))])
    plt.gca().set_title("method deviation results")

    plt.figure()
    plt.plot(ratio_c1)

    plt.figure()
    ind = range(len(comp_diff_vect[t1_ind]))
    plt.bar(ind, comp_diff_vect[t1_ind], width)

    plt.show()


def run_test_2():
    machine_learning.set_lib(True)

    # res_dual = machine_learning.run_dual_clustering_on_node_range(None, None, 3)
    n_clusters_for_nodes = None
    n_clusters = 3
    res_dual = machine_learning.run_dual_clustering_on_node_range(None, n_clusters_for_nodes, n_clusters)
    res_dual = res_dual[0]
    res_single = machine_learning.run_single_clustering_on_node_range(None, n_clusters)
    res_single = res_single[0]
    # for ts in res_standard:
    print(res_dual.shape)
    print(res_single.shape)
    res_all = np.concatenate((res_dual,res_single),axis=0)
    print(res_all.shape)

    comp,comp_avg,res_diff = get_comp(res_dual, res_single, True)

    # res_diff = res_dual - res_single

    # colors = ['r','g','b']
    colors = ['b'] * n_clusters
    colors2 = ['black'] * n_clusters
    cluster_labels1 = ["c1"+str(i+1) for i in range(n_clusters)]
    cluster_labels2 = ["c2" + str(i + 1) for i in range(n_clusters)]
    plot_from_matrix(res_dual, colors)
    plt.figure()
    plot_from_matrix(res_single, colors)
    plt.figure()

    plot_from_matrix(res_all, colors + colors2)

    plt.legend(cluster_labels1+cluster_labels2)

    if n_clusters_for_nodes is None:
        n_clusters_for_nodes = "auto"
    plt.title("number of clusters for nodes: " + str(n_clusters_for_nodes) + ", average deviation: " + str(int(comp_avg)))

    plt.figure()
    plot_from_matrix(res_diff, colors)

    plt.show()

if __name__ == "__main__":
    print("machine learning test")
    machine_learning = MachineLearningMain(use_scikit=False)
    machine_learning.read_data()

    run_test_2()




    #
    # plt.show()
    # print(machine_learning.assign_class_to_nodes())
    #
    #
    # res = machine_learning.assign_sample_to_cluster(1, 0)
    # print(res)
    #
    # for i in range(24):
    #     res = machine_learning.assign_partial_sample_to_cluster(1, 0)
    #     print(res)

