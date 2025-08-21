import unittest
from datetime import date, datetime, time
from typing import get_args

from parameterized import parameterized
from synth_crunch.data import PythClient
from synth_crunch.interface import Asset


class PythClientPriceProviderTest(unittest.TestCase):

    provider: PythClient

    @classmethod
    def setUpClass(cls):
        cls.provider = PythClient()

    @parameterized.expand(get_args(Asset))
    def test_get_price_history(self, asset: Asset):
        day = date(2024, 2, 1)  # 1st of january is a holiday

        data = self.provider.get_price_history(
            asset=asset,
            from_=datetime.combine(day, time.min),
            to=datetime.combine(day, time.max),
            timeout=120,  # cold data is slow
        )

        self.assertEqual(1440, len(data), msg="data length does not match expected number of minutes in a day")
        self.assertFalse(data.isna().any().any(), "data contains null values")

    @parameterized.expand(get_args(Asset))
    def test_one_year(self, asset: Asset):
        data = self.provider.get_price_history(
            asset=asset,
            from_=datetime(2024, 2, 1),
            to=datetime(2024, 12, 31),
            resolution="day",
            timeout=120,  # cold data is slow
        )

        self.assertLess(len(data), 366, msg="data length is greater than number of days in a year")

    @parameterized.expand(get_args(Asset))
    def test_get_last_price(self, asset: Asset):
        price = self.provider.get_last_price(
            asset=asset,
        )

        # TODO the last price should still be available even if the asset is not currently trading?
        # if asset == "XAU" and price is None:
        #     raise unittest.SkipTest("gold price is not available, but endpoint is still working")

        self.assertGreater(price, 0, msg="price should be greater than 0")
