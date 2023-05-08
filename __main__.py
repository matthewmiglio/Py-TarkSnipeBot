import random
from client import (
    buy_this_offer,
    check_if_offer_exists,
    get_to_flea_tab,
    orientate_tarkov_client,
    reset_filters,
    search_for_item,
    set_flea_filters,
)
from data_list import data_list
from logger import Logger
import time

logger = Logger()
orientate_tarkov_client("EscapeFromTarkov", logger)


def snipe_main():

    while 1:
        this_item = random.choice(data_list)
        print("\n-----------------------------------------")

        item_name = this_item[0]
        item_price = this_item[1] - 100

        print(f"Looking for {item_name} offers below {item_price}")

        # get to flea
        get_to_flea_tab(logger, print_mode=False)

        # reset existing filters
        reset_filters(logger,print_mode=False)

        # search for name
        search_for_item(item_name)

        # apply filters for this item
        set_flea_filters(logger, item_price, print_mode=False)
        time.sleep(2)

        # if offer exists, buy, else continue
        buy_this_offer(logger)


snipe_main()
