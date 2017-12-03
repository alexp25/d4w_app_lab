from modules.data import variables

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
        self.consumer_nodes = []
        self.pos = []
        self.colors = ["blue", "green", "yellow", "red"]

    def load_data(self, path="modules/data/test.adjlist"):
        fh = open(path, 'rb')
        # G=nx.read_adjlist(fh, create_using=nx.DiGraph())
        self.G = nx.read_multiline_adjlist(fh, create_using=nx.DiGraph())
        # print(G.adjacency())
        # for g in G.adjacency():
        #     print(g)

        # self.pos = nx.spring_layout(self.G) # positions for all nodes
        self.pos = nx.circular_layout(self.G)
        # self.pos = nx.shell_layout(self.G)
        # self.pos = nx.fruchterman_reingold_layout(self.G)
        print(self.pos)

        self.nodes = self.G.nodes()
        # self.nodes = self.pos
        self.edges = self.G.edges()
        # self.consumer_nodes = [x for x in self.G.nodes_iter() if self.G.out_degree(x) == 0 and self.G.in_degree(x) == 1]

        print(self.edges)
        print(self.nodes)

        self.fdata = {
            "nodes": [],
            "edges": []
        }

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

    def set_cluster_for_consumers(self, node_data=None):
        print("set cluster for consumers")
        i_cons = 0
        for (i, node) in enumerate(self.fdata["nodes"]):
            try:
                if node["id_consumer"] != -1:
                    node["cluster"] = 0
                    node["label"] += " cluster"
                    if node_data is not None:
                        node["label"] += ": " + str(node_data[node["id_consumer"]]["class"])
                        try:
                            color = self.colors[node_data[node["id_consumer"]]["class"]]
                        except:
                            color = "black"
                        node["color"] = {"border": color}
            except:
                variables.print_exception("set_cluster_for_consumers")
                break


    def add_labels(self, nodes, edges):
        i_cons = 0
        for (i, node) in enumerate(nodes):
            isdemand = True
            for (i, edge) in enumerate(edges):
                if edge["from"] == node["id"]:
                    isdemand = False
                    break
            if isdemand:
                print("cons node " + str(i_cons))
                node["label"] += " consumer: " + str(i_cons)
                node["id_consumer"] = i_cons
                i_cons += 1

        for (i, edge) in enumerate(edges):
            edge["label"] = "label " + str(i)
            for ad in self.G.adjacency():
                if ad[0] == edge["from"]:
                    edge["label"] = str(ad[1][edge["to"]]["weight"])
                    edge["weight"] = ad[1][edge["to"]]["weight"]
                    break

    def format_data(self):
        print("running pathfinder get data format")
        nodes = []
        edges = []
        for node in self.nodes:
            new_node = {
                "id": node,
                "id_consumer": -1,
                "color": {"border": "black"},
                "label": "node: " + str(node),
                "x": int(self.pos[node][0] * 500),
                "y": int(self.pos[node][1] * 500)
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
        self.add_labels(nodes, edges)
        self.fdata["nodes"] = nodes
        self.fdata["edges"] = edges


    def get_data_format(self):
        # self.get_path_from_formatted_data(edges)

        print("network data: ")
        ret = {"nodes": self.fdata["nodes"], "edges": self.fdata["edges"]}
        print(ret)
        return ret

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