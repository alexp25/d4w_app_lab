
import csv
import matplotlib.pylab as plt
import numpy as np

if __name__ == "__main__":
    mat = []
    with open("data/mat.txt") as f:
        r = csv.reader(f, delimiter='\t', quotechar='|')
        mat = [[float(col) for col in row if col != ''] for row in r]
        print(mat)

    width = 0.35  # the width of the bars

    case_index = 10
    node_index = 20

    lim1 = 4
    lim2 = 79

    npmat = np.array(mat)
    print(npmat)
    print(npmat.shape)

    # data for all nodes for a single case
    print(npmat[node_index, :])

    ind = np.arange(len(npmat[case_index, :]))
    plt.bar(ind, npmat[case_index, :], width)
    plt.gca().set_title("data for all nodes for test case " + str(case_index))

    #  data for node
    print(npmat[:, node_index])
    plt.figure()

    ind = np.arange(len(npmat[:, node_index]))
    plt.bar(ind, npmat[:, node_index], width)
    plt.gca().set_title("data for node " + str(node_index) + " for all test cases")
    plt.xlabel("test case: " + str(lim1) + " - " + str(lim2) + " initial samples")

    plt.show()


