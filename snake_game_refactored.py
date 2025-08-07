# --Required Libraries--
import pygame as pg
import os
import sys

# --Initialize Pygame--
# This must be called to initialize all the Pygame modules.
pg.init()

# --Helper Function for File Paths--
def resource_path(relative_path):
    """
    Get the absolute path to a resource. This works for development environments
    and for single-file executables created by PyInstaller.
    """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS.
        base_path = sys._MEIPASS
    except Exception:
        # If not running in a PyInstaller bundle, use the default absolute path.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --SNAKE Class--
# Manages all properties and actions related to the snake.
class SNAKE:
    
    # --Snake Initialization--
    def __init__(self):
        super().__init__()
        # --Attributes for Position, Direction, and Movement--
        self.direction = [(1, 0), (1, 0)]  # A list of direction vectors for each body segment.
        self.l_direction = (1, 0)          # The direction of the head in the previous frame, used for rotation.
        self.move_queue = []               # A queue for pending player direction changes.
        self.body_grid = [((GRID_COUNT) // 2 - 1, (GRID_COUNT) // 2), ((GRID_COUNT) // 2 - 2, (GRID_COUNT) // 2)] # List of (x, y) grid coordinates for each body part.
        self.body_pixels = [pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid] # List of pixel coordinates for smooth animation.
        
        # --State Attributes--
        self._is_growing = False           # A flag to check if the snake should grow on the next move.
        self.wanted_animations = []        # A temporary list to hold animation requests for the current frame.
        
    # --Image Rotation Method--
    @staticmethod    
    def rotate(image, direction):
        """ Rotates an image to match the snake's direction vector. """
        if direction == (1, 0):  return pg.transform.rotate(image, 270) # Right
        if direction == (-1, 0): return pg.transform.rotate(image, 90) # Left
        if direction == (0, 1):  return pg.transform.rotate(image, 180) # Down
        if direction == (0, -1): return image  # Up (no rotation needed for the default sprite orientation)
        
    # --Core Movement and Logic Update--
    def front_func(self):
        """
        Processes the snake's movement for one grid step.
        - Updates direction from the move queue.
        - Calculates the new head position.
        - Checks for collisions with walls or itself.
        - Updates the body segments.
        Returns False if a collision occurs (game over), True otherwise.
        """
        # Update head direction if there's a move in the queue.
        if self.move_queue:
            self.direction[0] = self.move_queue.pop(0)
        self.l_direction = self.direction[0]
        
        # Calculate the new head's grid position.
        head_x, head_y = self.body_grid[0]
        dir_x, dir_y = self.direction[0]
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # Check for game over conditions.
        if (not (0 <= new_head[0] < GRID_COUNT and
                0 <= new_head[1] < GRID_COUNT) or
                (new_head in self.body_grid)):
            return False # Collision detected.
        
        # Add the new head to the body lists.
        self.body_grid.insert(0, new_head)
        self.direction.insert(0, self.direction[0])
        self.body_pixels.insert(0, self.body_pixels[0].copy())
        
        # Handle snake growth.
        if self._is_growing:
            self.wanted_animations.append("snake_eat")  # Request the "eat" animation.
            self._is_growing = False
        else:
            # If not growing, remove the tail segment.
            self.body_grid.pop()
            self.direction.pop()
            self.body_pixels.pop()
            
        return True # Movement was successful.

    # --Blink Animation Request--
    def blink(self):
        """ Randomly requests a blink animation. """
        from random import randint
        if randint(0, 4) == 0:
            self.wanted_animations.append("snake_blink")
        
    # --Visual Animation Update--
    def animate(self):
        """ Smoothly interpolates the pixel positions of each body part towards its target grid position. """
        for i in range(len(self.body_pixels)):
            target_pixel_pos = pg.Vector2(self.body_grid[i]) * GRID_SIZE
            self.body_pixels[i] = self.body_pixels[i].lerp(target_pixel_pos, 0.25)      
        
    # --Main Drawing Method--
    def draw(self, screen, graphics):
        """ Draws the entire snake (tail, body, and head) onto the screen. """
        # Draw the tail first (it's at the end of the list).
        center_pos = self.body_pixels[-1] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
        screen.blit(self.rotate(graphics["snake_tail"], self.direction[-1]), graphics["snake_tail"].get_rect(center=center_pos))
        
        # Draw the body segments.
        self.draw_body(screen, graphics)

        # Draw the head last so it appears on top.
        center_pos = self.body_pixels[0] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)           
        screen.blit(self.rotate(graphics["under_head"], self.direction[1]), graphics["under_head"].get_rect(center=center_pos))
        screen.blit(self.rotate(graphics["snake_head"], self.l_direction), graphics["snake_head"].get_rect(center=center_pos))
        
    # --Body Drawing Logic--
    def draw_body(self, screen, graphics):
        """ Draws the snake's body, correctly choosing between straight and corner pieces. """
        # Iterate through body segments, excluding the head (index 0) and tail (last index).
        for i in range(1, len(self.body_pixels) - 1):
            center_pos = self.body_pixels[i] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)

            # Get the grid positions of the current, previous, and next segments.
            current_grid_pos = pg.Vector2(self.body_grid[i])
            head_side_grid_pos = pg.Vector2(self.body_grid[i-1])
            tail_side_grid_pos = pg.Vector2(self.body_grid[i+1])

            # Calculate vectors to determine if it's a straight or corner piece.
            vec_from_head = head_side_grid_pos - current_grid_pos
            vec_from_tail = tail_side_grid_pos - current_grid_pos

            if vec_from_head == vec_from_tail * -1:
                # If vectors are opposite, it's a straight piece.
                screen.blit(self.rotate(graphics["snake_body"], self.direction[i]), graphics["snake_body"].get_rect(center=center_pos))
            else:
                # Otherwise, it's a corner piece. Determine which corner it is.
                turn_vectors = {(int(vec_from_head.x), int(vec_from_head.y)), 
                                (int(vec_from_tail.x), int(vec_from_tail.y))}
                image_to_draw = None
                if turn_vectors == {(0, -1), (-1, 0)}: image_to_draw = graphics["body_corner"][0]  # Top Left
                elif turn_vectors == {(0, -1), (1, 0)}: image_to_draw = graphics["body_corner"][1]  # Top Right
                elif turn_vectors == {(0, 1), (-1, 0)}: image_to_draw = graphics["body_corner"][2]  # Bottom Left
                elif turn_vectors == {(0, 1), (1, 0)}: image_to_draw = graphics["body_corner"][3]  # Bottom Right

                if image_to_draw:
                    screen.blit(image_to_draw, image_to_draw.get_rect(center=center_pos))
                    
    # --"See" Animation Request--
    def has_seen(self, food_pos):
        """ Checks if the food is close to the snake's head and requests the "see" animation. """
        if abs(self.body_grid[0][0] - food_pos[0]) < 3 and abs(self.body_grid[0][1] - food_pos[1]) < 3:
            self.wanted_animations.append("snake_see")
            
    # --Handle Player Input for Direction--
    def change_direction(self, new_direction):
        """
        Adds a player's direction command to the move queue.
        Prevents 180-degree turns and limits the queue size to prevent erratic movement.
        """
        # Determine the last commanded direction to prevent reversals.
        if self.move_queue:
            last_direction = self.move_queue[-1]
        else:
            last_direction = self.l_direction
        
        # Ignore moves that are the same as the last one or a direct reversal.
        if (new_direction[0] * -1, new_direction[1] * -1) == last_direction or new_direction == last_direction:
            return
        
        # Limit the move queue to 2 to buffer rapid inputs.
        if len(self.move_queue) < 2:
            self.move_queue.append(new_direction)
            
# --HEAD_ANIMATION_HANDLER Class--
# Manages the state and logic for playing all head animations.
class HEAD_ANIMATION_HANDLER:
    
    # --Animation Handler Initialization--
    def __init__(self):
        self.animation_frames = []        # The list of images for the current animation.
        self.current_frame = 0            # The index of the current frame in the list.
        self.frame_counter = 0            # A counter to control animation speed.
        self.animation_speed = 10         # Number of game frames to wait before showing the next animation frame.
        self.active_animation = None      # The name of the animation currently playing.
    
    # --Add/Change Animation Logic--
    def add_animation(self, graphics, wanted_animations):
        """
        Decides which animation to play based on a priority system.
        'snake_eat' can interrupt other animations and can be re-triggered.
        'snake_see' and 'snake_blink' will not interrupt higher-priority animations and will not reset if already playing.
        """
        if not wanted_animations:
            return

        # 1. Define animation categories and priorities.
        animation_tiers = ["snake_blink", "snake_see", "snake_eat", "snake_xx"]
        one_shot_animations = {"snake_eat", "snake_xx"} # Animations that should reset if triggered again.

        # 2. Find the highest-priority animation requested in the current frame.
        highest_prio_wanted = None
        highest_prio_level = -1
        for anim_name in wanted_animations:
            if anim_name in animation_tiers:
                level = animation_tiers.index(anim_name)
                if level > highest_prio_level:
                    highest_prio_level = level
                    highest_prio_wanted = anim_name
        
        if not highest_prio_wanted:
            return

        # 3. Get the priority of the currently playing animation.
        current_prio_level = -1
        if self.active_animation in animation_tiers:
            current_prio_level = animation_tiers.index(self.active_animation)

        # 4. Decision: If the new request has higher priority, switch to it.
        if highest_prio_level > current_prio_level:
            self.active_animation = highest_prio_wanted
            self.animation_frames = graphics[self.active_animation]
            # Always reset counters for a new animation.
            self.current_frame = 0
            self.frame_counter = 0

        # 5. Decision: If priorities are the same.
        elif highest_prio_level == current_prio_level:
            # Check if it's a "one-shot" animation.
            if highest_prio_wanted in one_shot_animations:
                # If so, reset the animation to play it again from the beginning.
                self.current_frame = 0
                self.frame_counter = 0
        
    # --Update Animation State--
    def update(self):
        """ Advances the animation to the next frame if enough time has passed. """
        if not self.animation_frames:
            return
        
        self.frame_counter += 1
        
        if self.frame_counter >= self.animation_speed:
            self.current_frame += 1
            # If the animation is over (reaches the end or a "finish" tag), clear the state.
            if self.current_frame >= len(self.animation_frames) or self.animation_frames[self.current_frame] == "finish":
                self.animation_frames = []
                self.active_animation = None
            self.frame_counter = 0
        
    # --Get Current Animation Image--
    def get_image(self):
        """ Returns the pygame.Surface for the current animation frame, or None. """
        if self.animation_frames:
            image = self.animation_frames[self.current_frame]
            if isinstance(image, pg.Surface):
                return image
        return None

# --FOOD Class--
# Manages the food's properties and actions.
class FOOD:    
    # --Food Generation--
    def generate_food(self, body_grid):
        """ Randomly places the food on the grid, avoiding the snake's body. """
        from random import randint
        while True:
            self.position = (randint(0, GRID_COUNT - 1), randint(0, GRID_COUNT - 1))
            if self.position not in body_grid:
                break
        
    # --Collision Check--
    def _is_food_eaten(self, pos):
        """ Checks if the given position (snake's head) matches the food's position. """
        return pos == self.position
        
    # --Drawing Method--
    def draw(self, screen, graphics):
        """ Draws the food item on the screen. """
        center_pos = pg.Vector2(self.position) * GRID_SIZE + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
        screen.blit(graphics["food"], graphics["food"].get_rect(center=center_pos))
            
# --GAME Class--
# The main class that runs the game loop and manages all game objects and states.
class Game:
    
    # --Game Initialization--
    def start(self):
        """ Initializes the game window, constants, and loads all assets. """
        print("Game is starting...")
        
        Info_Object = pg.display.Info()
        
        # --Global Game Constants--
        global SCREEN_SIZE, GRID_COUNT, GRID_SIZE, HEAD_SIZE
        SCREEN_SIZE = (Info_Object.current_h)*4//5
        GRID_COUNT = 12
        GRID_SIZE = SCREEN_SIZE // GRID_COUNT
        HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2
        
        # --Global Game Dependencies--
        global SCREEN, CLOCK, FPS, FRAMES_PER_MOVE, SCORE
        SCREEN = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        CLOCK = pg.time.Clock()
        FPS = 60
        FRAMES_PER_MOVE = 7
        SCORE = 0
        
        # --Game State Variables--
        self.running = True
        self.game_over = False
        
        # Load all graphics into a dictionary.
        self.graphics = self.load_images()
        
        # Create a dictionary of images that can be manipulated during the game (e.g., for animations).
        self.manipulated_images = self.graphics.copy()
        
        print("Game has started!")
        
    # --Asset Loading Methods--
    @staticmethod    
    def load_images():
        """ Loads, scales, and returns a dictionary of all game images. """
        print("Loading images...")
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
                "snake_see": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_see{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(3)] + ["finish"],
                "snake_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_eat{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(4)] + ["finish"],
                "snake_xx": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_xx.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE))] + ["finish"]
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            sys.exit(1)
        
    @staticmethod
    def load_sounds():
        """ Loads and returns a dictionary of all game sounds. """
        print("Loading sounds...")
        try:
            return {
                "A4": pg.mixer.Sound(resource_path("music_notes/A4.wav")), "A5": pg.mixer.Sound(resource_path("music_notes/A5.wav")), "B4": pg.mixer.Sound(resource_path("music_notes/B4.wav")), "B5": pg.mixer.Sound(resource_path("music_notes/B5.wav")), "C5": pg.mixer.Sound(resource_path("music_notes/C5.wav")), "C6": pg.mixer.Sound(resource_path("music_notes/C6.wav")), "C#6": pg.mixer.Sound(resource_path("music_notes/Cb6.wav")), "D5": pg.mixer.Sound(resource_path("music_notes/D5.wav")), "D#5": pg.mixer.Sound(resource_path("music_notes/Db5.wav")), "E5": pg.mixer.Sound(resource_path("music_notes/E5.wav")), "F5": pg.mixer.Sound(resource_path("music_notes/F5.wav")), "F#5": pg.mixer.Sound(resource_path("music_notes/Fb5.wav")), "G5": pg.mixer.Sound(resource_path("music_notes/G5.wav")), "G#4": pg.mixer.Sound(resource_path("music_notes/Gb4.wav")), "G#5": pg.mixer.Sound(resource_path("music_notes/Gb5.wav")), "C1": pg.mixer.Sound(resource_path("music_notes/C1.wav"))
            }
        except Exception as e:
            print(f"Error loading sounds: {e}")
            sys.exit(1)
            
    # --Main Drawing Function--
    def draw_objects(self, *args):
        """ Clears the screen and draws all provided game objects. """
        SCREEN.blit(self.graphics["background"], (0, 0))
        for obj in args:
            # Pass the manipulatable image dictionary to the draw method.
            obj.draw(SCREEN, self.manipulated_images)
            
    # --Event Handling--
    def handle_events(self, snake):
        """ Processes user input and other game events. """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            # Handle direction changes from keyboard input.
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_UP, pg.K_w]: snake.change_direction((0, -1))
                elif event.key in [pg.K_DOWN, pg.K_s]: snake.change_direction((0, 1))
                elif event.key in [pg.K_LEFT, pg.K_a]: snake.change_direction((-1, 0))
                elif event.key in [pg.K_RIGHT, pg.K_d]: snake.change_direction((1, 0))
                
    # --Main Logic Update Function--
    def front_update(self, snake, animation_handler, food):
        """ Updates the core game state based on a move tick. """
        # Move the snake and check for collisions.
        if not snake.front_func():
            snake.wanted_animations.append("snake_xx")  # Request the death animation.
            # Set a death timer to allow the animation to play before the game ends.
            if not hasattr(self, 'death_counter'):
                self.death_counter = pg.time.get_ticks()
        elif hasattr(self, 'death_counter'):
            # If the snake is somehow alive again, remove the timer.
            del self.death_counter
            
        # Check for and request other animations.
        snake.has_seen(food.position)
        snake.blink()
    
        # Pass all requested animations to the handler to process.
        animation_handler.add_animation(self.graphics, snake.wanted_animations)
        # Clear the request list for the next frame.
        snake.wanted_animations = []

    # --Food Consumption Logic--
    @staticmethod
    def snake_eat(snake, food):
        """ Checks for food collision and updates the game state accordingly. """
        if food._is_food_eaten(snake.body_grid[0]):
            food.generate_food(snake.body_grid)
            snake._is_growing = True
            global SCORE
            SCORE += 1
            print(f"Score: {SCORE}")
            
    # --Animation Image Handling--
    def handle_animations(self, animation_handler):
        """ Updates the snake head image based on the current animation frame. """
        animated_image = animation_handler.get_image()
        if animated_image:
            # If an animation is playing, use its frame for the snake head.
            self.manipulated_images["snake_head"] = animated_image
        else:
            # Otherwise, use the default snake head image.
            self.manipulated_images["snake_head"] = self.graphics["snake_head"]
                
    # --Main Game Loop--
    def run(self):
        """ Contains the main loop that runs the entire game. """
        self.start()
        # Create instances of all game objects.
        snake = SNAKE()
        food = FOOD()
        animation_handler = HEAD_ANIMATION_HANDLER()
        food.generate_food(snake.body_grid)
        
        frame_counter = 0
        while self.running:
            # A flag to check if it's time for the snake to move one grid step.
            move_time = frame_counter % FRAMES_PER_MOVE == 0
            
            # 1. Handle Events (Input)
            self.handle_events(snake)
            
            # 2. Update Game State (Logic)
            if move_time:
                self.front_update(snake, animation_handler, food)
                self.snake_eat(snake, food)

            animation_handler.update()
            self.handle_animations(animation_handler)
            
            # If the death timer is active, check if enough time has passed to end the game.
            if hasattr(self, 'death_counter'):
                if pg.time.get_ticks() - self.death_counter > 100:
                    self.game_over = True
                    self.running = False
                    return
                    
            snake.animate() # Update the snake's visual pixel positions.
            
            # 3. Render (Draw)
            self.draw_objects(snake, food)
            pg.display.flip()
            
            # 4. Tick the Clock
            CLOCK.tick(FPS)
            frame_counter += 1
            
        print("Game Over!")
        pg.quit()
        sys.exit()

# --Entry Point of the Program--
if __name__ == "__main__":
    # Create a Game instance and run it.
    game = Game()
    game.run()