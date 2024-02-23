from pathlib import Path

import pyautogui


def try_locate(image_path, hint_region, confidence):
    image_path_str = str(image_path)
    try:
        return pyautogui.locateCenterOnScreen(image_path_str, region=hint_region, confidence=confidence)
    # not found
    except pyautogui.PyAutoGUIException:
        return None


def locate_image_on_screen(image_path: Path, hint_region=None, confidence=0.9):
    if not image_path.exists():
        print(f'Expected image is missing: {image_path}')
        return None

    xy = try_locate(image_path, hint_region, confidence)

    if xy is None and hint_region:
        xy = try_locate(image_path, None, confidence)
        if xy:
            print(f'{image_path} found at {xy} outside of ecpected region')

    return xy
