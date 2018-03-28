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


class ML_Anomaly:
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



    def run_test_3(self):
        """
        adding an anomaly at a certain point (constant additional demand)
        comparing the evolution of clusters (with partial clustering) to the normal evolution of clusters
        observing the velocity of change that gives the time until steady state error
        """

        day_start_deviation = 10
        day_end = 20
        deviation = 200
        # iterations = day_end - day_start_deviation
        iterations = day_end
        deviation_element_vect = [None]*iterations
        deviation_total_vect = [None]*iterations
        res_partial_whole_vect = [None]*iterations
        res_partial_whole_anomaly_vect = [None]*iterations

        data = copy.deepcopy(self.data[0]["series"])
        data_with_constant_anomaly = copy.deepcopy(self.data[0]["series"])


        # add constant deviation (anomaly) to the second data set
        # starting with day_start_deviation (index for the day of the start of the anomaly)
        for i,d in enumerate(range(day_start_deviation, day_end)):
            for j in range(len(data_with_constant_anomaly[d])):
                data_with_constant_anomaly[d][j] += deviation

        centroids_init = dcluster.reinit(data[0:day_start_deviation-1], 2, 5)
        res_partial_whole, a = dcluster.k_means_clust_dynamic()

        # for i, d in enumerate(range(day_start_deviation, day_end)):
        for i,d in enumerate(range(day_end)):
            print(str(i)+","+str(d))
            res_partial_whole_vect[i] = copy.deepcopy(dcluster.k_means_clust_dynamic_partial_update_whole(data[d]))

        # run clustering update for second data set with anomalies
        dcluster.reinit(data_with_constant_anomaly[0:day_start_deviation-1], 2, 5, centroids_init)
        res_partial_whole_anomaly, a = dcluster.k_means_clust_dynamic()

        # for i,d in enumerate(range(day_start_deviation, day_end)):
        for i, d in enumerate(range(day_end)):
            print(str(i) + "," + str(d))
            res_partial_whole_anomaly_vect[i] = copy.deepcopy(dcluster.k_means_clust_dynamic_partial_update_whole(data_with_constant_anomaly[d]))

        # plot the results (deviation between the 2 data sets)
        for i,d in enumerate(range(day_end)):
            total_deviation, average_deviation, deviation = get_comp(res_partial_whole_anomaly_vect[i], res_partial_whole_vect[i])
            print(average_deviation)
            deviation_total_vect[i] = average_deviation
            deviation_element_vect[i] = deviation

            plt.clf()
            for ts in res_partial_whole_vect[i]:
                plt.plot(ts)
            for ts in res_partial_whole_anomaly_vect[i]:
                plt.plot(ts)

            plt.gca().set_title("deviation " + str(d) + ", with anomaly from day " + str(day_start_deviation))
            plt.pause(0.2)


        print(deviation_total_vect)

        plt.clf()
        # plt.subplot(212)
        plt.plot(deviation_total_vect)
        # plt.ylim([-100, 100])
        plt.gca().set_title("anomaly transient effect on cluster centroids")
        plt.xlabel("time (days)")
        plt.ylabel("standard deviation")
        plt.show()


if __name__ == "__main__":
    print("machine learning test")
    machine_learning = ML_Anomaly(use_scikit=False)
    machine_learning.read_data()
    machine_learning.run_test_3()
