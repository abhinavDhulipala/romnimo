from networkx.algorithms.centrality.current_flow_betweenness_subset import current_flow_betweenness_centrality_subset
from config import Config, RoadTile
import networkx as nx
import arcade
from collections import deque
from car import Car
from typing import List


class RoadEnvironment(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title, car1=(0, 0), car2=(1,0), 
        riders=[(Config.ROW_COUNT - 1, Config.COLUMN_COUNT - 1), (Config.ROW_COUNT - 1, Config.COLUMN_COUNT - 2)]):
        """
        Set up the application.
        """
        super().__init__(width, height, title)
        self.riders: List = riders

        # Create a 2 dimensional array. A two dimensional
        self.grid: nx.Graph = nx.grid_2d_graph(Config.ROW_COUNT, Config.COLUMN_COUNT)
        self.grid.edges(data=True)


        for val in self.grid.nodes.values():
            val['state'] = RoadTile.EMPTY

        for r in riders:
            self.grid.nodes[r]['state'] = RoadTile.RIDER

        # closest passenger for car1
        car1_closest_rider = min(self.riders, key=lambda r: nx.shortest_path_length(self.grid, car1, r))
        # closest passenger for car2
        car2_closest_rider = min(self.riders, key=lambda r: nx.shortest_path_length(self.grid, car2, r))
        self.car1, self.car2 = None, None
        if car1_closest_rider == car2_closest_rider:
            c1_length, c2_length = nx.shortest_path_length(self.grid, car1, car2_closest_rider), nx.shortest_path_length(self.grid, car2, car2_closest_rider)
            if c1_length < c2_length:
                self.car1 = Car(RoadTile.CAR1, RoadTile.PATH1, self.grid, nx.shortest_path(self.grid, car1, self.riders.remove(car1_closest_rider)[car1_closest_rider]))
                car2_closest_rider = min(self.riders, key=lambda r: nx.shortest_path_length(self.grid, car2, r))
                self.car2 = Car(RoadTile.CAR2, RoadTile.PATH2, self.grid, nx.shortest_path(self.grid, car2, self.riders.remove(car2_closest_rider))[car2_closest_rider])
            else:
                self.car2 = Car(RoadTile.CAR2, RoadTile.PATH2, self.grid, nx.shortest_path(self.grid, car2, self.riders.remove(car2_closest_rider))[car2_closest_rider])
                car1_closest_rider = min(self.riders, key=lambda r: nx.shortest_path_length(self.grid, car1, r))
                self.car1 = Car(RoadTile.CAR1, RoadTile.PATH1, self.grid, nx.shortest_path(self.grid, car1, self.riders.remove(car1_closest_rider))[car1_closest_rider])
        else:
            self.car1 = Car(RoadTile.CAR1, RoadTile.PATH1, self.grid, nx.shortest_path(self.grid, source=car1, target=self.riders.remove(car1_closest_rider))[car1_closest_rider])
            self.car2 = Car(RoadTile.CAR2, RoadTile.PATH2, self.grid, nx.shortest_path(self.grid, source=car2, target=self.riders.remove(car2_closest_rider))[car2_closest_rider])


        arcade.set_background_color(arcade.color.BLACK)

        self.grid_sprite_list = arcade.SpriteList()
        print(self.grid.edges.data)
        # Create a list of solid-color sprites to represent each grid location
        for row, column in self.grid.nodes:
            x = column * (Config.WIDTH + Config.MARGIN) + (Config.WIDTH / 2 + Config.MARGIN)
            y = row * (Config.HEIGHT + Config.MARGIN) + (Config.HEIGHT / 2 + Config.MARGIN)
            sprite = arcade.SpriteSolidColor(Config.WIDTH, Config.HEIGHT, RoadTile.EMPTY.value)
            sprite.set_position(x, y)
            self.grid_sprite_list.append(sprite)
        self.resync_grid_with_sprites()

    def resync_grid_with_sprites(self):

        for (i, j), state in self.grid.nodes.data('state'):
            # We need to convert our two dimensional grid to our
            # one-dimensional sprite list. For example a 10x10 grid might have
            # row 2, column 8 mapped to location 28. (Zero-basing throws things
            # off, but you get the idea.)
            # ALTERNATIVELY you could set self.grid_sprite_list[pos].texture
            # to different textures to change the image instead of the color.
            pos = i * Config.COLUMN_COUNT + j
            self.grid_sprite_list[pos].color = state.value

    def on_draw(self):
        # This command has to happen before we start drawing
        arcade.start_render()

        self.grid_sprite_list.draw()

    def on_mouse_press(self, x, y, button, modifiers):

        # Change the x/y screen coordinates to grid coordinates
        column = x // (Config.WIDTH + Config.MARGIN)
        row = y // (Config.HEIGHT + Config.MARGIN)

        print(f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column})")

        # Make sure we are on-grid. It is possible to click in the upper right
        # corner in the margin and go to a grid location that doesn't exist
        node = (row, column)

        if row < Config.ROW_COUNT and column < Config.COLUMN_COUNT and self.grid.nodes[node]['state'] not in {RoadTile.CAR1, RoadTile.CAR2}:
            cur_state = self.grid.nodes[node]['state']
            if button == arcade.MOUSE_BUTTON_LEFT:
                if cur_state != RoadTile.CRASH:
                    self._adj_tile_edges(node, RoadTile.CRASH, float('inf'))
                else:
                    self._adj_tile_edges(node, RoadTile.EMPTY, 1)
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                if cur_state != RoadTile.RIDER:
                    self._adj_tile_edges(node, RoadTile.RIDER, float('inf'))
                else:
                    self._adj_tile_edges(node, RoadTile.EMPTY, 1)
            print(f"Tile: {self.grid.nodes[node]['state']}")

        self.car1.refresh_spt()
        self.car2.refresh_spt()
        self.resync_grid_with_sprites()

    def debug_graph(self):
        A = nx.nx_agraph.to_agraph(self.grid)
        A.draw('debug.png', prog='neato')

    def _adj_tile_edges(self, node, new_tile, weight):
        self.grid.nodes[node]['state'] = new_tile
        for e1, e2 in self.grid.edges(node):
            self.grid[e1][e2]['weight'] = weight


def main():
    RoadEnvironment(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT, Config.SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()