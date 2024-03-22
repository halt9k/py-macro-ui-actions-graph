from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from typing import Optional, final
import pyautogui
from pyrect import Rect

from code_tools.virtual_methods import override, virutalmethod
from helpers.gui import locate_image_on_screen, CONFIDENCE_DEFAULT_THRESHOLD

# it's rarely possible to execute user actions instantly after ech other
DEFAULT_DELAY_SECONDS = 0.1  # 0.2
DEFAULT_IMAGE_LOC_INTERVAL = 0.5  # 3.0


@dataclass(init=True)
class ActionSheduleInfo:
	""" Time in seconds. If two options with timeout fail, simultaneous attempts are started """

	block_parallel_run: bool = False
	is_extra_entry_node: bool = False
	start_delay: float = DEFAULT_DELAY_SECONDS
	max_attempts: int = 1
	attempts_interval: float = 0
	done_attempts: int = 0
	start_time: time = None


@dataclass(init=True)
class Action(ABC, ActionSheduleInfo):

	@final
	def run(self):
		# __before_run__() # Not used yet
		return self.__on_run__()
		# __after_run__() # Not used yet

	@abstractmethod
	def __on_run__(self) -> bool:
		raise NotImplementedError()

	@virutalmethod
	def info(self, short: bool = False) -> Optional[str]:
		return None

	@virutalmethod
	def description_image_path(self) -> Optional[str]:
		return None

	def __repr__(self):
		return f"{self.__class__}  {self.__hash__()} {self.info(short=True)}"

	def __hash__(self):
		# All actions are different
		# TODO test
		return id(self)


class ImageRelatedAction(Action, ABC):
	def __init__(self,
				 image_path: Path,
				 expected_region: Optional[Rect],
				 confidence: float = CONFIDENCE_DEFAULT_THRESHOLD,
				 attempts_interval: float = DEFAULT_IMAGE_LOC_INTERVAL,
				 max_attempts: int = 5,
				 *args, **kwargs):
		""" Args: confidence: required threshold """

		super().__init__(attempts_interval=attempts_interval, max_attempts=max_attempts, *args, **kwargs)
		self.image_path = image_path
		self.expected_region = expected_region
		self.confidence = confidence

	@override
	def info(self, short: bool = False) -> Optional[str]:
		if short:
			return self.image_path.name
		else:
			return str(self.image_path)

	@override
	def description_image_path(self):
		return str(self.image_path)


class ImageClick(ImageRelatedAction):
	""" Can be used to click on any icons or buttons which don't change picture """

	@override
	def __on_run__(self):
		xy = locate_image_on_screen(self.image_path, self.expected_region, self.confidence)
		if xy:
			pyautogui.click(xy[0], xy[1])
			return True

		return False


class LocateImage(ImageRelatedAction):
	@override
	def __on_run__(self):
		xy = locate_image_on_screen(self.image_path, self.expected_region, self.confidence)
		return xy is not None


class KeyPress(Action):
	def __init__(self,
				 key: str,
				 *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.key = key

	@override
	def info(self, short: bool = False) -> Optional[str]:
		return self.key.capitalize()

	@override
	def __on_run__(self):
		pyautogui.press(self.key)
		return True


class MacroAbort(Exception):
	pass


class Exit(Action):
	@override
	def info(self, short: bool = False) -> Optional[str]:
		return "Exit"

	@override
	def __on_run__(self):
		raise MacroAbort()


class Actions:
	ImageClick = ImageClick
	LocateImage = LocateImage
	KeyPress = KeyPress
	Exit = Exit
