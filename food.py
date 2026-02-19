import pygame as pg
import constants


class FOOD:
    # --Food Generation--
    def generate_food(self, body_grid):
        """Randomly places the food on the grid, avoiding the snake's body."""
        from random import randint

        GRID_COUNT = constants.SizeConstants.GRID_COUNT.value

        while True:
            self.position = (randint(0, GRID_COUNT - 1), randint(0, GRID_COUNT - 1))
            if self.position not in body_grid:
                break

    # --Collision Check--
    def _is_food_eaten(self, pos):
        """Checks if the given position (snake's head) matches the food's position."""
        return pos == self.position

    # --Drawing Method--
    def draw(self, screen, graphics, GRID_SIZE):
        """Draws the food item on the screen."""
        center_pos = pg.Vector2(self.position) * GRID_SIZE + pg.Vector2(
            GRID_SIZE // 2, GRID_SIZE // 2
        )
        screen.blit(graphics["food"], graphics["food"].get_rect(center=center_pos))
