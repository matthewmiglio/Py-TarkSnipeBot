import time
import webbrowser
from queue import Queue

import PySimpleGUI as sg
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
    if values["bitcoin_checkbox"]:
        jobs.append("Bitcoin")

    if values["lavatory_checkbox"]:
        jobs.append("Lavatory")

    if values["medstation_checkbox"]:
        jobs.append("medstation")

    if values["water_checkbox"]:
        jobs.append("water")

    if values["workbench_checkbox"]:
        jobs.append("Workbench")

    if values["scav_case_checkbox"]:
        jobs.append("scav_case")
        jobs.append(values["scav_case_type"])

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

            state = "start"

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # CODE TO RUN
                pass

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
                print("There are no jobs!")

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
            print("help button event")

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
    # from hideoutbot.bot.client import orientate_tarkov_client

    # orientate_tarkov_client()

    pass


# dummy_main()

if __name__ == "__main__":
    main()
