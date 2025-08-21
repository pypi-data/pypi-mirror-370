import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import datetime
import argparse

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cli.cli import CliApp


class TestCliApp(unittest.TestCase):
    
    def setUp(self):
        self.app = CliApp()
    
    def test_parse_args_defaults(self):
        # Test default argument values
        with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
            proxy=None,
            retry_count=3,
            max_concurrent_downloads=5,
            output_dir='./downloads',
            verify_checksum=False,
            log_level='INFO'
        )):
            args = self.app._parse_args()
            
            self.assertIsNone(args.proxy)
            self.assertEqual(args.retry_count, 3)
            self.assertEqual(args.max_concurrent_downloads, 5)
            self.assertEqual(args.output_dir, './downloads')
            self.assertFalse(args.verify_checksum)
            self.assertEqual(args.log_level, 'INFO')
    
    @patch('os.makedirs')
    @patch('src.cli.cli.logger')
    def test_configure_from_args(self, mock_logger, mock_makedirs):
        # Test configuration from arguments
        args = argparse.Namespace(
            proxy='http://proxy.example.com:8080',
            retry_count=5,
            max_concurrent_downloads=10,
            output_dir='/tmp/downloads',
            verify_checksum=True,
            log_level='DEBUG'
        )
        
        # Mock the downloader
        self.app.downloader = MagicMock()
        
        # Call the method
        self.app._configure_from_args(args)
        
        # Check that the downloader was configured correctly
        self.app.downloader.set_proxy.assert_called_once_with('http://proxy.example.com:8080')
        self.app.downloader.set_retry_count.assert_called_once_with(5)
        
        # Check that the output directory was created
        mock_makedirs.assert_called_once_with('/tmp/downloads', exist_ok=True)
    
    def test_display_progress(self):
        # Test progress display
        self.app.progress_bar = MagicMock()
        
        self.app._display_progress(1, 10, 'file.zip')
        
        self.app.progress_bar.update.assert_called_once_with(1)
        self.app.progress_bar.set_description.assert_called_once_with('Downloading file.zip')
    
    @patch('prompt_toolkit.prompt')
    def test_prompt_for_date_range_valid(self, mock_prompt):
        # Test valid date range input
        mock_prompt.side_effect = ['2020-01-01', '2020-01-31']
        
        start_date, end_date = self.app._prompt_for_date_range()
        
        self.assertEqual(start_date, datetime.date(2020, 1, 1))
        self.assertEqual(end_date, datetime.date(2020, 1, 31))
    
    @patch('prompt_toolkit.prompt')
    def test_prompt_for_date_range_empty(self, mock_prompt):
        # Test empty date range input
        mock_prompt.side_effect = ['', '']
        
        start_date, end_date = self.app._prompt_for_date_range()
        
        self.assertIsNone(start_date)
        self.assertIsNone(end_date)
    
    @patch('builtins.print')
    @patch('prompt_toolkit.prompt')
    def test_select_from_list(self, mock_prompt, mock_print):
        # Test item selection
        items = ['item1', 'item2', 'item3']
        mock_prompt.return_value = '2'
        
        selected = self.app._select_from_list(items, 'Select an item:')
        
        self.assertEqual(selected, 'item2')
        mock_prompt.assert_called_once()


if __name__ == '__main__':
    unittest.main()
