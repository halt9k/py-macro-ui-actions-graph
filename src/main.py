from copy import copy
from pathlib import Path

from pyrect import Rect

from helpers import os  # noqa: F401
from macro_actions import Actions
from macro_walk import Macro
from plot_workflow import draw_macro_result

# used to improve perfomance, but is alllowed to be incorrect
EXPECTED_BAR_REGION = Rect(1200, 0, 800, 100)
EXPECTED_MENU_REGION = Rect(1000, 0, 480, 600)


class UserMacroHoxx:
    description = "Trying to reactivate Hoxx VPN"

    DMY = Actions.Dummy("Start")

    P_S = Path('./reference_screen_images/setup_vpn')
    SC = Actions.LocateImage(P_S / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, block_parallel_run=True)

    P_H = Path('./reference_screen_images/hoxx_vpn')
    ID = Actions.ImageClick(P_H / 'bar_icon_disabled.png', EXPECTED_BAR_REGION)
    TE = Actions.ImageClick(P_H / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION)
    T1 = Actions.ImageClick(P_H / 'try_again.png', EXPECTED_MENU_REGION)
    # example of dupe noes and layout improvement
    T2 = copy(T1)
    R = Actions.ImageClick(P_H / 'reconnect_button.png', EXPECTED_MENU_REGION)
    UK = Actions.ImageClick(P_H / 'uk_button.png', EXPECTED_MENU_REGION)
    FL = Actions.ImageClick(P_H / 'failed_to_connect.png', EXPECTED_MENU_REGION)
    F = Actions.ImageClick(P_H / 'continue_as_free.png', EXPECTED_MENU_REGION)
    ESC = Actions.KeyPress('esc')
    EXIT = Actions.Exit()

    # Duplicates are ok for readability
    # @formatter:off
    actions_graph = [(DMY, SC), (DMY, ID), (DMY, TE), (DMY, UK),
                     (SC, EXIT),
                     (ID, UK), (UK, ESC),
                     (TE, R),
                     (ID, R), (R, UK),
                     (ID, F), (F, UK), (UK, ESC),
                     (ID, T2), (T2, UK),
                     (TE, T2),
                     (UK, ESC),
                     (UK, FL), (FL, T1), (T1, UK)]
    # @formatter:on

    macro = Macro(description, actions_graph)


class UserMacroSetup:
    description = "Trying to reactivate Setup VPN"

    DMY = Actions.Dummy("Start")

    P_H = Path('./reference_screen_images/hoxx_vpn')
    HC = Actions.LocateImage(P_H / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, block_parallel_run=True)

    P_S = Path('./reference_screen_images/setup_vpn')
    ID = Actions.ImageClick(P_S / 'bar_icon_disabled.png', EXPECTED_BAR_REGION)
    B = Actions.ImageClick(P_S / 'back_to_server_list_button.png', EXPECTED_BAR_REGION)
    U = Actions.ImageClick(P_S / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, confidence=0.7)
    T = Actions.ImageClick(P_S / 'try_again.png', EXPECTED_MENU_REGION)
    C = Actions.ImageClick(P_S / 'canada_button.png', EXPECTED_MENU_REGION)
    ESC = Actions.KeyPress(key='esc')
    EXIT = Actions.Exit()

    # Duplicates are ok for readability
    # @formatter:off
    actions_graph = [(DMY, HC), (DMY, ID), (DMY, U),
                     (HC, EXIT),
                     (ID, C), (C, ESC),
                     (ID, B), (B, C),
                     (ID, T),
                     (U, T), (T, C), (C, ESC)]
    # @formatter:on

    macro = Macro(description, actions_graph)


if __name__ == '__main__':
    print("Please remember not to abuse usage of this script demo templates. \n")

    UserMacroSetup.macro.run_macro()
    UserMacroHoxx.macro.run_macro()

    draw_macro_result(UserMacroSetup.macro)
    draw_macro_result(UserMacroHoxx.macro)
