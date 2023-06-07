import subprocess
import sys
import time
import tkinter.messagebox
from os.path import abspath, join, pardir
from pathlib import Path
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryValueEx

import numpy
import pygetwindow

from bot.client import (
    click,
    close_launcher,
    close_tarkov_client,
    orientate_launcher,
    orientate_tarkov_client,
    screenshot,
)
from utils.image_rec import check_for_location, find_references, pixel_is_equal


def get_bsg_launcher_path() -> str:
    """get the path to the bsg launcher"""
    try:
        akey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{B0FDA062-7581-4D67-B085-C4E7C358037F}_is1"
        areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        akey = OpenKey(areg, akey)
    except FileNotFoundError:
        akey = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{B0FDA062-7581-4D67-B085-C4E7C358037F}_is1"
        areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        akey = OpenKey(areg, akey)
    launcher_file = abspath(
        join(QueryValueEx(akey, "InstallLocation")[0], "BsgLauncher.exe")
    )
    if not Path(launcher_file).exists():
        try:
            akey = (
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\EscapeFromTarkov"
            )
            areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            akey = OpenKey(areg, akey)
        except FileNotFoundError:
            akey = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\EscapeFromTarkov"
            areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            akey = OpenKey(areg, akey)
        launcher_file = abspath(
            join(
                QueryValueEx(akey, "InstallLocation")[0],
                pardir,
                "BsgLauncher",
                "BsgLauncher.exe",
            )
        )
    return launcher_file


def restart_tarkov(logger):
    # sourcery skip: extract-duplicate-method, extract-method

    # check if tarkov is open
    tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")
    tark_launcher = pygetwindow.getWindowsWithTitle("BsgLauncher")

    # if tark open
    if len(tark_window) != 0:
        logger.log("Tarkov client detected. Closing it.")
        close_tarkov_client(logger, tark_window)
        time.sleep(5)

    # if launcher open
    if len(tark_launcher) != 0:
        logger.log("Tarkov launcher detected. Closing it.")
        close_launcher(logger, tark_launcher)
        time.sleep(5)

    # open tark launcher
    logger.log("Opening launcher.")
    try:
        subprocess.Popen(get_bsg_launcher_path())  # pylint: disable=consider-using-with
    except FileNotFoundError:
        tkinter.messagebox.showinfo(
            "CRITICAL ERROR",
            "Could not start launcher. Open a bug report on github and share your BSGlauncher install path.",
        )
        sys.exit("Launcher path not found")

    # Wait for launcher to open and load up
    logger.log("Waiting for launcher to open.")
    index = 0
    has_window = False
    while not has_window:
        time.sleep(1)
        index += 1
        if len(pygetwindow.getWindowsWithTitle("BsgLauncher")) > 0:
            has_window = True
        if index > 25:
            logger.log("Launcher failed to open.")
            return restart_tarkov(logger)
    time.sleep(5)

    # orientate launcher
    logger.log("Orientating launcher")
    orientate_launcher()
    print("Done orientating launcher")
    time.sleep(3)

    # wait for launcher play button to appear
    logger.log("Waiting for launcher's play button")
    if wait_for_play_button_in_launcher(logger) == "restart":
        return restart_tarkov(logger)

    # click play
    logger.log("Clicking play.")
    click(942, 558)
    time.sleep(20)

    # wait for client opening
    logger.log("Waiting for tarkov client to open.")
    if wait_for_tarkov_to_open(logger) == "restart":
        return restart_tarkov(logger)
    for index in range(0, 30, 2):
        logger.log(f"Manually giving tark time to load: {index}")
        time.sleep(2)

    # orientate tark client
    orientate_tarkov_client()
    time.sleep(1)

    # wait for us to reach main menu
    logger.log("Waiting for tarkov client to reach main menu.")
    if wait_for_tark_main(logger) == "restart":
        return restart_tarkov(logger)
    orientate_tarkov_client()
    time.sleep(3)


def wait_for_tarkov_to_open(logger):
    tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")
    loops = 0
    logger.log("Waiting for tarkov to open. . .")
    while len(tark_window) == 0:
        loops = loops + 2
        time.sleep(2)
        tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")
        if loops > 50:
            logger.log("#8927592 Failure within restart state")
            return "restart"


def wait_for_tark_main(logger):
    on_main = check_if_on_tark_main()
    loops = 0
    logger.log("Waiting for tark main.")
    while not (on_main):
        loops = loops + 2
        time.sleep(2)
        on_main = check_if_on_tark_main()
        if loops > 120:
            logger.log("#87639485 Failure waiting for tark main within restart state")
            return "restart"


def check_if_on_tark_main():
    iar = numpy.asarray(screenshot())
    pix_list = []
    pix_list.append(iar[613][762])
    pix_list.append(iar[616][926])
    pix_list.append(iar[611][294])
    pix_list.append(iar[618][769])
    pix_list.append(iar[651][427])
    pix_list.append(iar[615][1010])
    pix_list.append(iar[648][290])

    for pix in pix_list:
        if not pixel_is_equal(pix, [175, 90, 50], tol=100):
            return False
    return True


def check_if_play_button_exists_in_launcher():
    current_image = screenshot()
    reference_folder = "check_if_play_button_exists_in_launcher2"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99,
    )
    return check_for_location(locations)


def wait_for_play_button_in_launcher(logger):
    if len(pygetwindow.getWindowsWithTitle("BsgLauncher")) == 0:
        logger.log(
            "#575637 Launcher not detected while waiting for play button in launcher."
        )
        return "restart"
    loop = 0
    waiting = not (check_if_play_button_exists_in_launcher())
    while waiting:
        loop = loop + 2
        waiting = not (check_if_play_button_exists_in_launcher())
        time.sleep(2)
        if loop > 50:
            logger.log(
                "#8568445 Spent too long waiting for launcher's play button. Restarting."
            )
            return "restart"
