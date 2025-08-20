#!/usr/bin/env python3
"""
Bitbucket Cloud MCP Server

This MCP server provides tools to interact with Bitbucket Cloud APIs
for generating timeline reports on Jira issues.

Run with: uv run bitbucket_mcp_server.py
"""

import asyncio
import json
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from urllib.parse import quote

import aiohttp
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.models import InitializationOptions
from mcp.types import AnyUrl


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bitbucket API configuration
BITBUCKET_API_BASE = "https://api.bitbucket.org/2.0"

@dataclass
class BitbucketConfig:
    """Bitbucket authentication configuration"""
    username: str
    app_password: str
    
    @classmethod
    def from_env(cls) -> "BitbucketConfig":
        username = os.getenv("BITBUCKET_USERNAME")
        app_password = os.getenv("BITBUCKET_APP_PASSWORD")
        
        if not username or not app_password:
            raise ValueError(
                "BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables must be set"
            )
        
        return cls(username=username, app_password=app_password)

@dataclass
class AppContext:
    """Application context with dependencies"""
    http_session: aiohttp.ClientSession
    bitbucket_config: BitbucketConfig

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle"""
    # Initialize HTTP session and config
    bitbucket_config = BitbucketConfig.from_env()
    
    # Create HTTP session with basic auth
    auth = aiohttp.BasicAuth(bitbucket_config.username, bitbucket_config.app_password)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
        logger.info("Bitbucket MCP Server initialized")
        try:
            yield AppContext(
                http_session=session,
                bitbucket_config=bitbucket_config
            )
        finally:
            logger.info("Bitbucket MCP Server shutting down")

# Create MCP server with lifespan
mcp = FastMCP("Bitbucket Cloud API Server", lifespan=app_lifespan)



async def make_bitbucket_request(
    ctx: Context,
    endpoint: str,
    params: Optional[dict] = None
) -> dict:
    """Make authenticated request to Bitbucket API"""
    app_context = ctx.request_context.lifespan_context
    url = f"{BITBUCKET_API_BASE}{endpoint}"
    
    try:
        async with app_context.http_session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                return {"values": [], "error": "Not found"}
            else:
                response.raise_for_status()
    except Exception as e:
        logger.error(f"Bitbucket API request failed: {e}")
        raise

async def paginate_bitbucket_request(
    ctx: Context,
    endpoint: str,
    params: Optional[dict] = None,
    max_pages: int = 10
) -> list[dict]:
    """Paginate through Bitbucket API responses"""
    results = []
    current_url = endpoint
    pages = 0
    
    while current_url and pages < max_pages:
        response = await make_bitbucket_request(ctx, current_url, params)
        
        if "values" in response:
            results.extend(response["values"])
            current_url = response.get("next", "").replace(BITBUCKET_API_BASE, "") if response.get("next") else None
        else:
            break
            
        pages += 1
        params = None  # Only use params on first request
    
    return results

@mcp.tool()
async def list_repositories(
    ctx: Context,
    workspace: str,
    pagelen: int = 100,
    page: int = 1
) -> dict:
    """
    List repositories in a workspace
    
    Args:
        workspace: Bitbucket workspace name
        pagelen: Number of items per page (max 100)
        page: Pagination number
    """
    params = {"pagelen": min(pagelen, 100), "page": page}
    
    endpoint = f"/repositories/{workspace}"
    response = await make_bitbucket_request(ctx, endpoint, params)
    
    repositories = []
    for repo in response.get("values", []):
        repositories.append(repo["name"])

    return {
        "values": repositories,
        "next": response.get("next")
    }



@mcp.tool()
async def search_pull_requests(
    ctx: Context,
    workspace: str,
    repo: str,
    q: str,
    states: Optional[list[str]] = None,
    pagelen: int = 50,
    cursor: Optional[str] = None
) -> dict:
    """
    Search pull requests in a repository
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        q: Search query (e.g., 'title~"ABC-123"')
        states: Filter by states (OPEN, MERGED, DECLINED)
        pagelen: Number of items per page (max 100)
        cursor: Pagination cursor
    """
    params = {"q": q, "pagelen": min(pagelen, 100)}
    
    if states:
        state_filter = " AND ".join([f'state="{state}"' for state in states])
        params["q"] = f"({q}) AND ({state_filter})"
    
    if cursor:
        params["after"] = cursor
    
    endpoint = f"/repositories/{workspace}/{repo}/pullrequests"
    response = await make_bitbucket_request(ctx, endpoint, params)
    
    pull_requests = []
    for pr in response.get("values", []):
        pull_requests.append({
            "id": pr["id"],
            "title": pr["title"],
            "description": pr.get("description"),
            "state": pr["state"],
            "created_on": pr["created_on"],
            "closed_on": pr.get("closed_on"),
            "merge_commit": pr.get("merge_commit"),
            "source": {
                "branch": {"name": pr["source"]["branch"]["name"]}
            },
            "destination": {
                "branch": {"name": pr["destination"]["branch"]["name"]}
            },
            "author": {
                "display_name": pr["author"]["display_name"],
                "uuid": pr["author"]["uuid"]
            }
        })
    
    return {
        "values": pull_requests,
        "next": response.get("next")
    }

@mcp.tool()
async def get_pull_request(
    ctx: Context,
    workspace: str,
    repo: str,
    pr_id: int
) -> dict:
    """
    Get detailed information about a specific pull request
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pr_id: Pull request ID
    """
    endpoint = f"/repositories/{workspace}/{repo}/pullrequests/{pr_id}"
    response = await make_bitbucket_request(ctx, endpoint)
    
    if "error" in response:
        return response
    
    return {
        "id": response["id"],
        "title": response["title"],
        "description": response.get("description"),
        "state": response["state"],
        "created_on": response["created_on"],
        "closed_on": response.get("closed_on"),
        "merge_commit": response.get("merge_commit"),
        "source": response["source"],
        "destination": response["destination"],
        "participants": response.get("participants", [])
    }

@mcp.tool()
async def list_pull_request_commits(
    ctx: Context,
    workspace: str,
    repo: str,
    pr_id: int,
    pagelen: int = 50,
    cursor: Optional[str] = None
) -> dict:
    """
    List commits in a pull request
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pr_id: Pull request ID
        pagelen: Number of items per page (max 100)
        cursor: Pagination cursor
    """
    params = {"pagelen": min(pagelen, 100)}
    if cursor:
        params["after"] = cursor
    
    endpoint = f"/repositories/{workspace}/{repo}/pullrequests/{pr_id}/commits"
    response = await make_bitbucket_request(ctx, endpoint, params)
    
    commits = []
    for commit in response.get("values", []):
        commits.append({
            "hash": commit["hash"],
            "date": commit["date"],
            "author": {
                "display_name": commit["author"]["user"]["display_name"] if commit["author"].get("user") else commit["author"]["raw"],
                "uuid": commit["author"]["user"]["uuid"] if commit["author"].get("user") else None
            },
            "message": commit["message"],
            "parents": commit.get("parents", [])
        })
    
    return {
        "values": commits,
        "next": response.get("next")
    }

@mcp.tool()
async def list_pull_request_activity(
    ctx: Context,
    workspace: str,
    repo: str,
    pr_id: int,
    pagelen: int = 50,
    cursor: Optional[str] = None
) -> dict:
    """
    List activity (comments, approvals) for a pull request
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pr_id: Pull request ID
        pagelen: Number of items per page (max 100)
        cursor: Pagination cursor
    """
    params = {"pagelen": min(pagelen, 100)}
    if cursor:
        params["after"] = cursor
    
    endpoint = f"/repositories/{workspace}/{repo}/pullrequests/{pr_id}/activity"
    response = await make_bitbucket_request(ctx, endpoint, params)
    
    activities = []
    for activity in response.get("values", []):
        activity_item = {
            "action": activity.get("action", "unknown")
        }
        
        if "comment" in activity:
            activity_item["comment"] = {
                "created_on": activity["comment"]["created_on"],
                "user": {
                    "display_name": activity["comment"]["user"]["display_name"],
                    "uuid": activity["comment"]["user"]["uuid"]
                },
                "content": activity["comment"]["content"]["raw"],
                "inline": activity["comment"].get("inline")
            }
        
        if "approval" in activity:
            activity_item["approval"] = {
                "date": activity["approval"]["date"],
                "user": {
                    "display_name": activity["approval"]["user"]["display_name"],
                    "uuid": activity["approval"]["user"]["uuid"]
                }
            }
        
        if "update" in activity:
            activity_item["update"] = activity["update"]
        
        activities.append(activity_item)
    
    return {
        "values": activities,
        "next": response.get("next")
    }

@mcp.tool()
async def list_branches(
    ctx: Context,
    workspace: str,
    repo: str,
    pagelen: int = 50,
    cursor: Optional[str] = None,
    prefixes: Optional[list[str]] = None
) -> dict:
    """
    List branches in a repository
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pagelen: Number of items per page (max 100)
        cursor: Pagination cursor
        prefixes: Filter branches by name prefixes (e.g., ["release/", "hotfix/"])
    """
    params = {"pagelen": min(pagelen, 100)}
    if cursor:
        params["after"] = cursor
    
    endpoint = f"/repositories/{workspace}/{repo}/refs/branches"
    response = await make_bitbucket_request(ctx, endpoint, params)
    
    branches = []
    for branch in response.get("values", []):
        branch_name = branch["name"]
        
        # Filter by prefixes if specified
        if prefixes:
            if not any(branch_name.startswith(prefix) for prefix in prefixes):
                continue
        
        branches.append({
            "name": branch_name,
            "target": {
                "hash": branch["target"]["hash"]
            }
        })
    
    return {
        "values": branches,
        "next": response.get("next")
    }

@mcp.tool()
async def get_pr_diff(
    ctx: Context,
    workspace: str,
    repo: str,
    pr_id: int,
    context: int = 3,
    ignore_whitespace: bool = False
) -> dict:
    """
    Get the git diff for a pull request
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pr_id: Pull request ID
        context: Number of context lines around changes (default: 3)
        ignore_whitespace: Whether to ignore whitespace changes
    """
    app_context = ctx.request_context.lifespan_context
    
    # Build URL and parameters
    url = f"{BITBUCKET_API_BASE}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/diff"
    params = {"context": context}
    
    if ignore_whitespace:
        params["ignore_whitespace"] = "true"
    
    try:
        async with app_context.http_session.get(url, params=params) as response:
            if response.status == 200:
                diff_content = await response.text()
                return {
                    "diff": diff_content,
                    "size": len(diff_content),
                    "context_lines": context,
                    "ignore_whitespace": ignore_whitespace
                }
            elif response.status == 404:
                return {"error": "Pull request not found"}
            else:
                response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to get PR diff: {e}")
        return {"error": f"Failed to get PR diff: {str(e)}"}

@mcp.tool()
async def search_pull_requests_across_workspace(
    ctx: Context,
    workspace: str,
    q: str,
    states: Optional[list[str]] = None
) -> dict:
    """
    Search pull requests across all repositories in a workspace
    
    This tool combines repository listing and pull request searching:
    1. Lists all repositories in the workspace (across multiple pages)
    2. Searches for pull requests matching the query in each repository
    3. Returns all matching PRs with detailed information
    
    Args:
        workspace: Bitbucket workspace name
        q: Search query (e.g., 'source.branch.name~"ABC-123"')
        states: Filter by states (OPEN, MERGED, DECLINED)
    """
    logger.info(f"Starting workspace-wide PR search in '{workspace}' for query: {q}")
    
    # Step 1: Get all repositories in the workspace (no limits)
    try:
        repositories = await paginate_bitbucket_request(
            ctx, 
            f"/repositories/{workspace}",
            params={"pagelen": 100},
            max_pages=1000  # Very high limit to effectively get all repos
        )
        
        repo_names = [repo["name"] for repo in repositories]
        
        logger.info(f"Found {len(repo_names)} repositories to search")
        
    except Exception as e:
        logger.error(f"Failed to list repositories: {e}")
        return {
            "error": f"Failed to list repositories: {str(e)}",
            "repositories_searched": 0,
            "matching_prs": []
        }
    
    # Step 2: Search for PRs in each repository
    matching_prs = []
    repositories_searched = 0
    search_errors = []
    
    for repo in repositories:
        repo_name = repo["name"]
        try:
            # Search PRs in this repository
            params = {"q": q}
            
            if states:
                state_filter = " AND ".join([f'state="{state}"' for state in states])
                params["q"] = f"({q}) AND ({state_filter})"
            
            endpoint = f"/repositories/{workspace}/{repo_name}/pullrequests"
            response = await make_bitbucket_request(ctx, endpoint, params)
            
            # Process found PRs
            for pr in response.get("values", []):
                pr_details = {
                    "repository": {
                        "name": repo_name,
                        "slug": repo.get("slug", repo_name),
                        "uuid": repo.get("uuid"),
                        "full_name": repo.get("full_name")
                    },
                    "pull_request": {
                        "id": pr["id"],
                        "title": pr["title"],
                        "description": pr.get("description"),
                        "state": pr["state"],
                        "created_on": pr["created_on"],
                        "closed_on": pr.get("closed_on"),
                        "merge_commit": pr.get("merge_commit"),
                        "source_branch": pr["source"]["branch"]["name"],
                        "destination_branch": pr["destination"]["branch"]["name"],
                        "author": {
                            "display_name": pr["author"]["display_name"],
                            "uuid": pr["author"]["uuid"]
                        },
                        "url": pr.get("links", {}).get("html", {}).get("href")
                    }
                }
                matching_prs.append(pr_details)
            
            repositories_searched += 1
            
            if len(response.get("values", [])) > 0:
                logger.info(f"Found {len(response.get('values', []))} matching PRs in repository '{repo_name}'")
            
        except Exception as e:
            error_msg = f"Failed to search repository '{repo_name}': {str(e)}"
            logger.warning(error_msg)
            search_errors.append(error_msg)
            repositories_searched += 1
            continue
    
    # Step 3: Return results
    result = {
        "query": q,
        "workspace": workspace,
        "repositories_searched": repositories_searched,
        "total_repositories": len(repositories),
        "matching_prs_count": len(matching_prs),
        "matching_prs": matching_prs
    }
    
    if search_errors:
        result["search_errors"] = search_errors
    
    if states:
        result["state_filter"] = states
    
    logger.info(f"Workspace search completed. Found {len(matching_prs)} matching PRs across {repositories_searched} repositories")
    
    return result

@mcp.tool()
async def add_pr_comment(
    ctx: Context,
    workspace: str,
    repo: str,
    pr_id: int,
    content: str,
    inline_path: Optional[str] = None,
    inline_from: Optional[int] = None,
    inline_to: Optional[int] = None
) -> dict:
    """
    Add a review comment to a pull request
    
    Args:
        workspace: Bitbucket workspace name
        repo: Repository slug
        pr_id: Pull request ID
        content: Comment content (raw text)
        inline_path: File path for inline comments (optional)
        inline_from: Starting line number for inline comments (optional)
        inline_to: Ending line number for inline comments (optional)
    """
    app_context = ctx.request_context.lifespan_context
    
    # Build URL
    url = f"{BITBUCKET_API_BASE}/repositories/{workspace}/{repo}/pullrequests/{pr_id}/comments"
    
    # Build comment payload
    comment_data = {
        "content": {
            "raw": content
        }
    }
    
    # Add inline comment data if provided
    if inline_path and inline_from is not None:
        comment_data["inline"] = {
            "path": inline_path,
            "from": inline_from
        }
        if inline_to is not None:
            comment_data["inline"]["to"] = inline_to
    
    try:
        async with app_context.http_session.post(
            url, 
            json=comment_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 201:
                comment_response = await response.json()
                return {
                    "id": comment_response["id"],
                    "created_on": comment_response["created_on"],
                    "content": comment_response["content"]["raw"],
                    "user": {
                        "display_name": comment_response["user"]["display_name"],
                        "uuid": comment_response["user"]["uuid"]
                    },
                    "inline": comment_response.get("inline"),
                    "links": comment_response.get("links", {})
                }
            elif response.status == 404:
                return {"error": "Pull request not found"}
            elif response.status == 403:
                return {"error": "Insufficient permissions to add comment"}
            else:
                error_text = await response.text()
                return {"error": f"Failed to add comment: {response.status} - {error_text}"}
    except Exception as e:
        logger.error(f"Failed to add PR comment: {e}")
        return {"error": f"Failed to add PR comment: {str(e)}"}

def main():
    """Main entry point for the MCP server"""
    try:
        # Validate environment variables early
        BitbucketConfig.from_env()
        logger.info("Bitbucket MCP Server starting...")
        mcp.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables")
        raise
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise

if __name__ == "__main__":
    main()

