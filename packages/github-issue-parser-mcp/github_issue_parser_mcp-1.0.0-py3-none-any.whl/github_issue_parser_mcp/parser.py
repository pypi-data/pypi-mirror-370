"""
GitHub Issue Parser Server

Usage:
    uv run server github_issue_parser_mcp.parser stdio
"""

import re
import requests
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from bs4 import BeautifulSoup
# 一个更仿真的浏览器
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Create an MCP server
mcp = FastMCP("GitHub Issue Parser")


def extract_github_info(url: str) -> Dict[str, str]:
    """Extract owner, repo, and issue number from GitHub URL"""
    patterns = [
        r"github\.com/([^/]+)/([^/]+)/issues/(\d+)",
        r"api\.github\.com/repos/([^/]+)/([^/]+)/issues/(\d+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2),
                "issue_number": match.group(3)
            }
    
    raise ValueError("Invalid GitHub issue URL format")


def fetch_github_issue(owner: str, repo: str, issue_number: str) -> Dict[str, Any]:
    """Fetch issue data from GitHub API"""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent":  USER_AGENT
    }
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def fetch_github_issue_comments(owner: str, repo: str, issue_number: str) -> list:
    """Fetch comments for a GitHub issue"""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    headers = {
        "Accept": "application/vnd.github.v3+json+reactions",
        "User-Agent":  USER_AGENT
    }
    
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def format_comment_reactions(reactions_data: dict) -> str:
    """Format comment reactions from the reactions data included in comment"""
    if not reactions_data or reactions_data.get('total_count', 0) == 0:
        return ""
    
    reaction_counts = {}
    for reaction_type in ['+1', '-1', 'laugh', 'hooray', 'confused', 'heart', 'rocket', 'eyes']:
        count = reactions_data.get(reaction_type, 0)
        if count > 0:
            reaction_counts[reaction_type] = count
    
    if not reaction_counts:
        return ""
    
    reaction_emojis = {
        '+1': '👍',
        '-1': '👎',
        'laugh': '😄',
        'hooray': '🎉',
        'confused': '😕',
        'heart': '❤️',
        'rocket': '🚀',
        'eyes': '👀'
    }
    
    formatted_reactions = []
    for content, count in reaction_counts.items():
        emoji = reaction_emojis.get(content, content)
        formatted_reactions.append(f"{count} people react {emoji}")
    
    return " | ".join(formatted_reactions)


def format_reactions(reactions: list) -> str:
    """Format reactions into readable text"""
    if not reactions:
        return ""
    
    # Count reactions by content type
    reaction_counts = {}
    for reaction in reactions:
        content = reaction.get('content', '')
        if content:
            reaction_counts[content] = reaction_counts.get(content, 0) + 1
    
    # Map GitHub reaction content to emojis
    reaction_emojis = {
        '+1': '👍',
        '-1': '👎',
        'laugh': '😄',
        'hooray': '🎉',
        'confused': '😕',
        'heart': '❤️',
        'rocket': '🚀',
        'eyes': '👀'
    }
    
    formatted_reactions = []
    for content, count in reaction_counts.items():
        emoji = reaction_emojis.get(content, content)
        formatted_reactions.append(f"{count} people react {emoji}")
    
    return " | ".join(formatted_reactions)


def format_issue_content(issue_data: Dict[str, Any], comments_data: list = None, issue_reactions: list = None) -> str:
    """Format GitHub issue data into readable plain text"""
    formatted_text = []
    
    # Title
    formatted_text.append(f"Title: {issue_data.get('title', 'No title')}")
    formatted_text.append("=" * 50)
    
    # Basic info
    formatted_text.append(f"Repository: {issue_data.get('repository_url', '').split('/')[-2:]}")
    formatted_text.append(f"Issue #{issue_data.get('number', 'Unknown')}")
    formatted_text.append(f"State: {issue_data.get('state', 'Unknown').upper()}")
    formatted_text.append(f"Author: {issue_data.get('user', {}).get('login', 'Unknown')}")
    
    # Labels
    labels = issue_data.get('labels', [])
    if labels:
        label_names = [label.get('name', '') for label in labels]
        formatted_text.append(f"Labels: {', '.join(label_names)}")
    
    # Dates
    formatted_text.append(f"Created: {issue_data.get('created_at', 'Unknown')}")
    formatted_text.append(f"Updated: {issue_data.get('updated_at', 'Unknown')}")
    
    if issue_data.get('closed_at'):
        formatted_text.append(f"Closed: {issue_data.get('closed_at')}")
    
    # Issue reactions
    if issue_reactions:
        issue_reactions_text = format_reactions(issue_reactions)
        if issue_reactions_text:
            formatted_text.append(f"Reactions: {issue_reactions_text}")
    
    formatted_text.append("")
    
    # Body content
    body = issue_data.get('body', 'No description provided.')
    if body and body.strip():
        formatted_text.append("Description:")
        formatted_text.append("-" * 20)
        formatted_text.append(body)
        formatted_text.append("")
    
    # Comments
    if comments_data and len(comments_data) > 0:
        formatted_text.append(f"Comments ({len(comments_data)}):")
        formatted_text.append("-" * 20)
        
        for i, comment in enumerate(comments_data, 1):
            author = comment.get('user', {}).get('login', 'Unknown')
            created_at = comment.get('created_at', 'Unknown date')
            comment_body = comment.get('body', 'No content')
            comment_id = comment.get('id')
            
            formatted_text.append(f"Comment #{i} by {author} on {created_at}:")
            formatted_text.append("-" * 15)
            formatted_text.append(comment_body)
            
            # Add comment reactions if available
            comment_reactions_data = comment.get('reactions', {})
            comment_reactions_text = format_comment_reactions(comment_reactions_data)
            if comment_reactions_text:
                formatted_text.append(f"Reactions: {comment_reactions_text}")
            
            formatted_text.append("")
    
    return "\n".join(formatted_text)


# Add GitHub issue parsing tool
@mcp.tool()
def parse_github_issue(issue_url: str) -> str:
    """
    Parse a GitHub issue URL and return formatted plain text content.
    
    Args:
        issue_url: GitHub issue URL (e.g., "https://github.com/owner/repo/issues/123")
    
    Returns:
        Formatted plain text content of the GitHub issue including comments and reactions
    """
    try:
        # Extract GitHub info from URL
        github_info = extract_github_info(issue_url)
        
        # Fetch issue data
        issue_data = fetch_github_issue(
            github_info["owner"],
            github_info["repo"],
            github_info["issue_number"]
        )
        
        # Fetch comments data
        comments_data = fetch_github_issue_comments(
            github_info["owner"],
            github_info["repo"],
            github_info["issue_number"]
        )
        
        # Format and return with comments and reactions
        return format_issue_content(issue_data, comments_data)
        
    except ValueError as e:
        return f"Error: {str(e)}"
    except requests.RequestException as e:
        return f"Network error: Failed to fetch issue data - {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# Add a resource for GitHub issues
@mcp.resource("github-issue://{url}")
def get_github_issue(url: str) -> str:
    """
    Get formatted GitHub issue content as a resource.
    
    Args:
        url: GitHub issue URL
    
    Returns:
        Formatted plain text content of the GitHub issue
    """
    return parse_github_issue(url)


# Add a prompt for GitHub issue analysis
@mcp.prompt()
def analyze_github_issue(issue_url: str, analysis_type: str = "summary") -> str:
    """
    Generate a prompt for analyzing a GitHub issue.
    
    Args:
        issue_url: GitHub issue URL
        analysis_type: Type of analysis ("summary", "technical", "priority")
    
    Returns:
        Analysis prompt for the GitHub issue
    """
    issue_content = parse_github_issue(issue_url)
    
    analysis_prompts = {
        "summary": "Please provide a concise summary of this GitHub issue, including the main problem, key details, and current status.",
        "technical": "Please analyze the technical aspects of this GitHub issue, including potential implementation approaches, technical challenges, and relevant code considerations.",
        "priority": "Please assess the priority and urgency of this GitHub issue based on its description, labels, and impact."
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["summary"])
    
    return f"{prompt}\n\nHere is the issue content:\n\n{issue_content}"


def run_server():
    """Run the MCP server with streamable-http transport."""
    mcp.run(transport="streamable-http")
