from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pyautogui
from typing_extensions import override

from helpers.gui_helpers import locate_image_on_screen


# TODO extract and any way to improve
def virutalmethod(self):
    """ Dummy decorator to highlight methods for optional overrides """
    pass


class Action(ABC):
    parallel_run: bool = False
    is_extra_entry_node: bool = False
    timeout: float = 0
    attempts: int = 1

    def __init__(self,
                 parallel_run: bool = False,
                 extra_entry_node: bool = False,
                 timeout: float = 0,
                 attempts: int = 1):
        self.parallel_run = parallel_run
        self.is_extra_entry_node = extra_entry_node
        self.timeout = timeout
        self.attempts = attempts

    @abstractmethod
    def run(self) -> bool:
        raise NotImplementedError()

    @virutalmethod
    def description_text(self, in_short: bool = False) -> Optional[str]:
        return None

    @virutalmethod
    def description_image_path(self) -> Optional[str]:
        return None

    def __repr__(self):
        return f"{self.__class__}  {self.__hash__()} {self.description_text()}"


class ImageClick(Action):
    """ Can be used to click on any icons or buttons which don't change picture """

    def __init__(self, image_path: Path, expected_region, confidence=0.6, timeout=0.2, attempts=5, **kwargs):
        super().__init__(timeout=timeout, attempts=attempts, **kwargs)
        self.expected_region = expected_region
        self.image_path: Path = image_path
        self.confidence = confidence

    @override
    def description_text(self, in_short: bool = False) -> Optional[str]:
        if in_short:
            return self.image_path.name
        else:
            return str(self.image_path)

    @override
    def description_image_path(self):
        return str(self.image_path)

    @override
    def run(self):
        xy = locate_image_on_screen(self.image_path, self.expected_region, self.confidence)
        if xy:
            pyautogui.click(xy[0], xy[1])
            return True

        return False


class LocateImage(Action):
    def __init__(self, image_path: Path, expected_region, confidence=0.6, timeout=0, attempts=1, **kwargs):
        super().__init__(**kwargs)
        self.expected_region = expected_region
        self.image_path: Path = image_path
        self.confidence = confidence
        self.timeout = timeout
        self.attempts = attempts

    @override
    def description_text(self, in_short: bool = False) -> Optional[str]:
        if in_short:
            return self.image_path.name
        else:
            return str(self.image_path)

    @override
    def description_image_path(self):
        return str(self.image_path)

    @override
    def run(self):
        xy = locate_image_on_screen(self.image_path, self.expected_region, self.confidence)
        return xy is not None


class KeyPress(Action):
    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key

    @override
    def description_text(self, in_short: bool = False) -> Optional[str]:
        return self.key.capitalize()

    @override
    def run(self):
        pyautogui.press(self.key)
        return True


class Exit(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @override
    def description_text(self, in_short: bool = False) -> Optional[str]:
        return "Exit"

    @override
    def run(self):
        exit()


class Actions:
    ImageClick = ImageClick
    LocateImage = LocateImage
    KeyPress = KeyPress
    Exit = Exit
