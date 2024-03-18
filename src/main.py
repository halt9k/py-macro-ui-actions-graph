from pathlib import Path
import networkx as nx

from helpers import ensure_paths  # noqa: F401
from actions import Actions
from macro_walk import try_walk_actions_graph, Macro
from plots_drawing import draw_macro_result


# used to improve perfomance, but is alllowed to be incorrect
# (left, top, width, height)
EXPECTED_BAR_REGION = (1200, 0, 800, 100)
EXPECTED_MENU_REGION = (1000, 0, 480, 600)


class MacroHoxxVPN(Macro):
    description = "Trying to reactivate Hoxx VPN"

    P_S = Path('./reference_screen_images/setup_vpn')
    SC = Actions.LocateImage(P_S / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, block_parallel_run=True)

    P_H = Path('./reference_screen_images/hoxx_vpn')
    D = Actions.ImageClick(P_H / 'bar_icon_disabled.png', EXPECTED_BAR_REGION)
    TE = Actions.ImageClick(P_H / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION)
    T1 = Actions.ImageClick(P_H / 'try_again.png', EXPECTED_MENU_REGION)
    # T2 = Actions.ImageClick(P_H / 'try_again.png', EXPECTED_MENU_REGION, timeout=2)
    R = Actions.ImageClick(P_H / 'reconnect_button.png', EXPECTED_MENU_REGION)
    UK = Actions.ImageClick(P_H / 'uk_button.png', EXPECTED_MENU_REGION)
    FL = Actions.ImageClick(P_H / 'failed_to_connect.png', EXPECTED_MENU_REGION)
    F = Actions.ImageClick(P_H / 'continue_as_free.png', EXPECTED_MENU_REGION)
    ESC = Actions.KeyPress('esc')
    EXIT = Actions.Exit()

    # Duplicates are ok for readability
    actions_graph = nx.DiGraph([(SC, EXIT),
                                (D, UK), (UK, ESC),
                                (TE, R),
                                (D, R), (R, UK),
                                (D, F), (F, UK), (UK, ESC),
                                (D, T1),
                                (TE, T1), (T1, UK), (UK, ESC),
                                (UK, FL), (FL, T1)])


class MacroSetupVPN(Macro):
    description = "Trying to reactivate Setup VPN"

    P_H = Path('./reference_screen_images/hoxx_vpn')
    HC = Actions.LocateImage(P_H / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, block_parallel_run=True)

    P_S = Path('./reference_screen_images/setup_vpn')
    D = Actions.ImageClick(P_S / 'bar_icon_disabled.png', EXPECTED_BAR_REGION)
    B = Actions.ImageClick(P_S / 'back_to_server_list_button.png', EXPECTED_BAR_REGION)
    U = Actions.ImageClick(P_S / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, confidence=0.6)
    T = Actions.ImageClick(P_S / 'try_again.png', EXPECTED_MENU_REGION)
    C = Actions.ImageClick(P_S / 'canada_button.png', EXPECTED_MENU_REGION)
    ESC = Actions.KeyPress('esc')
    EXIT = Actions.Exit()

    # Duplicates are ok for readability
    actions_graph = nx.DiGraph([(HC, EXIT),
                                (D, C), (C, ESC),
                                (D, B), (B, C),
                                (D, T),
                                (U, T), (T, C), (C, ESC)])


if __name__ == '__main__':
    print("Please remember not to abuse usage of this script demo templates. \n")
    try_walk_actions_graph(MacroSetupVPN)
    try_walk_actions_graph(MacroHoxxVPN)

    draw_macro_result(MacroSetupVPN)
    draw_macro_result(MacroHoxxVPN)

