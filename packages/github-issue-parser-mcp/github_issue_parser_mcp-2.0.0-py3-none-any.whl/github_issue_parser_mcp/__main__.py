"""Command-line entry point for the GitHub Issue Parser MCP server."""

from github_issue_parser_mcp.parser import run_server

def main():
    """Run the GitHub Issue Parser MCP server."""
    run_server()

if __name__ == "__main__":
    main()
