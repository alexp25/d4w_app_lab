
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
    node_index = 15



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
    plt.ylabel("average deviation")


    plt.figure()

    plt.pcolormesh(npmat)

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Make data.
    X = np.arange(-5, 5, 0.25)
    Y = np.arange(-5, 5, 0.25)
    X, Y = np.meshgrid(X, Y)
    R = np.sqrt(X ** 2 + Y ** 2)
    Z = np.sin(R)

    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()


