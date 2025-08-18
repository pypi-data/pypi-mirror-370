"""
Command-line interface for multi-browser-crawler.
"""

import argparse
import asyncio
import json
import sys
from typing import Dict, Any

from . import BrowserCrawler, BrowserConfig, __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="multi-browser-crawler",
        description="Enterprise-grade browser automation with advanced features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch a single URL
  multi-browser-crawler fetch https://example.com

  # Discover APIs from a page
  multi-browser-crawler discover-apis https://api.example.com

  # Fetch with custom options
  multi-browser-crawler fetch https://example.com --headless --timeout 30

  # Execute JavaScript on a page
  multi-browser-crawler execute-js https://example.com "return document.title"
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for results (default: stdout)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch HTML content from a URL")
    fetch_parser.add_argument("url", help="URL to fetch")
    fetch_parser.add_argument("--download-images", action="store_true", help="Download images from the page")
    fetch_parser.add_argument("--execute-js", help="JavaScript code to execute on the page")
    
    # Discover APIs command
    api_parser = subparsers.add_parser("discover-apis", help="Discover API calls from a page")
    api_parser.add_argument("url", help="URL to analyze for API calls")
    
    # Execute JavaScript command
    js_parser = subparsers.add_parser("execute-js", help="Execute JavaScript on a page")
    js_parser.add_argument("url", help="URL to load")
    js_parser.add_argument("code", help="JavaScript code to execute")
    
    # Batch fetch command
    batch_parser = subparsers.add_parser("batch", help="Fetch multiple URLs concurrently")
    batch_parser.add_argument("urls", nargs="+", help="URLs to fetch")
    batch_parser.add_argument("--max-concurrent", type=int, default=3, help="Maximum concurrent requests")
    
    return parser


async def fetch_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Handle the fetch command."""
    config = BrowserConfig(
        headless=args.headless,
        page_timeout=args.timeout * 1000
    )
    
    async with BrowserCrawler(config) as crawler:
        result = await crawler.fetch(
            args.url,
            download_images=args.download_images,
            execute_js=args.execute_js
        )
        
        return {
            "command": "fetch",
            "url": args.url,
            "success": result.success,
            "title": result.title,
            "html_length": len(result.html),
            "images_count": len(result.images) if result.images else 0,
            "error": result.error,
            "metadata": result.metadata
        }


async def discover_apis_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Handle the discover-apis command."""
    config = BrowserConfig(
        headless=args.headless,
        page_timeout=args.timeout * 1000
    )
    
    async with BrowserCrawler(config) as crawler:
        result = await crawler.discover_apis(args.url)
        
        return {
            "command": "discover-apis",
            "url": args.url,
            "success": result.get("success", False),
            "total_api_calls": result.get("total_api_calls", 0),
            "api_calls": result.get("api_calls", []),
            "discovery_summary": result.get("discovery_summary", {}),
            "error": result.get("error")
        }


async def execute_js_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Handle the execute-js command."""
    config = BrowserConfig(
        headless=args.headless,
        page_timeout=args.timeout * 1000
    )
    
    async with BrowserCrawler(config) as crawler:
        result = await crawler.execute_js(args.url, args.code)
        
        return {
            "command": "execute-js",
            "url": args.url,
            "code": args.code,
            "success": result.get("success", False),
            "result": result.get("result"),
            "error": result.get("error")
        }


async def batch_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Handle the batch command."""
    config = BrowserConfig(
        headless=args.headless,
        page_timeout=args.timeout * 1000
    )
    
    async with BrowserCrawler(config) as crawler:
        results = await crawler.fetch_batch(
            args.urls,
            max_concurrent=args.max_concurrent
        )
        
        return {
            "command": "batch",
            "urls": args.urls,
            "total_urls": len(args.urls),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [
                {
                    "url": r.url,
                    "success": r.success,
                    "title": r.title,
                    "html_length": len(r.html),
                    "error": r.error
                }
                for r in results
            ]
        }


def format_output(result: Dict[str, Any], format_type: str) -> str:
    """Format the output based on the specified format."""
    if format_type == "json":
        return json.dumps(result, indent=2, default=str)
    elif format_type == "text":
        if result.get("command") == "fetch":
            return f"URL: {result['url']}\nSuccess: {result['success']}\nTitle: {result.get('title', 'N/A')}\nHTML Length: {result['html_length']}"
        elif result.get("command") == "discover-apis":
            return f"URL: {result['url']}\nSuccess: {result['success']}\nAPI Calls Found: {result['total_api_calls']}"
        elif result.get("command") == "execute-js":
            return f"URL: {result['url']}\nSuccess: {result['success']}\nResult: {result.get('result', 'N/A')}"
        elif result.get("command") == "batch":
            return f"Total URLs: {result['total_urls']}\nSuccessful: {result['successful']}\nFailed: {result['failed']}"
    
    return str(result)


async def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute the appropriate command
        if args.command == "fetch":
            result = await fetch_command(args)
        elif args.command == "discover-apis":
            result = await discover_apis_command(args)
        elif args.command == "execute-js":
            result = await execute_js_command(args)
        elif args.command == "batch":
            result = await batch_command(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        # Format and output the result
        output = format_output(result, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cli_main() -> None:
    """Synchronous wrapper for the main CLI function."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    cli_main()
