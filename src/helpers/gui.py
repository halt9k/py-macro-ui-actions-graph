from copy import copy
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from matplotlib import pyplot as plt
from mss import mss

# confidence threshold
# when trying to find, for example, light image on dark theme
# it's much lower than when light image on light theme with 1.0 perfect match
from pyrect import Rect

CONFIDENCE_DEFAULT_THRESHOLD = 0.65
# give warning if above, but not enough to be sure
CONFIDENCE_WARNING_THRESHOLD = 0.45


def debug_show_images(imgs: [np.array]):
	assert len(imgs) < 10

	for img in imgs:
		plt.figure()
		if len(img.shape) == 2:
			plt.imshow(img, cmap='gray')
		else:
			plt.imshow(img)
	plt.show()


# TODO finish later color and scale invariant icon detection
'''
def debug_draw(matches, img, img_keypoints, sub_img, sub_keypoints):
	good_matches = []
	for m, n in matches:
		if m.distance < 0.7 * n.distance:
			good_matches.append(m)

	flags = cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS | cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS
	matched_img = cv2.drawMatches(sub_img, sub_keypoints, img, img_keypoints, good_matches, None, flags=flags)

	scale = 2
	scaled_sh = matched_img.shape[1] * scale, matched_img.shape[0] * scale,
	matched_img_scaled = cv2.resize(matched_img, scaled_sh, interpolation=cv2.INTER_NEAREST)
	cv2.imshow("Matches", matched_img_scaled)

	sub_keypoints = np.float32([sub_img[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
	img_keypoints = np.float32([img[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

	H, mask = cv2.findHomography(sub_keypoints, img_keypoints, cv2.RANSAC, 5.0)

	h, w = sub_img.shape
	corners = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
	transformed_corners = cv2.perspectiveTransform(corners, H)

	larger_image_with_box = cv2.polylines(img.copy(), [np.int32(transformed_corners)], True, 255, 3, cv2.LINE_AA)
	cv2.imshow("Sub-image found", larger_image_with_box)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def locate_subimage_canter_surf(img, sub_img, req_confidence):
	""" Locate even is up/downscaled (but not rotated) """

	# orb = cv2.ORB_create()
	# patchSize is size of detection area around key point
	orb = cv2.ORB_create(fastThreshold=6, edgeThreshold=6, patchSize=6)

	img_keypoints, img_desc = orb.detectAndCompute(img, None)
	sub_keypoints, sub_desc = orb.detectAndCompute(sub_img, None)

	img_desc = img_desc.astype(np.float32)
	sub_desc = sub_desc.astype(np.float32)

	flann_index_kdtree = 1
	index_params = dict(algorithm=flann_index_kdtree, trees=5)
	search_params = dict(checks=5)
	flann = cv2.FlannBasedMatcher(index_params, search_params)

	matches = flann.knnMatch(sub_desc, img_desc, k=2)

	debug_draw(matches, img, img_keypoints, sub_img, sub_keypoints)

	matches = sorted(matches, key=lambda x: x.distance)
	sub_img_loc = sub_keypoints[matches[0].trainIdx].pt

	# loc = np.where(matches >= confidence_threshold)
	min_val, min_confidence, min_loc, pos_lt = cv2.minMaxLoc(matches)
	pos_center = pos_lt[0] + sub_img.shape[1] / 2, pos_lt[1] + sub_img.shape[0] / 2

	if min_confidence > req_confidence:
		return pos_center, min_confidence
	else:
		return None, min_confidence
'''


def find_best_match_cv(img: np.array, query: np.array, req_confidence):
	""" Locate exaclty same image without scaling """
	
	matches = cv2.matchTemplate(img, query, cv2.TM_CCOEFF_NORMED)

	# loc = np.where(matches >= confidence_threshold)
	min_conf, max_conf, min_pt, max_pt = cv2.minMaxLoc(matches)
	pos_center = max_pt[0] + query.shape[1] / 2, max_pt[1] + query.shape[0] / 2

	if max_conf > req_confidence + 0.2:
		return pos_center, max_conf
	else:
		return None, max_conf


def is_same_image_type(img1, img2):
	return len(img1.shape) == len(img2.shape) and img1.shape[-1] == img2.shape[-1]


def find_confident_match(img, query, req_confidence):
	assert is_same_image_type(img, query)

	# if req_confidence > CONFIDENCE_DEFAULT_THRESHOLD:
	#  	print(f"Warning: high confidence {req_confidence} may not work for color independent (edge) matching")

	# return locate_subimage_canter_surf(img_nb, query_nb, req_confidence)
	xy, res_confidence = find_best_match_cv(img, query, req_confidence)

	if req_confidence == CONFIDENCE_DEFAULT_THRESHOLD:
		if not xy and res_confidence > CONFIDENCE_WARNING_THRESHOLD:
			print(f"Confidence is in questonable zone: req {req_confidence} got {res_confidence}")

	return xy


def screenshot(expected_region: Rect = None):
	er = expected_region

	with mss() as screen:
		monitor = screen.monitors[1]
		if er:
			grab = screen.grab((er.left, er.top, er.right, er.bottom))
		else:
			grab = screen.grab(monitor)
	return np.array(grab)[:, :, :3]


def get_edge_colors(img: np.array):
	return np.unique([img[1, 1], img[1, -1], img[-1, -1], img[-1, 1]], axis=0)


def replace_background_colors(image, remove_colors, threshold=4, replace_with=np.array([255, 255, 255])):
	assert image.ndim == 3 and image.shape[-1] == 3
	mask = np.zeros_like(False, shape=image.shape[:2], dtype=bool)

	for col in remove_colors:
		mask = mask | (np.sum(np.abs(image - col), axis=2) < threshold)

	result = copy(image)
	result[mask] = replace_with
	return result


def find_best_onscreen_match_in_region(query_img, req_confidence, hint_region=None):
	""" Skip hint_region to do slower search all screen """

	img = screenshot(hint_region)

	# img_edges = cv2.Canny(img, 8, 8)
	# subimage_edges = cv2.Canny(subimage, 8, 8)

	img_nb = replace_background_colors(img, get_edge_colors(img))
	query_nb = replace_background_colors(query_img, get_edge_colors(query_img))

	xy = find_confident_match(img_nb, query_nb, req_confidence)
	if xy and hint_region:
		xy = xy[0] + hint_region.x, xy[1] + hint_region.y
	return xy


def optimized_find_best_onscreen_match(query_img_path: Path, hint_region=None, req_confidence=CONFIDENCE_DEFAULT_THRESHOLD):
	if not query_img_path.exists():
		print(f'Expected image is missing: {query_img_path}')
		return None

	query = cv2.imread(str(query_img_path))

	xy = find_best_onscreen_match_in_region(query, req_confidence, hint_region)
	if not xy:
		xy = find_best_onscreen_match_in_region(query, req_confidence, None)
		if xy:
			print(f'{query_img_path} found at {xy} outside of ecpected region')

	return xy


def opencv_ensure_installed():
	import cv2
	# reminder if fails to do BOTH:
	# 1) conda -> opencv
	# 2) pip install opencv-python
	print(f"OpenCV is detected: {cv2.__version__}")


opencv_ensure_installed()
