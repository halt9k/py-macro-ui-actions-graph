from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, final

import pyautogui
from pyrect import Rect

from code_tools.virtual_methods import override, virutalmethod
from helpers.gui import optimized_find_best_onscreen_match, CONFIDENCE_DEFAULT_THRESHOLD

# it's rarely possible to execute user actions instantly after ech other
DEFAULT_DELAY_SECONDS = 0.1  # 0.2
DEFAULT_IMAGE_LOC_INTERVAL = 0.5  # 3.0


class Action(ABC):
    class DrawMode(Enum):
        TEXT, IMAGE = 1, 2

    def __init__(self,
                 draw_mode: DrawMode = DrawMode.TEXT,
                 extra_info: str = "",
                 *args, **kwargs):
        self.draw_mode = draw_mode
        self.extra_info = extra_info

    @final
    def run(self):
        # __before_run__() # Not used yet
        return self.__on_run__()
        # __after_run__() # Not used yet

    @abstractmethod
    def __on_run__(self) -> bool:
        raise NotImplementedError()

    @final
    def info(self, short: bool = False) -> Optional[str]:
        info = self.__on_info__(short) or ""
        return info + self.extra_info

    @virutalmethod
    def __on_info__(self, short: bool = False) -> Optional[str]:
        return None

    @virutalmethod
    def description_image_path(self) -> Optional[str]:
        return None

    def __repr__(self):
        # method just to improve debug
        return f"{self.__class__}  {self.__hash__()} {self.info(short=True)}"


@dataclass(init=True, eq=False, repr=False)
class ActionSheduleInfo(ABC):
    """ Time in seconds. If two options with timeout fail, simultaneous attempts are started """

    block_parallel_run: bool = False
    start_delay: float = DEFAULT_DELAY_SECONDS
    max_attempts: int = 1
    attempts_interval: float = 0


class ScheduledAction(Action, ActionSheduleInfo, ABC):
    pass


class ImageRelatedAction(ScheduledAction):
    def __init__(self,
                 image_path: Path,
                 expected_region: Optional[Rect],
                 confidence: float = CONFIDENCE_DEFAULT_THRESHOLD,
                 attempts_interval: float = DEFAULT_IMAGE_LOC_INTERVAL,
                 max_attempts: int = 5,
                 draw_mode=Action.DrawMode.IMAGE,
                 *args,
                 **kwargs):
        """ Args: confidence: required threshold """

        super().__init__(attempts_interval=attempts_interval, max_attempts=max_attempts, draw_mode=draw_mode, *args,
                         **kwargs)
        self.image_path = image_path
        self.expected_region = expected_region
        self.confidence = confidence

    @override
    def __on_info__(self, short: bool = False) -> Optional[str]:
        if short:
            return self.image_path.name
        else:
            return str(self.image_path)

    @override
    def description_image_path(self):
        return str(self.image_path)


class Dummy(ScheduledAction):
    """ Can be used, for example, to add more entry nodes """

    def __init__(self, info: str = ""):
        extra_info = info if info else "Dummy"
        super().__init__(start_delay=0, extra_info=extra_info)

    @override
    def __on_run__(self):
        return True


class ImageClick(ImageRelatedAction):
    """ Can be used to click on any icons or buttons which don't change picture """

    @override
    def __on_run__(self):
        xy = optimized_find_best_onscreen_match(self.image_path, self.expected_region, self.confidence)
        if xy:
            pyautogui.click(xy[0], xy[1])
            return True

        return False


class LocateImage(ImageRelatedAction):
    @override
    def __on_run__(self):
        xy = optimized_find_best_onscreen_match(self.image_path, self.expected_region, self.confidence)
        return xy is not None


class KeyPress(ScheduledAction):
    def __init__(self, key: str, *args, **kwargs):
        key_name = key.capitalize()
        super().__init__(extra_info=key_name, *args, **kwargs)
        self.key = key

    @override
    def __on_run__(self):
        pyautogui.press(self.key)
        return True


class MacroAbort(Exception):
    pass


class Exit(ScheduledAction):
    def __init__(self):
        super().__init__(start_delay=0, extra_info="Exit")

    @override
    def __on_run__(self):
        raise MacroAbort()


class Actions(SimpleNamespace):
    ImageClick = ImageClick
    LocateImage = LocateImage
    KeyPress = KeyPress
    Exit = Exit
    Dummy = Dummy
