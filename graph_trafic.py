#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from itertools import cycle

"""
Traffic simulation.
@author: Michael Girardot
"""

class Traffic():
    def __init__(self, edge_list=None, nb_nodes=10, car_count=50, layout=None):
        """
        A traffic class encapsulating a traffic network and its utilities.

        :param edge_list:
        This is a list of tuples of (start_node, end_node, weight dict). The weight dict {'w': n}
        contains the name of the parameter (‘w’) and its value corresponding to the car flow per time step.
        :param nb_nodes: If the edge_list is None, it will generate a random graph with the specified
        number of nodes.
        :param car_count: The number of cars specified are generated and randomly distributed over the
        network nodes.
        :param layout: spectral or None. If None, it will fall back on the default spring layout.
        """
        self.G = self.build_graph(nb_nodes, edge_list=edge_list)
        self.G = self.distribute_tags(self.G, car_count)
        if layout=='spectral':
            self.pos = nx.spectral_layout(self.G)
        else:
            self.pos = nx.spring_layout(self.G)
        if edge_list:
            self.edge_list = edge_list
        self.edge_list = sorted(self.edge_list)
        self.open_path = list(edge_list)
        self.start, self.end, _, _ = self.longest_path()
        self.find_gates()
        self.car1pos = self.find_tag()

    def rand_edges(self, n):
        """
        Generate random pairs of numbers (nodes) with random weights
        :param n: int
        :return: list of tuples
        """
        self.edge_list = []
        nodes_list = list(np.random.choice(n, n, replace=False))
        start = nodes_list.pop()
        for end in nodes_list:
            prev_node = np.random.choice(nodes_list)
            end = np.random.choice([prev_node, end], p=[.2,.8])
            w = int(np.ceil(np.random.rand()*10))
            if end != start:
                self.edge_list.append((start,end,{'w':w}))

            start = np.random.choice([start,end], p=[.2,.8,])
        # return self.edge_list


    def build_graph(self, n, edge_list=None):
        """
        Generate a directed graph with the specified number of nodes
        :param n: int
        :return: networkx DiGraph
        """
        if edge_list:
            G =nx.DiGraph(edge_list, tags=deque([]))
        else:
            self.rand_edges(n)
            G = nx.DiGraph(self.edge_list, tags=deque([]))
        return G


    def longest_path(self):
        """
        Get start and end nodes of the longest path
        :param G:
        :return:
        """
        paths = dict(nx.all_pairs_bellman_ford_path(self.G, weight='w'))
        max_len = 0
        long_path = []

        for k1,v1 in paths.items():
            for k2,v in v1.items():
                l = len(v)
                if l > max_len:
                    max_len = l
                    long_path = v
                    start = k1
                    end = k2
        return (start, end, max_len, long_path)


    def get_multi_edges(self, node):
        if len(self.G.in_edges(node)) > len(self.G.out_edges(node)):
            e = list(self.G.in_edges(node, data=True))
        else:
            e = list(self.G.out_edges(node, data=True))
        return e

    def select_open_path(self, g):
        edges = self.get_multi_edges(g)
        self.open_path = [x for x in self.open_path if x not in edges]
        self.open_path.append(next(self.G.nodes[g]['switch']))
        self.open_path.sort()

    def find_gates(self):
        self.gates = [x[0] for x in self.G.degree() if x[1] > 2]
        for g in self.gates:
            e = self.get_multi_edges(g)
            pool = cycle(e)
            self.G.nodes[g]['switch'] = pool
            self.select_open_path(g)


    def distribute_tags(self, G, n):
        self.cars = ['car_'+str(i) for i in range(n)]
        sample_nodes = np.random.choice(G.nodes, n)
        for car, i in zip(self.cars, sample_nodes):
            if 'tags' in G.nodes[i]:
                G.nodes[i]['tags'].extend([car])
            else:
                G.nodes[i]['tags'] = deque([car])
        return G

    def find_tag(self, tag='car_1'):
        for node in self.G.nodes:
            if ('tags' in self.G.nodes[node]) and (tag in self.G.nodes[node]['tags']):
                return node

    def draw_car(self):
        H = nx.Graph()
        H.add_node('car')
        # pos = nx.spectral_layout(self.G)

        H_pos = {'car': [x+.1 for x in self.pos[self.car1pos]]}
        nx.draw_networkx_nodes(H, H_pos, node_size=15, node_color='black')


    def plot_graph(self):
        plt.cla()
        self.draw_car()

        cols = []
        labs ={}
        for x in self.G.nodes:
            if 'tags' in self.G.nodes[x]:
                l = len(self.G.nodes[x]['tags'])
                cols.append(l)
                labs[x] = l
            else:
                cols.append(0)
                labs[x] = 0
        e_col = []
        for e in self.edge_list:
            if e in self.open_path:
                e_col.append('green')
            else:
                e_col.append('black')
        # pos = nx.spectral_layout(self.G)
        nx.draw_networkx_nodes(self.G,self.pos, node_color=cols, cmap=plt.cm.RdYlGn_r)
        nx.draw_networkx_edges(self.G, self.pos, edge_color=e_col)
        nx.draw_networkx_labels(self.G, self.pos, labels=labs, font_color='w')
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels={x:self.G[x[0]][x[1]]['w'] for x in self.G.edges}, font_size=6)
        plt.axis('off')
        plt.pause(1)

        #plt.show()

    def move(self, start, end, flow=None):
        if not flow:
            flow = self.G[start][end]['w']
        for _ in range(flow):
            if ('tags' in self.G.nodes[start]) and (self.G.nodes[start]['tags']):
                if ('tags' in self.G.nodes[end]) and (self.G.nodes[end]['tags'] != 0):
                    self.G.nodes[end]['tags'].append(self.G.nodes[start]['tags'].popleft())
                else:
                    self.G.nodes[end]['tags'] = deque([self.G.nodes[start]['tags'].popleft()])


    def step(self, refeed=False, flow=2):
        for s, e, w in reversed(self.open_path):
            self.move(s,e)
        if refeed:
            self.move(self.end, self.start, flow)
        self.car1pos = self.find_tag()
        return self.state(), self.reward(), self.is_finished()


    def state(self):
        """
        Car position and number of cars at each nodes
        :return:
        """
        vector = np.zeros(len(self.G.nodes))

        for node in self.G.nodes:
            if 'tags' in self.G.nodes[node]:
                vector[node] = len(self.G.nodes[node]['tags'])
            else:
                vector[node] = 0.0

        return np.concatenate(([self.car1pos], vector))


    def action(self, vector):
        """
        activate the cycle of the ordered gate nodes
        :param vector:
        :return:
        """
        # self.open_path = list(self.edge_list)
        for i, g in enumerate(self.gates):
            if vector[i]:
                self.select_open_path(g)

    def reward(self):
        if self.car1pos == self.end:
            # self.goal_count += 1
            return 20
        else:
            return -1

    def is_finished(self):
        if self.car1pos == self.end:
            return True
        else:
            return False

