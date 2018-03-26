import csv
import numpy as np

import random
from math import sqrt
import json

import copy
from modules.data import variables

class ClusteringClass:

    def __init__(self, num_clust=8, num_iter=5):
        # self.centroids = random.sample(data, num_clust)
        self.centroids = None
        self.num_iter = num_iter
        self.num_clust = num_clust
        self.data = None
        self.w = 5
        self.assignments = {}


    def reinit(self, data, num_clust=8, num_iter=5, centroids=None):
        self.num_clust = num_clust
        self.num_iter = num_iter
        d = copy.deepcopy(data)
        if centroids is None:
            self.centroids = np.array(random.sample(d.tolist(), self.num_clust))
        else:
            self.centroids = copy.deepcopy(centroids)
        self.data = None
        self.data = d
        self.assignments = {}
        # print(self.data)
        # print(len(self.data))
        return self.centroids

    def add_new_data(self, data, num_clust=8):
        if self.centroids is None:
            self.reinit(data, num_clust)
        else:
            self.data = copy.deepcopy(data)

    def euclid_dist(self, t1, t2):
        return sqrt(sum((t1 - t2) ** 2))

    def DTWDistance_base(self, s1, s2):
        DTW = {}

        for i in range(len(s1)):
            DTW[(i, -1)] = float('inf')
        for i in range(len(s2)):
            DTW[(-1, i)] = float('inf')
        DTW[(-1, -1)] = 0

        for i in range(len(s1)):
            for j in range(len(s2)):
                dist = (s1[i] - s2[j]) ** 2
                DTW[(i, j)] = dist + min(DTW[(i - 1, j)], DTW[(i, j - 1)], DTW[(i - 1, j - 1)])

        return sqrt(DTW[len(s1) - 1, len(s2) - 1])

    def DTWDistance(self, s1, s2, w):
        # speed up
        DTW = {}
        w = max(w, abs(len(s1) - len(s2)))
        for i in range(-1, len(s1)):
            for j in range(-1, len(s2)):
                DTW[(i, j)] = float('inf')
        DTW[(-1, -1)] = 0
        for i in range(len(s1)):
            for j in range(max(0, i - w), min(len(s2), i + w)):
                dist = (s1[i] - s2[j]) ** 2
                DTW[(i, j)] = dist + min(DTW[(i - 1, j)], DTW[(i, j - 1)], DTW[(i - 1, j - 1)])
        return sqrt(DTW[len(s1) - 1, len(s2) - 1])

    def LB_Keogh(self, s1, s2, r):
        LB_sum = 0
        for ind, i in enumerate(s1):
            lower_bound = min(s2[(ind - r if ind - r >= 0 else 0):(ind + r)])
            upper_bound = max(s2[(ind - r if ind - r >= 0 else 0):(ind + r)])
            if i > upper_bound:
                LB_sum = LB_sum + (i - upper_bound) ** 2
            elif i < lower_bound:
                LB_sum = LB_sum + (i - lower_bound) ** 2
        return sqrt(LB_sum)

    def k_means_clust_dynamic_partial_update(self, nsamp, data=None):
        """
        self.data should be only the current time series (partial)
        :param nsamp:
        :return:
        """
        counter = 0
        ni = self.num_iter
        # ni = 1
        for n in range(1):
            # assign data points to clusters
            if data is None:
                ts1 = self.data
            else:
                ts1 = data

            ts1_partial = ts1[0:nsamp]
            # print(ts1_partial)
            min_dist = float('inf')
            closest_clust = None
            for c_ind, ts2 in enumerate(self.centroids):
                # compare the partial time series to the partial centroid
                ts2_partial = ts2[0:nsamp]
                # print(ts2_partial)
                # print(ts1_partial.shape)
                # print(ts2_partial.shape)
                cur_dist = self.euclid_dist(ts1_partial, ts2_partial)
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    closest_clust = c_ind

            centroid = [0] * nsamp
            for di, d in enumerate(ts1.tolist()):
                centroid[di] += d
            try:
                n_assignments = len(self.assignments[closest_clust])
                self.centroids[closest_clust][0:len1] = (self.centroids[closest_clust][0:len1] * n_assignments + centroid)/(n_assignments+1)
            except:
                variables.print_exception("")

        return self.centroids

    def k_means_clust_dynamic_partial_update_whole(self, data):
        """
        adding sample to data and updating the clusters
        there should be already clusters
        and new data is only added to the cluster
        :param nsamp:
        :return:
        """
        for n in range(self.num_iter):
            # assign data points to clusters
            # print(ts1_partial)
            min_dist = float('inf')
            closest_clust = None
            for c_ind, ts2 in enumerate(self.centroids):
                # compare the data to each cluster centroids
                cur_dist = self.euclid_dist(data, ts2)
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    closest_clust = c_ind

            try:
                n_assignments = len(self.assignments[closest_clust])
                self.centroids[closest_clust] = (self.centroids[closest_clust] * n_assignments + data)/(n_assignments+1)
                # self.centroids[closest_clust] = (self.centroids[closest_clust] + data) / 2
            except:
                print("exception")
                variables.print_exception("")
        # print(np.average(self.centroids))

        return self.centroids

    def k_means_clust_dynamic(self):
        counter = 0
        ni = self.num_iter
        # ni = 1
        for n in range(ni):
            # print(n)
            # print(self.centroids)
            counter += 1
            # print counter
            self.assignments = {}
            # assign data points to clusters
            for ind, ts1 in enumerate(self.data):
                min_dist = float('inf')
                closest_clust = None
                for c_ind, ts2 in enumerate(self.centroids):
                    # compare the time series to the centroid
                    # by the euclidean distance
                    cur_dist = self.euclid_dist(ts1, ts2)
                    if cur_dist < min_dist:
                        min_dist = cur_dist
                        closest_clust = c_ind

                    # if self.LB_Keogh(i, j, 5) < min_dist:
                    #     cur_dist = self.DTWDistance(i, j, self.w)
                    #     # find the closest cluster (centroid) for the time series
                    #     if cur_dist < min_dist:
                    #         min_dist = cur_dist
                    #         closest_clust = c_ind

                # if the cluster contains other time series
                # append the time series index
                # otherwise initialize the cluster with empty array
                if closest_clust in self.assignments:
                    self.assignments[closest_clust].append(ind)
                else:
                    self.assignments[closest_clust] = []

            # recalculate centroids of clusters using the assigned time series
            for key in self.assignments:
                # calculate sum of time series from the current assignment, then
                # calculate the cluster by averaging time series
                n_assignments = len(self.assignments[key])

                # print(str(key)+","+str(n_assignments))
                centroid = [0] * len(self.data[0])
                # print(centroid)
                if n_assignments == 0:
                    self.centroids[key] = centroid
                    continue

                for ai, k in enumerate(self.assignments[key]):
                    for di, d in enumerate(self.data[k].tolist()):
                        centroid[di] += d
                # print(centroid)
                # print(self.data[0])
                # print(str(key) + "," + np.sum(centroid))
                # print("centroid " + str(key))
                # print(centroid/n_assignments)
                if centroid is not None:
                    # for ci, centroid_val in self.centroids[key]:
                    #     centroid_val = (centroid_val + centroid[ci] / n_assignments)/2
                    # self.centroids[key] = [0] * len(centroid)
                    # for ci, m in enumerate(centroid):
                    #     self.centroids[key][ci] = m / n_assignments
                    self.centroids[key] = [m / n_assignments for m in centroid]
                    # print([m / n_assignments for m in centroid])
                    # self.centroids[key] = (self.centroids[key] + [m / n_assignments for m in centroid])/2

        # print(self.assignments)
        ts_assignments = [0] * len(self.data)

        for key in self.assignments:
            # print(key)
            for a in self.assignments[key]:
                ts_assignments[a] = key

        # print(ts_assignments)
        return self.centroids, ts_assignments




