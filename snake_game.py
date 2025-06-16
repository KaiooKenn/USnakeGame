import pygame as pg
import sys

def main():
    pg.init()
    screen = pg.display.set_mode((640, 480))
    pg.display.set_caption("Snake Game")
    
    clock = pg.time.Clock()
    running = True
    
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        screen.fill((0, 0, 0))  # Clear the screen with black
        pg.display.flip()  # Update the display
        
        clock.tick(60)  # Limit to 60 frames per second
    
    pg.quit()
    sys.exit()