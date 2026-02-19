import pygame as pg
import constants


class SNAKE:

    # --Snake Initialization--
    def __init__(self, GRID_COUNT: int, GRID_SIZE: int):
        super().__init__()

        self.RIGHT = constants.Direction.RIGHT.value
        self.LEFT = constants.Direction.LEFT.value
        self.UP = constants.Direction.UP.value
        self.DOWN = constants.Direction.DOWN.value

        self.GRID_COUNT = GRID_COUNT
        self.GRID_SIZE = GRID_SIZE

        # --Attributes for Position, Direction, and Movement--
        self.direction = [
            self.RIGHT,  # right
            self.RIGHT,  # right
        ]  # A list of direction vectors for each body segment.
        self.l_direction = (
            self.RIGHT
        )  # The direction of the head in the previous frame, used for rotation.
        self.move_queue = []  # A queue for pending player direction changes.
        self.body_grid = [
            ((self.GRID_COUNT) // 2 - 1, (self.GRID_COUNT) // 2),
            ((self.GRID_COUNT) // 2 - 2, (self.GRID_COUNT) // 2),
        ]  # List of (x, y) grid coordinates for each body part.
        self.body_pixels = [
            pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid
        ]  # List of pixel coordinates for smooth animation.

        # --State Attributes--
        self._is_growing = (
            False  # A flag to check if the snake should grow on the next move.
        )
        self.wanted_animations = (
            []
        )  # A temporary list to hold animation requests for the current frame.
        self.bulge_indexes = []  # A list to hold the indexes of body segments to bulge.

    # --Image Rotation Method--
    def rotate(self, image, direction):
        """Rotates an image to match the snake's direction vector."""
        if direction == self.RIGHT:
            return pg.transform.rotate(
                image, constants.RotationAngles.RIGHT.value
            )  # Right
        if direction == self.LEFT:
            return pg.transform.rotate(
                image, constants.RotationAngles.LEFT.value
            )  # Left
        if direction == self.DOWN:
            return pg.transform.rotate(
                image, constants.RotationAngles.DOWN.value
            )  # Down
        if direction == self.UP:
            return image  # Up (no rotation needed for the default sprite orientation)

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
        if not (
            0 <= new_head[0] < self.GRID_COUNT and 0 <= new_head[1] < self.GRID_COUNT
        ) or (new_head in self.body_grid):
            return False  # Collision detected.

        # Add the new head to the body lists.
        self.body_grid.insert(0, new_head)
        self.direction.insert(0, self.direction[0])
        self.body_pixels.insert(0, self.body_pixels[0].copy())

        self.bulge_indexes = self.update_bulge_indexes(self.bulge_indexes)

        # Handle snake growth.
        if self._is_growing:
            self.bulge_indexes.append(
                constants.SnakeMovementConstants.BULGE_ANIMATION_TRIGGER.value
            )
            self.wanted_animations.append(
                constants.SnakeAnimations.SNAKE_EAT
            )  # Request the "eat" animation.
            self._is_growing = False
        else:
            # If not growing, remove the tail segment.
            self.body_grid.pop()
            self.direction.pop()
            self.body_pixels.pop()
        return True  # Movement was successful.

    def update_bulge_indexes(self, bulge_indexes):
        bulge_indexes = [
            i + constants.SnakeMovementConstants.BULGE_UPDATE_OFFSET.value
            for i in bulge_indexes
            if i < len(self.body_grid)
        ]
        return bulge_indexes

    # --Blink Animation Request--
    def blink(self):
        """Randomly requests a blink animation."""
        from random import randint

        if randint(0, constants.SnakeMovementConstants.BLINK_CHANCE.value - 1) == 0:
            self.wanted_animations.append(constants.SnakeAnimations.SNAKE_BLINK)

    # --Visual Animation Update--
    def animate(self):
        """Smoothly interpolates the pixel positions of each body part towards its target grid position."""
        for i in range(len(self.body_pixels)):
            target_pixel_pos = pg.Vector2(self.body_grid[i]) * self.GRID_SIZE
            self.body_pixels[i] = self.body_pixels[i].lerp(
                target_pixel_pos,
                constants.SnakeMovementConstants.MOVEMENT_SMOOTHING.value,
            )

    # --Main Drawing Method--
    def draw(self, screen, graphics, get_bulge_image, get_image):
        """Draws the entire snake (tail, body, and head) onto the screen."""
        # Draw the tail first (it's at the end of the list).
        center_pos = self.body_pixels[-1] + pg.Vector2(
            self.GRID_SIZE // 2, self.GRID_SIZE // 2
        )
        screen.blit(
            self.rotate(graphics[constants.SnakeBodyParts.TAIL], self.direction[-1]),
            graphics[constants.SnakeBodyParts.TAIL].get_rect(center=center_pos),
        )

        # Draw the body segments.
        self.draw_body(screen, graphics, get_bulge_image)

        # Draw the head last so it appears on top.
        center_pos = self.body_pixels[0] + pg.Vector2(
            self.GRID_SIZE // 2, self.GRID_SIZE // 2
        )
        screen.blit(
            self.rotate(
                graphics[constants.SnakeBodyParts.UNDER_HEAD], self.direction[1]
            ),
            graphics[constants.SnakeBodyParts.UNDER_HEAD].get_rect(center=center_pos),
        )
        screen.blit(
            self.rotate(get_image, self.l_direction),
            graphics[constants.SnakeBodyParts.HEAD].get_rect(center=center_pos),
        )

    # --Body Drawing Logic--
    def draw_body(self, screen, graphics, get_bulge_image):
        """Draws the snake's body, correctly choosing between straight and corner pieces."""
        # Iterate through body segments, excluding the head (index 0) and tail (last index).
        for i in range(1, len(self.body_pixels) - 1):
            center_pos = self.body_pixels[i] + pg.Vector2(
                self.GRID_SIZE // 2, self.GRID_SIZE // 2
            )

            # Get the grid positions of the current, previous, and next segments.
            current_grid_pos = pg.Vector2(self.body_grid[i])
            head_side_grid_pos = pg.Vector2(self.body_grid[i - 1])
            tail_side_grid_pos = pg.Vector2(self.body_grid[i + 1])

            # Calculate vectors to determine if it's a straight or corner piece.s
            vec_from_head = head_side_grid_pos - current_grid_pos
            vec_from_tail = tail_side_grid_pos - current_grid_pos

            if vec_from_head == vec_from_tail * -1:
                # If vectors are opposite, it's a straight piece.
                image_to_draw = graphics[constants.SnakeBodyParts.BODY]
                if i in self.bulge_indexes:
                    image_to_draw = get_bulge_image
                    if image_to_draw is None:  # Check if image_to_draw is None
                        image_to_draw = graphics[
                            constants.SnakeBodyParts.BODY
                        ]  # Use the default image if get_bulge_image returns None
                screen.blit(
                    self.rotate(image_to_draw, self.direction[i]),
                    graphics[constants.SnakeBodyParts.BODY].get_rect(center=center_pos),
                )
            else:
                # Otherwise, it's a corner piece. Determine which corner it is.
                turn_vectors = {
                    (int(vec_from_head.x), int(vec_from_head.y)),
                    (int(vec_from_tail.x), int(vec_from_tail.y)),
                }
                image_to_draw = None
                corner_set = "body_corner"
                if i in self.bulge_indexes:
                    corner_set = "bulge_corner"
                if turn_vectors == {self.UP, self.LEFT}:
                    image_to_draw = graphics[corner_set][0]  # Top Left
                elif turn_vectors == {self.UP, self.RIGHT}:
                    image_to_draw = graphics[corner_set][1]  # Top Right
                elif turn_vectors == {self.DOWN, self.LEFT}:
                    image_to_draw = graphics[corner_set][2]  # Bottom Left
                elif turn_vectors == {self.DOWN, self.RIGHT}:
                    image_to_draw = graphics[corner_set][3]  # Bottom Right

                if image_to_draw:
                    screen.blit(
                        image_to_draw, image_to_draw.get_rect(center=center_pos)
                    )

    # --"See" Animation Request--
    def has_seen(self, food_pos):
        """Checks if the food is close to the snake's head and requests the "see" animation."""
        if (
            abs(self.body_grid[0][0] - food_pos[0])
            < constants.SnakeMovementConstants.FOOD_DETECTION_RANGE.value
            and abs(self.body_grid[0][1] - food_pos[1])
            < constants.SnakeMovementConstants.FOOD_DETECTION_RANGE.value
        ):
            self.wanted_animations.append(constants.SnakeAnimations.SNAKE_SEEN)

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
        if (
            new_direction[0] * -1,
            new_direction[1] * -1,
        ) == last_direction or new_direction == last_direction:
            return

        # Limit the move queue to buffer rapid inputs.
        if (
            len(self.move_queue)
            < constants.SnakeMovementConstants.MAX_MOVE_QUEUE_SIZE.value
        ):
            self.move_queue.append(new_direction)
