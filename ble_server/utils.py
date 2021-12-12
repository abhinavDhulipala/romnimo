from dataclasses import dataclass
import networkx as nx
from typing import List
from config import Config, RoadTile, CarRequest

@dataclass
class Car:
    """
    @param: car_tile: either RoadTile.CAR1 or 2
    @param: current_rider: represents whether 
    @param: path : represents shortest path to next destination as a List[tuple]
    path[0] represents current position
    path[-1] represent destinaiton
    @param: graph -> nx.Graph: pointer to the parent graph from the calling window object

    assumptions:
        - on init, we are garunteed a rider.
    """
    def __init__(self, car_tile, path_tile, graph, path, rider=None) -> None:
        self.car_tile: RoadTile = car_tile
        self.path_tile: RoadTile = path_tile
        self.current_rider: Rider = rider
        self.graph: nx.Graph = graph
        self.path: List[tuple] = path
        self.graph.nodes[self.path[0]]['state'] = self.car_tile

    @property
    def path(self) -> List[tuple]:
        return self._path

    @path.setter
    def path(self, o :List[tuple]) -> None:
        self._path = o
        for p in self.filter_out_populated():
            tile = self.graph.nodes[p]['state']
            if RoadTile.is_path_tile(tile):
                self.graph.nodes[p]['state'] = RoadTile.PATH_COLLIDE
            else:
                self.graph.nodes[p]['state'] = self.path_tile          


    def has_arrived(self) -> bool:
        return len(self.path) == 1

    def current_position(self) -> tuple:
        return self.path[0]
    
    """
    @returns None if we require recalculation of path. 
    if we have reached our destination, then we require a new path
    TODO:  add support for collision detection. in the event that one car moves where another car just was
    TODO: add bluetooth emit from here
    """
    def move(self) -> CarRequest:
        if not self.current_rider:
            return CarRequest.RIDER
        if self.has_arrived():
            # rider has been picked up so this means we have dropped them off
            if self.current_rider.pick_up:
                self.current_rider = None
                return CarRequest.RIDER
            else:
                self.current_rider.pick_up = True
                self.path = nx.shortest_path(self.graph, self.path[0], self.current_rider.destination)
                return None
        
        prev = self.path.pop(0)
        if self.graph.nodes[prev]['state'] == self.car_tile:
            self.graph.nodes[prev]['state'] = RoadTile.EMPTY
        self.graph.nodes[self.path[0]]['state'] = self.car_tile

    def refresh_spt(self):
        # purge old path
        for p in self.filter_out_populated():
            tile = self.graph.nodes[p]['state']
            if tile == RoadTile.PATH_COLLIDE:
                self.graph.nodes[p]['state'] = RoadTile.PATH2 if self.path_tile == RoadTile.PATH1 else RoadTile.PATH1
            else:
                self.graph.nodes[p]['state'] = RoadTile.EMPTY
        self.path = nx.shortest_path(self.graph, self.path[0], self.path[-1], weight='weight')

    """
    @returns a filter of all tiles that should be adjusted. any tile with a car, destination, rider.
    In other words any "populated" tile
    """
    def filter_out_populated(self) -> filter:
        return filter(lambda p: not RoadTile.is_populated(self.graph.nodes[p]['state']), self._path)

@dataclass
class Rider:
    start: tuple
    destination: tuple

    def __init__(self, start, dest, graph) -> None:
        self.start = start
        self.graph = graph
        self.destination = dest
        self.graph.nodes[start]['state'] = RoadTile.RIDER
        self.pick_up = False


    def gen_top_2_corners(graph: nx.Graph):
        return [Rider((Config.COLUMN_COUNT - 1, Config.ROW_COUNT - 1), (0, 0), graph),
          Rider((Config.COLUMN_COUNT - 1, Config.ROW_COUNT - 2), (1, 0), graph)]



        
