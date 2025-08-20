# Bitbucket Cloud MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with Bitbucket Cloud APIs for generating timeline reports on Jira issues.

## Features

This MCP server exposes the following tools to analyze Jira issue timelines through Bitbucket data:

- **Repository Management**: List repositories in a workspace
- **Pull Request Search**: Search PRs by issue keys, branch names, or custom queries  
- **Pull Request Analysis**: Get detailed PR information including commits and activity
- **Branch Operations**: List branches and search commits across branches
- **Timeline Calculation**: Comprehensive tools for computing development timelines

## Installation

### Prerequisites

- Python 3.11+
- Bitbucket Cloud account with API access
- App Password for Bitbucket authentication

### Install from PyPI

```bash
# Install using pipx (recommended)
pipx install bitbucket-mcp-server

# Or install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install bitbucket-mcp-server

# Or install with --user flag
pip install --user bitbucket-mcp-server
```

### Creating a Bitbucket App Password

1. Go to Bitbucket Settings → App passwords
2. Create new app password with these permissions:
   - Repositories: Read
   - Pull requests: Read
   - Account: Read

## MCP Configuration

Add this configuration to your MCP client (e.g., Cursor IDE, Claude Desktop):

```json
{
  "mcpServers": {
    "bitbucket-mcp-server": {
      "command": "bitbucket-mcp-server",
      "env": {
        "BITBUCKET_USERNAME": "<your-bitbucket-username>",
        "BITBUCKET_APP_PASSWORD": "<your-app-password>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Configuration File Locations

- **Cursor IDE**: `.kiro/settings/mcp.json` (workspace) or `~/.kiro/settings/mcp.json` (global)
- **Claude Desktop**: Platform-specific configuration file

## Usage

### Available Tools

#### Repository Tools
- `list_repositories(workspace, pagelen?, cursor?)` - List repositories in workspace
- `list_branches(workspace, repo, pagelen?, cursor?, prefixes?)` - List branches with optional filtering
- `list_commits(workspace, repo, rev, pagelen?, cursor?)` - List commits on branch/from commit

#### Pull Request Tools  
- `search_pull_requests(workspace, repo, q, states?, pagelen?, cursor?)` - Search PRs with query
- `get_pull_request(workspace, repo, pr_id)` - Get detailed PR information
- `list_pull_request_commits(workspace, repo, pr_id, pagelen?, cursor?)` - List PR commits
- `list_pull_request_activity(workspace, repo, pr_id, pagelen?, cursor?)` - List PR comments/activity

#### Advanced Search Tools
- `workspace_search_prs_by_branch_keys(workspace, branch_keys, match_side?, states?, repos?, page_size?, max_concurrency?, time_window?)` - Search PRs by branch names across workspace
- `search_prs_by_issue_key(workspace, issue_key, repos?, states?, page_size?, max_concurrency?)` - Search PRs by Jira issue key
- `search_commits_by_message(workspace, repo, branches, contains, since?, until?, page_size?)` - Search commits by message content
- `get_pr_full(workspace, repo, pr_id)` - Get complete PR data (details + commits + activity)

### Timeline Report Generation

The server provides tools for LLMs to generate comprehensive timeline reports by:

1. Searching for PRs related to a Jira issue key
2. Analyzing PR commits and activity 
3. Calculating four key timeline metrics:
   - First commit → PR creation
   - PR creation → first review comment
   - First review comment → PR merged
   - Develop branch → release/hotfix branch

## Example Usage with Claude/LLM

```
Generate a timeline report for Jira issue ABC-123 in workspace "mycompany"
```

The LLM will use the MCP tools to:
1. Call `search_prs_by_issue_key("mycompany", "ABC-123")`
2. For each PR, call `get_pr_full()` to get complete data
3. Calculate timeline metrics and return structured JSON report

## Configuration

### Environment Variables

- `BITBUCKET_USERNAME` - Your Bitbucket username (required)
- `BITBUCKET_APP_PASSWORD` - Your Bitbucket app password (required)

### Query Examples

The search tools support Bitbucket's query syntax:

```python
# Search PRs by title containing issue key
q = 'title~"ABC-123"'

# Search PRs by branch name
q = 'source.branch.name~"feature/ABC-123"'

# Complex query with multiple conditions
q = '(title~"ABC-123" OR description~"ABC-123") AND state="MERGED"'
```

## Troubleshooting

### Installation Issues

If you encounter "externally-managed-environment" error on macOS:

```bash
# Use pipx (recommended)
brew install pipx
pipx install bitbucket-mcp-server

# Or use virtual environment
python -m venv ~/.venv/bitbucket-mcp
source ~/.venv/bitbucket-mcp/bin/activate
pip install bitbucket-mcp-server
```

### Finding Installation Path

```bash
# Check where the command is installed
which bitbucket-mcp-server

# For pipx installations
pipx list
```

Use the full path in your MCP configuration if the command isn't in your PATH.

## API Rate Limits

The server implements:
- Automatic retry with exponential backoff
- Concurrent request limiting (configurable via `max_concurrency`)
- Pagination handling for large datasets
- Request timeout handling (30 second default)

## Error Handling

- Network errors are logged and retried automatically
- Missing repositories/PRs return empty results rather than errors
- Partial failures in batch operations continue processing remaining items
- All errors are logged with context for debugging

## Security

- Credentials are loaded from environment variables only
- HTTP basic authentication is used for Bitbucket API
- No credentials are logged or exposed in responses
- All API requests use HTTPS

## License

MIT License - see LICENSE file for details.



