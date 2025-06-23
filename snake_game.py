import pygame as pg
import sys
import random

# --- Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
GRID_SIZE = 50
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# How many screen frames it takes for the snake to move one square.
FRAMES_PER_MOVE = 10

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DARK_GREEN = (0, 100, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GRID_COLOR = (169, 217, 131)


def main():
    pg.init()


    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Snake Game")

    graphics = {
        "background": pg.transform.scale(pg.image.load("graphs/background.png").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        "food_image": pg.transform.scale(pg.image.load("graphs/food.png").convert_alpha(), (GRID_SIZE , GRID_SIZE)),
        "snake_head": pg.transform.scale(pg.image.load("graphs/snake_head.png").convert_alpha(), (GRID_SIZE, GRID_SIZE )),
        "snake_body": pg.transform.scale(pg.image.load("graphs/snake_body.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_tl": pg.transform.scale(pg.image.load("graphs/corner_tl.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_tr": pg.transform.scale(pg.image.load("graphs/corner_tr.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_bl": pg.transform.scale(pg.image.load("graphs/corner_bl.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_br": pg.transform.scale(pg.image.load("graphs/corner_br.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_tail": pg.transform.scale(pg.image.load("graphs/snake_tail.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_blink0": pg.transform.scale(pg.image.load("graphs/snake_blink0.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_blink1": pg.transform.scale(pg.image.load("graphs/snake_blink1.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_see0": pg.transform.scale(pg.image.load("graphs/snake_see0.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_see1": pg.transform.scale(pg.image.load("graphs/snake_see1.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_see2": pg.transform.scale(pg.image.load("graphs/snake_see2.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_eat0": pg.transform.scale(pg.image.load("graphs/snake_eat0.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_eat1": pg.transform.scale(pg.image.load("graphs/snake_eat1.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_eat2": pg.transform.scale(pg.image.load("graphs/snake_eat2.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_eat3": pg.transform.scale(pg.image.load("graphs/snake_eat3.png").convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_dead": pg.transform.scale(pg.image.load("graphs/snake_dead.png").convert_alpha(), (GRID_SIZE, GRID_SIZE))
    }

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
            # MUST start with at least 2 segments for the draw logic to work
            self.body_grid = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2)]
            self.direction = [(1, 0), (1, 0)]
            self.l_direction = (1, 0)
            self.is_growing = False
            # Sync all lists at the start
            self.body_pixels = [pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid]

        def change_direction(self, new_direction):
            if (new_direction[0] * -1, new_direction[1] * -1) != self.l_direction:
                self.direction[0] = new_direction

        def rotate(self, name, direction_vector):
            # UP (0, -1) -> 0 degrees
            # RIGHT (1, 0) -> 270 degrees
            # DOWN (0, 1) -> 180 degrees
            # LEFT (-1, 0) -> 90 degrees
            if direction_vector == (1, 0):
                return pg.transform.rotate(graphics[name], 270)
            elif direction_vector == (-1, 0):
                return pg.transform.rotate(graphics[name], 90)
            elif direction_vector == (0, 1):
                return pg.transform.rotate(graphics[name], 180)
            elif direction_vector == (0, -1):
                return pg.transform.rotate(graphics[name], 0)
            return graphics[name]

        def front_fonction(self):
            self.l_direction = self.direction[0]
            head_x, head_y = self.body_grid[0]
            dir_x, dir_y = self.direction[0]

            new_head = (head_x + dir_x, head_y + dir_y)
            # Use proper boundary checks instead of wrapping with %
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in self.body_grid:
                return False

            # Update all lists in sync, every time
            self.body_grid.insert(0, new_head)
            self.direction.insert(0, self.direction[0])
            self.body_pixels.insert(0, self.body_pixels[0].copy())

            if self.is_growing:
                self.is_growing = False
            else:
                self.body_grid.pop()
                self.direction.pop()
                self.body_pixels.pop() # Now this is safe to do

            return True
        
        def grow(self):
            self.is_growing = True

        def animate(self):
            for i in range(len(self.body_pixels)):
                target_pixel_pos = pg.Vector2(self.body_grid[i]) * GRID_SIZE
                self.body_pixels[i] = self.body_pixels[i].lerp(target_pixel_pos, 0.25)

        def draw(self, surface):
            for i, pixel_pos in enumerate(self.body_pixels):
                center_pos = (pixel_pos.x + GRID_SIZE / 2, pixel_pos.y + GRID_SIZE / 2)

                # HEAD
                if i == 0:
                    rotated_image = self.rotate("snake_head", self.direction[i])
                    rect = rotated_image.get_rect(center=center_pos)
                    surface.blit(rotated_image, rect)
                
                # TAIL
                elif i == len(self.body_pixels) - 1:
                    # NEW LOGIC: The tail now uses its own direction from the list, like other parts.
                    tail_direction = self.direction[i]
                    
                    rotated_image = self.rotate("snake_tail", tail_direction)
                    rect = rotated_image.get_rect(center=center_pos)
                    surface.blit(rotated_image, rect)

                # BODY (STRAIGHT OR CORNER)
                else:
                    current_grid_pos = pg.Vector2(self.body_grid[i])
                    head_side_grid_pos = pg.Vector2(self.body_grid[i-1])
                    tail_side_grid_pos = pg.Vector2(self.body_grid[i+1])
                    
                    vec_from_head = head_side_grid_pos - current_grid_pos
                    vec_to_tail = tail_side_grid_pos - current_grid_pos

                    # IF STRAIGHT
                    if vec_from_head == vec_to_tail * -1:
                        rotated_image = self.rotate("snake_body", self.direction[i])
                        rect = rotated_image.get_rect(center=center_pos)
                        surface.blit(rotated_image, rect)
                    
                    # IF CORNER - Select the correct image
                    else:
                        vec_from_head_tuple = (int(vec_from_head.x), int(vec_from_head.y))
                        vec_to_tail_tuple = (int(vec_to_tail.x), int(vec_to_tail.y))
                        turn_vectors = {vec_from_head_tuple, vec_to_tail_tuple}
                        
                        image_to_draw = None
                        
                        if turn_vectors == {(0, -1), (-1, 0)}: # Top-Left
                           image_to_draw = graphics["corner_tl"]
                        elif turn_vectors == {(0, -1), (1, 0)}: # Top-Right
                           image_to_draw = graphics["corner_tr"]
                        elif turn_vectors == {(0, 1), (-1, 0)}: # Bottom-Left
                           image_to_draw = graphics["corner_bl"]
                        elif turn_vectors == {(0, 1), (1, 0)}: # Bottom-Right
                           image_to_draw = graphics["corner_br"]

                        if image_to_draw:
                            rect = image_to_draw.get_rect(center=center_pos)
                            surface.blit(image_to_draw, rect)
 
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
            surface.blit(graphics["food_image"], 
                         (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE))

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

        screen.blit(graphics["background"], (0, 0))
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