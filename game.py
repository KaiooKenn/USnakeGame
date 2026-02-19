import pygame as pg
import sys
import random
import constants


from utils import resource_path
from snake import SNAKE
from food import FOOD
from animation import ANIMATION_HANDLER
from sound import SOUND_PLAYER


class Game:

    # --Game Initialization--
    def __init__(self):
        """Initializes the game window, constants, and loads all assets."""
        print("Game is starting...")

        Info_Object = pg.display.Info()

        # --Global Game Constants--
        self.SCREEN_SIZE = constants.SizeConstants.SCREEN_SIZE.value
        self.GRID_COUNT = constants.SizeConstants.GRID_COUNT.value
        self.GRID_SIZE = self.SCREEN_SIZE // self.GRID_COUNT
        self.HEAD_SIZE = self.GRID_SIZE + (self.GRID_SIZE // 5) * 2

        # --Global Game Dependencies--
        self.SCREEN = pg.display.set_mode((self.SCREEN_SIZE, self.SCREEN_SIZE))
        pg.display.set_caption("Snake Game")
        self.CLOCK = pg.time.Clock()
        self.FPS = constants.OtherConstants.FPS.value
        self.FRAMES_PER_MOVE = constants.OtherConstants.FRAMES_PER_MOVE.value
        self.SCORE = constants.OtherConstants.SCORE.value

        # --Game State Variables--
        self.running = True
        self.game_over = False

        # Load all graphics into a dictionary.
        self.graphics = self.load_images()
        self.sounds = self.load_sounds()
        self.font = pg.font.Font(
            resource_path("fonts/snake_game_font.ttf"),
            constants.SizeConstants.FONT_SIZE.value,
        )
        pg.display.set_icon(self.graphics[constants.SnakeAnimations.SNAKE_SEEN][1])

        print("Game has started!")

    # --Asset Loading Methods--
    def load_images(self):
        """Loads, scales, and returns a dictionary of all game images."""
        print("Loading images...")
        try:
            return {
                "background": pg.transform.scale(
                    pg.image.load(resource_path("graphs/background.png")).convert(),
                    (self.SCREEN_SIZE, self.SCREEN_SIZE),
                ),
                "food": pg.transform.scale(
                    pg.image.load(resource_path("graphs/food.png")).convert_alpha(),
                    (self.GRID_SIZE, self.GRID_SIZE),
                ),
                constants.SnakeBodyParts.HEAD: pg.transform.scale(
                    pg.image.load(
                        resource_path("graphs/snake_head.png")
                    ).convert_alpha(),
                    (self.HEAD_SIZE, self.HEAD_SIZE),
                ),
                constants.SnakeBodyParts.UNDER_HEAD: pg.transform.scale(
                    pg.image.load(
                        resource_path("graphs/under_head.png")
                    ).convert_alpha(),
                    (self.GRID_SIZE, self.GRID_SIZE),
                ),
                constants.SnakeBodyParts.BODY: pg.transform.scale(
                    pg.image.load(
                        resource_path("graphs/snake_body.png")
                    ).convert_alpha(),
                    (self.GRID_SIZE, self.GRID_SIZE),
                ),
                "body_bulge": [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/body_bulge{i}.png")
                        ).convert_alpha(),
                        (self.GRID_SIZE, self.GRID_SIZE),
                    )
                    for i in range(
                        constants.AnimationFrameCounts.BULGE_BODY_FRAMES.value
                    )
                ],
                "bulge_corner": [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/bulge_corner_{i}.png")
                        ).convert_alpha(),
                        (self.GRID_SIZE, self.GRID_SIZE),
                    )
                    for i in [
                        constants.CornerDirections.TOP_LEFT.value,
                        constants.CornerDirections.TOP_RIGHT.value,
                        constants.CornerDirections.BOTTOM_LEFT.value,
                        constants.CornerDirections.BOTTOM_RIGHT.value,
                    ]
                ],
                "body_corner": [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/corner_{i}.png")
                        ).convert_alpha(),
                        (self.GRID_SIZE, self.GRID_SIZE),
                    )
                    for i in [
                        constants.CornerDirections.TOP_LEFT.value,
                        constants.CornerDirections.TOP_RIGHT.value,
                        constants.CornerDirections.BOTTOM_LEFT.value,
                        constants.CornerDirections.BOTTOM_RIGHT.value,
                    ]
                ],
                constants.SnakeBodyParts.TAIL: pg.transform.scale(
                    pg.image.load(
                        resource_path("graphs/snake_tail.png")
                    ).convert_alpha(),
                    (self.GRID_SIZE, self.GRID_SIZE),
                ),
                constants.SnakeAnimations.SNAKE_BLINK: [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/snake_blink{i}.png")
                        ).convert_alpha(),
                        (self.HEAD_SIZE, self.HEAD_SIZE),
                    )
                    for i in range(constants.AnimationFrameCounts.BLINK_FRAMES.value)
                ]
                + ["finish"],
                constants.SnakeAnimations.SNAKE_SEEN: [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/snake_see{i}.png")
                        ).convert_alpha(),
                        (self.HEAD_SIZE, self.HEAD_SIZE),
                    )
                    for i in range(constants.AnimationFrameCounts.SEEN_FRAMES.value)
                ]
                + ["finish"],
                constants.SnakeAnimations.SNAKE_EAT: [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/snake_eat{i}.png")
                        ).convert_alpha(),
                        (self.HEAD_SIZE, self.HEAD_SIZE),
                    )
                    for i in range(constants.AnimationFrameCounts.EAT_FRAMES.value)
                ]
                + ["finish"],
                constants.SnakeAnimations.SNAKE_DEAD: [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path(f"graphs/snake_dead{i}.png")
                        ).convert_alpha(),
                        (self.SCREEN_SIZE, self.SCREEN_SIZE),
                    )
                    for i in range(constants.AnimationFrameCounts.DEAD_FRAMES.value)
                ]
                + ["finish"],
                constants.SnakeAnimations.SNAKE_XX: [
                    pg.transform.scale(
                        pg.image.load(
                            resource_path("graphs/snake_xx.png")
                        ).convert_alpha(),
                        (self.HEAD_SIZE, self.HEAD_SIZE),
                    )
                ]
                + ["finish"],
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            sys.exit(1)

    @staticmethod
    def load_sounds():
        """Loads and returns a dictionary of all game sounds."""
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
                "C1": pg.mixer.Sound(resource_path("music_notes/C1.wav")),
            }
        except Exception as e:
            print(f"Error loading sounds: {e}")
            sys.exit(1)

    # --Main Drawing Function--
    def draw_objects(self, snake: SNAKE, food: FOOD, get_bulge_image, get_image):
        """Clears the screen and draws all provided game objects."""
        self.SCREEN.blit(self.graphics["background"], (0, 0))
        self.draw_grid()
        food.draw(self.SCREEN, self.graphics, self.GRID_SIZE)
        snake.draw(self.SCREEN, self.graphics, get_bulge_image, get_image)
        self.SCREEN.blit(
            self.font.render(
                f"Score: {self.SCORE}", True, constants.ColorConstants.SCORE_COLOR.value
            ),
            constants.OtherConstants.SCORE_POSITION.value,
        )

    def draw_grid(self):
        """Draws a grid overlay for debugging purposes."""
        for x in range(0, self.SCREEN_SIZE, self.GRID_SIZE):
            pg.draw.line(
                self.SCREEN,
                constants.ColorConstants.GRID_COLOR.value,
                (x, 0),
                (x, self.SCREEN_SIZE),
            )
        for y in range(0, self.SCREEN_SIZE, self.GRID_SIZE):
            pg.draw.line(
                self.SCREEN,
                constants.ColorConstants.GRID_COLOR.value,
                (0, y),
                (self.SCREEN_SIZE, y),
            )

    def playing_sound(self, sound_player):
        next_sound = next(sound_player)
        pg.mixer.stop()
        next_sound.play()

    # --Event Handling--
    def handle_events(self, snake, sound_player):
        """Processes user input and other game events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            # Handle direction changes from keyboard input.
            if event.type == pg.KEYDOWN:
                play_sound = False
                if event.key in [pg.K_UP, pg.K_w]:
                    snake.change_direction(constants.Direction.UP.value)
                    play_sound = True
                elif event.key in [pg.K_DOWN, pg.K_s]:
                    snake.change_direction(constants.Direction.DOWN.value)
                    play_sound = True
                elif event.key in [pg.K_LEFT, pg.K_a]:
                    snake.change_direction(constants.Direction.LEFT.value)
                    play_sound = True
                elif event.key in [pg.K_RIGHT, pg.K_d]:
                    snake.change_direction(constants.Direction.RIGHT.value)
                    play_sound = True
                if play_sound:
                    self.playing_sound(sound_player)

    # --Main Logic Update Function--
    def front_update(
        self, snake: SNAKE, animation_handler: ANIMATION_HANDLER, food: FOOD
    ):
        """Updates the core game state based on a move tick."""
        # Move the snake and check for collisions.
        if not snake.front_func():
            snake.wanted_animations.append(
                constants.SnakeAnimations.SNAKE_XX
            )  # Request the death animation.
            # Set a death timer to allow the animation to play before the game ends.
            if not hasattr(self, "death_counter"):
                self.death_counter = pg.time.get_ticks()
        elif hasattr(self, "death_counter"):
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
    def snake_eat(self, snake, food):
        """Checks for food collision and updates the game state accordingly."""
        if food._is_food_eaten(snake.body_grid[0]):
            food.generate_food(snake.body_grid)
            snake._is_growing = True
            self.SCORE += 1
            print(f"Score: {self.SCORE}")

    # --Animation Image Handling--
    def get_head_image(self, animation_handler):
        """Updates the snake head image based on the current animation frame."""
        animated_image = animation_handler.get_image()
        if animated_image:
            # If an animation is playing, use its frame for the snake head.
            return animated_image
        else:
            # Otherwise, use the default snake head image.
            return self.graphics[constants.SnakeBodyParts.HEAD]

    def game_over_screen(
        self, animation_handler: ANIMATION_HANDLER, frame_counter: int
    ):
        animation_handler.add_animation(
            self.graphics, [constants.SnakeAnimations.SNAKE_DEAD]
        )
        from random import randint

        animation_handler.animation_speed = randint(
            constants.AnimationConstants.DEATH_ANIMATION_SPEED_MIN.value,
            constants.AnimationConstants.DEATH_ANIMATION_SPEED_MAX.value,
        )
        dead_time = pg.time.get_ticks()
        while (
            pg.time.get_ticks() - dead_time
            < constants.AnimationConstants.DEATH_SCREEN_DURATION.value
        ):
            animation_handler.update(
                frame_counter, len(self.graphics["body_bulge"]), self.FRAMES_PER_MOVE
            )
            if not animation_handler.active_animation:
                animation_handler.add_animation(
                    self.graphics, [constants.SnakeAnimations.SNAKE_DEAD]
                )
            image = animation_handler.get_image()
            if image:
                self.SCREEN.blit(
                    image,
                    image.get_rect(topleft=(0, 0)),
                )
            pg.display.flip()
        self.running = False

    # --Main Game Loop--
    def run(self):
        """Contains the main loop that runs the entire game."""
        frame_counter = 0
        # Create instances of all game objects.
        snake = SNAKE(self.GRID_COUNT, self.GRID_SIZE)
        food = FOOD()
        sound_player = SOUND_PLAYER(self.sounds)
        animation_handler = ANIMATION_HANDLER(frame_counter)
        food.generate_food(snake.body_grid)

        while self.running:
            # A flag to check if it's time for the snake to move one grid step.
            move_time = frame_counter % self.FRAMES_PER_MOVE == 0

            # 1. Handle Events (Input)
            self.handle_events(snake, sound_player)

            # 2. Update Game State (Logic)
            if move_time:
                frame_counter = 0
                self.front_update(snake, animation_handler, food)
                self.snake_eat(snake, food)

            animation_handler.update(
                frame_counter, len(self.graphics["body_bulge"]), self.FRAMES_PER_MOVE
            )

            # If the death timer is active, check if enough time has passed to end the game.
            if hasattr(self, "death_counter"):
                if (
                    pg.time.get_ticks() - self.death_counter
                    > constants.AnimationConstants.DEATH_ANIMATION_DELAY.value
                ):
                    self.game_over = True

            snake.animate()  # Update the snake's visual pixel positions.

            # 3. Render (Draw)
            self.draw_objects(
                snake,
                food,
                animation_handler.get_bulge_image(self.graphics["body_bulge"]),
                self.get_head_image(animation_handler),
            )
            pg.display.flip()

            if self.game_over:
                self.game_over_screen(animation_handler, frame_counter)

            # 4. Tick the Clock
            self.CLOCK.tick(self.FPS)
            frame_counter += 1

        print("Game Over!")
        pg.quit()
        sys.exit()
