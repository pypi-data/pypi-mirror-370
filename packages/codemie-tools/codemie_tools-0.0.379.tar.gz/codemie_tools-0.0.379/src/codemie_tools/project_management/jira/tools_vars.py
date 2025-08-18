from codemie_tools.base.models import ToolMetadata

GENERIC_JIRA_TOOL = ToolMetadata(
    name="generic_jira_tool",
    description="""
    JIRA Tool for Official Atlassian JIRA REST API V2 to call, searching, creating, updating issues, etc.
    Required args: relative_url, method, params
    1. 'method': HTTP method (GET, POST, PUT, DELETE, etc.)
    2. 'relative_url': JIRA API URI starting with '/rest/api/2/...' (no query params in URL)
    3. 'params': Optional request body/query params as stringified JSON

    
    Key behaviors:
    - Get minimum required fields for search/read operations unless user requests more
    - Query API for missing required info, ask user if not found
    - For status updates: get available statuses first, compare with user input
    - For file attachments: get file paths from user
    
    File attachment format conversion:
    Replace `![filename.png](https://{company}.atlassian.net/rest/api/2/attachment/content/{attachment_id})` 
    with `!filename.png|thumbnail!`
    
    Provide files in "file_paths" parameter as:
    ```json
    {
        "url": "{file url}",
        "name": "filename.png"
    }
    ```
    """,
    label="Generic Jira",
    user_description="""
    Provides access to the Jira API, enabling interaction with Jira project management and issue tracking features. This tool allows the AI assistant to perform various operations related to issues, projects, and workflows in both Jira Server and Jira Cloud environments.
    Before using it, it is necessary to add a new integration for the tool by providing:
    1. Alias (A friendly name for the Jira integration)
    2. Jira URL
    3. Username/email for Jira (Required for Jira Cloud)
    4. Token (API token or Personal Access Token)
    Usage Note:
    Use this tool when you need to manage Jira issues, projects, sprints, or retrieve information from your Jira environment.
    """.strip()
)
