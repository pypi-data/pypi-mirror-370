import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import xmltodict

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.directory_tree.binance import BinanceDirectoryTreeProvider


class TestBinanceDirectoryTreeProvider(unittest.TestCase):
    
    def setUp(self):
        self.provider = BinanceDirectoryTreeProvider()
    
    def test_get_download_url_prefix(self):
        self.assertEqual(self.provider.get_download_url_prefix(), "https://data.binance.vision/")
    
    @patch('src.directory_tree.binance.httpx.get')
    def test_get_directory_tree_with_common_prefixes(self, mock_get):
        # Mock response with CommonPrefixes
        mock_response = MagicMock()
        mock_response.text = '''
        <ListBucketResult>
            <Name>data.binance.vision</Name>
            <Prefix>data/spot/daily/</Prefix>
            <Marker></Marker>
            <MaxKeys>1000</MaxKeys>
            <IsTruncated>false</IsTruncated>
            <CommonPrefixes>
                <Prefix>data/spot/daily/aggTrades/</Prefix>
            </CommonPrefixes>
            <CommonPrefixes>
                <Prefix>data/spot/daily/klines/</Prefix>
            </CommonPrefixes>
        </ListBucketResult>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.provider.get_directory_tree("data/spot/daily/")
        
        self.assertEqual(len(result), 2)
        self.assertIn("data/spot/daily/aggTrades/", result)
        self.assertIn("data/spot/daily/klines/", result)
    
    @patch('src.directory_tree.binance.httpx.get')
    def test_get_directory_tree_with_contents(self, mock_get):
        # Mock response with Contents
        mock_response = MagicMock()
        mock_response.text = '''
        <ListBucketResult>
            <Name>data.binance.vision</Name>
            <Prefix>data/spot/daily/klines/BTCUSDT/</Prefix>
            <Marker></Marker>
            <MaxKeys>1000</MaxKeys>
            <IsTruncated>false</IsTruncated>
            <Contents>
                <Key>data/spot/daily/klines/BTCUSDT/BTCUSDT-daily-2020-01-01.zip</Key>
                <LastModified>2020-01-02T00:00:00.000Z</LastModified>
                <ETag>"abcdef1234567890"</ETag>
                <Size>1234567</Size>
                <StorageClass>STANDARD</StorageClass>
            </Contents>
            <Contents>
                <Key>data/spot/daily/klines/BTCUSDT/BTCUSDT-daily-2020-01-01.zip.CHECKSUM</Key>
                <LastModified>2020-01-02T00:00:00.000Z</LastModified>
                <ETag>"abcdef1234567890"</ETag>
                <Size>64</Size>
                <StorageClass>STANDARD</StorageClass>
            </Contents>
        </ListBucketResult>
        '''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.provider.get_directory_tree("data/spot/daily/klines/BTCUSDT/")
        
        self.assertEqual(len(result), 2)
        self.assertIn("data/spot/daily/klines/BTCUSDT/BTCUSDT-daily-2020-01-01.zip", result)
        self.assertIn("data/spot/daily/klines/BTCUSDT/BTCUSDT-daily-2020-01-01.zip.CHECKSUM", result)
    
    @patch('src.directory_tree.binance.httpx.get')
    def test_get_directory_tree_with_pagination(self, mock_get):
        # Mock first response with pagination
        first_response = MagicMock()
        first_response.text = '''
        <ListBucketResult>
            <Name>data.binance.vision</Name>
            <Prefix>data/spot/daily/</Prefix>
            <Marker></Marker>
            <MaxKeys>1000</MaxKeys>
            <IsTruncated>true</IsTruncated>
            <NextMarker>data/spot/daily/klines/</NextMarker>
            <CommonPrefixes>
                <Prefix>data/spot/daily/aggTrades/</Prefix>
            </CommonPrefixes>
        </ListBucketResult>
        '''
        first_response.raise_for_status.return_value = None
        
        # Mock second response
        second_response = MagicMock()
        second_response.text = '''
        <ListBucketResult>
            <Name>data.binance.vision</Name>
            <Prefix>data/spot/daily/</Prefix>
            <Marker>data/spot/daily/klines/</Marker>
            <MaxKeys>1000</MaxKeys>
            <IsTruncated>false</IsTruncated>
            <CommonPrefixes>
                <Prefix>data/spot/daily/klines/</Prefix>
            </CommonPrefixes>
        </ListBucketResult>
        '''
        second_response.raise_for_status.return_value = None
        
        # Configure mock to return different responses
        mock_get.side_effect = [first_response, second_response]
        
        result = self.provider.get_directory_tree("data/spot/daily/")
        
        self.assertEqual(len(result), 2)
        self.assertIn("data/spot/daily/aggTrades/", result)
        self.assertIn("data/spot/daily/klines/", result)
    
    @patch('src.directory_tree.binance.BinanceDirectoryTreeProvider.get_directory_tree')
    def test_get_available_data_types(self, mock_get_directory_tree):
        mock_get_directory_tree.return_value = [
            "data/spot/",
            "data/futures/",
            "data/options/"
        ]
        
        result = self.provider.get_available_data_types()
        
        self.assertEqual(len(result), 3)
        self.assertIn("spot", result)
        self.assertIn("futures", result)
        self.assertIn("options", result)
    
    @patch('src.directory_tree.binance.BinanceDirectoryTreeProvider.get_directory_tree')
    def test_get_available_intervals(self, mock_get_directory_tree):
        mock_get_directory_tree.return_value = [
            "data/spot/daily/",
            "data/spot/monthly/"
        ]
        
        result = self.provider.get_available_intervals("spot")
        
        self.assertEqual(len(result), 2)
        self.assertIn("daily", result)
        self.assertIn("monthly", result)
    
    @patch('src.directory_tree.binance.BinanceDirectoryTreeProvider.get_directory_tree')
    def test_get_available_symbols(self, mock_get_directory_tree):
        mock_get_directory_tree.return_value = [
            "data/spot/daily/BTCUSDT/",
            "data/spot/daily/ETHUSDT/"
        ]
        
        result = self.provider.get_available_symbols("spot", "daily")
        
        self.assertEqual(len(result), 2)
        self.assertIn("BTCUSDT", result)
        self.assertIn("ETHUSDT", result)


if __name__ == '__main__':
    unittest.main()
