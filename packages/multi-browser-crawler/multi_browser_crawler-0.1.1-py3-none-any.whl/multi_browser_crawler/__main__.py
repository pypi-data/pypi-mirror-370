"""
Entry point for running multi-browser-crawler as a module.

Usage:
    python -m multi_browser_crawler --help
    python -m multi_browser_crawler fetch https://example.com
"""

from .cli import cli_main

if __name__ == "__main__":
    cli_main()
