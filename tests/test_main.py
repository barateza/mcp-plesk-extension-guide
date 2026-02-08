"""Tests for main.py module"""

from unittest.mock import patch
import main


def test_main():
    """Test the main function"""
    with patch('builtins.print') as mock_print:
        main.main()
        mock_print.assert_called_once_with("Hello from extensions-guide!")