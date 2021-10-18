import sys

from modules.config import Config
from modules.discord import DiscordNotifier
from modules.dataparser import DataParser

# main function
def main() -> int:

    print("Starting utility scraper...")

    # get config
    config = Config.load_data('config.ini')

    # load parser
    parser = DataParser(config)
    parser.load_scrapers()

    # try to load data
    try:
        data = parser.get_data()
    except Exception as e:
        raise e

    # format message and send to discord
    print("Sending discord message...")
    bot = DiscordNotifier(config)
    msg = bot.format_discord_message(data)
    bot.send_rich_message(msg, int(0xdddddd))

    # return successful exit code
    print("Exiting...\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
