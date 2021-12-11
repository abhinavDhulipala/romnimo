class Config:
    # Set how many rows and columns we will have
    ROW_COUNT = 6
    COLUMN_COUNT = 6

    # This sets the WIDTH and HEIGHT of each grid location
    WIDTH = 30
    HEIGHT = 30

    # This sets the margin between each cell
    # and on the edges of the screen.
    MARGIN = 5

    # Do the math to figure out our screen dimensions
    SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
    SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
    SCREEN_TITLE = "Road Projection"