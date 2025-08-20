import logging
from dataclasses import dataclass
from typing import Optional, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScrapingConfig:
    url: str
    parent_tag: Optional[str] = None
    parent_attrs: Optional[Dict] = None
    symbol_tag: str = "span"
    symbol_attrs: Optional[Dict] = None
    name_tag: str = "a"
    name_attrs: Optional[Dict] = None


class WebScraper:
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    @staticmethod
    def scrape_stocks(scraping_config: ScrapingConfig) -> Optional[pd.DataFrame]:

        try:
            response = requests.get(
                scraping_config.url,
                headers=WebScraper.DEFAULT_HEADERS,
                timeout=10
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            if scraping_config.parent_tag:
                if scraping_config.parent_attrs is None:
                    parent = soup.find(scraping_config.parent_tag)
                else:
                    parent = soup.find(scraping_config.parent_tag, scraping_config.parent_attrs)
                if not parent:
                    logger.warning(f"Parent tag not found: {scraping_config.parent_tag}")
                    return None

                soup = parent

            symbol_elements = soup.find_all(scraping_config.symbol_tag, scraping_config.symbol_attrs)
            name_elements = soup.find_all(scraping_config.name_tag, scraping_config.name_attrs)

            if not symbol_elements or not name_elements:
                logger.warning("No stock elements found")
                return None

            symbols = [elem.get_text(strip=True) for elem in symbol_elements if elem.get_text(strip=True)]
            names = []

            for elem in name_elements:
                name = elem.get('title', '').strip()
                if not name:
                    name = elem.get_text(strip=True)
                names.append(name)

            min_length = min(len(symbols), len(names))
            if min_length == 0:
                logger.warning("No valid stock data extracted")
                return None

            symbols = symbols[:min_length]
            names = names[:min_length]

            return pd.DataFrame({
                'symbol': symbols,
                'name': names
            })

        except requests.RequestException as e:
            logger.error(f"Request failed for {scraping_config.url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping stocks from {scraping_config.url}: {e}")
            return None
