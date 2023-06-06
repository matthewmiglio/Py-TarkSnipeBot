import time
from bot.client import (
    buy_this_offer,
    get_to_flea_tab,
    reset_filters,
    search_for_item,
    set_flea_filters,
)
from bot.data_list import data_list

import random
from bot.launcher import restart_tarkov


def state_tree(state, logger, jobs):
    if state == "restart":
        restart_state(logger)
        state = "snipe"

    if state == "snipe":
        state = snipe_state(logger)

    return state


def restart_state(logger):
    # close all of tarkov, start launcher, then tarkov, then get to main menu
    logger.log("Entered restart state")

    restart_tarkov(logger)

    logger.add_restart()

    pass


def snipe_state(logger):
    # pick random item
    this_item = random.choice(data_list)

    # unpack name and price from tuple
    item_name = this_item[0]
    item_price = this_item[1] - 100

    logger.log(f"Looking for {item_name} offers below {item_price}")

    # get to flea
    if get_to_flea_tab(logger, print_mode=False) == "restart":
        logger.log(f"#235987 Failure with getting to flea tab")
        return "restart"

    # reset existing filters
    reset_filters(logger, print_mode=False)

    # search for name
    search_for_item(item_name)

    # apply filters for this item
    set_flea_filters(logger, item_price, print_mode=False)
    time.sleep(2)

    # if offer exists, buy, else continue
    buy_this_offer(logger)

    return "snipe"
