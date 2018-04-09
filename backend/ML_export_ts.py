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

from modules.aux_fn import *


class ML_Export_TS:
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

    def export_ts(self, node):
        self.dc.write_data("data/output/"+str(node)+".csv", self.data[node]["series"], 2)


if __name__ == "__main__":
    print("machine learning test")
    machine_learning = ML_Export_TS(use_scikit=False)
    machine_learning.read_data()
    machine_learning.export_ts(15)
