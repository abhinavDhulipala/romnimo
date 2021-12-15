from enum import Enum, auto
import arcade
import os

class Config:
    # Set how many rows and columns we will have
    ROW_COUNT = 4
    COLUMN_COUNT = 4

    # This sets the WIDTH and HEIGHT of each grid location
    WIDTH = 60
    HEIGHT = 60

    # This sets the margin between each cell
    # and on the edges of the screen.
    MARGIN = 5

    # Do the math to figure out our screen dimensions
    SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
    SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
    SCREEN_TITLE = "Road Projection"
    # interval of refresh rate in seconds
    BLE_REFRESH_RATE = os.getenv('BLE_REFRESH_RATE') or 1.5
    # ble buffer size
    BUFF_SIZE = 1024

class RoadTile(Enum):
    CRASH = arcade.color.CRIMSON_GLORY
    EMPTY = arcade.color.CHAMPAGNE
    CAR1 = arcade.color.UNIVERSITY_OF_CALIFORNIA_GOLD
    PATH1 = arcade.color.JADE
    DEST1 = arcade.color.BITTER_LIME
    CAR2 = arcade.color.CATALINA_BLUE
    PATH2 = arcade.color.KHAKI
    DEST2 = arcade.color.BLAST_OFF_BRONZE
    RIDER = arcade.color.BATTLESHIP_GREY
    # tile used if a path is being used by both path1 and path2
    PATH_COLLIDE = arcade.color.BLUE_GREEN

    def is_path_tile(tile) -> bool:
        return isinstance(tile, RoadTile) and tile in {RoadTile.PATH1, RoadTile.PATH2}
    
    """
    @returns any tile that shouldn't be drowned by a path tile. Any tile with a rider, car, or destination
    In other words any "populated" tile
    """
    def is_populated(tile) -> bool:
        return isinstance(tile, RoadTile) and tile in {RoadTile.CAR1,
          RoadTile.DEST1,
          RoadTile.RIDER,
          RoadTile.DEST2,
          RoadTile.CAR2,
          RoadTile.CRASH
        }

class CarRequest(Enum):
    RIDER = auto()
    DESITNATION = auto()