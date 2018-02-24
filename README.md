# Traffic simulator

Traffic regulation is a well-known problem for reinforcement learning. However one could not expect to deploy artificial intelligence without simulation. In this experiment, I would like to develop a simple traffic simulation that I could use to learn and test current deep-reinforcement learning (RL) technics. Existing tools for traffic simulation includes the SUMO simulator. Such advanced tools are not fit for this task since one needs to process raw images from the GUI. On the other hand, reinforcement learning frameworks such as gym form OpenAI are great tools to test deep-RL with its simple API. I will follow the gym design guidelines to design this traffic simulator. Designing my own traffic simulator will allow to fully understand the environment and control its complexity.

## Design
Graph is a natural choice for modeling a transportation network. I will use the networkx library that comes with algorithms and drawing capabilities. Geographic coordinates are represented by nodes and roads by edges.
```
   o --> o
   o  f  d 
```
This is a directed graph with nodes and edges attributes (o,d and f) corresponding to the number of cars at that position and the flow of cars per time step, respectively. at each time step, we can update the network as follow:
```
   o --> o
 o-f  f  d+f 
```
Cars at each node are stored in a “First In First Out” queue. Thus a car that just arrives at a node can spend several steps at that node until other cars that arrived before moving to another node. This will allow traffic jams situations where the flow is suboptimal for the number of cars present.

## Traffic class

The transportation network can be randomly generated or specified by an edge list. 
* **edge_list** parameter:
This is a list of tuples of (start_node, end_node, weight dict)
The weight dict contains the name of the parameter (‘w’) and its value corresponding to the car flow per time step.

* **car_count** parameter:
The number of cars specified are generated and randomly distributed over the network nodes. We will follow ‘car_1’ to compute traffic statistics.

## Tests
* Without an agent to control the traffic, we observe about half of the cars reaching the destination in the defined time frame (30 steps).
* A random agent is able to decrease the fraction of cars that do not reach the destination (-30) in the defined time frame. Thus turning red lights on and off even randomly is good to regulate the network.
* Using a schedule can decrease drastically the number of cars that do not reach the destination. However, we observe significantly more traffic jams (shoulders in between -30 and +20) than the random agent.