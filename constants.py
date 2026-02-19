import enum
from dataclasses import dataclass
import pygame as pg

Info_Object = pg.display.Info()


class SizeConstants(enum.Enum):
    """Class to hold all size constants for easy access and modification."""

    SCREEN_SIZE = (Info_Object.current_h) * 4 // 5
    GRID_COUNT = 12
    GRID_SIZE = SCREEN_SIZE // GRID_COUNT
    HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2
    FONT_SIZE = 28


class SnakeAnimations(enum.Enum):
    """Class to hold all snake animation constants for easy access and modification."""

    SNAKE_BLINK = 0
    SNAKE_SEEN = 1
    SNAKE_EAT = 2
    SNAKE_XX = 3
    SNAKE_DEAD = 4


class SnakeBodyParts(enum.Enum):
    """Enumeration for snake body parts."""

    HEAD = enum.auto()
    UNDER_HEAD = enum.auto()
    BODY = enum.auto()
    TAIL = enum.auto()


class ColorConstants(enum.Enum):
    """Class to hold all color constants for easy access and modification."""

    SCORE_COLOR = (149, 197, 111)
    GRID_COLOR = (255, 255, 255)


class OtherConstants(enum.Enum):
    """Class to hold all other miscellaneous constants for easy access and modification."""

    FPS = 60
    FRAMES_PER_MOVE = 7

    SCORE = 0
    SCORE_POSITION = (10, 10)


class AnimationConstants(enum.Enum):
    """Class to hold all animation-related constants for easy access and modification."""

    ANIMATION_SPEED = (
        10  # Number of game frames to wait before showing the next animation frame
    )
    DEATH_ANIMATION_SPEED_MIN = 240  # Minimum speed for death animation
    DEATH_ANIMATION_SPEED_MAX = 300  # Maximum speed for death animation
    DEATH_SCREEN_DURATION = 1500  # Duration in milliseconds to show death screen
    DEATH_ANIMATION_DELAY = (
        100  # Milliseconds to wait after collision before triggering game over
    )


class SnakeMovementConstants(enum.Enum):
    """Class to hold all snake movement and animation constants."""

    MOVEMENT_SMOOTHING = 0.25  # Lerp interpolation factor for smooth animation
    BLINK_CHANCE = 5  # 1 in N chance to blink (randint(0, BLINK_CHANCE-1) == 0)
    FOOD_DETECTION_RANGE = 3  # How close food must be to trigger "see" animation
    MAX_MOVE_QUEUE_SIZE = 3  # Maximum number of buffered direction inputs
    BULGE_UPDATE_OFFSET = 2  # Offset for updating bulge animation indexes
    BULGE_ANIMATION_TRIGGER = 1  # Value appended when snake eats food


class RotationAngles(enum.Enum):
    """Class to hold rotation angles for snake sprite direction."""

    RIGHT = 270
    LEFT = 90
    DOWN = 180
    UP = 0  # No rotation needed for default sprite orientation


class CornerDirections(enum.Enum):
    """Class to hold corner direction identifiers for body corner sprites."""

    TOP_LEFT = "tl"
    TOP_RIGHT = "tr"
    BOTTOM_LEFT = "bl"
    BOTTOM_RIGHT = "br"


class AnimationFrameCounts(enum.Enum):
    """Class to hold the number of animation frames for each animation type."""

    BLINK_FRAMES = 2
    SEEN_FRAMES = 3
    EAT_FRAMES = 4
    DEAD_FRAMES = 2
    XX_FRAMES = 1
    BULGE_BODY_FRAMES = 3


class Direction(enum.Enum):
    """Enumeration for snake movement directions."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
