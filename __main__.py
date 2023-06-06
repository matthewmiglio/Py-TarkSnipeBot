import random
import time
import webbrowser
from queue import Queue

import PySimpleGUI as sg
from bot.client import (
    buy_this_offer,
    get_to_flea_tab,
    orientate_launcher,
    reset_filters,
    search_for_item,
    set_flea_filters,
)
from states import state_tree
from utils.logger import Logger

from utils.caching import cache_user_settings, check_user_settings, read_user_settings
from utils.thread import StoppableThread, ThreadKilled

from interface.layout import disable_keys, main_layout, user_config_keys


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

    # if values["bitcoin_checkbox"]:
    #     jobs.append("Bitcoin")

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
    window = sg.Window("Py-TarkBot", main_layout)

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
            # show_help_gui()
            logger.log("help button event")

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


def dummy_main():
    from bot.client import orientate_tarkov_client
    from bot.client import click
    import pyautogui

    # orientate_tarkov_client()
    # orientate_launcher()
    # state = state_tree("restart", Logger(), [])
    # print(state)

    pass

    # buy_this_offer(logger)

    # logger = Logger()
    # logger.add_snipe()

    # # click purchase
    # click(1186, 152)
    # time.sleep(0.33)

    # # click all
    # click(773, 475)
    # time.sleep(0.33)

    # # press y to buy it
    # pyautogui.press("y")

    # logger.log("Bought an item")
    # logger.log(f"Bought {logger.snipes} items")

    # # sleep to avoid captcha
    # time.sleep(7)

    


# dummy_main()


if __name__ == "__main__":
    main()
