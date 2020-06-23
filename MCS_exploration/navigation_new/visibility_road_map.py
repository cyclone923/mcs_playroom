"""

Visibility Road Map Planner

author: Atsushi Sakai (@Atsushi_twi)

"""

import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import random

from descartes import PolygonPatch
#from geometry import Geometry
import Geometry


import shapely.geometry as sp
from MCS_exploration.navigation.dijkstra_search import DijkstraSearch

show_animation = True

class IncrementalVisibilityRoadMap:

    def __init__(self, robot_radius, do_plot=False):
        self.robot_radius = robot_radius
        self.do_plot = do_plot
        self.obs_nodes = []
        self.obs_roadmap_adj = []
        self.obstacles = sp.MultiPolygon()

    
    def addObstacle(self, obstacle):
        # add obstacle
        self.obstacles = self.obstacles.union(sp.polygon.orient(sp.Polygon(obstacle),sign=1))

        # add nodes for each vertex
        x_list = [p[0] for p in obstacle.exterior.coords]
        y_list = [p[1] for p in obstacle.exterior.coords]
        
        cvx_list, cvy_list = self.calc_vertexes_in_configuration_space(x_list, y_list)

        #new_nodes = [DijkstraSearch.Node(vx, vy) for vx,vy in zip(cvx_list, cvy_list) if self.can_node_fit_circle(DijkstraSearch.Node(vx, vy))]
        new_nodes = [DijkstraSearch.Node(vx, vy) for vx,vy in zip(cvx_list, cvy_list)]
        self.obs_nodes.extend(new_nodes)

        #check new edges for intersection with all objects
        for i,node in enumerate(new_nodes):
            self.obs_roadmap_adj.append(self.getValidNodeEdges(node))
        
        for i in range(len(new_nodes)):
            idx = len(self.obs_nodes)-len(new_nodes)+i
            for n in self.obs_roadmap_adj[idx]:
                self.obs_roadmap_adj[n].append(idx)

            
        #check old edges for intersection with this object
        for src_id, adj in enumerate(self.obs_roadmap_adj):
            rm = []
            for i,tar_id in enumerate(adj):
                #print(len(self.obs_nodes), src_id, tar_id)
                if not self.validEdge(self.obs_nodes[src_id], self.obs_nodes[tar_id]):
                    rm.append(i)
            rm.reverse()
            for i in rm:
                del self.obs_roadmap_adj[src_id][i]
    
    def validEdge(self, p1, p2):
        if math.sqrt( (p1.x - p2.x)**2 + (p1.y - p2.y)**2) <= 0.01:
                 return False

        radiusPolygon = sp.LineString([[p1.x,p1.y], [p2.x,p2.y]]).buffer(self.robot_radius)
        #patch2b = PolygonPatch(radiusPolygon, fc="blue", ec="blue", alpha=0.5, zorder=2)
        #plt.gca().add_patch(patch2b)
        return not radiusPolygon.intersects(self.obstacles)


    def getValidNodeEdges(self, src_node):
        #draw a point to each other point and check valid
        node_adj = []
        for node_id, node in enumerate(self.obs_nodes):
            if self.validEdge(src_node, node):
                node_adj.append(node_id)

        return node_adj
        

    def planning(self, start_x, start_y, goal_x, goal_y):

        sg_nodes = [DijkstraSearch.Node(start_x, start_y),
                 DijkstraSearch.Node(goal_x, goal_y)]

        sg_edges = [[],[]]


        planNodes = self.obs_nodes.copy() + sg_nodes
        planRoadmap = self.obs_roadmap_adj.copy() + sg_edges
        
        for node_id in range(len(planRoadmap)):
            if self.validEdge(planNodes[node_id], planNodes[-2]) and node_id != len(planRoadmap)-2:
                planRoadmap[node_id].append(len(planNodes)-2)
                planRoadmap[-2].append(node_id)
            if self.validEdge(planNodes[node_id], planNodes[-1]) and node_id != len(planRoadmap)-1:
                planRoadmap[node_id].append(len(planNodes)-1)
                planRoadmap[-1].append(node_id)

        #print(planNodes)
        #print(planRoadmap)
        #self.plot_road_map(planNodes, planRoadmap)
        #plt.pause(0.5)

        rx, ry = DijkstraSearch(False).search(
            start_x, start_y,
            goal_x, goal_y,
            [node.x for node in planNodes],
            [node.y for node in planNodes],
            planRoadmap
        )

        return rx, ry


    def calc_vertexes_in_configuration_space(self, x_list, y_list):
        x_list = x_list[0:-1]
        y_list = y_list[0:-1]
        cvx_list, cvy_list = [], []

        n_data = len(x_list)

        for index in range(n_data):
            offset_x, offset_y = self.calc_offset_xy(
                x_list[index - 1], y_list[index - 1],
                x_list[index], y_list[index],
                x_list[(index + 1) % n_data], y_list[(index + 1) % n_data],
            )
            cvx_list.append(offset_x)
            cvy_list.append(offset_y)

        return cvx_list, cvy_list



    @staticmethod
    def is_edge_valid(target_node, node, obstacle):


        p1 = Geometry.Point(target_node.x, target_node.y)
        p2 = Geometry.Point(node.x, node.y)

        for i in range(len(obstacle.x_list) - 1):
            
            q1 = Geometry.Point(obstacle.x_list[i], obstacle.y_list[i])
            q2 = Geometry.Point(obstacle.x_list[i + 1], obstacle.y_list[i + 1])

            if Geometry.is_seg_intersect(p1, p2, q1, q2):
                return False

        return True

    def calc_offset_xy(self, px, py, x, y, nx, ny):
        p_vec = math.atan2(y - py, x - px)
        n_vec = math.atan2(ny - y, nx - x)
        offset_vec = math.atan2(math.sin(p_vec) + math.sin(n_vec),
                                math.cos(p_vec) + math.cos(
                                    n_vec)) + math.pi / 2.0
        offset_x = x - (self.robot_radius*1.5) * math.cos(offset_vec)
        offset_y = y - (self.robot_radius*1.5) * math.sin(offset_vec)
        return offset_x, offset_y

    @staticmethod
    def plot_road_map(nodes, road_map_info_list):
        for i, node in enumerate(nodes):
            plt.plot(node.x, node.y, "+g")
            for index in road_map_info_list[i]:
                if index >= len(nodes)-2 or i >= len(nodes)-2:
                    plt.plot([node.x, nodes[index].x],
                             [node.y, nodes[index].y], "-r")
                else:
                    plt.plot([node.x, nodes[index].x],
                             [node.y, nodes[index].y], "-b")


class ObstaclePolygon(sp.Polygon):
    
    def plot(self, clr="grey"):
        patch1 = PolygonPatch(self, fc=clr, ec="black", alpha=0.2, zorder=1)
        plt.gca().add_patch(patch1)
        patch2 = PolygonPatch(self, fc=clr, ec="black", alpha=0.2, zorder=1)
        plt.gca().add_patch(patch2)
