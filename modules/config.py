from dataclasses import dataclass
from configparser import ConfigParser

@dataclass
class Config():
    """Class for holding main config data for runtime"""

    # default settings
    headless: bool = False
    debug: bool = False
    vendor: str = None

    # cache settings
    c_enabled: bool = True
    c_path: str = 'cache'
    c_format: str = '%Y-%m-%d.json'

    # vendor specific config
    v_name: str = None
    v_scraper: str = None
    v_entry_url: str = None
    v_username: str = None
    v_password: str = None

    # discord config
    d_bot_name: str = None
    d_bot_pfp: str = None
    d_post_url: str = None
    d_ping_id: str = None

    def load_data(config_path: str):
        """Loads config data from config at path"""

        config = ConfigParser()
        config.read(config_path)

        # check to make sure valid vendor settings
        vendor = config.get('settings', 'vendor')
        try:
            if vendor not in config.keys():
                raise KeyError
        except KeyError:
            print("Invalid config, vendor section not specified")

        # return config data
        return Config(
            headless=config.getboolean('settings', 'headless'),
            debug=config.getboolean('settings', 'debug'),
            vendor=vendor,

            c_enabled=config.getboolean('caching', 'enabled'),
            c_path=config.get('caching', 'cache_path'),
            c_format=config.get('caching', 'format'),

            d_bot_name=config.get('discord', 'bot_name'),
            d_bot_pfp=config.get('discord', 'bot_pfp'),
            d_post_url=config.get('discord', 'post_url'),
            d_ping_id=config.get('discord', 'ping_id'),

            v_name=config.get(vendor, 'name'),
            v_scraper=config.get(vendor, 'scraper'),
            v_entry_url=config.get(vendor, 'entry_url'),
            v_username=config.get(vendor, 'username'),
            v_password=config.get(vendor, 'password'),
        )
