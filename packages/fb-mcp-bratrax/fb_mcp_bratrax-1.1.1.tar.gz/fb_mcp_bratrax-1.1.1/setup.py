#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the contents of PyPI description file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "PYPI_DESCRIPTION.md"), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, "requirements.txt"), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="fb-mcp-bratrax",
    version="1.1.1",  # Change from 1.1.0 to 1.1.1
    author="GoMarble AI",
    author_email="support@gomarble.ai",
    description="MCP server for Facebook/Meta Ads API integration enabling programmatic access to Meta Ads data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gomarble-ai/facebook-mcp",
    py_modules=["server"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fb-mcp-bratrax=server:main",
        ],
    },
    keywords="facebook ads mcp server meta marketing api advertising insights campaigns dbt bratrax",
    project_urls={
        "Bug Reports": "https://github.com/gomarble-ai/facebook-mcp/issues",
        "Source": "https://github.com/gomarble-ai/facebook-mcp",
        "Documentation": "https://github.com/gomarble-ai/facebook-mcp/blob/main/readme.md",
        "Community": "https://join.slack.com/t/ai-in-ads/shared_invite/zt-36hntbyf8-FSFixmwLb9mtEzVZhsToJQ",
        "Homepage": "https://gomarble.ai/mcp",
    },
    include_package_data=True,
    package_data={
        "": ["PYPI_DESCRIPTION.md", "LICENSE", "manifest.json", "favicon.png"],
    },
)
