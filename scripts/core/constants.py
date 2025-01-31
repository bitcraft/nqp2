from __future__ import annotations

from enum import auto, Enum, IntEnum
from pathlib import Path

VERSION: str = "0.0.1"

INFINITE: int = 999

# paths
ROOT_PATH = Path(__file__).parent.parent.parent  # constants.py is 2 directories deep
DATA_PATH = ROOT_PATH / "data/"
ASSET_PATH = ROOT_PATH / "assets/"
SAVE_PATH = DATA_PATH / "saves/"
DEBUGGING_PATH = ROOT_PATH / ".debug"
LOGGING_PATH = DEBUGGING_PATH / "logging"
PROFILING_PATH = DEBUGGING_PATH / "profiling"

# sizes
DEFAULT_IMAGE_SIZE = 16
GAP_SIZE = 10

# algorithm/formula constants
WEIGHT_SCALE = 5
DEFENSE_SCALE = 10
PUSH_FORCE = 14

# other
DAYS_UNTIL_BOSS = 30

# UI customisation
TEXT_FADE_OUT_SPEED = 0.5  # N.B. make sure it is slower than the fade in
TEXT_FADE_IN_SPEED = 2


# states
class GameState(IntEnum):
    PLAYING = auto()
    EXITING = auto()


class CombatState(IntEnum):
    UNIT_CHOOSE_CARD = auto()
    UNIT_SELECT_TARGET = auto()
    ACTION_CHOOSE_CARD = auto()
    ACTION_SELECT_TARGET_FREE = auto()
    WATCH = auto()


class OverworldState(IntEnum):
    LOADING = auto()
    READY = auto()
    TRAVELLING = auto()
    BOSS_APPROACHING = auto()


class TrainingState(IntEnum):
    CHOOSE_UPGRADE = auto()
    CHOOSE_TARGET_UNIT = auto()


class PostCombatState(IntEnum):
    DEFEAT = auto()
    VICTORY = auto()
    BOSS_VICTORY = auto()


class EventState(IntEnum):
    MAKE_DECISION = auto()
    RESULT = auto()


class NodeType(IntEnum):
    COMBAT = auto()
    EVENT = auto()
    INN = auto()
    TRAINING = auto()
    BLANK = auto()
    BOSS_COMBAT = auto()


class SceneType(IntEnum):
    COMBAT = auto()
    BOSS_COMBAT = auto()
    POST_COMBAT = auto()
    EVENT = auto()
    INN = auto()
    TRAINING = auto()
    OVERWORLD = auto()
    MAIN_MENU = auto()
    VIEW_TROUPE = auto()
    RUN_SETUP = auto()
    DEV_DATA_EDITOR = auto()
    DEV_GALLERY = auto()


class RewardType(IntEnum):
    UNIT = auto()
    ACTION = auto()
    UPGRADE = auto()
    RESOURCE = auto()


class StatModifiedStatus(IntEnum):
    NONE = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    POSITIVE_AND_NEGATIVE = auto()


class Direction(IntEnum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class FontType(Enum):
    DEFAULT = auto()
    NEGATIVE = auto()
    DISABLED = auto()
    POSITIVE = auto()
    INSTRUCTION = auto()
    NOTIFICATION = auto()


class FontEffects(IntEnum):
    FADE_IN = auto()
    FADE_OUT = auto()
