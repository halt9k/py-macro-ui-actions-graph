from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, final
import pyautogui
from pyrect import Rect

from code_tools.virtual_methods import override, virutalmethod
from helpers.gui_helpers import locate_image_on_screen

# it's rarely possible to execute user actions instantly after ech other
DEFAULT_DELAY_SECONDS = 0.0  # 0.2
DEFAULT_IMAGE_LOC_TIMEOUT = 0.0  # 3.0


class Action(ABC):
	def __init__(self,
	             start_delay: float = DEFAULT_DELAY_SECONDS,
	             attempts: int = 1,
	             attempts_timeout: float = 0,
	             block_parallel_run: bool = False,
	             is_extra_entry_node: bool = False):
		""" Args:
		attempts_timeout: In seconds. If two options with timeout fail, simultaneous attempts are started
		block_parallel_run: Not implemented yet """

		# TODO implement also parallel_block ?
		self.block_parallel_run = block_parallel_run
		self.is_extra_entry_node = is_extra_entry_node
		# TODO implement
		self.start_delay = start_delay
		self.attempts = attempts
		self.attempts_timeout = attempts_timeout

	@final
	def run(self):
		pyautogui.sleep(self.start_delay)
		self.on_run()

	@abstractmethod
	def on_run(self) -> bool:
		raise NotImplementedError()

	@virutalmethod
	def info(self, short: bool = False) -> Optional[str]:
		return None

	# TODO invent check if virtualmethod maring exists
	@virutalmethod
	def description_image_path(self) -> Optional[str]:
		return None

	def __repr__(self):
		return f"{self.__class__}  {self.__hash__()} {self.info(short=True)}"


class ImageClick(Action):
	""" Can be used to click on any icons or buttons which don't change picture """

	def __init__(self,
	             image_path: Path,
	             expected_region: Rect,
	             confidence=0.6,
	             attempts_timeout=DEFAULT_IMAGE_LOC_TIMEOUT,
	             attempts=5,
	             **kwargs):
		""" Args: confidence: required minimal threshold """

		super().__init__(attempts=attempts, attempts_timeout=attempts_timeout, **kwargs)
		self.image_path = image_path
		self.expected_region = expected_region
		self.req_confidence = confidence

	@override
	def info(self, short: bool = False) -> Optional[str]:
		if short:
			return self.image_path.name
		else:
			return str(self.image_path)

	@override
	def description_image_path(self):
		return str(self.image_path)

	@override
	def on_run(self):
		xy = locate_image_on_screen(self.image_path, self.expected_region, self.req_confidence)
		if xy:
			pyautogui.click(xy[0], xy[1])
			return True

		return False


class LocateImage(Action):
	def __init__(self, image_path: Path, expected_region: Rect, confidence=0.6, **kwargs):
		""" Args: confidence: required minimal threshold"""
		super().__init__(**kwargs)
		self.expected_region = expected_region
		self.image_path: Path = image_path
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

	@override
	def on_run(self):
		xy = locate_image_on_screen(self.image_path, self.expected_region, self.confidence)
		return xy is not None


class KeyPress(Action):
	def __init__(self, key: str, **kwargs):
		super().__init__(**kwargs)
		self.key = key

	@override
	def info(self, short: bool = False) -> Optional[str]:
		return self.key.capitalize()

	@override
	def on_run(self):
		pyautogui.press(self.key)
		return True


class MacroAbort(Exception):
	pass


class Exit(Action):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@override
	def info(self, short: bool = False) -> Optional[str]:
		return "Exit"

	@override
	def on_run(self):
		raise MacroAbort()


class Actions:
	ImageClick = ImageClick
	LocateImage = LocateImage
	KeyPress = KeyPress
	Exit = Exit
