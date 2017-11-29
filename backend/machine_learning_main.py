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

        self.files = [f for f in listdir("data") if isfile(join("data", f))]
        print(self.files)

        self.n_nodes = len(self.files)
        self.n_series_disp = 20
        # self.i_run = int(self.n_nodes/2)
        self.i_run1 = 1
        self.i_run2 = 1
        # self.n_nodes = 1

        # self.use_previous_cluster_data = False

        self.centroids = None
        self.final_centroids = None

    def get_info(self):

        info = {
            "n_nodes": len(self.data),
            "nodes": list(range(0, len(self.data)))
        }

        return info

    def get_raw_data(self, node=0):
        t_start = time.time()
        # self.read_data()

        data = self.data[node]
        imax = data["series"].shape[0]
        imax_all = 0

        for i in range(len(self.data)):
            data_array = self.data[i]["series"]
            imax_all += data_array.shape[0]

        print('imax: ' + str(imax))
        t_end = time.time()

        dt = t_end - t_start
        info = {"min": np.min(data["series"]), "max": np.max(data["series"]), "description": "Raw data", "details": [
            {
                "key": "node",
                "value": node
            },
            {
                "key": "n_series",
                "value": imax
            },
            {
                "key": "n_nodes",
                "value": len(self.data)
            },
            {
                "key": "n_series_total",
                "value": imax_all
            },
            {
                "key": "dt_ms",
                "value": int(dt * 1000)
            }
        ], "headers": np.ndarray.tolist(data["headers"]), "dt": dt, "lines": data["series"].shape[0],
                "columns": data["series"].shape[1]}

        return (np.ndarray.tolist(self.data[node]["series"][:self.n_series_disp]), info)

    def run_clustering(self, node_id=None):
        """
        run clustering for all consumer nodes and get clusters
        it can run for first self.i_run consumer nodes and increment at each run so that we can see how the clusters
        change when adding a new consumer
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

        start_index = 0
        end_index = self.i_run1

        if node_id is not None:
            start_index = node_id
            end_index = node_id + 1

        print("consumer nodes: " + str(len(self.data)))

        # for i in range(0, len(self.data)):
        for i in range(start_index, end_index):
            # print("I: " + str(i))
            data_array = self.data[i]["series"]
            # data_array_for_all.append([d.tolist() for d in data_array])
            for data_array1 in data_array:
                data_array_for_all.append(data_array1)
            # data_array has multiple time series from the same consumer
            kmeans = KMeans(n_clusters=nclusters)
            # print kmeans
            # Compute cluster centers and predict cluster index for each sample.
            a = kmeans.fit(data_array)
            # print a.cluster_centers_
            assignments = a.predict(data_array)
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

        desc = "Clusters from all data (single clustering)"
        # assign each time series to a cluster
        assignments = []
        data = centroids_np

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
        print("min: " + str(np.min(data)))
        info = {"min": np.min(data), "max": np.max(data), "description": desc, "headers": headers,
                "dt": t_end - t_start, "details": [
                {
                    "key": "new_node",
                    "value": self.i_run1
                },
                {
                    "key": "n_clusters",
                    "value": n_clusters_total
                },
                {
                    "key": "n_nodes",
                    "value": len(self.data)
                },
                {
                    "key": "dt_ms",
                    "value": int(dt * 1000)
                }
            ], "class": assignments_series}

        # info = {}

        if node_id is not None:
            self.i_run1 += 1
            if self.i_run1 >= self.n_nodes:
                self.i_run1 = 1
        return np.ndarray.tolist(data[:self.n_series_disp]), info

    def run_clustering_twice(self, node=-1):
        """
        node == -1 => run clustering for all nodes and then run clustering again on all clusters
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
            if node == -1:
                print("consumer nodes: " + str(len(self.data)))

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
            # print("min: " + str(np.min(data)))
            info = {"min": np.min(data), "max": np.max(data), "description": desc, "headers": headers,
                    "dt": t_end - t_start, "details": [
                    {
                        "key": "node",
                        "value": node
                    },
                    {
                        "key": "new_node",
                        "value": self.i_run2
                    },
                    {
                        "key": "n_clusters",
                        "value": n_clusters_total
                    },
                    {
                        "key": "n_nodes",
                        "value": len(self.data)
                    },
                    {
                        "key": "dt_ms",
                        "value": int(dt * 1000)
                    }
                ], "class": assignments_series}
        except:
            info = "failed"

        self.i_run2 += 1
        if self.i_run2 >= self.n_nodes:
            self.i_run2 = 1
        return np.ndarray.tolist(data[:self.n_series_disp]), info



    def read_data(self):

        """
            read data from files
            each file has the data for a measurement node
            over a time frame of n days, for every hour
        :return:
        """

        for i, f in enumerate(self.files[0:self.n_nodes]):
            print(str(i) + ". reading: " + f)
            fdata = self.dc.read_data(join("data/", f))
            # print(fdata["series"])
            self.data.append(copy.copy(fdata))

        # print("TEST")
        # print(self.data[0]["series"])
        # print(self.data[17]["series"])




