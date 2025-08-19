# setup.py
from setuptools import setup, find_packages

setup(
    name="web-tool-mcp-server",  # 个人命名空间
    version="0.0.2",
    author="linview",
    author_email="linview@gmail.com",
    description="linview's MCP server tools for web utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/linview/sandbox_agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=1.0.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
    ],
    entry_points={
        "console_scripts": [
            "web-tool-server=web_tool.server:main"
        ]
    }
)
