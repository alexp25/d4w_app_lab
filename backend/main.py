
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


from matplotlib import style
style.use('ggplot')

dc = DataClass()

from os import listdir
from os.path import isfile, join
files = [f for f in listdir("data") if isfile(join("data", f))]
print(files)

centroids = []

plotdata = 1
plot_original_data = 0


n_series = len(files)
n_series = 1


experiment_id = 2

# use last n_elem from data
# [n-n_elem:n]
n_elem = 168
# use offset
# [n-n_elem-n_elem_offset:n-n_elem_offset]
n_elem_offset = 0

if experiment_id == 0:
    nclusters_final = 4
    nclusters = 2
    for i, f in enumerate(files[0:n_series]):
        data = dc.read_data(join("data/", f))
        print(i)
        leg = []
        imax = data["series"].shape[0]
        imax = 5
        ts = []
        if plotdata:
            plt.figure(i)
            if plot_original_data:
                plt.subplot(211)
                for j in range(0, imax):
                    plt.plot(data["series"][j, :])
                    plt.draw()
                    plt.pause(0.001)
                    leg.append('ts' + str(j))
                plt.legend(leg)

        # print(data["series"])
        len_data = len(data["series"])
        data1 = data["series"]
        kmeans = KMeans(n_clusters=nclusters)
        # print kmeans
        # Compute cluster centers and predict cluster index for each sample.
        a = kmeans.fit(data1)
        # print a.cluster_centers_
        # print a.predict(data1)
        print(a.predict(data1))
        print('transform')
        d = a.transform(data1)
        print(d)

        plt.draw()
        plt.pause(0.001)
        plt.show(block=True)

elif experiment_id == 1:
    nclusters_final = 4
    nclusters = 5
    for i,f in enumerate(files[0:n_series]):
        data = dc.read_data(join("data/",f))
        print(i)
        leg=[]
        imax = data["series"].shape[0]
        imax = 5
        ts=[]
        if plotdata:
            plt.figure(i)
            if plot_original_data:
                plt.subplot(211)
                for j in range(0,imax):
                    plt.plot(data["series"][j,:])
                    plt.draw()
                    plt.pause(0.001)
                    leg.append('ts'+str(j))
                plt.legend(leg)

        # print(data["series"])
        len_data = len(data["series"])
        data1 = data["series"][0:int(len_data/2)]
        data2 = data["series"]
        kmeans = KMeans(n_clusters=nclusters)
        # print kmeans
        # Compute cluster centers and predict cluster index for each sample.
        a = kmeans.fit(data1)
        # print a.cluster_centers_
        # print a.predict(data1)
        print(a.predict(data1))
        print(a.predict(data2))

        a = kmeans.fit(data2)
        centroids.append(a.cluster_centers_)

        if plotdata:
            if plot_original_data:
                plt.subplot(212)
            leg=[]
            for (j,centroid) in enumerate(centroids[i]):
                plt.plot(centroid)
                leg.append("centroid "+str(j))
            plt.legend(leg)
            plt.draw()
            plt.pause(0.001)
            plt.show(block=False)
            plt.savefig('img/' + f + '.png')

    centroids_all = []
    for centroid_group in centroids:
        for centroid in centroid_group:
            centroids_all.append(centroid)
    centroids_np = [centroid for centroid in centroids_all]
    centroids_np = np.array(centroids_np)
    centroids_np = centroids_np[:, 1:].astype(float)
    # print centroids_np
    plot_original_data=1
    plt.figure(n_series+1)

    kmeans = KMeans(n_clusters=nclusters_final)
    # print kmeans
    # Compute cluster centers and predict cluster index for each sample.
    a = kmeans.fit(centroids_np)
    # print a.cluster_centers_
    # print a.predict(data1)
    final_centroids = a.cluster_centers_

    if plotdata:
        if plot_original_data:
            plt.subplot(211)
            for centroid in centroids_np:
                plt.plot(centroid)
                # plt.draw()
                # plt.pause(0.001)

        leg=[]
        if plot_original_data:
            plt.subplot(212)
        for j in range(0,len(final_centroids)):
            plt.plot(final_centroids[j])
            leg.append("final centroid "+str(j))
        # plt.ylim(-2,10)
        plt.legend(leg)
        # plt.ion()
        plt.draw()
        plt.pause(0.001)
        plt.show(block=False)
        plt.savefig('img/' + 'centroids' + '.png')



elif experiment_id == 2:
    nclusters = 4

    nseries=len(files)
    # nseries = 5
    data_array = []
    centroids = []
    for i, f in enumerate(files[0:nseries]):
        data = dc.read_data(join("data/", f))
        data = data["series"].flatten()
        data_len = len(data)
        data = data[data_len-n_elem-n_elem_offset:data_len-n_elem_offset]
        data_array.append(data)

        if plotdata and plot_original_data:
            plt.figure(i)

            plt.plot(data)
            leg = f
            plt.legend(leg)
            plt.draw()
            plt.pause(0.001)
            plt.show(block=False)
            plt.savefig('img/'+f+'.png')

    plt.figure(n_series + 1)

    kmeans = KMeans(n_clusters=nclusters)
    # print kmeans
    # Compute cluster centers and predict cluster index for each sample.
    a = kmeans.fit(data_array)
    # print a.cluster_centers_
    assignments = a.predict(data_array)
    centroids = a.cluster_centers_
    # d = a.transform(data_array) #calculates distance from centroids
    #
    # avg_dist_centroid=[]
    # for j in range(len(d)):
    #     avg_dist_centroid.append(np.mean(d[j,:]))
    # avg_dist_centroid = np.array(avg_dist_centroid)
    # print avg_dist_centroid
    # # print assignments
    # index = sorted(range(len(assignments)), key=lambda k: assignments[k])
    # # print index
    # assignments_arranged = assignments[index]
    # avg_dist_centroid_arranged = avg_dist_centroid[index]
    # # print assignments_arranged
    #
    #
    # assignment_count=[]
    # average_centroid=[]
    # leg=[]
    # for j in range(nclusters):
    #     assignment_count.append(len(assignments[assignments==j]))
    #     average_centroid.append(np.mean(centroids[j]))
    #     leg.append("cluster " + str(j))
    # # plt.figure(i)
    #
    # # plt.stem(assignment_count)
    # index = np.arange(nclusters)
    # bar_width = 0.35
    # plt.bar(index,average_centroid,bar_width)
    # plt.xticks(index, leg)
    # plt.ylabel('Average consumption')
    # plt.draw()
    #
    # plt.pause(0.001)
    # plt.show(block=False)
    # plt.savefig('img/' + 'average_cons' + '.png')
    #
    # plt.figure(n_series + 2)
    # index = np.arange(nclusters)
    # bar_width = 0.35
    # plt.bar(index, assignment_count, bar_width)
    # plt.xticks(index, leg)
    # plt.ylabel('Number of consumers')
    # plt.draw()
    # plt.pause(0.001)
    # plt.show(block=False)
    # plt.savefig('img/' + 'cluster_count' + '.png')
    #
    # plt.figure(n_series + 3)
    # index = np.arange(nclusters)
    # bar_width = 0.35
    # plt.stem(avg_dist_centroid_arranged)
    # # plt.xticks(index, leg)
    # plt.ylabel('Distance from centroid')
    # plt.draw()
    # plt.pause(0.001)
    # plt.show(block=False)
    # plt.savefig('img/' + 'cluster_map' + '.png')


    plt.figure(n_series + 4)
    if plotdata:
        leg = []
        for j in range(0, len(centroids)):
            plt.plot(centroids[j])
            leg.append("centroid " + str(j))
        plt.legend(leg)
        plt.draw()
        plt.xlabel('Time (h)')
        plt.ylabel('Consumption')
        plt.pause(0.001)
        plt.show(block=False)
        plt.savefig('img/' + 'centroids' + '.png')

plt.show()