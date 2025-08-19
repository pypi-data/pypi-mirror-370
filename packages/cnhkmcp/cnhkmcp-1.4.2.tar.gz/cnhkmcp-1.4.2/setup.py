from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cnhkmcp",
    version="1.4.2",
    author="CNHK",
    author_email="cnhk@example.com",
    description="A comprehensive Model Context Protocol (MCP) server for quantitative trading platform integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/cnhk/cnhkmcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "cnhkmcp=cnhkmcp.untracked.platform_functions:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    package_data={
        'cnhkmcp': ['untracked/*.py', 'untracked/*.json'],
    },
    keywords="mcp, quantitative, trading, api, client",
    project_urls={
        "Bug Reports": "https://github.com/cnhk/cnhkmcp/issues",
        "Source": "https://github.com/cnhk/cnhkmcp",
        "Documentation": "https://github.com/cnhk/cnhkmcp#readme",
    },
) 