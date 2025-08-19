from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional

import pandas as pd


class Resource(Enum):
    YAHOO = 'yahoo'
    TRADINGVIEW = 'tradingview'


class Market(Enum):
    US = "us"
    UK = "uk"
    CHINA = "china"
    HK = "hk"
    JAPAN = "japan"


class Asset(Enum):
    STOCKS = "stocks"
    ETFS = "etfs"
    CRYPTO = "crypto"


class BaseDataProvider(ABC):

    @abstractmethod
    def get_stocks(self, count: int = 50) -> Optional[pd.DataFrame]:
        pass
