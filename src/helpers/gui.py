from pathlib import Path

import cv2
import numpy as np
from mss import mss

# confidence threshold
# when trying to find, for example, light image on dark theme
# it's much lower than when light image on light theme with 1.0 perfect match
CONFIDENCE_DEFAULT_THRESHOLD = 0.65
# give warning if above, but not enough to be sure
CONFIDENCE_WARNING_THRESHOLD = 0.45


def locate_subimage_canter(img, subimage, req_confidence):
	matches = cv2.matchTemplate(img, subimage, cv2.TM_CCOEFF_NORMED)

	# loc = np.where(matches >= confidence_threshold)
	min_val, min_confidence, min_loc, pos_lt = cv2.minMaxLoc(matches)
	pos_center = pos_lt[0] + subimage.shape[1] / 2, pos_lt[1] + subimage.shape[0] / 2

	# Switch columns and rows
	# w, h = subimage.shape[:-1]
	# for pt in zip(*loc[::-1]):
	#    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

	if min_confidence > req_confidence:
		return pos_center, min_confidence
	else:
		return None, min_confidence


def locate_subshape_center(img, subimage, req_confidence):
	img_edges = cv2.Canny(img, 8, 8)
	subimage_edges = cv2.Canny(subimage, 8, 8)

	if req_confidence > CONFIDENCE_DEFAULT_THRESHOLD:
		print(f"Warning: high confidence {req_confidence} may not work for color independent (edge) matching")

	# debug
	# from matplotlib import pyplot as plt
	# plt.imshow(img_edges, interpolation='nearest')
	# plt.show()

	return locate_subimage_canter(img_edges, subimage_edges, req_confidence)


def locate_image_in_screen_region(image_path: Path, expected_region, req_confidence):
	""" expected_region: if None than search all screen"""

	with mss() as screen:
		screenshot = np.array(screen.grab(screen.monitors[1]))

	if expected_region:
		er = expected_region
		img = screenshot[er.top:er.bottom, er.left:er.right, :]
	else:
		img = screenshot

	subimage = cv2.imread(str(image_path))

	xy, res_confidence = locate_subshape_center(img, subimage, req_confidence)
	if xy and expected_region:
		xy = xy[0] + expected_region.x, xy[1] + expected_region.y

	if req_confidence == CONFIDENCE_DEFAULT_THRESHOLD:
		if not xy and res_confidence > CONFIDENCE_WARNING_THRESHOLD:
			print(f"Confidence in questonable zone: req {req_confidence} got {res_confidence}")

	return xy


def locate_image_on_screen(image_path: Path, hint_region=None, req_confidence=CONFIDENCE_DEFAULT_THRESHOLD):
	if not image_path.exists():
		print(f'Expected image is missing: {image_path}')
		return None

	xy = locate_image_in_screen_region(image_path, hint_region, req_confidence)

	if xy is None and hint_region:
		xy = locate_image_in_screen_region(image_path, None, req_confidence)
		if xy:
			print(f'{image_path} found at {xy} outside of ecpected region')

	return xy


def opencv_ensure_installed():
	import cv2
	# reminder if fails to do BOTH:
	# 1) conda -> opencv
	# 2) pip install opencv-python
	print(f"OpenCV is detected: {cv2.__version__}")


opencv_ensure_installed()
