#!/usr/bin/env python3
"""
Setup script for multi-browser-crawler package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Multi-Browser Crawler - Enterprise-grade browser automation package"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="multi-browser-crawler",
    version="0.1.0",
    author="Spider MCP Team",
    author_email="team@spider-mcp.com",
    description="Enterprise-grade browser automation with advanced features",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/spider-mcp/multi-browser-crawler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "performance": [
            "uvloop>=0.17.0; sys_platform != 'win32'",
            "orjson>=3.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "multi-browser-crawler=multi_browser_crawler.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "multi_browser_crawler": [
            "config/*.json",
            "utils/*.js",
            "data/*.txt",
        ],
    },
    keywords=[
        "browser", "automation", "crawling", "scraping", "playwright", 
        "selenium", "web", "testing", "multiprocess", "proxy"
    ],
    project_urls={
        "Bug Reports": "https://github.com/spider-mcp/multi-browser-crawler/issues",
        "Source": "https://github.com/spider-mcp/multi-browser-crawler",
        "Documentation": "https://multi-browser-crawler.readthedocs.io/",
    },
)
