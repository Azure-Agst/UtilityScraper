import socket
import requests
import calendar

from enum import Enum
from datetime import datetime, timedelta

from modules.config import Config
from modules.utilitydata import UtilityData

class DiscordColors(int, Enum):
    """Main Color Enum, used in Discord embeds"""
    LIGHTBLUE = int(0x00ffff)
    RED = int(0xA00000)
    GREEN = int(0x00A000)

class DiscordNotifier():
    """Main Discord Webhook Post Class"""

    def __init__(self, config: Config):
        self.config = config

    def send_rich_message(self, message_text: str, color: int = DiscordColors.LIGHTBLUE):
        """Main Discord Message Function"""
        embed = {
            "username": self.config.d_bot_name,
            "avatar_url": self.config.d_bot_pfp,
            "content": f"<@&{self.config.d_ping_id}>",
            "embeds": [
                {
                    "title": "Utility Update",
                    "description": message_text,
                    "color": color,
                    "timestamp": str(datetime.utcnow().isoformat()),
                    "footer": {
                        "text": f"Utility Script on '{socket.gethostname()}'"
                    }
                }
            ]
        }
        requests.post(self.config.d_post_url, json=embed)

    def format_discord_message(self, data: UtilityData) -> str:

        # get data into manageable formats
        now = datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        # last_bill_date = data.last_bill.strftime("%m/%d")
        next_bill_date = (data.last_bill + timedelta(days=days_in_month)).strftime("%m/%d")
        next_due_date = data.next_bill.strftime("%m/%d")
        last_est_date = data.e_usage_date.strftime("%m/%d")

        # calculate estimates for the month
        tracked_cost = data.e_breakdown['Electric'] + data.e_breakdown['Water']
        static_cost = data.e_usage - tracked_cost
        days_since_start = (data.e_usage_date - data.last_bill).days
        est_cost = static_cost + (tracked_cost * (days_in_month / days_since_start))

        # format data for discord
        breakdown = ""
        for item in data.e_breakdown.keys():
            breakdown += f"- {item}: `${data.e_breakdown[item]}`"
            if item == "Electric":
                breakdown += " (@ $0.1096/kWh)"
            elif item == "Water":
                breakdown += " (@ ~$0.202/cgal)"
            elif item == "Sewer Water":
                breakdown += " (@ $0.669/cgal)"
            breakdown += "\n"

        # format final message
        message = f"\
            __**Current {data.vendor} Utility Bill:**__\n\
            - Account Number: `{data.account_num}`\n\
            - Account Balance: `${round(data.account_bal, 2)}` due `{next_due_date}`\n\n\
            __**Estimates:**__\n\
            - Current: `${round(data.e_usage, 2)}` as of `{last_est_date}`\n\
            - Projected: `${round(est_cost, 2)}` by `{next_bill_date}`\n\n\
            __**Current Cost Breakdown:**__\n\
            {breakdown}\n\
        "

        return message
