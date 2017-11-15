




try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx


class FindPath:
    def __init__(self):
        self.G = None
        self.nodes = []
        self.edges = []
        self.pos = []

    def load_data(self, path="modules/data/test.adjlist"):
        fh=open(path, 'rb')
        # G=nx.read_adjlist(fh, create_using=nx.DiGraph())
        self.G=nx.read_multiline_adjlist(fh, create_using=nx.DiGraph())
        # print(G.adjacency())
        # for g in G.adjacency():
        #     print(g)

        self.pos = nx.spring_layout(self.G) # positions for all nodes
        print(self.pos)

        self.nodes = self.G.nodes()
        # self.nodes = self.pos
        self.edges = self.G.edges()

        print(self.edges)
        print(self.nodes)


        print(list(self.G.adjacency()))
        print("done reading graph data")

    def get_data(self):
        return list(self.G.adjacency())

    def get_path(self):
        """
        path should be calculated by node priority !! (not by edge weights)
        SOLUTION:
        the edge weights can be defined as the average between end node priorities

        Still not good, because it doesn't treat the case when there are other affected nodes (end nodes) on the path
        :return:
        """
        source = '1'
        dest = '10'
        path_vect = list(nx.all_simple_paths(self.G, source=source, target=dest))
        print("all paths")
        print(path_vect)
        print("min weight path")
        mw_path = list(nx.all_shortest_paths(self.G, source, dest, weight='weight'))[0]
        print(mw_path)


        return mw_path

    # def get_path_from_formatted_data(self, edges):
    #     source = '1'
    #     dest = '10'
    #
    #     def get_weight(edges, path):
    #         w = 0
    #         for i in range(len(path) - 1):
    #             for edge in edges:
    #                 if path[i] == edge["from"]:
    #                     if path[i + 1] in edge["to"]:
    #                         # print("color red: " + str(edge))
    #                         w += edge["weight"]
    #                         break
    #         return w
    #
    #     path = list(nx.all_simple_paths(self.G, source, dest))[0]
    #     print("get path weight: ")
    #     print(path)
    #     mw_path = get_weight(edges, path)
    #     # mw_path = max((path for path in nx.all_simple_paths(self.G, source, dest)),
    #     #               key=lambda path: get_weight(self.edges, path))
    #     print(mw_path)


    def draw_path(self, nodes, edges, mw_path):
        for i in range(len(mw_path) - 1):
            for edge in edges:
                # print("edge: " + str(edge))
                if mw_path[i] == edge["from"]:
                    if mw_path[i+1] in edge["to"]:
                        # print("color red: " + str(edge))
                        edge["color"] = {"color": "red"}
                        break

    def add_labels(self, edges):
        for (i, edge) in enumerate(edges):
            edge["label"] = "label " + str(i)
            for ad in self.G.adjacency():
                if ad[0] == edge["from"]:
                    edge["label"] = str(ad[1][edge["to"]]["weight"])
                    edge["weight"] = ad[1][edge["to"]]["weight"]
                    break

    def get_data_format(self):
        nodes = []
        edges = []
        for node in self.nodes:
            # print(node)
            new_node = {
                "id": node,
                "label": "node: " + str(node),
                "x": self.pos[node][0],
                "y": self.pos[node][1]
            }
            nodes.append(new_node)
        for edge in self.edges:
            new_edge = {
                "from": edge[0],
                "to": edge[1],
                "color": {"color": "blue"},
                "label": ""
            }
            edges.append(new_edge)

        mw_path = self.get_path()
        self.draw_path(nodes, edges, mw_path)
        self.add_labels(edges)
        # self.get_path_from_formatted_data(edges)
        return {"nodes": nodes, "edges": edges}

    # G=nx.Graph()
    #
    #
    # G.add_node('a')
    #
    # G.add_edge('a','b',weight=0.6)
    # G.add_edge('a','c',weight=0.2)
    # G.add_edge('c','d',weight=0.1)
    # G.add_edge('c','e',weight=0.7)
    # G.add_edge('c','f',weight=0.9)
    # G.add_edge('a','d',weight=0.3)

    # elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >0.5]
    # esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=0.5]
    #
    # pos=nx.spring_layout(G) # positions for all nodes
    # print(pos)
    #
    # # nodes
    # nx.draw_networkx_nodes(G,pos,node_size=700)
    #
    # # edges
    # nx.draw_networkx_edges(G,pos,edgelist=elarge,
    #                     width=6)
    # nx.draw_networkx_edges(G,pos,edgelist=esmall,
    #                     width=6,alpha=0.5,edge_color='b',style='dashed')
    #
    # # labels
    # nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
    #
    #
    # print(G.adjacency())
    # for g in G.adjacency():
    #     print(g)
    #
    #
    #
    # source = '1'
    # dest = '10'
    #
    # # path_gen = nx.all_simple_paths(G, source=source, target=dest)
    # # path_vect = []
    # # for path in path_gen:
    # #     print(path)
    # #     path_vect.append(path)
    # #
    # # def get_weight(path, G):
    # #     nodes = G.nodes()
    # #
    # #     w = 0
    # #     print("get weight")
    # #     print(nodes)
    # #     for node in path:
    # #         print(nodes[node])
    # #         # w += nodes[node]
    # #
    # #
    # # get_weight(path_vect[0], G)
    #
    # path_vect = list(nx.all_simple_paths(G, source=source, target=dest))
    # print("all paths")
    # print(path_vect)
    # print("min weight path")
    # print(list(nx.all_shortest_paths(G, source, dest, weight='weight')))
    #
    # # heaviest_path = max((path for path in nx.all_simple_paths(G, source, dest)), key=lambda path: get_weight(path))
    # # print(heaviest_path)
    #
    # plt.axis('off')
    # plt.savefig("weighted_graph.png") # save as png
    # plt.show() # display

if __name__ == '__main__':
    fp = FindPath()
    fp.load_data("data/test.adjlist")
    fp.get_path()
    print(fp.get_data_format())