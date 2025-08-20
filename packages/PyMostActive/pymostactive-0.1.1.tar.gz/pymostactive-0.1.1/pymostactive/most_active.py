from pymostactive.tradingview_data_provider import *
from pymostactive.yahoo_data_provider import *


class MostActive:

    @staticmethod
    def download(resource: Resource = None,
                 market: Market = Market.US,
                 asset: Asset = None,
                 count: int = 50) -> Optional[pd.DataFrame]:
        providers = []

        if resource is None or resource == Resource.YAHOO:
            if market == Market.US:
                assets = [asset] if asset is not None else list(Asset)
                for a in assets:
                    providers.append(YahooDataProvider(a))

        if resource is None or resource == Resource.TRADINGVIEW:
            markets = [market] if market is not None else list(Market)
            assets = [asset] if asset is not None else list(Asset)
            for m in markets:
                for a in assets:
                    providers.append(TradingViewDataProvider(m, a))

        combined_df = None
        for provider in providers:
            df = provider.get_stocks(count)
            if df is not None:
                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pd.concat([combined_df, df]).drop_duplicates(
                        subset='symbol', keep='first'
                    )

        if combined_df is not None:
            combined_df = combined_df.reset_index(drop=True)
        return combined_df


if __name__ == '__main__':
    most_active = MostActive()
    result = most_active.download(resource=Resource.YAHOO,
                                  market=Market.US,
                                  asset=Asset.STOCKS)
    if result is not None:
        print(result.head())
    else:
        print(f"download failed from tradingview")
