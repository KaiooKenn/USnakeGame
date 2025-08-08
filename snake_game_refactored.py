# --Required Libraries--
import pygame as pg
import os
import sys

# --Initialize Pygame--
# This must be called to initialize all the Pygame modules.
pg.init()
pg.mixer.init()

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
        self.bulge_indexes = []            # A list to hold the indexes of body segments to bulge.
        
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
        
        self.bulge_indexes = self.update_bulge_indexes(self.bulge_indexes)
        
        # Handle snake growth.
        if self._is_growing:
            self.bulge_indexes.append(1)
            self.wanted_animations.append("snake_eat")  # Request the "eat" animation.
            self._is_growing = False
        else:
            # If not growing, remove the tail segment.
            self.body_grid.pop()
            self.direction.pop()
            self.body_pixels.pop()
            
        return True # Movement was successful.

    def update_bulge_indexes(self, bulge_indexes):
        bulge_indexes = [i + 2 for i in bulge_indexes if i < len(self.body_grid)]
        return bulge_indexes

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
    def draw(self, screen, graphics, get_bulge_image, get_image):
        """ Draws the entire snake (tail, body, and head) onto the screen. """
        # Draw the tail first (it's at the end of the list).
        center_pos = self.body_pixels[-1] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
        screen.blit(self.rotate(graphics["snake_tail"], self.direction[-1]), graphics["snake_tail"].get_rect(center=center_pos))
        
        # Draw the body segments.
        self.draw_body(screen, graphics, get_bulge_image)

        # Draw the head last so it appears on top.
        center_pos = self.body_pixels[0] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)           
        screen.blit(self.rotate(graphics["under_head"], self.direction[1]), graphics["under_head"].get_rect(center=center_pos))
        screen.blit(self.rotate(get_image, self.l_direction), graphics["snake_head"].get_rect(center=center_pos))
        
    # --Body Drawing Logic--
    def draw_body(self, screen, graphics, get_bulge_image):
        """ Draws the snake's body, correctly choosing between straight and corner pieces. """
        # Iterate through body segments, excluding the head (index 0) and tail (last index).
        for i in range(1, len(self.body_pixels) - 1):
            center_pos = self.body_pixels[i] + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)

            # Get the grid positions of the current, previous, and next segments.
            current_grid_pos = pg.Vector2(self.body_grid[i])
            head_side_grid_pos = pg.Vector2(self.body_grid[i-1])
            tail_side_grid_pos = pg.Vector2(self.body_grid[i+1])

            # Calculate vectors to determine if it's a straight or corner piece.s
            vec_from_head = head_side_grid_pos - current_grid_pos
            vec_from_tail = tail_side_grid_pos - current_grid_pos

            if vec_from_head == vec_from_tail * -1:
                # If vectors are opposite, it's a straight piece.
                image_to_draw = graphics["snake_body"]
                if i in self.bulge_indexes: 
                    image_to_draw = get_bulge_image
                    if image_to_draw is None:  # Check if image_to_draw is None
                        image_to_draw = graphics["snake_body"]  # Use the default image if get_bulge_image returns None
                screen.blit(self.rotate(image_to_draw, self.direction[i]), graphics["snake_body"].get_rect(center=center_pos))
            else:
                # Otherwise, it's a corner piece. Determine which corner it is.
                turn_vectors = {(int(vec_from_head.x), int(vec_from_head.y)), 
                                (int(vec_from_tail.x), int(vec_from_tail.y))}
                image_to_draw = None
                corner_set = "body_corner"
                if i in self.bulge_indexes: corner_set = "bulge_corner"
                if turn_vectors == {(0, -1), (-1, 0)}: image_to_draw = graphics[corner_set][0]  # Top Left
                elif turn_vectors == {(0, -1), (1, 0)}: image_to_draw = graphics[corner_set][1]  # Top Right
                elif turn_vectors == {(0, 1), (-1, 0)}: image_to_draw = graphics[corner_set][2]  # Bottom Left
                elif turn_vectors == {(0, 1), (1, 0)}: image_to_draw = graphics[corner_set][3]  # Bottom Right

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
            
# --ANIMATION_HANDLER Class--
# Manages the state and logic for playing all head animations.
class ANIMATION_HANDLER:
    
    # --Animation Handler Initialization--
    def __init__(self, game_class_frame_count):
        self.animation_frames = []        # The list of images for the current animation.
        self.current_frame = 0            # The index of the current frame in the list.
        self.current_bulge_frame = 0      # The index of the current bulge frame in the list.
        self.frame_counter = 0            # A counter to control animation speed.
        self.game_class_frame_count = game_class_frame_count
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
        animation_tiers = ["snake_blink", "snake_see", "snake_eat", "snake_xx", "snake_dead"]
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
    def update(self, game_class_frame_count, len_b_frames):
        """ Advances the animation to the next frame if enough time has passed. """
        if not self.animation_frames:
            return
        
        self.game_class_frame_count = game_class_frame_count
        self.frame_counter += 1
        
        if self.frame_counter >= self.animation_speed:
            self.current_frame += 1
            # If the animation is over (reaches the end or a "finish" tag), clear the state.
            if self.current_frame >= len(self.animation_frames) or self.animation_frames[self.current_frame] == "finish":
                self.animation_frames = []
                self.active_animation = None
            self.frame_counter = 0
            
        index_slicer = FRAMES_PER_MOVE / len_b_frames
        self.current_bulge_frame = int(self.game_class_frame_count // index_slicer)
                    
    # --Get Current Animation Image--
    def get_image(self):
        """ Returns the pygame.Surface for the current animation frame, or None. """
        if self.animation_frames:
            image = self.animation_frames[self.current_frame]
            if isinstance(image, pg.Surface):
                return image
        return None
    
    def get_bulge_image(self, bulge_body: list[pg.Surface]):
        """ Returns the pygame.Surface for the current bulge frame, or None. """
        if self.animation_frames:
            image = bulge_body[self.current_bulge_frame]
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
        
class SOUND_PLAYER:
    def __init__(self, sounds):
        self.sounds = sounds
        self.index = 0
        self.MELODY = [
    'B4', 'A4', 'G#4', 'A4', 'C5',
    'D5', 'C5', 'B4', 'C5', 'E5',
    'F5', 'E5', 'D#5', 'E5',
    'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6',
    'A5', 'C6', 'G5', 'A5', 'B5', 'A5',
    'G5', 'A5', 'G5', 'A5', 'B5', 'A5',
    'G5', 'A5', 'G5', 'A5', 'B5', 'A5', 'G5', 'F#5', 'E5',

    'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5',
    'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5',
    'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4',
    'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4',

    'B4', 'A4', 'G#4', 'A4', 'C5',
    'D5', 'C5', 'B4', 'C5', 'E5',
    'F5', 'E5', 'D#5', 'E5',
    'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5'
]
    def __iter__(self):
        return self
    
    def __next__(self):
        self.index = (self.index + 1) % len(self.MELODY)
        return self.sounds[self.MELODY[self.index]]
        
            
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
        pg.display.set_caption("Snake Game")
        CLOCK = pg.time.Clock()
        FPS = 60
        FRAMES_PER_MOVE = 7
        SCORE = 0
        
        # --Game State Variables--
        self.running = True
        self.game_over = False
        
        # Load all graphics into a dictionary.
        self.graphics = self.load_images()
        self.sounds = self.load_sounds()
        self.font = pg.font.Font(resource_path("fonts/snake_game_font.ttf"), 28)
        pg.display.set_icon(self.graphics["snake_see"][1])
        
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
                "body_bulge": [pg.transform.scale(pg.image.load(resource_path(f"graphs/body_bulge{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(3)],
                "bulge_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/bulge_corner_{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in ["tl", "tr", "bl", "br"]],
                "body_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/corner_{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in ["tl", "tr", "bl", "br"]],
                "snake_tail": pg.transform.scale(pg.image.load(resource_path("graphs/snake_tail.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_blink": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_blink{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(2)] + ["finish"],
                "snake_see": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_see{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(3)] + ["finish"],
                "snake_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_eat{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(4)] + ["finish"],
                "snake_dead": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_dead{i}.png")).convert_alpha(), (SCREEN_SIZE, SCREEN_SIZE)) for i in range(2)] + ["finish"], 
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
            
    # --Main Drawing Function--
    def draw_objects(self, snake, food, get_bulge_image, get_image):
        """ Clears the screen and draws all provided game objects. """
        SCREEN.blit(self.graphics["background"], (0, 0))
        food.draw(SCREEN, self.graphics)
        snake.draw(SCREEN, self.graphics, get_bulge_image, get_image)
        SCREEN.blit(self.font.render(f"Score: {SCORE}", True, (149, 197, 111)), (10, 10))
        
    def playing_sound(self, sound_player):
        next_sound = next(sound_player)
        pg.mixer.stop()
        next_sound.play()
         
            
    # --Event Handling--
    def handle_events(self, snake, sound_player):
        """ Processes user input and other game events. """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            # Handle direction changes from keyboard input.
            if event.type == pg.KEYDOWN:
                play_sound = False
                if event.key in [pg.K_UP, pg.K_w]: 
                    snake.change_direction((0, -1)) 
                    play_sound = True
                elif event.key in [pg.K_DOWN, pg.K_s]: 
                    snake.change_direction((0, 1))
                    play_sound = True
                elif event.key in [pg.K_LEFT, pg.K_a]: 
                    snake.change_direction((-1, 0))
                    play_sound = True
                elif event.key in [pg.K_RIGHT, pg.K_d]: 
                    snake.change_direction((1, 0))
                    play_sound = True
                if play_sound: self.playing_sound(sound_player)
                 
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
    def get_head_image(self, animation_handler):
        """ Updates the snake head image based on the current animation frame. """
        animated_image = animation_handler.get_image()
        if animated_image:
            # If an animation is playing, use its frame for the snake head.
            return animated_image
        else:
            # Otherwise, use the default snake head image.
            return self.graphics["snake_head"]
        
    def game_over_screen(self, animation_handler, frame_counter):
        animation_handler.add_animation(self.graphics, ["snake_dead"])
        from random import randint
        animation_handler.animation_speed = randint(240, 300)
        dead_time = pg.time.get_ticks()
        while pg.time.get_ticks() - dead_time < 1500:
            animation_handler.update(frame_counter, len(self.graphics["body_bulge"]))
            if not animation_handler.active_animation:
                animation_handler.add_animation(self.graphics, ["snake_dead"])
            if animation_handler.get_image():
                SCREEN.blit(animation_handler.get_image(), animation_handler.get_image().get_rect(topleft = (0, 0)))
            pg.display.flip()
        self.running = False
                
    # --Main Game Loop--
    def run(self):
        """ Contains the main loop that runs the entire game. """
        self.start()
        frame_counter = 0
        # Create instances of all game objects.
        snake = SNAKE()
        food = FOOD()
        sound_player = SOUND_PLAYER(self.sounds)
        animation_handler = ANIMATION_HANDLER(frame_counter)
        food.generate_food(snake.body_grid)
        
        while self.running:
            # A flag to check if it's time for the snake to move one grid step.
            move_time = frame_counter % FRAMES_PER_MOVE == 0
            
            # 1. Handle Events (Input)
            self.handle_events(snake, sound_player)
            
            # 2. Update Game State (Logic)
            if move_time:
                frame_counter = 0
                self.front_update(snake, animation_handler, food)
                self.snake_eat(snake, food)

            animation_handler.update(frame_counter, len(self.graphics["body_bulge"]))
            
            # If the death timer is active, check if enough time has passed to end the game.
            if hasattr(self, 'death_counter'):
                if pg.time.get_ticks() - self.death_counter > 100:
                    self.game_over = True
                    
            snake.animate() # Update the snake's visual pixel positions.
            
            # 3. Render (Draw)
            self.draw_objects(snake, food, animation_handler.get_bulge_image(self.graphics["body_bulge"]), self.get_head_image(animation_handler))
            pg.display.flip()
            
            if self.game_over:
                self.game_over_screen(animation_handler, frame_counter)
            
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