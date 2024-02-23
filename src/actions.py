from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pyautogui

from helpers.gui_helpers import locate_image_on_screen


class Action(ABC):
    parallel_run: bool = False
    extra_entry_node: bool = False

    def __init__(self, parallel_run: bool = False, extra_entry_node: bool = False):
        self.parallel_run = parallel_run
        self.extra_entry_node = extra_entry_node

    @abstractmethod
    def run(self) -> bool:
        raise NotImplementedError()

    def description_text(self) -> Optional[str]:
        return None

    def description_image_path(self) -> Optional[str]:
        return None


class ImageClickAction(Action):
    def __init__(self, image_path: Path, expected_region, confidence=0.8, timeout=0.2, **kwargs):
        super().__init__(**kwargs)
        self.expected_region = expected_region
        self.image_path: Path = image_path
        self.confidence = confidence
        self.timeout = timeout

    def __repr__(self):
        return f'Action {self.__hash__()} {str(self.image_path.name)}'

    def description_image_path(self):
        return str(self.image_path)

    def run(self):
        delay = 0.1
        attempts = self.timeout // delay
        for _ in range(int(attempts)):
            xy = locate_image_on_screen(self.image_path, hint_region=self.expected_region, confidence=self.confidence)
            if xy:
                pyautogui.click(xy.x, xy.y)
                return True

            pyautogui.sleep(delay)
            continue

        return False


class KeyPressAction(Action):
    def __init__(self, key: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key

    def __repr__(self):
        return 'Action ' + self.key

    def description_text(self) -> Optional[str]:
        return self.key.capitalize()

    def run(self):
        pyautogui.press(self.key)
        return True
