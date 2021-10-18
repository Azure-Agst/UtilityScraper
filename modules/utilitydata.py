from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UtilityData:
    """Class for holding Utility Data"""

    # General Data
    vendor: str = ""
    account_num: str = ""
    account_bal: float = 0.0
    last_bill: datetime = None
    next_bill: datetime = None

    # Monthly Usage Data
    e_usage: float = 0.0
    e_usage_date: datetime = None
    e_breakdown: dict = field(default_factory=dict)
