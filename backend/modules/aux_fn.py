
import math
import numpy as np
import matplotlib.pylab as plt

def euclid_dist(t1, t2):
    return math.sqrt(sum((t1 - t2) ** 2))


def get_comp(a1, a2):
    """
    compares two cluster sets
    each cluster set is an array of arrays
    the clusters can be scrambles
    so the comparison should check which are the closest clusters
    and then return the difference
    :param a1:
    :param a2:
    :param get_diff:
    :return:
    """
    comp_euclid_dist = [0] * len(a1)

    comp_array = [0] * len(a1)
    for icomp, ri in enumerate(a1):
        # take average distance as distance to the first centroid from the second data set
        comp_euclid_dist[icomp] = euclid_dist(ri, a2[0])
        comp_array[icomp] = ri - a2[0]
        for jcomp, rj in enumerate(a2):
            dist = euclid_dist(ri, rj)
            # check if there is another centroid that is closer and use that to calculate the difference
            if dist < comp_euclid_dist[icomp]:
                comp_euclid_dist[icomp] = dist

                comp_array[icomp] = ri - rj
    # for comp1 in comp:
    #     print(comp1)
    # comp_avg = np.sqrt(np.mean(comp_euclid_dist))
    # comp_avg = np.mean(comp_euclid_dist)
    comp_avg = 0
    for c in comp_euclid_dist:
        comp_avg = comp_avg + c*c
    comp_avg = np.sqrt(comp_avg)
    # comp_avg = np.std(comp_euclid_dist)
    return comp_euclid_dist, comp_avg, comp_array



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