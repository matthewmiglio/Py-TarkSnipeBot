import PySimpleGUI as sg

from .theme import THEME

sg.theme(THEME)


def stat_box(stat_name: str, size=(5, 1)):
    return sg.Text(
        "0",
        key=stat_name,
        relief=sg.RELIEF_SUNKEN,
        text_color="blue",
        size=size,
    )


stats_title = [
    [
        [
            sg.Text("Program Restarts: "),
        ],
    ],
    [
        [
            sg.Text("Ruble Snipes"),
        ],
        [
            sg.Text("Specific Snipes"),
        ],
    ],
]


stats_values = [
    [
        [
            stat_box("restarts"),
        ],
    ],
    [
        [
            stat_box("ruble_snipes"),
        ],
        [
            stat_box("specific_snipes"),
        ],
    ],
]

stats = [
    [
        sg.Column(stats_title[0], element_justification="right"),
        sg.Column(stats_values[0], element_justification="left"),
        sg.Column(stats_title[1], element_justification="right"),
        sg.Column(stats_values[1], element_justification="left"),
    ]
]
