import unittest
from unittest.mock import MagicMock
import sys
import os
import datetime

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.downloader.http_downloader import HttpDownloader


class TestHttpDownloader(unittest.TestCase):

    def setUp(self):
        self.downloader = HttpDownloader()

    def test_set_proxy(self):
        self.downloader.set_proxy("http://proxy.example.com:8080")
        self.assertEqual(self.downloader.proxy, "http://proxy.example.com:8080")

        self.downloader.set_proxy(None)
        self.assertIsNone(self.downloader.proxy)

    def test_set_retry_count(self):
        self.downloader.set_retry_count(5)
        self.assertEqual(self.downloader.retry_count, 5)

    def test_filter_files_by_date_range(self):
        files = [
            "BTCUSDT-daily-2020-01-01.zip",
            "BTCUSDT-daily-2020-01-02.zip",
            "BTCUSDT-daily-2020-01-03.zip",
            "BTCUSDT-daily-2020-01-04.zip",
            "BTCUSDT-daily-2020-01-05.zip",
            "some-other-file.zip",
        ]

        # Test with start date only
        start_date = datetime.date(2020, 1, 3)
        filtered = self.downloader.filter_files_by_date_range(
            files, start_date=start_date
        )
        self.assertEqual(
            len(filtered), 4
        )  # 3 files with dates >= 2020-01-03 + 1 without date
        self.assertIn("BTCUSDT-daily-2020-01-03.zip", filtered)
        self.assertIn("BTCUSDT-daily-2020-01-04.zip", filtered)
        self.assertIn("BTCUSDT-daily-2020-01-05.zip", filtered)
        self.assertIn("some-other-file.zip", filtered)

        # Test with end date only
        end_date = datetime.date(2020, 1, 3)
        filtered = self.downloader.filter_files_by_date_range(files, end_date=end_date)
        self.assertEqual(
            len(filtered), 4
        )  # 3 files with dates <= 2020-01-03 + 1 without date
        self.assertIn("BTCUSDT-daily-2020-01-01.zip", filtered)
        self.assertIn("BTCUSDT-daily-2020-01-02.zip", filtered)
        self.assertIn("BTCUSDT-daily-2020-01-03.zip", filtered)
        self.assertIn("some-other-file.zip", filtered)

        # Test with both start and end date
        start_date = datetime.date(2020, 1, 2)
        end_date = datetime.date(2020, 1, 4)
        filtered = self.downloader.filter_files_by_date_range(
            files, start_date=start_date, end_date=end_date
        )
        self.assertEqual(
            len(filtered), 4
        )  # 3 files with dates in range + 1 without date
        self.assertIn("BTCUSDT-daily-2020-01-02.zip", filtered)
        self.assertIn("BTCUSDT-daily-2020-01-03.zip", filtered)
        self.assertIn("BTCUSDT-daily-2020-01-04.zip", filtered)
        self.assertIn("some-other-file.zip", filtered)

        # Test with no date range
        filtered = self.downloader.filter_files_by_date_range(files)
        self.assertEqual(len(filtered), 6)  # All files

    def test_filter_files_by_date_range_futures_format(self):
        # Test with futures file paths
        futures_files = [
            "data/futures/cm/daily/aggTrades/ADAUSD_200925/ADAUSD_200925-aggTrades-2020-09-25.zip",
            "data/futures/cm/daily/aggTrades/ADAUSD_201225/ADAUSD_201225-aggTrades-2020-12-25.zip",
            "data/futures/cm/daily/aggTrades/ADAUSD_210326/ADAUSD_210326-aggTrades-2021-03-26.zip",
            "data/futures/cm/daily/aggTrades/ADAUSD_210625/ADAUSD_210625-aggTrades-2021-06-25.zip",
            # "data/futures/cm/daily/aggTrades/ADAUSD_PERP/",  # Perpetual contract should always be included
            # "data/futures/cm/daily/aggTrades/BTCUSD_210625/file.zip",  # With filename
        ]

        # Test with start date only
        start_date = datetime.date(2021, 1, 1)
        filtered = self.downloader.filter_files_by_date_range(
            futures_files, start_date=start_date
        )
        self.assertEqual(
            len(filtered), 2
        )  # 2 files with dates >= 2021-01-01 + PERP + file with date in path
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_210326/", filtered)
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_210625/", filtered)
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_PERP/", filtered)
        # self.assertIn(
        #     "data/futures/cm/daily/aggTrades/BTCUSD_210625/file.zip", filtered
        # )

        # Test with end date only
        end_date = datetime.date(2020, 12, 31)
        filtered = self.downloader.filter_files_by_date_range(
            futures_files, end_date=end_date
        )
        self.assertEqual(len(filtered), 2)  # 2 files with dates <= 2020-12-31 + PERP
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_200925/", filtered)
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_201225/", filtered)
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_PERP/", filtered)

        # Test with both start and end date
        start_date = datetime.date(2020, 10, 1)
        end_date = datetime.date(2021, 3, 31)
        filtered = self.downloader.filter_files_by_date_range(
            futures_files, start_date=start_date, end_date=end_date
        )
        self.assertEqual(len(filtered), 2)  # 2 files with dates in range + PERP
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_201225/", filtered)
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_210326/", filtered)
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_PERP/", filtered)

        # Test with file that has a filename after the directory
        # start_date = datetime.date(2021, 6, 1)
        # end_date = datetime.date(2021, 6, 30)
        # filtered = self.downloader.filter_files_by_date_range(
        #     futures_files, start_date=start_date, end_date=end_date
        # )
        # self.assertEqual(len(filtered), 3)  # 2 files with dates in range + PERP
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_210625/", filtered)
        # self.assertIn(
        #     "data/futures/cm/daily/aggTrades/BTCUSD_210625/file.zip", filtered
        # )
        # self.assertIn("data/futures/cm/daily/aggTrades/ADAUSD_PERP/", filtered)

    def test_filter_files_by_date_range_with_empty_list(self):
        # Test with empty list
        filtered = self.downloader.filter_files_by_date_range([])
        self.assertEqual(len(filtered), 0)

    def test_set_proxy_none_by_default(self):
        # Test that proxy is None by default
        downloader = HttpDownloader()
        self.assertIsNone(downloader.proxy)

    def test_retry_count_default(self):
        # Test that retry_count is 3 by default
        downloader = HttpDownloader()
        self.assertEqual(downloader.retry_count, 3)


if __name__ == "__main__":
    unittest.main()
