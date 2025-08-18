from setuptools import setup, find_packages

setup(
    name="github-issue-parser-mcp",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastmcp>=0.1.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
    ],
    entry_points={
        'console_scripts': [
            'github-issue-parser=github_issue_parser_mcp.__main__:main',
        ],
    },
)
