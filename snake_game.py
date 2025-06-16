import pygame as pg
import sys
import random

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# How many screen frames it takes for the snake to move one square.
FRAMES_PER_MOVE = 6

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DARK_GREEN = (0, 100, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GRID_COLOR = (40, 40, 40)


def main():
    pg.init()

    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Snake Game")

    clock = pg.time.Clock()
    game_over = False

    def draw_grid(surface):
        # vertical lines
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pg.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        # horizontal lines
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pg.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
    class Snake:
        def __init__(self):
            self.body_grid = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
            self.direction = (1, 0)
            self.l_direction = (1, 0)  # last direction
            self.is_growing = False

            start_pixel_pos = pg.Vector2(self.body_grid[0]) * GRID_SIZE
            self.body_pixels = [start_pixel_pos]

        def change_direction(self, new_direction):
            if (new_direction[0] * -1, new_direction[1] * -1) != self.l_direction:
                self.direction = new_direction

        def front_fonction(self):
            self.l_direction = self.direction

            head_x, head_y = self.body_grid[0]
            dir_x, dir_y = self.direction

            new_head = ((head_x + dir_x) % GRID_WIDTH, (head_y + dir_y) % GRID_HEIGHT)

            if new_head in self.body_grid[1:]:
                return False

            self.body_grid.insert(0, new_head)

            if self.is_growing:
                self.is_growing = False
                self.body_pixels.append(self.body_pixels[-1].copy())
            else:
                self.body_grid.pop()

            return True
        
        def grow(self):
            self.is_growing = True

        def animate(self):
            for i in range(len(self.body_pixels)):
                target_grid_pos = self.body_grid[i]
                target_pixel_pos = pg.Vector2(target_grid_pos) * GRID_SIZE

                current_pixel_pos = self.body_pixels[i]
                self.body_pixels[i] = current_pixel_pos.lerp(target_pixel_pos, 1.0 / FRAMES_PER_MOVE)

        def draw(self, surface):
            head_rect = pg.Rect(self.body_pixels[0], (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(surface, GREEN, head_rect)

            for segment_pos in self.body_pixels[1:]:
                segment_rect = pg.Rect(segment_pos, (GRID_SIZE, GRID_SIZE))
                pg.draw.rect(surface, DARK_GREEN, segment_rect)

    class Food:
        def __init__(self, snake_body):
            self.ramdomize_position(snake_body)
        def ramdomize_position(self, snake_body):
            while True:
                self.position = (random.randint(0, GRID_WIDTH - 1), 
                                 random.randint(0, GRID_HEIGHT - 1))
                if self.position not in snake_body:
                    break

        def draw(self, surface):
            rect = pg.Rect(self.position[0] * GRID_SIZE,
                           self.position[1] * GRID_SIZE,
                           GRID_SIZE, GRID_SIZE)
            pg.draw.rect(surface, RED, rect)

    snake = Snake()
    food = Food(snake.body_grid)

    frame_count = 0

    while not game_over:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pg.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pg.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pg.K_RIGHT:
                    snake.change_direction((1, 0))

        frame_count += 1
        if frame_count >= FRAMES_PER_MOVE:
            frame_count = 0
            if not snake.front_fonction():
                game_over = True

        if snake.body_grid[0] == food.position:
            snake.grow()
            food.ramdomize_position(snake.body_grid)
        
        screen.fill(BLACK)

        draw_grid(screen)

        snake.animate()
        snake.draw(screen)
        food.draw(screen)

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()