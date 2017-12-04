from modules.data import variables
import json
try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx
from networkx.readwrite import json_graph


class FindPath:
    def __init__(self):
        self.G = None
        self.consumer_nodes = []
        self.pos = []
        self.colors = ["blue", "green", "yellow", "red"]
        self.graph_data = {}

    def write_data_json(self, filename="data/network.json"):
        try:
            with open(filename, 'w') as f:
                data = json_graph.node_link_data(self.G)
                f.write(json.dumps(data, indent=2))
        except:
            globals.print_exception("write data json")

    def load_data_json(self, filename="data/network.json"):
        try:
            with open(filename, 'r') as f:
                data = f.read()
                data = json.loads(data)
                self.get_graph_data(data)
                self.G = json_graph.node_link_graph(data)
                self.pos = nx.circular_layout(self.G)
        except:
            variables.print_exception("load data json")

    def get_graph_data(self, data):
        self.graph_data = data
        # for node in data["nodes"]:
        for (i, edge) in enumerate(data["links"]):
            edge["id"] = str(i)

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
        for (i, node) in enumerate(self.graph_data["nodes"]):
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

    def add_labels(self):
        i_cons = 0
        nodes = self.graph_data["nodes"]
        edges = self.graph_data["links"]
        # add random weights to edges for test purpose, these weights will represent the priorities
        for (i, edge) in enumerate(edges):
            edge["label"] += str(i)
            edge["weight"] = i

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


    def format_data(self):
        pos = self.pos
        for (i, node) in enumerate(self.graph_data["nodes"]):
            node["id_consumer"] = -1
            node["color"] = {"border": "black"}
            node["label"] = "node " + str(i)
            node["x"] = int(pos[node["id"]][0] * 500)
            node["y"] = int(pos[node["id"]][1] * 500)
        for (i, edge) in enumerate(self.graph_data["links"]):
            edge["from"] = edge["source"]
            edge["to"] = edge["target"]
            edge["color"] = {"color": "blue"}
            edge["label"] = str(i)

        self.add_labels()
        # mw_path = self.get_path()
        # self.draw_path(nodes, edges, mw_path)
        # self.add_labels(nodes, edges)
        # self.fdata["nodes"] = nodes
        # self.fdata["edges"] = edges

    def get_data_format(self):
        print("network data: ")
        ret = {"nodes": self.graph_data["nodes"], "edges": self.graph_data["links"]}
        print(ret)
        return ret

if __name__ == '__main__':
    fp = FindPath()
    fp.load_data_json("../data/network.json")
    fp.get_path()
    print(fp.get_data_format())
    