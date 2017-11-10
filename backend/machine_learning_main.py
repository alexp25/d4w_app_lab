import csv
import numpy as np


from read_data import DataClass
import scipy
# from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn.cluster import KMeans

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import math
import random

from math import sqrt

from os import listdir
from os.path import isfile, join


class MachineLearningMain:
    def __init__(self):
        self.dc = DataClass()

        self.files = [f for f in listdir("data") if isfile(join("data", f))]
        print(self.files)

        centroids = []

        plotdata = 1
        plot_original_data = 0

        self.n_series = len(self.files)
        self.n_series = 1

        experiment_id = 2

        # use last n_elem from data
        # [n-n_elem:n]
        n_elem = 168
        # use offset
        # [n-n_elem-n_elem_offset:n-n_elem_offset]
        n_elem_offset = 0

    def read_data(self):

        """
            read data from files
            each file has the data for a measurement node
            over a time frame of n days, for every hour
        :return:
        """
        for i, f in enumerate(self.files[0:self.n_series]):
            data = self.dc.read_data(join("data/", f))
            print(i)
            leg = []
            imax = data["series"].shape[0]

            print('imax: ' + str(imax))
            imax = 5
            ts = []

            info = {
                "min": 0,
                "max": 0,
                "headers": None
            }

            info["min"] = np.min(data["series"])
            info["max"] = np.max(data["series"])
            info["headers"] = np.ndarray.tolist(data["headers"])

            return (np.ndarray.tolist(data["series"]), info)


            # # data["series"][j, :]
            # if plotdata:
            #     plt.figure(i)
            #     if plot_original_data:
            #         plt.subplot(211)
            #         for j in range(0, imax):
            #             plt.plot(data["series"][j, :])
            #             plt.draw()
            #             plt.pause(0.001)
            #             leg.append('ts' + str(j))
            #         plt.legend(leg)
            #
            # # print(data["series"])
            # len_data = len(data["series"])
            # data1 = data["series"]
            # kmeans = KMeans(n_clusters=nclusters)
            # # print kmeans
            # # Compute cluster centers and predict cluster index for each sample.
            # a = kmeans.fit(data1)
            # # print a.cluster_centers_
            # # print a.predict(data1)
            # print(a.predict(data1))
            # print('transform')
            # d = a.transform(data1)
            # print(d)
            #
            # plt.draw()
            # plt.pause(0.001)
            # plt.show(block=True)



