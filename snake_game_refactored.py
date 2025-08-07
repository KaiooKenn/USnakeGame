# --Gerekli Kütüphaneler--
import pygame as pg
import os
import sys
pg.init()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --SNAKE Class--
class SNAKE:
    
    def __init__(self):
        super().__init__()
        # Positions and direction attributes
        self.direction = [(1, 0), (1, 0)]
        self.move_queue = []
        self.body_grid = [((GRID_COUNT) // 2 - 1, (GRID_COUNT) // 2), ((GRID_COUNT) // 2 - 2, (GRID_COUNT) // 2)]
        self.body_pixels = [pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid]
        
        # Case attributes
        self._is_growing = False
        self.wanted_animations = []
        
    @staticmethod    
    def rotate(image, direction):
        if direction == (1, 0):  return pg.transform.rotate(image, 270) # Right
        if direction == (-1, 0): return pg.transform.rotate(image, 90) # Left
        if direction == (0, 1):  return pg.transform.rotate(image, 180) # Down
        if direction == (0, -1): return image  # Up (no rotation)
        
    def front_func(self):
        # Must variables to determine next position of the snake
        if self.move_queue:
            self.direction[0] = self.move_queue.pop(0)
        self.l_direction = self.direction[0]
        head_x, head_y = self.body_grid[0]
        dir_x, dir_y = self.direction[0]
        
        new_head = (head_x + dir_x, head_y + dir_y) # New head position out of grids
        
        # Game over conditions
        if (not (0 <= new_head[0] < GRID_COUNT and
                0 <= new_head[1] < GRID_COUNT) or
                (new_head in self.body_grid)):
            return False
        
        # Adding new head to the body
        self.body_grid.insert(0, new_head)
        self.direction.insert(0, self.direction[0])  # Copy the current direction to the new head
        self.body_pixels.insert(0, self.body_pixels[0].copy()) # Copy the pixel position of the head
        
        #if snake eats food
        if self._is_growing:
            self.wanted_animations.append("snake_eat")  # Add the eat animation
            self._is_growing = False
        else:
            self.body_grid.pop()  # Remove the tail if not growing
            self.direction.pop()  # Remove the tail direction
            self.body_pixels.pop() # Remove the tail pixel position
        return True # if not game over
    
        
    
    # Animation for the snake
    def animate(self):
        for i in range(len(self.body_pixels)):
            target_pixel_pos = pg.Vector2(self.body_grid[i]) * GRID_SIZE
            self.body_pixels[i] = self.body_pixels[i].lerp(target_pixel_pos, 0.25)      
        
    def draw(self, screen, graphics):
        # -- Draw SNAKE -- !!! Head must be drawn last !!!
        center_pos = self.body_pixels[-1] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
        # Draw tail
        screen.blit(self.rotate(graphics["snake_tail"], self.direction[-1]), graphics["snake_tail"].get_rect(center=center_pos))
        
        # Draw body     
        self.draw_body(screen, graphics) # Draw body except head

        # Draw head
        center_pos = self.body_pixels[0] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)           
        screen.blit(self.rotate(graphics["under_head"], self.l_direction), graphics["under_head"].get_rect(center=center_pos)) # Draw under head
        screen.blit(self.rotate(graphics["snake_head"], self.l_direction), graphics["snake_head"].get_rect(center=center_pos)) # Draw head head
        
    def draw_body(self, screen, graphics):
        # Draw body segments except head and tail
        for i in range(1, len(self.body_pixels) - 1):
            pixel_pos = self.body_pixels[i]
            center_pos = pixel_pos + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)

            current_grid_pos = pg.Vector2(self.body_grid[i])
            head_side_grid_pos = pg.Vector2(self.body_grid[i-1])
            tail_side_grid_pos = pg.Vector2(self.body_grid[i+1])

            vec_from_head = head_side_grid_pos - current_grid_pos
            vec_from_tail = tail_side_grid_pos - current_grid_pos

            if vec_from_head == vec_from_tail * -1:
                screen.blit(self.rotate(graphics["snake_body"], self.direction[i]), graphics["snake_body"].get_rect(center=center_pos))
            else:
                turn_vectors = {(int(vec_from_head.x), int(vec_from_head.y)), 
                                (int(vec_from_tail.x), int(vec_from_tail.y))}
                image_to_draw = None
                if turn_vectors == {(0, -1), (-1, 0)}: image_to_draw = graphics["body_corner"][0]  # Top Left
                elif turn_vectors == {(0, -1), (1, 0)}: image_to_draw = graphics["body_corner"][1]  # Top Right
                elif turn_vectors == {(0, 1), (-1, 0)}: image_to_draw = graphics["body_corner"][2]  # Bottom Left
                elif turn_vectors == {(0, 1), (1, 0)}: image_to_draw = graphics["body_corner"][3]  # Bottom Right

                if image_to_draw:
                    rect = image_to_draw.get_rect(center=center_pos)
                    screen.blit(image_to_draw, rect)
                    
    def make_animation(self, active_animation):
        if not self.wanted_animations:
            return
        print(f"Current wanted animations: {self.wanted_animations} and active animation: {active_animation}")
        animation_tiers = ["snake_dead", "snake_eat", "snake_see", "snake_blink"]
        loop_animations = ["snake_see"]
        
        if not active_animation in animation_tiers and active_animation:
            return
        if not active_animation:
            active_animation = self.wanted_animations[0]
            self.animation = active_animation
        for animation_name in self.wanted_animations:
            if animation_name not in animation_tiers:
                continue
            if not animation_name in loop_animations:
                if animation_tiers.index(active_animation) <= animation_tiers.index(animation_name):
                    applyable = True
            else:
                if animation_tiers.index(active_animation) < animation_tiers.index(animation_name):
                    applyable = True
            if applyable:
                active_animation = self.animation = animation_name
                
        self.wanted_animations = []  # Clear the wanted animations after processing
            
    def change_direction(self, new_direction):
        if self.move_queue:
            last_direction = self.move_queue[-1]
        else:
            last_direction = self.l_direction
        
        # Prevent the snake from going in the opposite direction
        if (new_direction[0] * -1, new_direction[1] * -1) == last_direction or new_direction == last_direction:
            return
        
        if len(self.move_queue) < 2:
            self.move_queue.append(new_direction)
            
class HEAD_ANIMATION_HANDLER:
    def __init__(self):
        self.animation_frames = []
        self.current_frame = 0
        self.frame_counter = 0
        self.animation_speed = 10 # Speed of the animation, can be adjusted
        self.active_animation = None
    
    def add_animation(self, frames, name):
        self.animation_frames = frames 
        self.active_animation = name
        self.current_frame = 0
        self.frame_counter = 0
        print(f"Animation added: {self.active_animation}")

        
    def update(self):
        #print(f"Updating animation: {self.get_active_animation()}")
        if not self.animation_frames:
            return
        
        # Update the frame counter
        self.frame_counter += 1
        
        # Change frame based on the frame counter
        if self.frame_counter >= self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            if self.animation_frames[self.current_frame] == "finish":
                self.animation_frames = []
                self.active_animation = None
            self.frame_counter = 0
        
    def get_image(self):
        if self.animation_frames:
            image = self.animation_frames[self.current_frame]
            if isinstance(image, pg.Surface):
                return image
        return None
class FOOD:    
    def generate_food(self, body_grid):
        # Generate a random position for the food
        from random import randint
        while True:
            # Generate a random position within the grid
            self.position = (randint(0, GRID_COUNT - 1), randint(0, GRID_COUNT - 1))
            # Ensure the food does not spawn on the snake's body
            if self.position not in body_grid:
                break
        
    def _is_food_eaten(self, pos):
        # Check if the snake's head position matches the food position
        return pos == self.position
        
    def draw(self, screen, graphics):
        center_pos = pg.Vector2(self.position) * GRID_SIZE + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
        screen.blit(graphics["food"], graphics["food"].get_rect(center=center_pos))
            
# --Game Class--
class Game:
    
    def start(self):
        print("Game is starting...")
        
        Info_Object = pg.display.Info()
        
        # In Game Constants
        global SCREEN_SIZE, GRID_COUNT, GRID_SIZE, HEAD_SIZE
        SCREEN_SIZE = (Info_Object.current_h)*4//5 if Info_Object.current_h < Info_Object.current_w else (Info_Object.current_h)*4//5
        GRID_COUNT = 12
        GRID_SIZE = SCREEN_SIZE // GRID_COUNT
        HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2
        
        # In Game Dependencies
        global SCREEN, CLOCK, FPS, FRAMES_PER_MOVE, SCORE
        SCREEN = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        CLOCK = pg.time.Clock()
        FPS = 60
        FRAMES_PER_MOVE = 7
        SCORE = 0
        
        self.running = True
        self.game_over = False
        
        self.graphics = self.load_images()
        
        self.manipulated_images = {
            "snake_head": self.graphics["snake_head"],
            "snake_tail": self.graphics["snake_tail"],
            "snake_body": self.graphics["snake_body"],
            "under_head": self.graphics["under_head"],
            "body_corner": self.graphics["body_corner"],
            "food": self.graphics["food"]
        }
        
        print("Game has started!")
        
    @staticmethod    
    def load_images():
        print("Loading images...")
        # Loading assests like images, sounds, etc.
        try:
            return {
                "background": pg.transform.scale(pg.image.load(resource_path("graphs/background.png")).convert(), (SCREEN_SIZE, SCREEN_SIZE)),
                "food": pg.transform.scale(pg.image.load(resource_path("graphs/food.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_head": pg.transform.scale(pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
                "under_head": pg.transform.scale(pg.image.load(resource_path("graphs/under_head.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_body": pg.transform.scale(pg.image.load(resource_path("graphs/snake_body.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "body_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/corner_{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in ["tl", "tr", "bl", "br"]],
                "snake_tail": pg.transform.scale(pg.image.load(resource_path("graphs/snake_tail.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_blink": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_blink{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(2)] + ["finish"],
                "snake_see": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_see{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(3)],
                "snake_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_eat{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(4)] + ["finish"],
                "body_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/body_eat{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(3)],
                "eat_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/eat_{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in ["tl", "tr", "bl", "br"]],
                "snake_dead": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_dead{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(2)] + ["finish"],
                "snake_xx": pg.transform.scale(pg.image.load(resource_path("graphs/snake_xx.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE))
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            sys.exit(1)
        
    @staticmethod
    def load_sounds():
        print("Loading sounds...")
        # Loading sounds
        try:
            return {
                "A4": pg.mixer.Sound(resource_path("music_notes/A4.wav")),
                "A5": pg.mixer.Sound(resource_path("music_notes/A5.wav")),
                "B4": pg.mixer.Sound(resource_path("music_notes/B4.wav")),
                "B5": pg.mixer.Sound(resource_path("music_notes/B5.wav")),
                "C5": pg.mixer.Sound(resource_path("music_notes/C5.wav")),
                "C6": pg.mixer.Sound(resource_path("music_notes/C6.wav")),
                "C#6": pg.mixer.Sound(resource_path("music_notes/Cb6.wav")),
                "D5": pg.mixer.Sound(resource_path("music_notes/D5.wav")),
                "D#5": pg.mixer.Sound(resource_path("music_notes/Db5.wav")),
                "E5": pg.mixer.Sound(resource_path("music_notes/E5.wav")),
                "F5": pg.mixer.Sound(resource_path("music_notes/F5.wav")),
                "F#5": pg.mixer.Sound(resource_path("music_notes/Fb5.wav")),
                "G5": pg.mixer.Sound(resource_path("music_notes/G5.wav")),
                "G#4": pg.mixer.Sound(resource_path("music_notes/Gb4.wav")),
                "G#5": pg.mixer.Sound(resource_path("music_notes/Gb5.wav")),
                "C1": pg.mixer.Sound(resource_path("music_notes/C1.wav"))
            }
        except Exception as e:
            print(f"Error loading sounds: {e}")
            sys.exit(1)
            
        
    def draw_objects(self, *args):
        SCREEN.blit(self.graphics["background"], (0, 0))
        for obj in args:
            obj.draw(SCREEN, self.manipulated_images)
            
    def handle_events(self, snake):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            # Handle direction changes
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP: snake.change_direction((0, -1))
                elif event.key == pg.K_DOWN: snake.change_direction((0, 1))
                elif event.key == pg.K_LEFT: snake.change_direction((-1, 0))
                elif event.key == pg.K_RIGHT: snake.change_direction((1, 0))
                
    # Check for the positions            
    def front_update(self, snake, animation_handler):
        if not snake.front_func():
            self.game_over = True
            self.running = False
        snake.make_animation(animation_handler.active_animation)  # Make animation based on the current state
        if hasattr(snake, 'animation'):
            animation_handler.add_animation(self.graphics[snake.animation], str(snake.animation))  # Add the animation frames to the handler
            del snake.animation  # Remove the animation attribute after using it

            
    @staticmethod
    def snake_eat(snake, food):
        # Check if the snake's head has eaten the food
        if food._is_food_eaten(snake.body_grid[0]):
            food.generate_food(snake.body_grid)  # Generate new food position
            snake._is_growing = True
            global SCORE
            SCORE += 1
            print(f"Score: {SCORE}")
            
    def handle_animations(self, animation_handler):
        if animation_handler.get_image():
            # If there is an animation frame, draw it
            self.manipulated_images["snake_head"] = animation_handler.get_image()
        else:
            # If no animation frame, use the snake's head image
            self.manipulated_images["snake_head"] = self.graphics["snake_head"]
                
    def run(self):
        self.start()
        snake = SNAKE()
        food = FOOD()
        animation_handler = HEAD_ANIMATION_HANDLER()
        food.generate_food(snake.body_grid)
        
        frame_counter = 0
        while self.running:
            move_time = frame_counter % FRAMES_PER_MOVE == 0
            self.handle_events(snake)
            
            if move_time:
                self.front_update(snake, animation_handler)
                # Check if the snake's head has eaten the food
                self.snake_eat(snake, food)
            animation_handler.update()
            self.handle_animations(animation_handler)
                    
            snake.animate()        
            self.draw_objects(snake, food)
            pg.display.flip()
            
            CLOCK.tick(FPS)
            frame_counter += 1
            
        print("Game Over!")
        
        
if __name__ == "__main__":
    game = Game()
    game.run()