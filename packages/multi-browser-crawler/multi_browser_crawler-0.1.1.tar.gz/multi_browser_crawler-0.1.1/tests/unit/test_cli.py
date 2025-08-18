"""
Unit tests for CLI functionality.
"""

import pytest
import asyncio
import sys
from unittest.mock import patch, AsyncMock, MagicMock
from io import StringIO

from multi_browser_crawler.cli import (
    create_parser, 
    main, 
    cli_main,
    fetch_command,
    discover_apis_command,
    execute_js_command,
    batch_command,
    format_output
)


class TestCLI:
    """Test CLI functionality."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        
        # Test basic parser properties
        assert parser.prog == "multi-browser-crawler"
        assert "Enterprise-grade browser automation" in parser.description
        
        # Test that subparsers are created (version will exit, so catch it)
        with pytest.raises(SystemExit):
            args = parser.parse_args(["--version"])
    
    def test_parser_version(self):
        """Test version argument."""
        parser = create_parser()
        
        with patch('sys.exit') as mock_exit:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                try:
                    parser.parse_args(["--version"])
                except SystemExit:
                    pass
        
        # Should have attempted to exit (version command exits)
        mock_exit.assert_called_once_with(0)
    
    def test_parser_help(self):
        """Test help argument."""
        parser = create_parser()
        
        with patch('sys.exit') as mock_exit:
            with patch('sys.stdout', new_callable=StringIO):
                try:
                    parser.parse_args(["--help"])
                except SystemExit:
                    pass
        
        # Should have attempted to exit (help command exits)
        mock_exit.assert_called_once_with(0)
    
    def test_fetch_subcommand_parsing(self):
        """Test fetch subcommand parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "fetch", 
            "https://example.com",
            "--download-images",
            "--execute-js", "console.log('test')"
        ])
        
        assert args.command == "fetch"
        assert args.url == "https://example.com"
        assert args.download_images is True
        assert args.execute_js == "console.log('test')"
    
    def test_discover_apis_subcommand_parsing(self):
        """Test discover-apis subcommand parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "discover-apis",
            "https://api.example.com"
        ])
        
        assert args.command == "discover-apis"
        assert args.url == "https://api.example.com"
    
    def test_execute_js_subcommand_parsing(self):
        """Test execute-js subcommand parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "execute-js",
            "https://example.com",
            "return document.title"
        ])
        
        assert args.command == "execute-js"
        assert args.url == "https://example.com"
        assert args.code == "return document.title"
    
    def test_batch_subcommand_parsing(self):
        """Test batch subcommand parsing."""
        parser = create_parser()
        
        args = parser.parse_args([
            "batch",
            "https://site1.com",
            "https://site2.com",
            "--max-concurrent", "5"
        ])
        
        assert args.command == "batch"
        assert args.urls == ["https://site1.com", "https://site2.com"]
        assert args.max_concurrent == 5
    
    @pytest.mark.asyncio
    async def test_fetch_command(self):
        """Test fetch command execution."""
        # Mock arguments
        args = MagicMock()
        args.url = "https://example.com"
        args.download_images = False
        args.execute_js = None
        args.headless = True
        args.timeout = 30
        
        # Mock BrowserCrawler
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.title = "Test Title"
        mock_result.html = "<html>Test</html>"
        mock_result.images = []
        mock_result.error = None
        mock_result.metadata = {}
        
        mock_crawler = AsyncMock()
        mock_crawler.fetch.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None
        
        with patch('multi_browser_crawler.cli.BrowserCrawler', return_value=mock_crawler):
            result = await fetch_command(args)
        
        assert result["command"] == "fetch"
        assert result["url"] == "https://example.com"
        assert result["success"] is True
        assert result["title"] == "Test Title"
        assert result["html_length"] == len("<html>Test</html>")
    
    @pytest.mark.asyncio
    async def test_discover_apis_command(self):
        """Test discover-apis command execution."""
        # Mock arguments
        args = MagicMock()
        args.url = "https://api.example.com"
        args.headless = True
        args.timeout = 30
        
        # Mock result
        mock_result = {
            "success": True,
            "total_api_calls": 5,
            "api_calls": [{"url": "https://api.example.com/data"}],
            "discovery_summary": {"found": 5}
        }
        
        mock_crawler = AsyncMock()
        mock_crawler.discover_apis.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None
        
        with patch('multi_browser_crawler.cli.BrowserCrawler', return_value=mock_crawler):
            result = await discover_apis_command(args)
        
        assert result["command"] == "discover-apis"
        assert result["url"] == "https://api.example.com"
        assert result["success"] is True
        assert result["total_api_calls"] == 5
    
    @pytest.mark.asyncio
    async def test_execute_js_command(self):
        """Test execute-js command execution."""
        # Mock arguments
        args = MagicMock()
        args.url = "https://example.com"
        args.code = "return document.title"
        args.headless = True
        args.timeout = 30
        
        # Mock result
        mock_result = {
            "success": True,
            "result": "Test Title"
        }
        
        mock_crawler = AsyncMock()
        mock_crawler.execute_js.return_value = mock_result
        mock_crawler.__aenter__.return_value = mock_crawler
        mock_crawler.__aexit__.return_value = None
        
        with patch('multi_browser_crawler.cli.BrowserCrawler', return_value=mock_crawler):
            result = await execute_js_command(args)
        
        assert result["command"] == "execute-js"
        assert result["url"] == "https://example.com"
        assert result["code"] == "return document.title"
        assert result["success"] is True
        assert result["result"] == "Test Title"
    
    def test_format_output_json(self):
        """Test JSON output formatting."""
        result = {
            "command": "fetch",
            "url": "https://example.com",
            "success": True
        }
        
        output = format_output(result, "json")
        
        assert '"command": "fetch"' in output
        assert '"url": "https://example.com"' in output
        assert '"success": true' in output
    
    def test_format_output_text(self):
        """Test text output formatting."""
        result = {
            "command": "fetch",
            "url": "https://example.com",
            "success": True,
            "title": "Test Title",
            "html_length": 100
        }
        
        output = format_output(result, "text")
        
        assert "URL: https://example.com" in output
        assert "Success: True" in output
        assert "Title: Test Title" in output
        assert "HTML Length: 100" in output
    
    @pytest.mark.asyncio
    async def test_main_no_command(self):
        """Test main function with no command."""
        with patch('sys.argv', ['multi-browser-crawler']):
            with patch('sys.stdout', new_callable=StringIO):
                result = await main()
        
        assert result == 1  # Should return error code
    
    @pytest.mark.asyncio
    async def test_main_with_fetch_command(self):
        """Test main function with fetch command."""
        test_args = [
            'multi-browser-crawler',
            'fetch',
            'https://example.com'
        ]
        
        # Mock the fetch command
        with patch('sys.argv', test_args):
            with patch('multi_browser_crawler.cli.fetch_command') as mock_fetch:
                mock_fetch.return_value = {"success": True}
                with patch('sys.stdout', new_callable=StringIO):
                    result = await main()
        
        assert result == 0  # Should return success
        mock_fetch.assert_called_once()
    
    def test_cli_main_success(self):
        """Test cli_main function success case."""
        with patch('asyncio.run') as mock_run:
            mock_run.return_value = 0

            with patch('sys.exit') as mock_exit:
                cli_main()

            mock_exit.assert_called_once_with(0)
    
    def test_cli_main_keyboard_interrupt(self):
        """Test cli_main function with keyboard interrupt."""
        with patch('asyncio.run') as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            with patch('sys.exit') as mock_exit:
                cli_main()

            mock_exit.assert_called_once_with(130)
