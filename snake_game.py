import pygame as pg
import sys

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# How many screen frames it takes for the snake to move one square.
FRAMES_PER_MOVE = 5 

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DARK_GREEN = (0, 100, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

def main():
    pg.init()

    screen = pg.display.set_mode((640, 480))
    pg.display.set_caption("Snake Game")
    
    clock = pg.time.Clock()
    game_over = False

    class Snake:
        def __init__(self):

            self.body_grid = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
            self.direction = (1, 0)  # Initial direction is right

            start_pixel_pos = pg.Vector2(self.body_grid[0]) * GRID_SIZE
            self.body_pixels = [start_pixel_pos]

        def change_direction(self, new_direction):
            # Prevent the snake from reversing direction
            if(new_direction[0] * -1, new_direction[1] * -1) != self.direction:
                self.direction = new_direction


    
    while not game_over:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = True
        
        screen.fill((0, 0, 0))  # Clear the screen with black
        pg.display.flip()  # Update the display
        
        clock.tick(60)  # Limit to 60 frames per second
    
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()