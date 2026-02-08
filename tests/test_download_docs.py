"""Tests for download_docs.py module"""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
from scripts import download_docs


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestDownloadDocs:
    """Tests for download_docs.py module"""

    @patch('urllib.request.urlretrieve')
    def test_download_docs_success(self, mock_urlretrieve, temp_dir):
        """Test download_docs function with successful download"""
        with patch('scripts.download_docs.ZIP_FILE', temp_dir / 'test.zip'):
            result = download_docs.download_docs()
            assert result is True
            mock_urlretrieve.assert_called_once()

    @patch('urllib.request.urlretrieve', side_effect=Exception('Download failed'))
    def test_download_docs_failure(self, mock_urlretrieve, temp_dir):
        """Test download_docs function with download failure"""
        with patch('scripts.download_docs.ZIP_FILE', temp_dir / 'test.zip'):
            result = download_docs.download_docs()
            assert result is False

    @patch('zipfile.ZipFile')
    def test_extract_docs_success(self, mock_zip_file, temp_dir):
        """Test extract_docs function with successful extraction"""
        zip_path = temp_dir / 'test.zip'
        zip_path.touch()
        
        mock_zip_instance = MagicMock()
        
        with patch('scripts.download_docs.ZIP_FILE', zip_path), \
             patch('scripts.download_docs.HTML_DIR', temp_dir / 'html'):
            
            result = download_docs.extract_docs()
            
            assert result is True
            temp_dir.joinpath('html').exists()

    def test_extract_docs_missing_file(self, temp_dir):
        """Test extract_docs function with missing zip file"""
        with patch('scripts.download_docs.ZIP_FILE', temp_dir / 'nonexistent.zip'), \
             patch('scripts.download_docs.HTML_DIR', temp_dir / 'html'):
            
            result = download_docs.extract_docs()
            assert result is False

    @patch('zipfile.ZipFile', side_effect=Exception('Extract failed'))
    def test_extract_docs_extract_failure(self, mock_zip_file, temp_dir):
        """Test extract_docs function with extraction failure"""
        zip_path = temp_dir / 'test.zip'
        zip_path.touch()
        
        with patch('scripts.download_docs.ZIP_FILE', zip_path), \
             patch('scripts.download_docs.HTML_DIR', temp_dir / 'html'):
            
            result = download_docs.extract_docs()
            assert result is False

    @patch('os.chmod')
    def test_setup_storage_dir_success(self, mock_chmod, temp_dir):
        """Test setup_storage_dir function with successful setup"""
        with patch('scripts.download_docs.STORAGE_DIR', temp_dir / 'storage'):
            result = download_docs.setup_storage_dir()
            assert result is True
            assert (temp_dir / 'storage').exists()
            mock_chmod.assert_called_once()

    @patch('os.chmod', side_effect=Exception('Permission error'))
    def test_setup_storage_dir_failure(self, mock_chmod, temp_dir):
        """Test setup_storage_dir function with failure"""
        with patch('scripts.download_docs.STORAGE_DIR', temp_dir / 'storage'):
            result = download_docs.setup_storage_dir()
            assert result is False

    def test_cleanup_zip_success(self, temp_dir):
        """Test cleanup_zip function with successful cleanup"""
        zip_path = temp_dir / 'test.zip'
        zip_path.touch()
        
        with patch('scripts.download_docs.ZIP_FILE', zip_path):
            download_docs.cleanup_zip()
            assert not zip_path.exists()

    @patch('os.remove', side_effect=Exception('Remove failed'))
    def test_cleanup_zip_failure(self, mock_remove, temp_dir):
        """Test cleanup_zip function with failure to remove"""
        zip_path = temp_dir / 'test.zip'
        zip_path.touch()
        
        with patch('scripts.download_docs.ZIP_FILE', zip_path):
            # Should not raise exception
            download_docs.cleanup_zip()

    def test_cleanup_zip_nonexistent(self, temp_dir):
        """Test cleanup_zip function with non-existent file"""
        with patch('scripts.download_docs.ZIP_FILE', temp_dir / 'nonexistent.zip'):
            # Should not raise exception
            download_docs.cleanup_zip()

    @patch('scripts.download_docs.download_docs', return_value=True)
    @patch('scripts.download_docs.extract_docs', return_value=True)
    @patch('scripts.download_docs.setup_storage_dir', return_value=True)
    @patch('scripts.download_docs.cleanup_zip')
    def test_main_success(self, mock_cleanup, mock_setup, mock_extract, mock_download):
        """Test main function with successful execution"""
        with patch('sys.exit') as mock_exit:
            download_docs.main()
            mock_download.assert_called_once()
            mock_extract.assert_called_once()
            mock_setup.assert_called_once()
            mock_cleanup.assert_called_once()
            mock_exit.assert_not_called()

    @patch('scripts.download_docs.download_docs', return_value=False)
    @patch('scripts.download_docs.extract_docs')
    @patch('scripts.download_docs.setup_storage_dir')
    @patch('scripts.download_docs.cleanup_zip')
    def test_main_download_failure(self, mock_cleanup, mock_setup, mock_extract, mock_download):
        """Test main function with download failure"""
        with patch('sys.exit') as mock_exit:
            download_docs.main()
            mock_download.assert_called_once()
            mock_extract.assert_called_once()  # Extract docs is called but returns False
            mock_setup.assert_called_once()  # Setup storage is called but returns False
            mock_cleanup.assert_called_once()  # Cleanup is always called
            mock_exit.assert_called_once_with(1)

    @patch('scripts.download_docs.download_docs', return_value=True)
    @patch('scripts.download_docs.extract_docs', return_value=False)
    @patch('scripts.download_docs.setup_storage_dir')
    @patch('scripts.download_docs.cleanup_zip')
    def test_main_extract_failure(self, mock_cleanup, mock_setup, mock_extract, mock_download):
        """Test main function with extraction failure"""
        with patch('sys.exit') as mock_exit:
            download_docs.main()
            mock_download.assert_called_once()
            mock_extract.assert_called_once()
            mock_setup.assert_called_once()  # Setup storage is called but returns False
            mock_cleanup.assert_called_once()  # Cleanup is always called
            mock_exit.assert_called_once_with(1)

    @patch('scripts.download_docs.download_docs', return_value=True)
    @patch('scripts.download_docs.extract_docs', return_value=True)
    @patch('scripts.download_docs.setup_storage_dir', return_value=False)
    @patch('scripts.download_docs.cleanup_zip')
    def test_main_setup_failure(self, mock_cleanup, mock_setup, mock_extract, mock_download):
        """Test main function with storage setup failure"""
        with patch('sys.exit') as mock_exit:
            download_docs.main()
            mock_download.assert_called_once()
            mock_extract.assert_called_once()
            mock_setup.assert_called_once()
            mock_cleanup.assert_called_once()  # Cleanup is always called
            mock_exit.assert_called_once_with(1)

    @patch('pathlib.Path.unlink', side_effect=Exception('Remove failed'))
    def test_cleanup_zip_exception_handler(self, mock_unlink, temp_dir, capsys):
        """Test that cleanup_zip handles exceptions properly and prints warning"""
        zip_path = temp_dir / 'test.zip'
        zip_path.touch()
        
        with patch('scripts.download_docs.ZIP_FILE', zip_path):
            # Should not raise exception
            download_docs.cleanup_zip()
            
            # Verify warning message is printed
            captured = capsys.readouterr()
            assert "Warning: Could not remove" in captured.out