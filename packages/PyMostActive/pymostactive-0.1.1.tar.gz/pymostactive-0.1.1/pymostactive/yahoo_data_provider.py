from pymostactive.base_data_provider import *
from pymostactive.web_scraper import ScrapingConfig, WebScraper


class YahooDataProvider(BaseDataProvider):

    def __init__(self, asset: Asset = Asset.STOCKS):
        self.asset = asset

        self._config_mapping: dict = {
            Asset.STOCKS: 'https://finance.yahoo.com/markets/stocks/most-active/?start=0&count=100',
            Asset.ETFS: 'https://finance.yahoo.com/markets/etfs/most-active/?start=0&count=100',
            Asset.CRYPTO: 'https://finance.yahoo.com/markets/crypto/most-active/?start=0&count=100'
        }

    def get_stocks(self, count: int = 50) -> Optional[pd.DataFrame]:
        config_obj = ScrapingConfig(
            url=self._config_mapping[self.asset],
            parent_tag='table',
            symbol_tag='span',
            symbol_attrs={'class': 'symbol'},
            name_tag='a',
            name_attrs={'class': 'ticker'}
        )

        df = WebScraper.scrape_stocks(config_obj)
        if df is not None:
            df['market'] = 'us'
            df['asset'] = self.asset.value
        return df.head(count) if df is not None else None
