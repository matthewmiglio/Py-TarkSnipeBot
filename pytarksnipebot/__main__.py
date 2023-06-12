import random
import time
import webbrowser
from queue import Queue

import PySimpleGUI as sg
from bot.client import check_for_search_results

from interface.layout import disable_keys, main_layout, user_config_keys
from states import state_tree
from utils.caching import (
    cache_user_settings,
    check_user_settings,
    read_user_settings,
)
from utils.logger import Logger
from utils.thread import StoppableThread, ThreadKilled


def save_current_settings(values):
    # read the currently selected values for each key in user_config_keys
    user_settings = {key: values[key] for key in user_config_keys if key in values}
    # cache the user settings
    cache_user_settings(user_settings)


def load_last_settings(window):
    if check_user_settings():
        window.read(timeout=10)  # read the window to edit the layout
        user_settings = read_user_settings()
        if user_settings is not None:
            for key in user_config_keys:
                if key in user_settings:
                    window[key].update(user_settings[key])
        window.refresh()  # refresh the window to update the layout


def shutdown_thread(thread: StoppableThread | None, kill=True):
    if thread is not None:
        thread.shutdown_flag.set()
        if kill:
            thread.kill()


def update_layout(window: sg.Window, logger: Logger):
    # comm_queue: Queue[dict[str, str | int]] = logger.queue
    window["time_since_start"].update(logger.calc_time_since_start())  # type: ignore
    # update the statistics in the gui

    if not logger.queue.empty():
        # read the statistics from the logger
        for stat, val in logger.queue.get().items():
            window[stat].update(val)  # type: ignore


def start_button_event(logger: Logger, window, values):
    # check for invalid inputs

    logger.log("Starting")

    for key in disable_keys:
        window[key].update(disabled=True)

    # unpack job list
    jobs = []

    # if rouble sniping toggle activated, add it to job list
    if values["ruble_sniping_toggle"]:
        jobs.append("ruble_sniping")
    else:
        jobs.append("null")

    # if item sniping toggle activated, add it to job list, unpack item list and add to job list
    if values["item_sniping_toggle"]:
        # add item sniping to job list
        jobs.append("item_sniping")

        # unpack item list
        item_names = [
            values["item_name_1"],
            values["item_name_2"],
            values["item_name_3"],
        ]

        prices = [
            values["item_price_1"],
            values["item_price_2"],
            values["item_price_3"],
        ]

        data_list = []

        for index in range(len(item_names)):
            this_name = item_names[index]
            this_price = prices[index]

            # skip null params
            if (
                this_name == ""
                or this_price == ""
                or this_name is None
                or this_price is None
                or this_name == " "
                or this_price == " "
            ):
                continue

            this_datum = [this_name, this_price]
            data_list.append(this_datum)

        jobs.append(data_list)

    # setup thread and start it
    print("jobs: ", jobs)

    thread = WorkerThread(logger, jobs)
    thread.start()

    # enable the stop button after the thread is started
    window["Stop"].update(disabled=False)

    return thread


def stop_button_event(logger: Logger, window, thread):
    logger.log("Stopping")
    window["Stop"].update(disabled=True)
    shutdown_thread(thread, kill=True)  # send the shutdown flag to the thread


class WorkerThread(StoppableThread):
    def __init__(self, logger: Logger, args):
        super().__init__(args)
        self.logger = logger

    def run(self):
        try:
            jobs = self.args

            state = "restart"

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # CODE TO RUN
                state = state_tree(state, self.logger, jobs)

        except ThreadKilled:
            return

        except Exception as exc:  # pylint: disable=broad-except
            # catch exceptions and log to not crash the main thread
            self.logger.error(str(exc))


def main():
    # orientate_terminal()

    thread: WorkerThread | None = None
    comm_queue: Queue[dict[str, str | int]] = Queue()
    logger = Logger(comm_queue, timed=False)  # dont time the inital logger

    # window layout
    window = sg.Window("Py-Tark-Snipe-Bot v0.0.1", main_layout)

    load_last_settings(window)

    # start timer for autostart
    start_time = time.time()
    auto_start_time = 30  # seconds
    auto_started = False

    # run the gui
    while True:
        # get gui vars
        read = window.read(timeout=100)
        event, values = read or (None, None)

        # check if bot should be autostarted
        if (
            thread is None
            and values is not None
            and values["autostart"]
            and not auto_started
            and time.time() - start_time > auto_start_time
        ):
            auto_started = True
            event = "Start"

        if event in [sg.WIN_CLOSED, "Exit"]:
            # shut down the thread if it is still running
            shutdown_thread(thread)
            break

        if event == "Start":
            if values is None:
                return

            # if NO JOBS
            if False:  # CONDITIONS TO CHECK FOR NO JOBS
                logger.log("There are no jobs!")

            # if job list is good, start the worker thread
            else:
                save_current_settings(values)

                # start the bot with new queue and logger
                comm_queue = Queue()
                logger = Logger(comm_queue)
                thread = start_button_event(logger, window, values)

        elif event == "Stop":
            stop_button_event(logger, window, thread)

        elif event == "Help":
            show_help_gui()
            # logger.log("help button event")

        elif event == "issues-link":
            print("Issues event")
            webbrowser.open("https://github.com/matthewmiglio/Py-TarkSnipeBot/issues")

        elif event == "Donate":
            webbrowser.open(
                "https://www.paypal.com/donate/"
                + "?business=YE72ZEB3KWGVY"
                + "&no_recurring=0"
                + "&item_name=Support+my+projects%21"
                + "&currency_code=USD"
            )

        # handle when thread is finished
        if thread is not None and not thread.is_alive():
            # enable the start button and configuration after the thread is stopped
            for key in disable_keys:
                window[key].update(disabled=False)
            if thread.logger.errored:
                window["Stop"].update(disabled=True)
            else:
                # reset the communication queue and logger
                comm_queue = Queue()
                logger = Logger(comm_queue, timed=False)
                thread = None

        update_layout(window, logger)

    shutdown_thread(thread, kill=True)

    window.close()


def show_help_gui():
    # Define the GUI layout
    layout = [
        [sg.Text("1. Launch the program on your computer.")],
        [sg.Text("2. Upon starting the program, you will see two modes:")],
        [sg.Text('"Ruble Sniping Mode" and "Specific Item Sniping Mode."')],
        [
            sg.Text(
                "3. Both modes can be selected, and the program will automatically switch between them."
            )
        ],
        [
            sg.Text(
                '4. If you choose the "Ruble Sniping Mode," the program will run without requiring any user input.'
            )
        ],
        [
            sg.Text(
                '5. If you prefer to use the "Specific Item Sniping Mode," the program will prompt you to enter a maximum price for the items you want to buy.'
            )
        ],
        [
            sg.Text(
                "6. Once you have entered the maximum price for specific item sniping, the program will start scanning the available items and identify those that are below the specified price."
            )
        ],
        [
            sg.Text(
                "7. The program will display a list of items that meet your criteria, including their prices and other relevant information."
            )
        ],
        [
            sg.Text(
                '8. The program will automatically analyze the available options and purchase the cheap items for you in the "Ruble Sniping Mode." It will use a strategic approach to maximize your passive profit.'
            )
        ],
        [
            sg.Text(
                '9. In the "Specific Item Sniping Mode," you have the flexibility to manually select the item(s) you wish to purchase from the displayed list.'
            )
        ],
        [
            sg.Text(
                "10. The program will continue running until you manually exit or until it strategically switches between modes based on the opportunities it identifies."
            )
        ],
        [
            sg.Text(
                '11. To exit the program, click on the "Exit" button or close the program window.'
            )
        ],
        [sg.Button("OK")],
    ]

    # Create the window
    window = sg.Window("Py-Tark-Hideout-Bot Help", layout)

    # Event loop
    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED or event == "OK":
            break

    # Close the window

    window.close()


def dummy_main():
    import pyautogui
    from bot.client import click, orientate_tarkov_client

    # orientate_tarkov_client()
    # orientate_launcher()
    # state = state_tree("restart", Logger(), [])
    # print(state)

    while 1:
        print(check_for_search_results())

    pass


# dummy_main()


if __name__ == "__main__":
    main()
