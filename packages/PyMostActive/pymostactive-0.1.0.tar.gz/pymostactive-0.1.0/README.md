# PyMostActive

Retrieve the list of most active stocks from major financial websites.

### Currently Supported:

* **Financial websites**: Yahoo Finance, TradingView
* **Stock markets**: US, UK, CHINA, HK, JAPAN
* **Assets**: STOCKS, ETFS, CRYPTO

### Example:

    from pymostactive.most_active import MostActive

    most_active = MostActive()
    result = most_active.download(resource=Resource.YAHOO,
                                  market=Market.US,
                                  asset=Asset.STOCKS)
    if result is not None:
        print(result.head())
    else:
        print(f“download failed from Yahoo”)

Setting the parameter to None means that all options are included.

### Result:

|   | symbol | name                       | market | asset  |
|---|--------|----------------------------|--------|--------|
| 0 | OPEN   | Opendoor Technologies Inc. | us     | stocks |
| 1 | INTC   | Intel Corporation          | us     | stocks |
| 2 | WULF   | TeraWulf Inc.              | us     | stocks |
| 3 | NVDA   | NVIDIA Corporation         | us     | stocks |
| 4 | IQ     | iQIYI, Inc.                | us     | stocks |

