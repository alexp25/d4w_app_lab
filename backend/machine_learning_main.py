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
        # self.n_nodes = 1

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
        info = {"min": np.min(data["series"]), "max": np.max(data["series"]),
                "description": "Raw data",
                "details": [
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
                ],
                "headers": np.ndarray.tolist(data["headers"]), "dt": 0, "lines": data["series"].shape[0], "columns": data["series"].shape[1]}


        info["dt"] = dt
        return (np.ndarray.tolist(self.data[node]["series"][:self.n_series_disp]), info)

    def run_clustering(self, node=-1, plot=1):
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
        # print(data["series"])
        centroids = []
        data = []
        desc = ""
        assignments = []
        data_array_for_all = []
        n_clusters_total = 0

        if node == -1:
            print("consumer nodes: " + str(len(self.data)))

            for i in range(len(self.data)):

                data_array = self.data[i]["series"]
                # data_array_for_all.append([d.tolist() for d in data_array])
                for data_array1 in data_array:
                    data_array_for_all.append(data_array1)
                # data_array has multiple time series from the same consumer

                len_data = len(data_array)
                data_array1 = data_array
                # data_array1 = data_array[0:int(len_data / 2)]

                kmeans = KMeans(n_clusters=nclusters)
                # print kmeans
                # Compute cluster centers and predict cluster index for each sample.
                a = kmeans.fit(data_array1)
                # print a.cluster_centers_
                assignments = a.predict(data_array1)

                centroid = a.cluster_centers_
                # print(centroid)
                centroids.append(centroid)

            # data_array_for_all = np.reshape(data_array_for_all, -1)
            # print(centroids[0])
            # print(centroids)
            centroids_all = []
            for centroid_group in centroids:
                for centroid in centroid_group:
                    centroids_all.append(centroid)

            n_clusters_total = len(centroids_all)
            # print(len(centroids_all))
            # print(centroids_all[10])
            # print(centroids_all)
            # centroids_np = [centroid for centroid in centroids_all]
            centroids_np = centroids_all
            centroids_np = np.array(centroids_np)
            # centroids_np = centroids_np[:, 1:].astype(float)



            # data = final_centroids
            if plot == 0:
                desc = "Node based clusters"

                # assign each time series to a cluster
                assignments = []
                data = centroids_np
            elif plot == 1:
                desc = "Consumer patterns (clusters)"

                kmeans = KMeans(n_clusters=nclusters_final)
                # print kmeans
                # Compute cluster centers and predict cluster index for each sample.
                a = kmeans.fit(centroids_np)
                # print a.cluster_centers_
                # assignments = a.predict(centroids_np)

                # print("centroids: ")
                # print(centroids_np)
                # print("data arrays: ")
                # print(data_array_for_all)
                assignments = a.predict(data_array_for_all)
                final_centroids = a.cluster_centers_

                data = final_centroids

        else:
            desc = "Node based clusters"
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
        info = {"min": np.min(data), "max": np.max(data), "description": desc,
                "headers": headers, "dt": 0,
                "details": [
                    {
                        "key": "node",
                        "value": node
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
                ],
                "class": assignments_series}


        info["dt"] = t_end - t_start

        return (np.ndarray.tolist(data[:self.n_series_disp]), info)

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




