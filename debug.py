from client import check_if_offer_exists, orientate_tarkov_client
from configuration import load_user_config
from logger import Logger


user_settings = load_user_config()
launcher_path = user_settings["launcher_path"]
logger = Logger()


orientate_tarkov_client("EscapeFromTarkov",logger)

# while 1:
#     print(check_if_offer_exists())
