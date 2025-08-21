import pytest
from unittest.mock import patch, Mock
from mcp.types import TextContent
from mcp_logseq.tools import (
    CreatePageToolHandler,
    ListPagesToolHandler,
    GetPageContentToolHandler,
    DeletePageToolHandler,
    UpdatePageToolHandler,
    SearchToolHandler
)

class TestCreatePageToolHandler:
    """Test cases for CreatePageToolHandler."""

    def test_get_tool_description(self):
        """Test tool description schema."""
        handler = CreatePageToolHandler()
        tool = handler.get_tool_description()
        
        assert tool.name == "create_page"
        assert "Create a new page in LogSeq" in tool.description
        assert tool.inputSchema["required"] == ["title", "content"]

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success(self, mock_logseq_class):
        """Test successful page creation."""
        # Setup mock
        mock_api = Mock()
        mock_logseq_class.return_value = mock_api
        
        handler = CreatePageToolHandler()
        args = {"title": "Test Page", "content": "Test content"}
        
        result = handler.run_tool(args)
        
        # Verify API was called correctly
        mock_api.create_page.assert_called_once_with("Test Page", "Test content")
        
        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Successfully created page 'Test Page'" in result[0].text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    def test_run_tool_missing_args(self):
        """Test tool with missing required arguments."""
        handler = CreatePageToolHandler()
        
        with pytest.raises(RuntimeError, match="title and content arguments required"):
            handler.run_tool({"title": "Test"})  # Missing content
        
        with pytest.raises(RuntimeError, match="title and content arguments required"):
            handler.run_tool({"content": "Test"})  # Missing title

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_api_error(self, mock_logseq_class):
        """Test tool with API error."""
        # Setup mock to raise exception
        mock_api = Mock()
        mock_api.create_page.side_effect = Exception("API Error")
        mock_logseq_class.return_value = mock_api
        
        handler = CreatePageToolHandler()
        args = {"title": "Test Page", "content": "Test content"}
        
        with pytest.raises(Exception, match="API Error"):
            handler.run_tool(args)


class TestListPagesToolHandler:
    """Test cases for ListPagesToolHandler."""

    def test_get_tool_description(self):
        """Test tool description schema."""
        handler = ListPagesToolHandler()
        tool = handler.get_tool_description()
        
        assert tool.name == "list_pages"
        assert "Lists all pages in a LogSeq graph" in tool.description
        assert tool.inputSchema["required"] == []

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success_exclude_journals(self, mock_logseq_class):
        """Test successful page listing excluding journals."""
        # Setup mock
        mock_api = Mock()
        mock_api.list_pages.return_value = [
            {"originalName": "Regular Page", "journal?": False},
            {"originalName": "Journal Page", "journal?": True},
            {"name": "Another Page", "journal?": False}
        ]
        mock_logseq_class.return_value = mock_api
        
        handler = ListPagesToolHandler()
        result = handler.run_tool({"include_journals": False})
        
        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        text = result[0].text
        
        assert "Regular Page" in text
        assert "Another Page" in text
        assert "Journal Page" not in text
        assert "Total pages: 2" in text
        assert "(excluding journal pages)" in text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success_include_journals(self, mock_logseq_class):
        """Test successful page listing including journals."""
        # Setup mock
        mock_api = Mock()
        mock_api.list_pages.return_value = [
            {"originalName": "Regular Page", "journal?": False},
            {"originalName": "Journal Page", "journal?": True}
        ]
        mock_logseq_class.return_value = mock_api
        
        handler = ListPagesToolHandler()
        result = handler.run_tool({"include_journals": True})
        
        # Verify result
        text = result[0].text
        assert "Regular Page" in text
        assert "Journal Page" in text
        assert "Total pages: 2" in text
        assert "(including journal pages)" in text


class TestGetPageContentToolHandler:
    """Test cases for GetPageContentToolHandler."""

    def test_get_tool_description(self):
        """Test tool description schema."""
        handler = GetPageContentToolHandler()
        tool = handler.get_tool_description()
        
        assert tool.name == "get_page_content"
        assert "Get the content of a specific page" in tool.description
        assert tool.inputSchema["required"] == ["page_name"]

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success_text_format(self, mock_logseq_class):
        """Test successful page content retrieval in text format."""
        # Setup mock
        mock_api = Mock()
        mock_api.get_page_content.return_value = {
            "page": {
                "originalName": "Test Page",
                "properties": {"tags": ["test"], "priority": "high"}
            },
            "blocks": [
                {"content": "Block 1 content"},
                {"content": "Block 2 content"}
            ]
        }
        mock_logseq_class.return_value = mock_api
        
        handler = GetPageContentToolHandler()
        result = handler.run_tool({"page_name": "Test Page", "format": "text"})
        
        # Verify result
        assert len(result) == 1
        text = result[0].text
        
        assert "# Test Page" in text
        assert "tags: ['test']" in text
        assert "priority: high" in text
        assert "Block 1 content" in text
        assert "Block 2 content" in text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success_json_format(self, mock_logseq_class):
        """Test successful page content retrieval in JSON format."""
        # Setup mock
        mock_data = {"page": {"name": "Test"}, "blocks": []}
        mock_api = Mock()
        mock_api.get_page_content.return_value = mock_data
        mock_logseq_class.return_value = mock_api
        
        handler = GetPageContentToolHandler()
        result = handler.run_tool({"page_name": "Test Page", "format": "json"})
        
        # Verify result
        assert str(mock_data) in result[0].text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_page_not_found(self, mock_logseq_class):
        """Test page content retrieval for non-existent page."""
        # Setup mock
        mock_api = Mock()
        mock_api.get_page_content.return_value = None
        mock_logseq_class.return_value = mock_api
        
        handler = GetPageContentToolHandler()
        result = handler.run_tool({"page_name": "Non-existent"})
        
        # Verify result
        assert "Page 'Non-existent' not found" in result[0].text


class TestDeletePageToolHandler:
    """Test cases for DeletePageToolHandler."""

    def test_get_tool_description(self):
        """Test tool description schema."""
        handler = DeletePageToolHandler()
        tool = handler.get_tool_description()
        
        assert tool.name == "delete_page"
        assert "Delete a page from LogSeq" in tool.description
        assert tool.inputSchema["required"] == ["page_name"]

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success(self, mock_logseq_class):
        """Test successful page deletion."""
        # Setup mock
        mock_api = Mock()
        mock_api.delete_page.return_value = {"success": True}
        mock_logseq_class.return_value = mock_api
        
        handler = DeletePageToolHandler()
        result = handler.run_tool({"page_name": "Test Page"})
        
        # Verify API was called
        mock_api.delete_page.assert_called_once_with("Test Page")
        
        # Verify result
        text = result[0].text
        assert "✅ Successfully deleted page 'Test Page'" in text
        assert "🗑️  Page 'Test Page' has been permanently removed" in text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_page_not_found(self, mock_logseq_class):
        """Test deletion of non-existent page."""
        # Setup mock to raise ValueError
        mock_api = Mock()
        mock_api.delete_page.side_effect = ValueError("Page 'Test' does not exist")
        mock_logseq_class.return_value = mock_api
        
        handler = DeletePageToolHandler()
        result = handler.run_tool({"page_name": "Test"})
        
        # Verify error handling
        text = result[0].text
        assert "❌ Error: Page 'Test' does not exist" in text


class TestUpdatePageToolHandler:
    """Test cases for UpdatePageToolHandler."""

    def test_get_tool_description(self):
        """Test tool description schema."""
        handler = UpdatePageToolHandler()
        tool = handler.get_tool_description()
        
        assert tool.name == "update_page"
        assert "Update a page in LogSeq" in tool.description
        assert tool.inputSchema["required"] == ["page_name"]

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success(self, mock_logseq_class):
        """Test successful page update."""
        # Setup mock
        mock_api = Mock()
        mock_api.update_page.return_value = {
            "updates": [("properties", {"success": True}), ("content", {"success": True})],
            "page": "Test Page"
        }
        mock_logseq_class.return_value = mock_api
        
        handler = UpdatePageToolHandler()
        result = handler.run_tool({
            "page_name": "Test Page",
            "content": "New content",
            "properties": {"priority": "high"}
        })
        
        # Verify API was called
        mock_api.update_page.assert_called_once_with(
            "Test Page", 
            content="New content", 
            properties={"priority": "high"}
        )
        
        # Verify result
        text = result[0].text
        assert "✅ Successfully updated page 'Test Page'" in text
        assert "📝 Properties updated" in text
        assert "📄 Content appended" in text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    def test_run_tool_no_updates(self):
        """Test update with no content or properties."""
        handler = UpdatePageToolHandler()
        result = handler.run_tool({"page_name": "Test Page"})
        
        # Verify error handling
        text = result[0].text
        assert "❌ Error: Either 'content' or 'properties' must be provided" in text


class TestSearchToolHandler:
    """Test cases for SearchToolHandler."""

    def test_get_tool_description(self):
        """Test tool description schema."""
        handler = SearchToolHandler()
        tool = handler.get_tool_description()
        
        assert tool.name == "search"
        assert "Search for content across LogSeq pages" in tool.description
        assert tool.inputSchema["required"] == ["query"]

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_success(self, mock_logseq_class):
        """Test successful search."""
        # Setup mock
        mock_api = Mock()
        mock_api.search_content.return_value = {
            "blocks": [{"block/content": "Found content"}],
            "pages": ["Matching Page"],
            "pages-content": [{"block/snippet": "Snippet content"}],
            "files": [],
            "has-more?": False
        }
        mock_logseq_class.return_value = mock_api
        
        handler = SearchToolHandler()
        result = handler.run_tool({"query": "test"})
        
        # Verify API was called
        mock_api.search_content.assert_called_once_with("test", {"limit": 20})
        
        # Verify result
        text = result[0].text
        assert "# Search Results for 'test'" in text
        assert "📄 Content Blocks (1 found)" in text
        assert "Found content" in text
        assert "📑 Matching Pages (1 found)" in text
        assert "Matching Page" in text
        assert "Total results found: 2" in text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_no_results(self, mock_logseq_class):
        """Test search with no results."""
        # Setup mock
        mock_api = Mock()
        mock_api.search_content.return_value = None
        mock_logseq_class.return_value = mock_api
        
        handler = SearchToolHandler()
        result = handler.run_tool({"query": "nothing"})
        
        # Verify result
        text = result[0].text
        assert "No search results found for 'nothing'" in text

    @patch.dict('os.environ', {'LOGSEQ_API_TOKEN': 'test_token'})
    @patch('mcp_logseq.tools.logseq.LogSeq')
    def test_run_tool_with_options(self, mock_logseq_class):
        """Test search with custom options."""
        # Setup mock
        mock_api = Mock()
        mock_api.search_content.return_value = {"blocks": [], "pages": [], "files": []}
        mock_logseq_class.return_value = mock_api
        
        handler = SearchToolHandler()
        result = handler.run_tool({
            "query": "test",
            "limit": 5,
            "include_blocks": False,
            "include_files": True
        })
        
        # Verify API was called with correct options
        mock_api.search_content.assert_called_once_with("test", {"limit": 5})