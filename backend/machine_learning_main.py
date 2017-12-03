import csv
import json

import numpy as np
import time

from read_data import DataClass
import scipy
# from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.cluster import KMeans

import numpy as np
import math
import random

from math import sqrt

from os import listdir
from os.path import isfile, join

import copy


class MachineLearningMain:
    def __init__(self):
        self.dc = DataClass()
        self.data = []
        self.node_data = []
        self.assignments_series = []

        self.min_final = None
        self.max_final = None

        self.files = [f for f in listdir("data") if isfile(join("data", f))]
        print(self.files)

        self.n_nodes = len(self.files)
        self.n_series_disp = 10
        # self.i_run = int(self.n_nodes/2)

        self.i_run2 = 1
        # self.n_nodes = 1

        # self.use_previous_cluster_data = False

        self.centroids = None
        self.final_centroids = None

        # self.nodes = [None] * len(self.data)
        # for i in range(0, len(self.data)):
        #     self.nodes[i] = {
        #         "node": i,
        #         "series": [],
        #         "class": None
        #     }


    def init(self):
        self.final_centroids = None
        self.centroids = None
        self.read_data()
        self.run_dual_clustering_on_node_range(0, None, 3, 3)
        self.assign_class_to_nodes()

    def assign_class_to_nodes(self):
        assignment_index = 0
        for (i_node, node) in enumerate(self.node_data):
            cluster = 0
            # get average cluster index for node
            n_series_node = len(self.data[i_node]["series"])
            for i in range(n_series_node):
                cluster += self.assignments_series[assignment_index]["cluster"]
                assignment_index += 1
            node["class"] = int(cluster/n_series_node)
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
            fdata = self.dc.read_data(join("data/", f))

            data = copy.copy(fdata)
            self.data.append(data)
            self.node_data.append(
                {
                    "node": i,
                    "class": None
                }
            )


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

            # print("disp start: " + str(start) + ", disp end: " + str(end))
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

    def get_centroids(self, data, nclusters, init=None):
        if init is not None:
            kmeans = KMeans(n_clusters=nclusters, init=init)
        else:
            kmeans = KMeans(n_clusters=nclusters)
        a = kmeans.fit(data)
        centroids = a.cluster_centers_
        return centroids, a

    def get_assignments(self, a, data):
        return a.predict(data)

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
                "class": assignments_series}

        return centroids_np, info, data

    def run_clustering_on_node_range(self, start, end, nclusters):
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

        if end is None:
            end = len(self.data)

        # run clustering for each node and save clusters into array
        for node_id in range(start, end):
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
                    "first_node": start,
                    "last_node": end,
                    "n_clusters": len(centroids_np),
                    "n_nodes": len(self.data),
                    "dt": int(dt * 1000),
                    "min": min,
                    "max": max
                },
                "class": None}

        return centroids_np, info

    def run_dual_clustering_on_node_range(self, start, end, nclusters, nclusters_final):
        """
         Run dual clustering on specified node range.
         The data from a node is an array of arrays
        (for each day there is an array of 24 values).
        The clusters are calculated separately for each node and added to the cluster array.
        Then, there is another clustering on this cluster array which returns
        the final clusters for all the network (consumer types in the network)
        :param start:
        :param end:
        :param nclusters:
        :param nclusters_final:
        :return:
        """
        t_start = time.time()
        centroid_vect = []
        raw_data_vect = []

        if end is None:
            end = len(self.data)

        # run clustering for each node and save clusters into array
        for node_id in range(start, end):
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
        nc = len(centroids)
        centroids_np = np.array(centroids)

        # get assignments of time series to the final clusters
        assignments = self.get_assignments(res[1], raw_data_vect)

        headers = []
        for i in range(len(centroids_np)):
            headers.append("cluster " + str(i))

        # the assignments of the data series to the clusters
        self.assignments_series = [None] * len(assignments)
        for (i, a) in enumerate(assignments):
            self.assignments_series[i] = {
                "series": i,
                "cluster": int(assignments[i])
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
                    "first_node": start,
                    "last_node": end,
                    "n_clusters": nc,
                    "n_nodes": len(self.data),
                    "dt": int(dt * 1000),
                    "min": min,
                    "max": max
                },
                "class": self.assignments_series}

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
                    "class": assignments_series}
        except:
            info = "failed"

        self.i_run2 += 1
        if self.i_run2 >= self.n_nodes:
            self.i_run2 = 1
        return np.ndarray.tolist(data[:self.n_series_disp]), info


if __name__ == "__main__":
    print("machine learning test")
    machine_learning = MachineLearningMain()
    machine_learning.read_data()
    res = machine_learning.run_dual_clustering_on_node_range(0, None, 3, 3)
    print(machine_learning.assign_class_to_nodes())