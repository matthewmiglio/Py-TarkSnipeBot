

import time

import numpy
import pyautogui


from pySnipeBot.client import check_quit_key_press, click, pixel_is_equal, screenshot
from pySnipeBot.image_rec import  find_references, get_first_location


def find_dorm_room_314_in_wishlist():
    check_quit_key_press()
    
    current_image = screenshot(region=[39,121,400,600])
    reference_folder = "find_dorm_room_314_in_wishlist"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "13.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",
        "14.png",
    ]
    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.90
    )
    coord= get_first_location(locations)
    if coord is None: return None
    
    coord = [coord[1]+39,coord[0]+121]
    return coord


def get_to_wishlist(logger):
    at_wishlist=False
    while not (at_wishlist):
        check_quit_key_press()
        pyautogui.moveTo(164,85)
        pyautogui.click()
        time.sleep(0.5)
        at_wishlist=check_if_on_wishlist()
    logger.log("Made it to wishlist.")
    

def check_if_on_wishlist():
    iar=numpy.asarray(screenshot())
    pix_list=[
        iar[83][140],
        iar[93][139],
        iar[83][209],
        iar[96][208],
    ]
    color=[198,196,165]
    
    for pix in pix_list:
        if not(pixel_is_equal(pix,color,tol=50)):
            return False
    return True
    

def get_to_flee_tab(logger):
    on_flee = check_if_on_flee_page()
    loops = 0
    while not (on_flee):
        logger.log("Didnt find flea tab. Clicking flea tab.")
        if loops > 10:
            return "restart"
        loops = loops + 1

        check_quit_key_press()
        click(829, 977)
        time.sleep(2)
        on_flee = check_if_on_flee_page()
    logger.log("Made it to flea tab.")


def check_if_on_flee_page():
    iar=numpy.asarray(screenshot())

    pix1=iar[984][813]
    pix2=iar[972][810]
    pix3=iar[976][883]
    pix4=iar[984][883]
    
    COLOR_TAN=[159,157,144]
    
    if not(pixel_is_equal(pix1,COLOR_TAN,tol=25)): return False
    if not(pixel_is_equal(pix2,COLOR_TAN,tol=25)): return False
    if not(pixel_is_equal(pix3,COLOR_TAN,tol=25)): return False
    if not(pixel_is_equal(pix4,COLOR_TAN,tol=25)): return False
    return True


def check_if_has_offer():
    check_quit_key_press()
    iar=numpy.asarray(screenshot())
    pix_list=[
        iar[134][605],
        iar[164][623],
        iar[139][626],
        iar[161][603],
    ]
    sentinel=[70,70,50]
    for pix in pix_list:
        if not(pixel_is_equal(pix,sentinel,tol=50)):
            return True
    return False
    
    
def open_filters_window(logger):
    click(328, 87)
    time.sleep(0.33)
    orientate_filters_window(logger)


def purchase_first_offer():
    check_quit_key_press()
    pyautogui.moveTo(1193,150)
    pyautogui.click()
    time.sleep(0.5)
    
    pyautogui.press('y')
    time.sleep(0.5)


def orientate_filters_window(logger):
    
    is_orientated = check_filters_window_orientation()
    while not (is_orientated):
        logger.log("Orientating filters window.")
        coords = find_filters_window()
        if coords is not None:
            pyautogui.moveTo(coords[0], coords[1], duration=0.33)
            time.sleep(0.33)
            pyautogui.dragTo(3, 3, duration=0.33)
            time.sleep(0.33)
        is_orientated = check_filters_window_orientation()
    logger.log("Orientated filters window.")


def check_filters_window_orientation():
    coords=find_filters_window()
    #print(coords)
    if coords is None: return False
    value1=abs(coords[0] - 24)
    value2=abs(coords[1] - 35)
    if (value1>3)or(value2>3): return False
    return True


def find_filters_window():
    check_quit_key_press()
    current_image = screenshot()
    reference_folder = "find_filters_tab"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",
        "14.png",
        "15.png",
        "16.png",
        "17.png",
        "18.png",
        "19.png",
        "20.png",
        "21.png",
        "22.png",  
    ]
    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )
    coords = get_first_location(locations)
    if coords is None:
        return None
    return [coords[1] + 3, coords[0] + 3]


def snipe_items(logger,info):
    #for each slot in info, snipe the item
    for slot_info in info:
        this_name=slot_info[0]
        this_price=slot_info[1]
        this_quantity=slot_info[2]
        
        print('this_name',this_name)
        print('this_price',this_price)
        print('this_quantity',this_quantity)


        snipe_item(logger,item=this_name,price=this_price,quantity=this_quantity)

    # snipe_item(logger,item="violet_keycard",price=99)=="restart": 
        





def snipe_item(logger,item,price,quantity):
    #return if null params
    if (price == 0)or(item=="")or(quantity==""):
        print("Called snipe items with null params")
        return

    #if we've reached quantity, skip everything


    #get to flea tab
    check_quit_key_press()
    logger.log("Getting to flea")
    get_to_flee_tab(logger)
    time.sleep(1)
    
    #get to wishlist tab
    get_to_wishlist(logger)
    
    #refresh the page
    logger.log("Refreshing page")
    pyautogui.press('f5')
    time.sleep(3)
    
    #open filters tab
    logger.log("Setting filters.")
    open_filters_window(logger)
    time.sleep(1)
    
    #reset filters then reopen filter window
    reset_filters(logger)
    
    #search for the item
    search_for_item(item_name=item)

    #click first result
    click(95,140)
    time.sleep(1)

    #set filters
    logger.log("Setting filters.")
    set_filters(roubles=price)
    time.sleep(1)
    
    #if has offer, buy it
    if check_if_has_offer():
        purchase_first_offer()
        return "restart"

    
    
def reset_filters(logger):
    check_quit_key_press()
    logger.log("Resetting filters")
    pyautogui.moveTo(186,275)
    pyautogui.click()
    time.sleep(0.5)
    open_filters_window(logger)
    
    time.sleep(2)
    pyautogui.press('f5')
    time.sleep(2)
    
    
def set_filters(roubles=0):
    #if params are null return
    if roubles==0:
        print("Called set_filters with null params")
        return
    
    
    #open currency filter
    check_quit_key_press()
    pyautogui.moveTo(121,61)
    pyautogui.click()
    time.sleep(0.5)
    
    #set to roubles
    check_quit_key_press()
    pyautogui.moveTo(114,99)
    pyautogui.click()
    time.sleep(0.5)
    
    #set price limit of 500k
    check_quit_key_press()
    pyautogui.moveTo(222,82)
    pyautogui.click()
    time.sleep(0.5)
    to_write=str(roubles)
    pyautogui.write(to_write)
    time.sleep(0.5)

    #click OK
    check_quit_key_press()
    pyautogui.moveTo(88,272)
    pyautogui.click()
    time.sleep(3)


def get_to_browse_tab(logger):
    logger.log('Getting to browse tab')
    while not check_if_on_browse_tab():
        click(77,86)
        time.sleep(0.5)
    logger.log('Done getting to browse tab')
    

def check_if_on_browse_tab():
    iar=numpy.asarray(screenshot())
    for x_coord in range(40,60):
        this_pixel=iar[85][x_coord]
        if pixel_is_equal(this_pixel,[240,234,204],tol=35):
            return True
    return False



def search_for_item(item_name):
    #click deadspace
    click(22,100)
    time.sleep(0.33)

    #click search bar
    click(60,109)
    time.sleep(0.33)

    #backspace
    pyautogui.press('backspace')
    time.sleep(0.33)

    #type out item name
    pyautogui.write(item_name)
    time.sleep(4)

    
