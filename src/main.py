from pathlib import Path
import networkx as nx

from helpers import ensure_paths  # noqa: F401
from actions import ImageClickAction, KeyPressAction
from helpers.os_helpers import run_in_thread
from macro_walk import try_walk_actions_graph, Macro
from plots_drawing import draw_macro_result


# used to improve perfomance, but allowed to be incorrect
# (left, top, width, height)
EXPECTED_BAR_REGION = (1200, 0, 800, 100)
EXPECTED_MENU_REGION = (1000, 0, 480, 600)


class MacroHoxxVPN(Macro):
    description = "Trying to reactivate Hoxx VPN"
    BP = Path('./reference_screen_images/hoxx_vpn')

    D = ImageClickAction(BP / 'bar_icon_disabled.png', EXPECTED_BAR_REGION, parallel_run=True)
    U = ImageClickAction(BP / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, confidence=0.9, parallel_run=True)
    R = ImageClickAction(BP / 'try_again.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    T = ImageClickAction(BP / 'try_again.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    UK = ImageClickAction(BP / 'uk_button.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    FL = ImageClickAction(BP / 'failed_to_connect.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    F = ImageClickAction(BP / 'continue_as_free.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    E = KeyPressAction('esc')

    # Duplicates are ok for readability
    actions_graph = nx.DiGraph([(D, UK), (UK, E),
                                (D, T),
                                (D, F), (F, UK), (UK, E),
                                (U, R), (R, UK), (UK, E),
                                (UK, FL), (FL, R)])


class MacroSetupVPN(Macro):
    description = "Trying to reactivate Setup VPN"

    H_BP = Path('./reference_screen_images/hoxx_vpn')
    H_T = ImageClickAction(H_BP / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, timeout=1)
    H_R = ImageClickAction(H_BP / 'try_again.png', EXPECTED_MENU_REGION, timeout=1)

    BP = Path('./reference_screen_images/setup_vpn')
    D = ImageClickAction(BP / 'bar_icon_disabled.png', EXPECTED_BAR_REGION, parallel_run=True, extra_entry_node=True)
    B = ImageClickAction(BP / 'back_to_server_list_button.png', EXPECTED_BAR_REGION, timeout=3, parallel_run=True)
    U = ImageClickAction(BP / 'bar_icon_time_ended.png', EXPECTED_BAR_REGION, parallel_run=True)
    T = ImageClickAction(BP / 'try_again.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    C = ImageClickAction(BP / 'canada_button.png', EXPECTED_MENU_REGION, timeout=3, parallel_run=True)
    E = KeyPressAction('esc')

    # Duplicates are ok for readability
    actions_graph = nx.DiGraph([(H_T, H_R), (H_R, D),
                                (D, C), (C, E),
                                (D, B), (B, C),
                                (D, T),
                                (U, T), (T, C), (C, E)])


if __name__ == '__main__':
    print("Please remember not to abuse usage of this script demo templates. \n")
    try_walk_actions_graph(MacroSetupVPN)
    # try_walk_actions_graph(MacroHoxxVPN)

    draw_macro_result(MacroSetupVPN)
    # draw_macro_result(MacroHoxxVPN)

