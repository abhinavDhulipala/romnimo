from config import CarRequest, Config, RoadTile
import networkx as nx
import arcade
from utils import Car, Rider
from typing import List
from time import sleep


class RoadEnvironment(arcade.Window):
    """
    Main application class
    """

    def __init__(self, width, height, title, car1=(5, 5), car2=(4, 5),
                 riders=None,
                 shared_robot_states=None,
                 shared_robot_commands=None):
        """
        Set up the application.
        """
        super().__init__(width, height, title)

        self.car_states = shared_robot_states or [0, 0]
        self.robot_commands = shared_robot_commands or ([''] * 2)
        # Create a 2 dimensional array. A two dimensional
        self.grid: nx.Graph = nx.grid_2d_graph(Config.ROW_COUNT, Config.COLUMN_COUNT)
        self.grid.edges(data=True)

        for val in self.grid.nodes.values():
            val['state'] = RoadTile.EMPTY

        self.riders: List = riders or Rider.gen_top_2_corners(self.grid)

        self.car1 = Car(RoadTile.CAR1, self.grid, [car1])
        self.car2 = Car(RoadTile.CAR2, self.grid, [car2])

        self._handle_car_conflict()

        arcade.set_background_color(arcade.color.BLACK)

        self.grid_sprite_list = arcade.SpriteList()
        # Create a list of solid-color sprites to represent each grid location
        for row, column in self.grid.nodes:
            x = column * (Config.WIDTH + Config.MARGIN) + (Config.WIDTH / 2 + Config.MARGIN)
            y = row * (Config.HEIGHT + Config.MARGIN) + (Config.HEIGHT / 2 + Config.MARGIN)
            sprite = arcade.SpriteSolidColor(Config.WIDTH, Config.HEIGHT, RoadTile.EMPTY.value)
            sprite.set_position(x, y)
            self.grid_sprite_list.append(sprite)
        self.resync_grid_with_sprites()

        # schedule listening to the cars bluetooth
        arcade.schedule(self.ble_listen, Config.BLE_REFRESH_RATE)

        sleep(.05)

    """
    listener for inputs from robots
    """

    def ble_listen(self, delta_time: float):

        # if all cars have come to a stop
        # set them to start again and emit a start signal 
        # update them on the gui
        # todo: remove test var
        if all(self.car_states):
            # in memory fill
            for i, _ in enumerate(self.car_states):
                self.car_states[i] = 0
            car1_request = self.car1.move()
            car2_request = self.car2.move()
            # if both cars request a rider at the same time then we must handle the case that they are eqiudistant
            if self.riders:
                if car1_request == car2_request == CarRequest.RIDER:
                    self._handle_car_conflict()
                elif car2_request == CarRequest.RIDER:
                    rider = self.closest_rider(self.car2)
                    self.car2.path = \
                    nx.shortest_path(self.grid, self.car2.current_position(), self.riders.remove(rider))[rider.start]
                elif car1_request == CarRequest.RIDER:
                    rider = self.closest_rider(self.car1)
                    self.car2.path = \
                    nx.shortest_path(self.grid, self.car1.current_position(), self.riders.remove(rider))[rider.start]
            self.robot_commands[0] = self.car1.command()
            self.robot_commands[1] = self.car2.command()

        self.resync_grid_with_sprites()

    def ac_sleep(self):
        sleep()

    def closest_rider(self, car):
        if self.riders:
            return min(self.riders, key=lambda r: nx.shortest_path_length(self.grid, car, r.start))

    def pop_rider_spawn_car(self, car, rider, car_num):
        if not rider:
            return None
        if car_num == 1:
            self.car1.path = nx.shortest_path(self.grid, car, self.riders.remove(rider))[rider.start]
            self.car1.current_rider = rider
        elif car_num == 2:
            self.car2.path = nx.shortest_path(self.grid, car, self.riders.remove(rider))[rider.start]
            self.car2.current_rider = rider

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

        # Make sure we are on-grid. It is possible to click in the upper right
        # corner in the margin and go to a grid location that doesn't exist
        node = (row, column)

        if row < Config.ROW_COUNT and column < Config.COLUMN_COUNT and self.grid.nodes[node]['state'] not in {
            RoadTile.CAR1, RoadTile.CAR2}:
            cur_state = self.grid.nodes[node]['state']
            if button == arcade.MOUSE_BUTTON_LEFT:
                if cur_state != RoadTile.CRASH:
                    self._adj_tile_edges(node, RoadTile.CRASH, float('inf'))
                else:
                    self._adj_tile_edges(node, RoadTile.EMPTY, 1)
            print(
                f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column}). Tile: {self.grid.nodes[node]['state']}")

        self.car1.refresh_spt()
        self.car2.refresh_spt()
        self.resync_grid_with_sprites()

    def _handle_car_conflict(self):
        car1, car2 = self.car1.current_position(), self.car2.current_position()
        # closest passenger for car1
        car1_closest_rider = self.closest_rider(car1)
        # closest passenger for car2
        car2_closest_rider = self.closest_rider(car2)
        if car1_closest_rider == car2_closest_rider:
            c1_length, c2_length = nx.shortest_path_length(self.grid, car1,
                                                           car2_closest_rider.start), nx.shortest_path_length(self.grid,
                                                                                                              car2,
                                                                                                              car2_closest_rider.start)
            if c1_length < c2_length:
                self.pop_rider_spawn_car(car1, car1_closest_rider, 1)
                car2_closest_rider = self.closest_rider(car2)
                self.pop_rider_spawn_car(car2, car2_closest_rider, 2)
            else:
                self.pop_rider_spawn_car(car2, car2_closest_rider, 2)
                car1_closest_rider = self.closest_rider(car1)
                self.pop_rider_spawn_car(car1, car1_closest_rider, 1)
        else:
            self.pop_rider_spawn_car(car2, car2_closest_rider, 2)
            self.pop_rider_spawn_car(car1, car1_closest_rider, 1)

    def debug_graph(self):
        A = nx.nx_agraph.to_agraph(self.grid)
        A.draw('debug.png', prog='neato')

    def _adj_tile_edges(self, node, new_tile, weight):
        self.grid.nodes[node]['state'] = new_tile
        for e1, e2 in self.grid.edges(node):
            self.grid[e1][e2]['weight'] = weight


def run_gui(**kwargs):
    RoadEnvironment(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT, Config.SCREEN_TITLE, **kwargs)
    arcade.run()


def main():
    RoadEnvironment(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT, Config.SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
