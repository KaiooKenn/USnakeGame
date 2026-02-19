import pygame as pg
import constants


class ANIMATION_HANDLER:

    # --Animation Handler Initialization--
    def __init__(self, game_class_frame_count):
        self.animation_frames = []  # The list of images for the current animation.
        self.current_frame = 0  # The index of the current frame in the list.
        self.current_bulge_frame = (
            0  # The index of the current bulge frame in the list.
        )
        self.frame_counter = 0  # A counter to control animation speed.
        self.game_class_frame_count = game_class_frame_count
        self.animation_speed = (
            constants.AnimationConstants.ANIMATION_SPEED.value  # Number of game frames to wait before showing the next animation frame.
        )
        self.active_animation = None  # The name of the animation currently playing.

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
        one_shot_animations = {
            constants.SnakeAnimations.SNAKE_EAT,
            constants.SnakeAnimations.SNAKE_XX,
        }  # Animations that should reset if triggered again.

        # 2. Find the highest-priority animation requested in the current frame.
        highest_prio_wanted = None
        highest_prio_level = -1
        for anim_name in wanted_animations:
            if isinstance(anim_name, constants.SnakeAnimations):
                level = anim_name.value
                if level > highest_prio_level:
                    highest_prio_level = level
                    highest_prio_wanted = anim_name

        if not highest_prio_wanted:
            return

        # 3. Get the priority of the currently playing animation.
        current_prio_level = -1
        if self.active_animation is not None and isinstance(
            self.active_animation, constants.SnakeAnimations
        ):
            current_prio_level = self.active_animation.value

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
    def update(self, game_class_frame_count, len_b_frames, FRAMES_PER_MOVE):
        """Advances the animation to the next frame if enough time has passed."""
        if not self.animation_frames:
            return

        self.game_class_frame_count = game_class_frame_count
        self.frame_counter += 1

        if self.frame_counter >= self.animation_speed:
            self.current_frame += 1
            # If the animation is over (reaches the end or a "finish" tag), clear the state.
            if (
                self.current_frame >= len(self.animation_frames)
                or self.animation_frames[self.current_frame] == "finish"
            ):
                self.animation_frames = []
                self.active_animation = None
            self.frame_counter = 0

        index_slicer = FRAMES_PER_MOVE / len_b_frames
        self.current_bulge_frame = int(self.game_class_frame_count // index_slicer)

    # --Get Current Animation Image--
    def get_image(self):
        """Returns the pygame.Surface for the current animation frame, or None."""
        if self.animation_frames:
            image = self.animation_frames[self.current_frame]
            if isinstance(image, pg.Surface):
                return image
        return None

    def get_bulge_image(self, bulge_body: list[pg.Surface]):
        """Returns the pygame.Surface for the current bulge frame, or None."""
        if self.animation_frames:
            image = bulge_body[self.current_bulge_frame]
            if isinstance(image, pg.Surface):
                return image
        return None
