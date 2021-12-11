from enum import Enum
from config import Config
import arcade


class RoadTiles(Enum):
    CRASH = arcade.color.CRIMSON_GLORY
    EMPTY = arcade.color.CHAMPAGNE
    CAR1 = arcade.color.UNIVERSITY_OF_CALIFORNIA_GOLD
    PATH1 = arcade.color.JADE
    CAR2 = arcade.color.CATALINA_BLUE
    PATH2 = arcade.color.KHAKI
    RIDER = arcade.color.BATTLESHIP_GREY


class RoadEnvironment(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)

        # Create a 2 dimensional array. A two dimensional
        self.grid: RoadTiles = [[RoadTiles.EMPTY] * Config.COLUMN_COUNT for _ in range(Config.ROW_COUNT)]

        arcade.set_background_color(arcade.color.BLACK)

        self.grid_sprite_list = arcade.SpriteList()

        # Create a list of solid-color sprites to represent each grid location
        for row in range(Config.ROW_COUNT):
            for column in range(Config.COLUMN_COUNT):
                x = column * (Config.WIDTH + Config.MARGIN) + (Config.WIDTH / 2 + Config.MARGIN)
                y = row * (Config.HEIGHT + Config.MARGIN) + (Config.HEIGHT / 2 + Config.MARGIN)
                sprite = arcade.SpriteSolidColor(Config.WIDTH, Config.HEIGHT, RoadTiles.EMPTY.value)
                sprite.set_position(x, y)
                self.grid_sprite_list.append(sprite)
        self.resync_grid_with_sprites()

    def resync_grid_with_sprites(self):

        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                # We need to convert our two dimensional grid to our
                # one-dimensional sprite list. For example a 10x10 grid might have
                # row 2, column 8 mapped to location 28. (Zero-basing throws things
                # off, but you get the idea.)
                # ALTERNATIVELY you could set self.grid_sprite_list[pos].texture
                # to different textures to change the image instead of the color.
                pos = i * Config.COLUMN_COUNT + j
                self.grid_sprite_list[pos].color = cell.value

    def on_draw(self):
        # This command has to happen before we start drawing
        arcade.start_render()

        self.grid_sprite_list.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """

        # Change the x/y screen coordinates to grid coordinates
        column = x // (Config.WIDTH + Config.MARGIN)
        row = y // (Config.HEIGHT + Config.MARGIN)

        print(f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column})")

        # Make sure we are on-grid. It is possible to click in the upper right
        # corner in the margin and go to a grid location that doesn't exist
        if row < Config.ROW_COUNT and column < Config.COLUMN_COUNT:
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.grid[row][column] = RoadTiles.CRASH if self.grid[row][column] == RoadTiles.EMPTY else RoadTiles.EMPTY
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                self.grid[row][column] = RoadTiles.RIDER if self.grid[row][column] == RoadTiles.EMPTY else RoadTiles.EMPTY
            print(f'Tile: {self.grid[row][column]}')

        print(f"Click coordinates: ({x}, {y}). Grid coordinates: ({row}, {column})")

        self.resync_grid_with_sprites()


def main():
    RoadEnvironment(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT, Config.SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()