# --Required Libraries--
import pygame as pg

pg.init()
pg.mixer.init()

from game import Game

# --Entry Point of the Program--
if __name__ == "__main__":
    # Create a Game instance and run it.
    game = Game()
    game.run()
