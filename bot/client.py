import pythoncom
import time

import numpy
import pyautogui
import pygetwindow
import win32com.client as win32
import win32gui
from matplotlib import pyplot as plt
from screeninfo import get_monitors

from utils.image_rec import (
    find_references,
    get_first_location,
    make_reference_image_list,
)


def get_to_flea_tab(logger, print_mode=True):
    if print_mode:
        logger.log("Getting to flea tab")
    on_flea = check_if_on_flea_page()
    loops = 0
    while not on_flea:
        if loops > 20:
            print("#92537982735 Failure with get_to_flea_tab()")
            return "restart"
        loops = loops + 1

        click(829, 977)
        time.sleep(0.17)
        on_flea = check_if_on_flea_page()
    if print_mode:
        logger.log("Made it to flea tab.")


def check_if_on_flea_page():
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, reintroduce-else, swap-if-expression
    iar = numpy.asarray(screenshot())

    pix1 = iar[984][813]
    pix2 = iar[972][810]
    pix3 = iar[976][883]
    pix4 = iar[984][883]

    COLOR_TAN = [159, 157, 144]

    if not pixel_is_equal(pix1, COLOR_TAN, tol=25):
        return False
    if not pixel_is_equal(pix2, COLOR_TAN, tol=25):
        return False
    if not pixel_is_equal(pix3, COLOR_TAN, tol=25):
        return False
    if not pixel_is_equal(pix4, COLOR_TAN, tol=25):
        return False
    return True


def search_for_item(name):
    # click search bar in flea tab
    click(x=157, y=113)
    time.sleep(0.1)

    # write item name
    pyautogui.typewrite(name)
    time.sleep(4)

    # click item in search results page
    click(134, 142)

    # wait
    time.sleep(1)


def open_filters_window(logger, print_mode):
    click(328, 87)
    time.sleep(0.33)
    orientate_filters_window(logger, print_mode)


def orientate_filters_window(logger, print_mode=True):
    is_orientated = check_filters_window_orientation()
    loops = 0
    while not is_orientated:
        loops += 1
        if loops > 10:
            open_filters_window(logger, print_mode)
        if print_mode:
            logger.log("Orientating filters window.")
        coords = find_filters_window()
        if coords is not None:
            origin = pyautogui.position()
            pyautogui.moveTo(coords[0], coords[1], duration=0.1)
            time.sleep(0.33)
            pyautogui.dragTo(3, 3, duration=0.33)
            pyautogui.moveTo(origin[0], origin[1])
            time.sleep(0.33)
        is_orientated = check_filters_window_orientation()
    if print_mode:
        logger.log("Orientated filters window.")


def find_filters_window():
    current_image = screenshot()
    reference_folder = "find_filters_tab"
    references = make_reference_image_list(reference_folder)

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99,
    )

    coords = get_first_location(locations)
    return None if coords is None else [coords[1] + 3, coords[0] + 3]


def check_filters_window_orientation():
    coords = find_filters_window()
    if coords is None:
        return False
    value1 = abs(coords[0] - 24)
    value2 = abs(coords[1] - 35)
    return value1 <= 3 and value2 <= 3


def set_flea_filters(logger, price, print_mode):
    operation_delay = 0.15

    if print_mode:
        logger.log("Setting the flea filters for price undercut recognition")

    # open filter window
    if print_mode:
        logger.log("Opening the filters window")
    open_filters_window(logger, print_mode)
    time.sleep(operation_delay)

    # click currency dropdown
    if print_mode:
        logger.log("Filtering by roubles.")
    click(113, 62)
    time.sleep(operation_delay)

    # click RUB from dropdown
    click(124, 100)
    time.sleep(operation_delay)

    # click 'display offers from' dropdown
    if print_mode:
        logger.log("Filtering by player sales only.")
    click(171, 188)
    time.sleep(operation_delay)

    # click players from dropdown
    click(179, 250)
    time.sleep(operation_delay)

    # click 'condition from:' text input box
    click(131, 123)
    time.sleep(operation_delay)

    # write 100 in 'condition from:' text box
    pyautogui.typewrite("100")
    time.sleep(operation_delay)

    # click price input
    click(226, 84)
    time.sleep(operation_delay)

    # type price
    pyautogui.typewrite(str(price))
    time.sleep(operation_delay)

    # click OK
    if print_mode:
        logger.log("Clicking OK in filters tab.")
    click(83, 272)
    time.sleep(operation_delay)


def get_screen_resolution():
    monitor_1 = get_monitors()[0]
    w = monitor_1.width
    h = monitor_1.height
    return [w, h]


def check_if_offer_exists():
    iar = numpy.asarray(screenshot())
    for x in range(1148, 1236):
        this_pixel = iar[152][x]
        if pixel_is_equal(this_pixel, [151, 149, 137], tol=20):
            return True
    return False


def buy_this_offer(logger):
    if check_if_offer_exists():
        # click purchase
        click(1186, 152)
        time.sleep(0.33)

        # click all
        click(773, 475)
        time.sleep(0.33)

        # press y to buy it
        pyautogui.press("y")

        logger.log("Bought an item")
        logger.log(f"Bought {logger.snipes} items")
        logger.add_snipe()

        # sleep to avoid captcha
        time.sleep(7)


def reset_filters(logger, print_mode):
    open_filters_window(logger, print_mode)

    # reset filters
    click(182, 273)
    time.sleep(0.33)

    # click OK
    click(85, 274)
    time.sleep(0.33)


def orientate_terminal():
    try:
        terminal_window = pygetwindow.getWindowsWithTitle("py-SnipeBot v")[0]
        terminal_window.minimize()
        terminal_window.restore()

        # resize according to monitor size
        monitor_width = get_screen_resolution()[0]
        moitor_height = get_screen_resolution()[1]

        terminal_width = monitor_width - 1290
        terminal_height = moitor_height - 100

        terminal_window.resizeTo(terminal_width, terminal_height)

        # move window
        terminal_window.moveTo(970, 5)
        time.sleep(0.33)

        terminal_window.moveTo(1285, 5)
        time.sleep(0.33)
    except BaseException:
        pass

    try:
        terminal_window = pygetwindow.getWindowsWithTitle("__main__.py")[0]
        terminal_window.minimize()
        terminal_window.restore()

        # resize according to monitor size
        monitor_width = get_screen_resolution()[0]
        moitor_height = get_screen_resolution()[1]

        terminal_width = monitor_width - 1290
        terminal_height = moitor_height - 100

        terminal_window.resizeTo(terminal_width, terminal_height)

        # move window
        terminal_window.moveTo(970, 5)
        time.sleep(0.33)

        terminal_window.moveTo(1285, 5)
        time.sleep(0.33)
    except BaseException:
        pass


def close_tarkov_client(logger, tark_window):
    try:
        logger.log("Closing Tarkov")
        tark_window = tark_window[0]
        tark_window.close()
    except BaseException:
        logger.log("error closing tarkov client.")


def show_image(image):
    plt.imshow(numpy.asarray(image))
    plt.show()


def close_launcher(logger, tark_launcher):
    logger.log("Closing Tarkov launcher")
    tark_launcher = tark_launcher[0]
    tark_launcher.close()


def window_enumeration_handler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def move_window_to_top_left(window_name):
    window = pyautogui.getWindowsWithTitle(window_name)[0]
    window.moveTo(0, 0)


def orientate_tarkov_client():
    tark_window = pygetwindow.getWindowsWithTitle("EscapeFromTarkov")[0]
    tark_window.moveTo(0, 0)
    tark_window.resizeTo(1299, 999)


def orientate_launcher():
    resize = [1100, 600]
    title = "BsgLauncher"
    print("Resizing launcher")
    resize_window(window_name=title, resize=resize)
    print("Done resizing launcher")
    time.sleep(1)
    print("Moving launcher to top left")
    move_window(window_name=title, coord=[0, 0])
    print("Done moving launcher to top left")
    time.sleep(1)


def resize_window(window_name, resize):
    # Window name has to be a string
    # Resize has to be a 1x2 array like [width, height]
    pythoncom.CoInitialize()  # Initialize COM

    title = window_name  # Find first window with this title
    top_windows = []  # All open windows
    win32gui.EnumWindows(window_enumeration_handler, top_windows)

    winlst = []  # Windows to cycle through
    for i in top_windows:  # All open windows
        if i[1] == title:
            winlst.append(i)

    hwnd = winlst[0][0]  # First window with title, get hwnd id
    shell = win32.Dispatch("WScript.Shell")  # Set focus on desktop
    shell.SendKeys("%")  # Alt key, send key
    x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)

    win32gui.MoveWindow(hwnd, x0, y0, resize[0], resize[1], True)


def move_window(window_name, coord):
    window = pygetwindow.getWindowsWithTitle(window_name)[0]
    window.moveTo(coord[0], coord[1])


def click(x, y, clicks=1, interval=0.0, duration=0.1, button="left"):
    # move the mouse to the spot
    pyautogui.moveTo(x, y, duration=duration)

    # click it as many times as ur suppsoed to
    loops = 0
    while loops < clicks:
        pyautogui.click(x=x, y=y, button=button)
        loops = loops + 1
        time.sleep(interval)


def pixel_is_equal(pix1, pix2, tol):
    """check pixel equality

    Args:
        pix1 (list[int]): [R,G,B] pixel
        pix2 (list[int]): [R,G,B] pixel
        tol (float): tolerance

    Returns:
        bool: are pixels equal
    """
    diff_r = abs(pix1[0] - pix2[0])
    diff_g = abs(pix1[1] - pix2[1])
    diff_b = abs(pix1[2] - pix2[2])
    return (diff_r < tol) and (diff_g < tol) and (diff_b < tol)


def screenshot(region=(0, 0, 1400, 1400)):
    if region is None:
        return pyautogui.screenshot()
    else:
        return pyautogui.screenshot(region=region)
