import pygame as pg
import sys
from random import randint, choice
from time import sleep
import os

# --- Constants ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
GRID_SIZE = 100
HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5)*2  # For the head to be larger than the body
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCORE = 0

# How many screen frames it takes for the snake to move one square.
FRAMES_PER_MOVE = 25
# Colors
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
DARK_GREEN = (0, 100, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GRID_COLOR = (169, 217, 131)


def main():
    global SCORE

    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
    
    pg.init()


    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Snake Game")


    text_font = pg.font.Font(resource_path("graphs/snake_game_font.ttf"), 20)
    graphics = {
        "background": pg.transform.scale(pg.image.load(resource_path("graphs/background.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        "food_image": pg.transform.scale(pg.image.load(resource_path("graphs/food.png")).convert_alpha(), (GRID_SIZE , GRID_SIZE)),
        "snake_head": pg.transform.scale(pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha(), (HEAD_SIZE , HEAD_SIZE )),
        "under_head": pg.transform.scale(pg.image.load(resource_path("graphs/under_head.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE )),

        "snake_body": pg.transform.scale(pg.image.load(resource_path("graphs/snake_body.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_tl": pg.transform.scale(pg.image.load(resource_path("graphs/corner_tl.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_tr": pg.transform.scale(pg.image.load(resource_path("graphs/corner_tr.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_bl": pg.transform.scale(pg.image.load(resource_path("graphs/corner_bl.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "corner_br": pg.transform.scale(pg.image.load(resource_path("graphs/corner_br.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_tail": pg.transform.scale(pg.image.load(resource_path("graphs/snake_tail.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),

        "snake_blink": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_blink0.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_blink1.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        "finish"],

        "snake_see": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_see0.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_see1.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_see2.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE))],

        "snake_eat": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat0.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat1.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat2.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat3.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        "finish"],

        "snake_dead": [(pg.image.load(resource_path("graphs/snake_dead.png"))).convert_alpha(),
        (pg.image.load(resource_path("graphs/snake_dead0.png"))).convert_alpha()]
    }

    sfx = {
        "see": pg.mixer.Sound(resource_path("graphs/Erdem_GelLan.wav")),
        "start": pg.mixer.Sound(resource_path("graphs/Erdem_FightMe.wav")),
        "dead": pg.mixer.Sound(resource_path("graphs/Erdem_Dead.wav"))
    }

    pg.mixer.music.load(resource_path("graphs/snake_game_music.wav"))

    pg.mixer.music.play(loops=-1)


    clock = pg.time.Clock()
    game_over = False

    # Set the window icon using the original icon size (32x32 recommended)
    icon_surface = pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha()
    pg.display.set_icon(pg.transform.rotate(icon_surface, 180))  # Rotate the icon 180 degrees

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
            self.emotion = None  # Can be "blink", "see", "eat", or "dead"
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
                return pg.transform.rotate(name, 270)
            elif direction_vector == (-1, 0):
                return pg.transform.rotate(name, 90)
            elif direction_vector == (0, 1):
                return pg.transform.rotate(name, 180)
            elif direction_vector == (0, -1):
                return pg.transform.rotate(name, 0)
            return name

        def front_fonction(self):
            self.l_direction = self.direction[0]
            head_x, head_y = self.body_grid[0]
            dir_x, dir_y = self.direction[0]

            new_head = (head_x + dir_x, head_y + dir_y)
            # Losing conditions
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in self.body_grid:
                return False

            # Update all lists in sync, every time
            self.body_grid.insert(0, new_head)
            self.direction.insert(0, self.direction[0])
            self.body_pixels.insert(0, self.body_pixels[0].copy())

            if self.is_growing:
                self.emotion = "eat"
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

                
                # TAIL
                if i == len(self.body_pixels) - 1:
                    
                    rotated_image = self.rotate(graphics["snake_tail"], self.direction[i])
                    rect = rotated_image.get_rect(center=center_pos)
                    surface.blit(rotated_image, rect)

                # BODY (STRAIGHT OR CORNER)
                elif i != 0:
                    current_grid_pos = pg.Vector2(self.body_grid[i])
                    head_side_grid_pos = pg.Vector2(self.body_grid[i-1])
                    tail_side_grid_pos = pg.Vector2(self.body_grid[i+1])
                    
                    vec_from_head = head_side_grid_pos - current_grid_pos
                    vec_to_tail = tail_side_grid_pos - current_grid_pos

                    # IF STRAIGHT
                    if vec_from_head == vec_to_tail * -1:
                        rotated_image = self.rotate(graphics["snake_body"], self.direction[i])
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
            # HEAD
            head_pixel_pos = self.body_pixels[0]
            center_pos = (head_pixel_pos.x + GRID_SIZE / 2, head_pixel_pos.y + GRID_SIZE / 2)
            
            # Use self.direction[0] for the most up-to-date rotation          
            # Draw the layers for the head
            rotated_under_head_image = self.rotate(graphics["under_head"], self.l_direction)
            under_rect = rotated_under_head_image.get_rect(center=center_pos)
            surface.blit(rotated_under_head_image, under_rect)

            #print(self.emotion)
            if self.emotion:

                if self.emotion == "eat":
                    if not hasattr(self, 'event_start_time'):
                        self.event_start_time = pg.time.get_ticks()
                    eat_index = (pg.time.get_ticks() - self.event_start_time) // 200 % len(graphics["snake_eat"])
                    if eat_index != len(graphics["snake_eat"]) - 1:  # Avoid the last "finish" frame
                        rotated_head_image = self.rotate(graphics["snake_eat"][eat_index], self.l_direction)
                        surface.blit(rotated_head_image, rotated_head_image.get_rect(center=center_pos))
                    else:
                        self.emotion = None  # Reset emotion after eating animation
                        del self.event_start_time  # Remove the attribute to allow for future eating animations

                elif self.emotion == "see":
                    see_index = (pg.time.get_ticks() // 50) % len(graphics["snake_see"])
                    rotated_head_image = self.rotate(graphics["snake_see"][see_index], self.l_direction)
                    surface.blit(rotated_head_image, rotated_head_image.get_rect(center=center_pos))

                elif self.emotion == "blink":
                    if not hasattr(self, 'event_start_time'):
                        self.event_start_time = pg.time.get_ticks()
                    blink_index = (pg.time.get_ticks() - self.event_start_time) // 50 % len(graphics["snake_blink"])
                    if blink_index != len(graphics["snake_blink"]) - 1:  # Avoid the last "finish" frame
                        rotated_head_image = self.rotate(graphics["snake_blink"][blink_index], self.l_direction)
                        surface.blit(rotated_head_image, rotated_head_image.get_rect(center=center_pos))
                    else:
                        self.emotion = None  # Reset emotion after eating animation
                        del self.event_start_time  # Remove the attribute to allow for future eating animations

            else:
                rotated_head_image = self.rotate(graphics["snake_head"], self.l_direction)
                
                rect = rotated_head_image.get_rect(center=center_pos)
                
                surface.blit(rotated_head_image, rect)
    class Food:
        def __init__(self, snake_body):
            self.ramdomize_position(snake_body)
        def ramdomize_position(self, snake_body):
            
            while True:
                self.position = (randint(0, GRID_WIDTH - 1), 
                                 randint(0, GRID_HEIGHT - 1))
                if self.position not in snake_body:
                    break

        def draw(self, surface):
            surface.blit(graphics["food_image"], 
                         (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE))

    snake = Snake()
    food = Food(snake.body_grid)

    frame_count = 0

    BLINK_EVENT = pg.USEREVENT + 1
    GEL_LAN_EVENT = pg.USEREVENT + 2

    pg.time.set_timer(BLINK_EVENT, randint(1000, 2000))  # Set blink event every
    pg.time.set_timer(GEL_LAN_EVENT, randint(1000, 2000))  # Set Gel Lan event every 1-2 seconds
    sleep(0.5)

    sfx["start"].play()  # Play the start sound effect
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

            if event.type == BLINK_EVENT:
                if not snake.emotion:
                    snake.emotion = "blink"

            if event.type == GEL_LAN_EVENT and snake.emotion == "see":
                sfx["see"].play()  # Play the see sound effect

        frame_count += 1
        if frame_count >= FRAMES_PER_MOVE:
            frame_count = 0
            if not snake.front_fonction():
                game_over = True

        if snake.body_grid[0] == food.position:
            SCORE += 1
            snake.grow()
            food.ramdomize_position(snake.body_grid)

        else: # if not eated
            TRESHOLD = 3
            close_to_food = False
            for i in range(-1 * TRESHOLD, TRESHOLD + 1, 1):
                if food.position[0] + i == snake.body_grid[0][0]:
                    for j in range(-1 * TRESHOLD, TRESHOLD + 1, 1):
                        if food.position[1] + j == snake.body_grid[0][1]:
                            if snake.emotion != "eat": snake.emotion = "see"
                            close_to_food = True
                            break
            if not close_to_food and snake.emotion == "see": snake.emotion = None
        
        screen.fill(BLACK)

        screen.blit(graphics["background"], (0, 0))
        draw_grid(screen)

        snake.animate()
        snake.draw(screen)
        food.draw(screen)

        screen.blit(text_font.render(f"Score: {SCORE}", True, (149, 197, 111)), (10, 10))

        pg.display.flip()
        clock.tick(60)

    dead_start_time = pg.time.get_ticks()
    dead_screen = screen.copy()
    animate_speed = randint(400, 600)
    sfx["dead"].play()  # Play the dead sound effect
    while pg.time.get_ticks() - dead_start_time < 3000:
        
        dead_index = (pg.time.get_ticks() // animate_speed) % len(graphics["snake_dead"])

        screen.blit(dead_screen, (0, 0))
        screen.blit(pg.transform.scale(
            graphics["snake_dead"][dead_index], (SCREEN_WIDTH, SCREEN_HEIGHT))
            , graphics["snake_dead"][dead_index].get_rect(topleft=(0, 0)))

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()