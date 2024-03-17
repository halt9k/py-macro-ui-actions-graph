from pathlib import Path
import pyautogui
import cv2
import numpy as np
from PIL.Image import Image
from mss import mss


# TODO expected_region
def locate_subimage_canter(img, subimage, confidence_threshold):
    matches = cv2.matchTemplate(img, subimage, cv2.TM_CCOEFF_NORMED)

    # loc = np.where(matches >= confidence_threshold)
    min_val, min_confidence, min_loc, pos_lt = cv2.minMaxLoc(matches)
    pos_center = pos_lt[0] + subimage.shape[1] / 2, pos_lt[1] + subimage.shape[0] / 2
    # TODO why so low
    # if min_confidence > confidence_threshold:
    if min_confidence > 0.6:
        return pos_center

    # Switch columns and rows
    # w, h = subimage.shape[:-1]
    # for pt in zip(*loc[::-1]):
    #    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    return None


def locate_subshape_center(img, subimage, confidence):
    img_edges = cv2.Canny(img, 0, 500)
    subimage_edges = cv2.Canny(subimage, 0, 500)

    if confidence > 0.6:
        print(f"Warning: high confidence {confidence} may not work for color independent edge matching")

    # debug
    # from matplotlib import pyplot as plt
    # plt.imshow(img_edges, interpolation='nearest')
    # plt.show()

    return locate_subimage_canter(img_edges, subimage_edges, confidence)


def locate_image_in_screen_region(image_path, expected_region, confidence):
    """ if expected_region is None than all screen"""
    image_path_str = str(image_path)
    try:
        with mss() as sct:
            img = np.array(sct.grab(sct.monitors[1]))

        if expected_region:
            l, t, w, h = expected_region
            region = img[t:t+h, l:l+w, :]
        else:
            region = img

        subimage = cv2.imread(image_path_str)

        xy = locate_subshape_center(region, subimage, confidence)
        if xy and expected_region:
            l, t, w, h = expected_region
            xy = xy[0] + l, xy[1] + t

        return xy
        # return pyautogui.locateCenterOnScreen(image_path_str, region=expected_region, confidence=confidence)
    # not found
    # TODO other exceptions ?
    except pyautogui.PyAutoGUIException:
        return None


def locate_image_on_screen(image_path: Path, hint_region=None, confidence=0.9):
    if not image_path.exists():
        print(f'Expected image is missing: {image_path}')
        return None

    xy = locate_image_in_screen_region(image_path, hint_region, confidence)

    if xy is None and hint_region:
        xy = locate_image_in_screen_region(image_path, None, confidence)
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
