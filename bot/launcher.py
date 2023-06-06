import subprocess
import sys
import time

import numpy
import pygetwindow

from pySnipeBot.client import (check_quit_key_press, click, close_launcher,
                    close_tarkov_client, orientate_launcher,
                    orientate_tarkov_client, pixel_is_equal, screenshot)
from pySnipeBot.image_rec import check_for_location, find_references, get_first_location



def restart_tarkov(logger, launcher_path):
    # specify tark launcher path
    # launcher_path=r"B:\BsgLauncher\BsgLauncher.exe"

    # check if tarkov is open
    tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")
    tark_launcher = pygetwindow.getWindowsWithTitle("BsgLauncher")

    # if tark open
    check_quit_key_press()
    if len(tark_window) != 0:
        close_tarkov_client(logger, tark_window)
        time.sleep(5)

    # if launcher open
    if len(tark_launcher) != 0:
        close_launcher(logger, tark_launcher)
        time.sleep(5)

    # open tark launcher
    check_quit_key_press()
    logger.change_status("Opening launcher.")
    try:
        subprocess.Popen(launcher_path)
    except FileNotFoundError:
        print(r"Launcher path not found, edit config file: %appdata%\py-SnipeBot\config.json")
        sys.exit("Launcher path not found")
    time.sleep(10)

    # orientate launcher
    check_quit_key_press()
    logger.change_status("orientating launcher")
    orientate_launcher()

    #wait for launcher play button to appear
    if wait_for_play_button_in_launcher(logger)== "restart":
        restart_tarkov(logger,launcher_path)


    #click play
    check_quit_key_press()
    click(942,558)
    time.sleep(20)


    # wait for client opening
    check_quit_key_press()
    if wait_for_tarkov_to_open(logger) == "restart":
        restart_tarkov(logger, launcher_path)
    index = 0
    while index < 30:
        check_quit_key_press()
        logger.change_status(f"Giving tark time to load: {index}")
        time.sleep(2)
        index = index + 2

    # orientate tark client
    check_quit_key_press()
    orientate_tarkov_client("EscapeFromTarkov",logger)
    time.sleep(1)

    # wait for us to reach main menu
    check_quit_key_press()
    if wait_for_tark_main(logger)=="restart":
        restart_tarkov(logger,launcher_path)


def wait_for_tarkov_to_open(logger):
    tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")
    loops = 0
    logger.change_status("Waiting for tarkov to open. . .")
    while len(tark_window) == 0:
        check_quit_key_press()
        
        loops = loops + 2
        time.sleep(2)
        tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")
        if loops > 50:
            return "restart"

    
def wait_for_tark_main(logger):
    on_main = check_if_on_tark_main()
    loops = 0
    logger.change_status("Waiting for tark main.")
    while not (on_main):
        check_quit_key_press()
        
        loops = loops + 2
        time.sleep(2)
        on_main = check_if_on_tark_main()
        if loops > 120:
            return "restart"
    
def check_if_on_tark_main():
    iar=numpy.asarray(screenshot())
    pix_list=[]
    pix_list.append(iar[613][762])
    pix_list.append(iar[616][926])
    pix_list.append(iar[611][294])
    pix_list.append(iar[618][769])
    pix_list.append(iar[651][427])
    pix_list.append(iar[615][1010])
    pix_list.append(iar[648][290])
    

    for pix in pix_list:
        if not pixel_is_equal(pix,[175,90,50],tol=100):
            return False
    return True






def check_if_play_button_exists_in_launcher():
    check_quit_key_press()
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
        tolerance=0.99
    )
    return check_for_location(locations)




def wait_for_play_button_in_launcher(logger):
    if len(pygetwindow.getWindowsWithTitle("BsgLauncher")) == 0:
        logger.change_status(
            "Launcher not detected while waiting for play button in launcher.")
        return "restart"
    loop = 0
    waiting = not (check_if_play_button_exists_in_launcher())
    while waiting:
        
        loop = loop + 2
        waiting = not (check_if_play_button_exists_in_launcher())
        time.sleep(2)
        if loop > 50:
            logger.change_status(
                "Spent too long waiting for launcher's play button. Restarting.")
            return "restart"





