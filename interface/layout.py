import PySimpleGUI as sg

from .stats import stat_box, stats

info_text = """Py-Tark-Snipe-Bot strategically handles Tarkov Flea Market purchases to profit Rubles while you're AFK. 
Matthew Miglio, April 2023"""

instructions_text = """1. Tarkov MUST be set to windowed mode.
2. Program must be ran as administrator.

Ruble Sniping Mode:
-Buys underprices items from flea to sell to Therapist

Specific Item Sniping Mode:
-Buys a specific item from flea at a specific price
"""
# defining various things that r gonna be in the gui.
main_layout = [
    [
        sg.Frame(
            layout=[[sg.Text(info_text, size=(35, None))]],
            title="Info",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    # directions
    [
        sg.Frame(
            layout=[[sg.Text(instructions_text, size=(35, None))]],
            title="Directions",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    # job checkboxes
    [
        sg.Frame(
            layout=[
                [
                    sg.Text("'Ruble sniping (Therapist Vendor)'"),
                    sg.Checkbox("", key="ruble_sniping_toggle", default=True),
                ],
                [
                    sg.Text("'Specific item sniping'"),
                    sg.Checkbox("", key="item_sniping_toggle", default=True),
                ],
            ],
            title="Job List",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    # item sniping user input
    [
        sg.Frame(
            layout=[
                [
                    sg.Text("Name #1"),
                    sg.InputText("", key="item_name_1"),
                ],
                [
                    sg.Text("Price #1"),
                    sg.InputText("", key="item_price_1"),
                ],
            ],
            title="Item 1 Snipe Settings",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    [
        sg.Frame(
            layout=[
                [
                    sg.Text("Name #2"),
                    sg.InputText("", key="item_name_2"),
                ],
                [
                    sg.Text("Price #2"),
                    sg.InputText("", key="item_price_2"),
                ],
            ],
            title="Item 2 Snipe Settings",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    [
        sg.Frame(
            layout=[
                [
                    sg.Text("Name #3"),
                    sg.InputText("", key="item_name_3"),
                ],
                [
                    sg.Text("Price #3"),
                    sg.InputText("", key="item_price_3"),
                ],
            ],
            title="Item 3 Snipe Settings",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    # stats
    [
        sg.Frame(layout=stats, title="Stats", relief=sg.RELIEF_SUNKEN, expand_x=True),
    ],
    # buttons
    [
        sg.Frame(
            layout=[
                [
                    sg.Column(
                        [
                            [
                                sg.Button("Start"),
                                sg.Button("Stop", disabled=True),
                                sg.Checkbox(
                                    text="Auto-start",
                                    key="autostart",
                                    default=False,
                                    enable_events=True,
                                ),
                            ]
                        ],
                        element_justification="left",
                        expand_x=True,
                    ),
                    sg.Column(
                        [
                            [
                                sg.Button("Help"),
                                sg.Button("Issues?", key="issues-link"),
                                sg.Button("Donate"),
                            ]
                        ],
                        element_justification="right",
                        expand_x=True,
                    ),
                ],
            ],
            title="Controls",
            relief=sg.RELIEF_SUNKEN,
            expand_x=True,
        ),
    ],
    [
        stat_box("time_since_start", size=(7, 1)),
        sg.InputText(
            "Idle",
            key="message",
            use_readonly_for_disable=True,
            disabled=True,
            text_color="blue",
            expand_x=True,
        ),
    ],
    # https://www.paypal.com/donate/?business=YE72ZEB3KWGVY&no_recurring=0&item_name=Support+my+projects%21&currency_code=USD
]

# a list of all the keys that contain user configuration
# user_config_keys = ["rows_to_target", "remove_offers_timer", "autostart"]
user_config_keys = [
    # "rows_to_target",
    # "remove_offers_timer",
    "autostart",
    "ruble_sniping_toggle",
    "item_sniping_toggle",
    "item_name_1",
    "item_price_1",
    "item_name_2",
    "item_price_2",
    "item_name_3",
    "item_price_3",
]

# list of button and checkbox keys to disable when the bot is running
disable_keys = user_config_keys + ["Start"]
