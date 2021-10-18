import os
import sys
import json
import importlib
import dataclasses

from datetime import datetime

from modules.config import Config
from modules.utilitydata import UtilityData

class DataParserException(Exception):
    pass

class DataParser():
    """Main class that acts as a wrapper for individual parsers. Handles caching as well."""

    def __init__(self, config: Config):
        self.config = config
        self.cache_file = None
        self.scrapers = {}

    def _load_cached_data(self) -> UtilityData:
        """Loads data from cached file, if file exists"""

        # if target in cache, load it
        if os.path.exists(self.cache_file):

            # open file and load
            with open(self.cache_file, "r") as f:
                data = json.load(f)

            # return data
            print("- Cached data found and loaded!")
            return UtilityData(
                vendor=data['vendor'],
                account_num=data['account_num'],
                account_bal=float(data['account_bal']),
                last_bill=datetime.strptime(data['last_bill'], "%Y-%m-%d %H:%M:%S"),
                next_bill=datetime.strptime(data['next_bill'], "%Y-%m-%d %H:%M:%S"),
                e_usage=float(data['e_usage']),
                e_usage_date=datetime.strptime(data['e_usage_date'], "%Y-%m-%d %H:%M:%S"),
                e_breakdown=data['e_breakdown']
            )

        # if file not in cache, return None
        else:
            print("- Data not found in cache, continuing to scrape...")
            return None

    def _save_data_to_cache(self, data: UtilityData, overwrite: bool = False):
        """Saves data to our cache"""

        if data is None:
            raise DataParserException("UtilityData cannot be None, failed to save!")

        # save only if data doesn't already exist
        if not os.path.exists(self.cache_file) or overwrite:

            # create directory if it doesn't exist
            if not os.path.exists(self.config.c_path):
                os.makedirs(self.config.c_path)

            # open file and save
            with open(self.cache_file, "w") as f:
                json.dump(dataclasses.asdict(data), f, default=str)
                print("- Saved scraped data to cache!")

    def load_scrapers(self):
        """Loads all available scrapers"""

        # for each scraper file in scrapers directory
        for scraper in os.listdir("modules/scrapers"):
            if scraper.startswith("scrape_") and scraper.endswith(".py"):

                # this is some advanced python magic i reverse engineered from the discord.py repo.
                # https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/bot.py#L655

                # get module name
                modname = "modules.scrapers." + scraper.replace(".py", "")

                # get the spec associated with module
                modname = importlib.util.resolve_name(modname, None)
                modspec = importlib.util.find_spec(modname)

                # prepare to load module
                lib = importlib.util.module_from_spec(modspec)
                sys.modules[modname] = lib

                # try to import the module
                try:
                    modspec.loader.exec_module(lib)
                    setup = getattr(lib, 'setup')
                    setup(self, self.config)
                except Exception as e:
                    del sys.modules[modname]
                    raise e
                else:
                    print(f"- Loaded {scraper}")

    def add_scraper(self, scraper):
        """Called in each scraper file to it to dict of available scrapers"""
        self.scrapers[type(scraper).__name__] = scraper

    def get_data(self) -> UtilityData:
        """
        Returns a UtilityData object that is either:
        A.) populated using cached data from an earlier scrape
        B.) retrieved from an individual parser
        """

        print("Getting Utility Data...")

        # If cache enabled, try loading from cache
        if self.config.c_enabled:

            # determine filename
            filename = datetime.now().strftime(self.config.c_format)
            self.cache_file = os.path.join(self.config.c_path, filename)

            # start the search!
            data = self._load_cached_data()
            if data is not None:
                return data

        # If cache disabled or no cached data exists
        print(f"- Using {self.config.v_scraper}")
        print("[==========================================================]\n")
        data = self.scrapers[self.config.v_scraper].scrape_data()
        print("\n[==========================================================]")

        # If cache enabled, save data
        if self.config.c_enabled:
            self._save_data_to_cache(data)

        # return data
        return data
