
import math
import numpy as np
import matplotlib.pylab as plt

def euclid_dist(t1, t2):
    return math.sqrt(sum((t1 - t2) ** 2))


def get_comp(a1, a2):
    """
    compares two cluster sets
    each cluster set is an array of arrays
    the clusters can be scrambled
    so the comparison should check which are the closest clusters
    and then return the difference
    :param a1:
    :param a2:
    :param get_diff:
    :return:
    """
    comp_euclid_dist = [0] * len(a1)

    diff_array = [0] * len(a1)
    for i_comp, ri in enumerate(a1):
        # take average distance as distance to the first centroid from the second data set
        comp_euclid_dist[i_comp] = euclid_dist(ri, a2[0])
        diff_array[i_comp] = ri - a2[0]
        for j_comp, rj in enumerate(a2):
            dist = euclid_dist(ri, rj)
            # check if there is another centroid that is closer and use that to calculate the difference
            if dist < comp_euclid_dist[i_comp]:
                comp_euclid_dist[i_comp] = dist
                diff_array[i_comp] = ri - rj

    comp_euclid_dist_average = 0
    for c in comp_euclid_dist:
        comp_euclid_dist_average = comp_euclid_dist_average + c*c
    comp_euclid_dist_average = np.sqrt(comp_euclid_dist_average)
    # comp_avg = np.std(comp_euclid_dist)
    return comp_euclid_dist, comp_euclid_dist_average, diff_array



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

def get_array_of_arrays(a):
    array = []
    for ag in a:
        for ag1 in ag:
            array.append(ag1)
    return array