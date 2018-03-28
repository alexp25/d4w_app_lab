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

import itertools


import matplotlib.pylab as plt




from modules.data.constants import Constants
from modules import aux_fn as ml
from modules.dynamic_clustering import ClusteringClass
dcluster = ClusteringClass()

from modules.aux_fn import *
from modules.aux_fn_ML import *



class ML_dualVsSingleNumberOfClusters:
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

    def test(self):
        """
        test with different number of clusters for stage 2 (2 stage clustering)
        comparing the deviation from single stage clustering
        """
        self.set_lib(True)

        # res_dual = self.run_dual_clustering_on_node_range(None, None, 3)
        n_clusters = 3

        nc_max = 81
        n_data = nc_max

        r1 = list(range(2, nc_max))
        # r1 = [2, 10, 82]
        n_clusters_for_nodes_range = [None] + r1
        comp_avg_vect = [0] * len(n_clusters_for_nodes_range)
        # test_index = 0

        test_index = len(n_clusters_for_nodes_range) - 1

        for (i, k) in enumerate(n_clusters_for_nodes_range):
            ncn = k
            print("n_clusters_for_nodes: " + str(k))
            res_dual1 = run_dual_clustering_on_node_range(self.data, None, ncn, n_clusters)
            res_single1 = run_clustering_for_all_nodes_at_once(self.data, None, n_clusters, n_data)
            res_all1 = np.concatenate((res_dual1, res_single1), axis=0)
            comp, ca, rd = get_comp(res_dual1, res_single1)
            comp_avg_vect[i] = ca
            print("comp_avg: " + str(ca))

            if i == test_index:
                res_all = copy.copy(res_all1)
                res_dual = copy.copy(res_dual1)
                res_single = copy.copy(res_single1)
                n_clusters_for_nodes = k
                comp_avg = ca
                res_diff = rd

        colors = ['b'] * n_clusters
        colors2 = ['g:'] * n_clusters
        cluster_labels1 = ["cd" + str(i + 1) for i in range(n_clusters)]
        cluster_labels2 = ["cs" + str(i + 1) for i in range(n_clusters)]

        plot_from_matrix(res_all, colors + colors2)
        plt.legend(cluster_labels1+cluster_labels2)

        if n_clusters_for_nodes is None:
            n_clusters_for_nodes = "auto"

        plt.title("number of clusters for nodes: " + str(n_clusters_for_nodes) + ", average deviation: " + str(int(comp_avg)))
        plt.figure()

        comp_avg_dynamic = comp_avg_vect[0]
        comp_avg_vect = comp_avg_vect[1:]
        n_clusters_for_nodes_range = n_clusters_for_nodes_range[1:]

        print("comp_avg_trim")
        print(comp_avg_vect)
        print("comp_dynamic")
        print(comp_avg_dynamic)

        result_obj = [0] * len(n_clusters_for_nodes_range)
        for (i, nc) in enumerate(n_clusters_for_nodes_range):
            result_obj[i] = {
                "nc": nc,
                "val": comp_avg_vect[i]
            }

        result_b_obj = {
            "nc": None,
            "val": comp_avg_dynamic
        }

        print(result_obj)

        vmax = max(node["val"] for node in result_obj)
        vmin = min(node["val"] for node in result_obj)
        imin = result_obj[0]["nc"]
        imax = result_obj[0]["nc"]
        # ncmax = result_obj

        for obj in result_obj:
            if obj["val"] == vmax:
                imax = obj["nc"]
            if obj["val"] == vmin:
                imin = obj["nc"]

        if result_b_obj["val"] < vmin:
            result_b_obj["nc"] = imin
        if result_b_obj["val"] > vmax:
            result_b_obj["nc"] = imax
        for (i, res) in enumerate(result_obj):
            if i < len(result_obj) - 1:
                if (result_obj[i]["val"] <= result_b_obj["val"] and result_b_obj["val"] <= result_obj[i + 1]["val"]) or (result_obj[i]["val"] >= result_b_obj["val"] and result_b_obj["val"] >= result_obj[i + 1]["val"]):
                    result_b_obj["nc"] = result_obj[i]["nc"]
                    break

        print(result_b_obj)
        # return True
        width = 0.35  # the width of the bars
        plt.bar(n_clusters_for_nodes_range, comp_avg_vect, width)
        plt.bar(result_b_obj["nc"]-width, result_b_obj["val"], width)
        plt.xlabel("number of clusters for nodes")
        plt.ylabel("average deviation from single clustering")
        plt.show()




if __name__ == "__main__":
    print("machine learning test")
    machine_learning = ML_dualVsSingleNumberOfClusters(use_scikit=False)
    machine_learning.read_data()
    machine_learning.test()
