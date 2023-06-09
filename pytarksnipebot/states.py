import random
import time

from pytarksnipebot.bot.client import (
    buy_this_offer,
    get_to_flea_tab,
    reset_filters,
    search_for_item,
    set_flea_filters,
)
from pytarksnipebot.bot.data_list import data_list
from pytarksnipebot.bot.launcher import restart_tarkov


def state_tree(state, logger, jobs):
    print(f"Jobs in state tree: {jobs}")

    if state == "restart":
        restart_state(logger)
        state = "item_snipe"

    if state == "ruble_snipe":
        if "ruble_sniping" in jobs:
            state = ruble_snipe_main(logger)
        else:
            state = "item_snipe"

    if state == "item_snipe":
        if "item_sniping" in jobs:
            state = item_snipe_main(logger, jobs[2])
        else:
            state = "ruble_snipe"

    return state


def item_snipe_main(logger, snipe_data):
    # for each item in snipe_data, check for snipe

    item_index = 0
    for item in snipe_data:
        item_name = item[0]
        item_price = item[1]

        logger.log(
            f"Looking for {item_index}th item: [{item_name}] w/ offers below {item_price}"
        )

        # get to flea
        if get_to_flea_tab(logger, print_mode=False) == "restart":
            logger.log(f"#8435683 Failure with getting to flea tab")
            return "restart"

        # reset existing filters
        reset_filters(logger, print_mode=False)

        # search for name
        if search_for_item(item_name) == "no results":
            logger.log(f"no results for {item_name}")
            continue

        # apply filters for this item
        set_flea_filters(logger, item_price, print_mode=False)
        time.sleep(2)

        # if offer exists, buy, else continue
        logger.add_specific_snipe()
        buy_this_offer(logger)

        item_index += 1

    return "ruble_snipe"


def restart_state(logger):
    # close all of tarkov, start launcher, then tarkov, then get to main menu
    logger.log("Entered restart state")

    restart_tarkov(logger)

    logger.add_restart()

    pass


def ruble_snipe_main(logger):
    LOOP_PER_STATE = 6
    # loop LOOP_PER_STATE times, then run state_tree again
    for loop_index in range(LOOP_PER_STATE):
        logger.log(f"Starting ruble snipe loop {loop_index}")

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
        if search_for_item(item_name) == "no results":
            logger.log(f"no results for {item_name}")
            continue

        # apply filters for this item
        set_flea_filters(logger, item_price, print_mode=False)
        time.sleep(2)

        # if offer exists, buy, else continue
        logger.add_ruble_snipe()
        buy_this_offer(logger)

    return "item_snipe"
