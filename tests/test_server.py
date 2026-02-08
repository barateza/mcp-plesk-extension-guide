"""Tests for server.py module"""

import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch, mock_open
import server


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestHTMLParser:
    """Tests for parse_sphinx_html function"""

    def test_parse_valid_html(self, temp_dir):
        """Test parsing a valid HTML file"""
        test_html = """
        <html>
            <head>
                <title>Test Page — Developing Extensions for Plesk</title>
            </head>
            <body>
                <div itemprop="articleBody">
                    <h1>Test Content</h1>
                    <p>This is a test paragraph.</p>
                </div>
            </body>
        </html>
        """
        
        test_file = temp_dir / "test_page.htm"
        test_file.write_text(test_html, encoding="utf-8")
        
        title, content = server.parse_sphinx_html(test_file)
        
        assert title == "Test Page"
        assert "Test Content" in content
        assert "This is a test paragraph" in content

    def test_parse_html_without_article_body(self, temp_dir):
        """Test parsing HTML without itemprop='articleBody'"""
        test_html = """
        <html>
            <head>
                <title>Test Page — Developing Extensions for Plesk</title>
            </head>
            <body>
                <h1>Test Content</h1>
                <p>This is a test paragraph.</p>
            </body>
        </html>
        """
        
        test_file = temp_dir / "test_page.htm"
        test_file.write_text(test_html, encoding="utf-8")
        
        title, content = server.parse_sphinx_html(test_file)
        
        assert title == "Test Page"
        assert "Test Content" in content
        assert "This is a test paragraph" in content

    def test_parse_html_with_nav_and_scripts(self, temp_dir):
        """Test parsing HTML with navigation and script tags"""
        test_html = """
        <html>
            <head>
                <title>Test Page — Developing Extensions for Plesk</title>
                <script>console.log('test');</script>
            </head>
            <body>
                <nav>Navigation links</nav>
                <div itemprop="articleBody">
                    <h1>Test Content</h1>
                    <p>This is a test paragraph.</p>
                </div>
                <script>another script</script>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        
        test_file = temp_dir / "test_page.htm"
        test_file.write_text(test_html, encoding="utf-8")
        
        title, content = server.parse_sphinx_html(test_file)
        
        assert title == "Test Page"
        assert "Test Content" in content
        assert "This is a test paragraph" in content
        assert "Navigation links" not in content
        assert "console.log" not in content
        assert "Footer content" not in content

    def test_parse_empty_html(self, temp_dir):
        """Test parsing an empty HTML file"""
        test_file = temp_dir / "empty.htm"
        test_file.write_text("", encoding="utf-8")
        
        title, content = server.parse_sphinx_html(test_file)
        
        assert title == "Untitled"
        assert content is None

    def test_parse_nonexistent_file(self, temp_dir):
        """Test parsing a nonexistent file (should handle error gracefully)"""
        non_existent_file = temp_dir / "nonexistent.htm"
        
        title, content = server.parse_sphinx_html(non_existent_file)
        
        assert title == "Untitled"
        assert content is None


class TestServer:
    """Tests for server.py module"""

    @patch("server.get_db_client")
    @patch("server.get_embedding_fn")
    def test_index_extensions_guide(self, mock_embedding_fn, mock_db_client, temp_dir):
        """Test the index_extensions_guide tool"""
        # Create test files
        (temp_dir / "doc1.htm").write_text("""<html><body>Test content 1 with enough length to meet the 50 character requirement for indexing.</body></html>""", encoding="utf-8")
        (temp_dir / "_private.htm").write_text("<html><body>Private content</body></html>", encoding="utf-8")
        
        # Mock the collection
        mock_collection = MagicMock()
        mock_collection.upsert = MagicMock()
        
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_instance.get_or_create_collection.return_value = mock_collection
        mock_db_client.return_value = mock_db_instance
        
        # Run the indexing
        with patch("server.DOCS_DIR", temp_dir):
            result = server.index_extensions_guide()
        
        assert "Processed 1 documentation files" in result
        mock_collection.upsert.assert_called_once()

    @patch("server.get_db_client")
    @patch("server.get_embedding_fn")
    def test_search_extensions_guide(self, mock_embedding_fn, mock_db_client):
        """Test the search_extensions_guide tool"""
        # Setup mock results
        mock_results = {
            "documents": [["Test document content"]],
            "metadatas": [[{"title": "Test Document", "filename": "test.doc"}]]
        }
        
        # Setup mocks
        mock_collection = MagicMock()
        mock_collection.query.return_value = mock_results
        
        mock_db_instance = MagicMock()
        mock_db_instance.get_collection.return_value = mock_collection
        mock_db_client.return_value = mock_db_instance
        
        result = server.search_extensions_guide("test query")
        
        assert "Test Document" in result
        assert "Test document content" in result
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=3
        )

    @patch("server.get_db_client")
    @patch("server.get_embedding_fn")
    def test_search_extensions_guide_no_results(self, mock_embedding_fn, mock_db_client):
        """Test search_extensions_guide with no results"""
        # Setup mock results with no documents
        mock_results = {
            "documents": [[]],
            "metadatas": [[]]
        }
        
        # Setup mocks
        mock_collection = MagicMock()
        mock_collection.query.return_value = mock_results
        
        mock_db_instance = MagicMock()
        mock_db_instance.get_collection.return_value = mock_collection
        mock_db_client.return_value = mock_db_instance
        
        result = server.search_extensions_guide("nonexistent query")
        
        assert "No relevant documentation found" in result

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=True)
    def test_get_embedding_fn_with_env_var(self):
        """Test get_embedding_fn with valid API key"""
        ef = server.get_embedding_fn()
        
        assert hasattr(ef, "__call__")
        assert ef is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_get_embedding_fn_without_env_var(self):
        """Test get_embedding_fn without API key"""
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY not found"):
            server.get_embedding_fn()