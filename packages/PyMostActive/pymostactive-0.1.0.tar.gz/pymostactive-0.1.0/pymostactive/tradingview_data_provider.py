from pymostactive.base_data_provider import *
from pymostactive.web_scraper import ScrapingConfig, WebScraper


class TradingViewDataProvider(BaseDataProvider):

    def __init__(self, market: Market = Market.US, asset: Asset = Asset.STOCKS):
        self.market = market
        self.asset = asset

        self._config_mapping: dict = {
            (Market.US, Asset.STOCKS): {
                'url': 'https://www.tradingview.com/markets/stocks-usa/market-movers-active/',
                'symbol_processor': None
            },
            (Market.US, Asset.CRYPTO): {
                'url': 'https://www.tradingview.com/markets/cryptocurrencies/prices-most-traded/',
                'symbol_processor': None
            },
            (Market.US, Asset.ETFS): {
                'url': 'https://www.tradingview.com/markets/etfs/funds-most-traded/',
                'symbol_processor': None
            },
            (Market.CHINA, Asset.STOCKS): {
                'url': 'https://cn.tradingview.com/markets/stocks-china/market-movers-active/',
                'symbol_processor': self._add_china_exchange_suffix
            },
            (Market.HK, Asset.STOCKS): {
                'url': 'https://www.tradingview.com/markets/stocks-hong-kong/market-movers-active/',
                'symbol_processor': self._add_hk_exchange_suffix
            },
            (Market.JAPAN, Asset.STOCKS): {
                'url': 'https://www.tradingview.com/markets/stocks-japan/market-movers-active/',
                'symbol_processor': self._add_japan_exchange_suffix
            },
            (Market.UK, Asset.STOCKS): {
                'url': 'https://www.tradingview.com/markets/stocks-united-kingdom/market-movers-active/',
                'symbol_processor': None
            }
        }

    def get_stocks(self, count: int = 50) -> Optional[pd.DataFrame]:
        key = (self.market, self.asset)
        if key not in self._config_mapping.keys():
            return None

        config = self._config_mapping[key]
        config_obj = ScrapingConfig(
            url=config['url'],
            symbol_tag='a',
            symbol_attrs={'class': 'tickerNameBox-GrtoTeat'},
            name_tag='sup',
            name_attrs={'class': 'tickerDescription-GrtoTeat'}
        )

        df = WebScraper.scrape_stocks(config_obj)
        if df is not None:
            if config['symbol_processor'] is not None:
                df['symbol'] = df['symbol'].apply(config['symbol_processor'])
            df['market'] = self.market.value
            df['asset'] = self.asset.value
        return df.head(count) if df is not None else None

    @staticmethod
    def _add_china_exchange_suffix(symbol: str) -> str:
        if symbol.startswith('6'):
            return f"{symbol}.SS"
        elif symbol.startswith(('0', '3')):
            return f"{symbol}.SZ"
        return symbol

    @staticmethod
    def _add_hk_exchange_suffix(symbol: str) -> str:
        return f"{symbol}.HK"

    @staticmethod
    def _add_japan_exchange_suffix(symbol: str) -> str:
        return f"{symbol}.T"
