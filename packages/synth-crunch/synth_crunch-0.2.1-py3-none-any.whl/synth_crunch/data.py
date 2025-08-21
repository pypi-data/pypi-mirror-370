import logging
from datetime import datetime, timezone
from typing import Literal, get_args

import pandas
import requests

from .interface import Asset

logger = logging.getLogger()


class PriceUnavailableError(ValueError):
    """
    Raised when the price provider cannot fetch the price for an asset.
    """


PythHistoryResolution = Literal[
    "minute",
    "2minute",
    "5minute",
    "15minute",
    "30minute",
    "hour",
    "2hour",
    "4hour",
    "6hour",
    "12hour",
    "day",
    "week",
    "month"
]


class PythClient:

    # from https://docs.pyth.network/price-feeds/price-feeds
    _LATEST_PRICE_URL = "https://hermes.pyth.network/api/latest_price_feeds"
    _ASSET_TO_TOKEN_ID_MAP: dict[Asset, str] = {
        "BTC": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
        "ETH": "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
        "XAU": "765d2ba906dbc32ca17cc11f5310a89e9ee1f6420508c63861f2f8ba4ee34bb2",
        "SOL": "ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    }

    # from https://docs.pyth.network/price-feeds/price-feeds
    _HISTORY_URL = "https://benchmarks.pyth.network/v1/shims/tradingview/history"
    _ASSET_TO_SYMBOL_MAP: dict[Asset, str] = {
        "BTC": "Crypto.BTC/USD",
        "ETH": "Crypto.ETH/USD",
        "XAU": "Metal.XAU/USD",
        "SOL": "Crypto.SOL/USD",
    }
    _HISTORY_RESOLUTION_MAPPING: dict[PythHistoryResolution, int | str] = {
        "minute": 1,
        "2minute": 2,
        "5minute": 5,
        "15minute": 15,
        "30minute": 30,
        "hour": 60,
        "2hour": 120,
        "4hour": 240,
        "6hour": 360,
        "12hour": 720,
        "day": "D",
        "week": "W",
        "month": "M",
    }

    def __init__(self):
        self._history_cache: dict[tuple, pandas.Series] = {}

    # # from https://github.com/mode-network/synth-subnet/blob/d076dc3bcdf93256a278dfec1cbe72b0c47612f6/synth/validator/price_data_provider.py#L39
    def get_price_history(
        self,
        *,
        asset: Asset,
        from_: datetime,
        to: datetime,
        resolution: PythHistoryResolution = "minute",
        timeout=30,
    ) -> pandas.Series:
        resolution_value = self._HISTORY_RESOLUTION_MAPPING.get(resolution)
        if resolution_value is None:
            raise ValueError(f"invalid resolution: {resolution}, only {get_args(PythHistoryResolution)} are supported")

        cache_key = (asset, from_, to, resolution)
        cached = self._history_cache.get(cache_key)
        if cached is not None:
            logger.debug(f"using cached price history for {asset} from {from_} to {to} with resolution {resolution}")
            return cached.copy(deep=True)

        query = {
            "symbol": self._ASSET_TO_SYMBOL_MAP[asset],
            "resolution": resolution_value,
            "from": self._unix_timestamp(from_),
            "to": self._unix_timestamp(to),
        }

        try:
            response = requests.get(
                self._HISTORY_URL,
                timeout=timeout,
                params=query,
            )

            response.raise_for_status()

            root = response.json()
            if root.get("s") != "ok":
                error_message = root.get("errmsg") or str(root)

                if error_message == "Too many datapoints to return":
                    next_resolution = self._next_resolution(resolution)

                    if next_resolution is not None:
                        error_message += f": try using `resolution={next_resolution}`"

                raise ValueError(f"api didn't returned ok: {error_message}")
        except Exception as error:
            raise PriceUnavailableError(f"could not get price history for {asset}: {error}") from error

        dataframe = pandas.DataFrame(
            {
                "timestamp": root["t"],
                "price": root["c"],
            },
        )

        dataframe["timestamp"] = pandas.to_datetime(dataframe["timestamp"], unit="s", utc=True)
        dataframe.set_index("timestamp", inplace=True)

        prices = dataframe["price"]

        if len(prices):
            self._history_cache[cache_key] = prices.copy(deep=True)

        return prices

    def get_last_price(
        self,
        *,
        asset: Asset,
        timeout=30,
    ) -> float:
        query = {
            "ids[]": self._ASSET_TO_TOKEN_ID_MAP[asset],
        }

        try:
            response = requests.get(
                self._LATEST_PRICE_URL,
                timeout=timeout,
                params=query,
            )

            response.raise_for_status()

            root = response.json()
            if len(root) != 1:
                raise ValueError(f"only one entry must be received: {root}")
        except Exception as error:
            raise PriceUnavailableError(f"could not get last price for {asset}: {error}") from error

        entry = root[0]
        price = int(entry["price"]["price"])
        expo = int(entry["price"]["expo"])

        return price * (10**expo)

    def clear_cache(self):
        self._history_cache.clear()

    def _unix_timestamp(self, object: datetime) -> int:
        object = object.replace(tzinfo=timezone.utc)

        return int(object.timestamp())

    def _next_resolution(self, resolution: PythHistoryResolution) -> PythHistoryResolution | None:
        resolutions = get_args(PythHistoryResolution)
        index = resolutions.index(resolution)

        if index + 1 >= len(resolutions):
            return None

        return resolutions[index + 1]


shared_pyth_hermes = PythClient()
