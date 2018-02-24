import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

class Qlearning():
    def __init__(self,edge_list, goal, gamma):
        self.number_of_nodes = max(max(x) for x in edge_list) + 1

        self.G = nx.Graph()
        self.G.add_edges_from(edge_list)
        self.gamma = gamma
        self.goal = goal
        self.R_matrix = nx.adjacency_matrix(self.G).todense() - 1
        goal_positions = np.where(self.R_matrix[:, goal] == 0)[0]
        self.R_matrix[goal_positions, goal] = 100
        self.Q_matrix = np.zeros_like(self.R_matrix)

    def find_dims(self):
        cols = int(np.sqrt(self.number_of_nodes))
        rows = self.number_of_nodes/cols
        try:
            assert rows * cols == self.number_of_nodes
            return (rows, cols)
        except:
            print('non square matrix')

    def find_positions(self):
        position_mat = np.array(range(self.number_of_nodes))
        position_mat = position_mat.reshape(self.find_dims())

        position = {}
        for i in range(self.number_of_nodes):
            elements = [pos for pos in np.where(position_mat == i)]
            elements = map(lambda x: np.asscalar(x), elements)
            position[i] = elements
        return position

    def max_Q_next(self, rand_action):
        return np.max(self.Q_matrix[rand_action, :])

    def update_Q_matrix(self, rand_action, current_state):
        # Bellman equation
        self.Q_matrix[current_state, rand_action] = self.R_matrix[current_state, rand_action] + \
                                                    self.gamma * self.max_Q_next(rand_action)

    def sel_rand_action(self, current_state):
        possible_indices = np.where(self.R_matrix[current_state,:] >= 0 )[1]
        return np.random.choice(possible_indices)

    def draw(self):
        pos = self.find_positions()
        nx.draw_networkx_nodes(self.G, pos=pos)
        nx.draw_networkx_labels(self.G, pos=pos, font_color='w')
        nx.draw_networkx_edges(self.G, pos=pos)
        #plt.axis('off')
        plt.grid('on')
        plt.show()

    def optimize(self, epochs=200):
        for i in range(epochs):
            # select a stating node for each epoch
            current_state = np.random.choice(self.G.number_of_nodes())

            # run through the end of the maze
            while current_state != self.goal:
                # random select the next action
                rand_action = self.sel_rand_action(current_state)

                # update the Q_matrix
                self.update_Q_matrix(rand_action, current_state)

                # move to the next state
                current_state = rand_action

    def sel_best_path(self, current_state):
        path = [current_state]
        while current_state != self.goal:
            current_state = np.where(self.Q_matrix[current_state,:] == np.max(self.Q_matrix[current_state,:]))[1]
            current_state = np.random.choice(current_state)
            path.append(current_state)
        return path
