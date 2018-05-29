# Wireless-Sensor-Network
This is the project of Paristech master 1-2 for the lesson "Wireless Sensor Network".

## Background
The scenario is to monitor the environment of the forest and detect the fire on real-time by using sensors (ex: temperature sensor, humiture sensor).
The protocol behind the project is to using the protocol LEACH (Low-Energy Adoptive Clustering Heirarchy), the paper is [here](https://ieeexplore.ieee.org/abstract/document/926982/).

## Algorithm
1. Several nodes form a cluster and choose the one which has the largest energy as the cluster head. (The node will not join the cluster if the cluster head is too far away from it)
2. The cluster head collects messages (ex: temperature) from all nodes in the cluster, pack them and send the package to the base station.
3. After several time (using timer), back to step 1, nodes reform cluster and rechoose the cluster head.

Besides, we also use the photoresistor to detect the solar energy and charge nodes using this intensity.

## Code
- Node.py
Main code used by all nodes except the base station.
- Base_Station.py
Main code used by the base station.
