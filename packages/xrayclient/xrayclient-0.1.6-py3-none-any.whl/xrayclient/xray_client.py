import os
import re
import time
import json
from numpy import isin
import spacy
import base64
import requests
import mimetypes
from jira import JIRA
from jsonpath_nz import log as logger, jprint
from typing import Optional, Dict, Any, List, Union, Tuple


class JiraHandler():
    """A handler class for interacting with JIRA's REST API.
    This class provides methods to interact with JIRA's REST API, handling authentication,
    issue creation, retrieval, and various JIRA operations. It uses environment variables for
    configuration and provides robust error handling with comprehensive logging.
    The class supports creating issues with attachments, linking issues, and retrieving
    detailed issue information with customizable field selection. It handles various
    JIRA field types including user information, attachments, comments, and issue links.
    Attributes
    ----------
    client : JIRA
        The JIRA client instance used for API interactions
    Environment Variables
    --------------------
    JIRA_SERVER : str
        The JIRA server URL (default: 'https://arusa.atlassian.net')
    JIRA_USER : str
        The JIRA user email (default: 'yakub@arusatech.com')
    JIRA_API_KEY : str
        The JIRA API key for authentication (required)
    Methods
    -------
    create_issue(project_key, summary, description, **kwargs)
        Create a new JIRA issue with optional attachments, linking, and custom fields
    get_issue(issue_key, fields=None)
        Retrieve a JIRA issue with specified fields or all available fields
    Examples
    --------
    >>> handler = JiraHandler()
    >>> # Create a new issue
    >>> issue_key, issue_id = handler.create_issue(
    ...     project_key="PROJ",
    ...     summary="New feature implementation",
    ...     description="Implement new login flow",
    ...     issue_type="Story",
    ...     priority="High",
    ...     labels=["feature", "login"],
    ...     attachments=["/path/to/screenshot.png"]
    ... )
    >>> print(f"Created issue {issue_key} with ID {issue_id}")
    >>> # Retrieve issue details
    >>> issue = handler.get_issue("PROJ-123", fields=["summary", "status", "assignee"])
    >>> print(f"Issue: {issue['summary']} - Status: {issue['status']['name']}")
    Notes
    -----
    - Requires valid JIRA credentials stored in environment variables
    - Automatically loads configuration from .env file if present
    - Provides comprehensive error handling and logging
    - Supports various JIRA field types and custom fields
    - Handles file attachments with automatic MIME type detection
    - Creates issue links with configurable link types
    - Returns None for failed operations instead of raising exceptions
    """
    
    def __init__(self):
        """Initialize the JIRA client with configuration from environment variables.
        This constructor sets up the JIRA client by reading configuration from
        environment variables. It automatically loads variables from a .env file
        if present in the project root.
        Environment Variables
        -------------------
        JIRA_SERVER : str
            The JIRA server URL (default: 'https://arusatech.atlassian.net')
        JIRA_USER : str
            The JIRA user email (default: 'yakub@arusatech.com')
        JIRA_API_KEY : str
            The JIRA API key for authentication
        Raises
        ------
        Exception
            If the JIRA client initialization fails
        """
        try:
            # Load environment variables from .env file
            jira_server = os.getenv('JIRA_SERVER', 'https://arusatech.atlassian.net')
            jira_user = os.getenv('JIRA_USER', 'yakub@arusatech.com')
            jira_api_key = os.getenv('JIRA_API_KEY', "")
            # Validate required environment variables
            if not jira_api_key or jira_api_key == '<JIRA_API_KEY>':
                raise ValueError("JIRA_API_KEY environment variable is required and must be set to a valid API key")
            self.client = JIRA(
                server=jira_server,
                basic_auth=(jira_user, jira_api_key)
            )
            logger.info("JIRA client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize JIRA client: {str(e)}")
            logger.traceback(e)
            raise

    def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = None,
        priority: str = None,
        assignee: str = None,
        labels: List[str] = None,
        components: List[str] = None,
        attachments: List[str] = None,
        parent_issue_key: str = None,
        linked_issues: List[Dict[str, str]] = None,
        custom_fields: Dict[str, Any] = None
    ) -> Optional[tuple[str, str]]:
        """Create a new issue in JIRA with the specified details.
        This method creates a new JIRA issue with the provided details and handles
        optional features like attachments and issue linking.
        Parameters
        ----------
        project_key : str
            The key of the project where the issue should be created
        summary : str
            The summary/title of the issue
        description : str
            The detailed description of the issue
        issue_type : str, optional
            The type of issue (default: 'Bug')
        priority : str, optional
            The priority of the issue
        assignee : str, optional
            The username of the assignee
        labels : List[str], optional
            List of labels to add to the issue
        components : List[str], optional
            List of component names to add to the issue
        attachments : List[str], optional
            List of file paths to attach to the issue
        linked_issues : List[Dict[str, str]], optional
            List of issues to link to the new issue. Each dict should contain:
            - 'key': The issue key to link to
            - 'type': The type of link (default: 'Relates')
        custom_fields : Dict[str, Any], optional
            Dictionary of custom fields to set on the issue
        Returns
        -------
        Optional[tuple[str, str]]
            A tuple containing (issue_key, issue_id) if successful,
            (None, None) if creation fails
        Examples
        --------
        >>> handler = JiraHandler()
        >>> result = handler.create_issue(
        ...     project_key="PROJ",
        ...     summary="Bug in login",
        ...     description="User cannot login with valid credentials",
        ...     issue_type="Bug",
        ...     priority="High",
        ...     labels=["login", "bug"],
        ...     components=["Authentication"],
        ...     attachments=["/path/to/screenshot.png"],
        ...     linked_issues=[{"key": "PROJ-123", "type": "Blocks"}]
        ... )
        >>> print(f"Created issue {result[0]} with ID {result[1]}")
        """
        try:
            # Build basic issue fields
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type or 'Bug'},
                'parent': {'key': parent_issue_key} if parent_issue_key else None
            }
            # Add optional fields
            if priority:
                issue_dict['priority'] = {'name': priority}
            if assignee:
                issue_dict['assignee'] = {'name': assignee}
            if labels:
                issue_dict['labels'] = labels
            if components:
                issue_dict['components'] = [{'name': c} for c in components]
            # Add any custom fields
            if custom_fields:
                issue_dict.update(custom_fields)
            # Create the issue
            issue = self.client.create_issue(fields=issue_dict)
            logger.info(f"Created JIRA issue : {issue.key} [ID: {issue.id}]")
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self.client.add_attachment(
                            issue=issue.key,
                            attachment=file_path
                        )
                        logger.info(f"Added attachment: {file_path}")
                    else:
                        logger.warning(f"Attachment not found: {file_path}")
            # Create issue links if provided
            if linked_issues:
                for link in linked_issues:
                    try:
                        self.client.create_issue_link(
                            link.get('type', 'Relates'),
                            issue.key,
                            link['key']
                        )
                        logger.info(f"Created link between {issue.key} and {link['key']}")
                    except Exception as e:
                        logger.error(f"Failed to create link to {link['key']}: {str(e)}")
            return (issue.key, issue.id)
        except Exception as e:
            logger.error(f"Failed to create JIRA issue for project {project_key}: {str(e)}")
            logger.traceback(e)
            return (None, None)

    def get_issue(self, issue_key: str, fields: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get an issue by its key with specified fields.
        This method retrieves a JIRA issue using its key and returns the issue details
        with the specified fields. If no fields are specified, it returns all available fields.
        Parameters
        ----------
        issue_key : str
            The JIRA issue key to retrieve (e.g., "PROJ-123")
        fields : List[str], optional
            List of specific fields to retrieve. If None, all fields are returned.
            Common fields include: "summary", "description", "status", "assignee", 
            "reporter", "created", "updated", "priority", "labels", "components",
            "attachments", "comments", "issuetype", "project"
        Returns
        -------
        Optional[Dict[str, Any]]
            A dictionary containing the issue details if successful, None if the issue
            is not found or an error occurs.
        Examples
        --------
        >>> handler = JiraHandler()
        >>> # Get all fields
        >>> issue = handler.get_issue("PROJ-123")
        >>> print(f"Issue: {issue['summary']} - Status: {issue['status']['name']}")
        >>> # Get specific fields only
        >>> issue = handler.get_issue("PROJ-123", fields=["summary", "status", "assignee"])
        >>> print(f"Assignee: {issue['assignee']['displayName'] if issue['assignee'] else 'Unassigned'}")
        Notes
        -----
        - The issue key must be valid and accessible with current authentication
        - If fields parameter is None, all fields are returned
        - Some fields may be None if the issue doesn't have values for them
        - Failed operations are logged as errors with relevant details
        - The method handles missing issues gracefully by returning None
        """
        try:
            if not issue_key:
                logger.error("Issue key is required")
                return None
            # Define field mappings for JIRA API
            field_mappings = {
                'summary': 'summary',
                'description': 'description', 
                'status': 'status',
                'assignee': 'assignee',
                'reporter': 'reporter',
                'priority': 'priority',
                'labels': 'labels',
                'components': 'components',
                'issuetype': 'issuetype',
                'project': 'project',
                'created': 'created',
                'updated': 'updated',
                'resolutiondate': 'resolutiondate',
                'duedate': 'duedate',
                'attachments': 'attachments',
                'comment': 'comment',
                'issuelinks': 'issuelinks'
            }
            # Determine requested fields
            if fields is None:
                requested_fields = None
            else:
                # Map requested fields to JIRA field names
                jira_fields = [field_mappings.get(field, field) for field in fields]
                # Always include key and id as they're required
                if 'key' not in fields:
                    jira_fields.append('key')
                if 'id' not in fields:
                    jira_fields.append('id')
                requested_fields = ','.join(jira_fields)
            # Get the issue using the JIRA client
            issue = self.client.issue(issue_key, fields=requested_fields)
            if not issue:
                logger.warning(f"Issue not found: {issue_key}")
                return None
            # Helper function to safely get user attributes
            def get_user_dict(user_obj):
                if not user_obj:
                    return None
                try:
                    return {
                        'name': getattr(user_obj, 'name', None),
                        'displayName': getattr(user_obj, 'displayName', None),
                        'emailAddress': getattr(user_obj, 'emailAddress', None)
                    }
                except Exception:
                    return None
            # Helper function to safely get field value
            def safe_get_field(field_name, default=None):
                try:
                    return getattr(issue.fields, field_name, default)
                except AttributeError:
                    return default
            # Helper function to get object attributes safely
            def get_object_attrs(obj, attrs):
                if not obj:
                    return None
                return {attr: getattr(obj, attr, None) for attr in attrs}
            # Helper function to process attachments
            def process_attachments(attachments):
                if not attachments:
                    return []
                return [
                    {
                        'id': getattr(att, 'id', None),
                        'filename': getattr(att, 'filename', None),
                        'size': getattr(att, 'size', None),
                        'created': getattr(att, 'created', None),
                        'mimeType': getattr(att, 'mimeType', None)
                    } for att in attachments
                ]
            # Helper function to process comments
            def process_comments(comments):
                if not comments or not hasattr(comments, 'comments'):
                    return []
                return [
                    {
                        'id': getattr(comment, 'id', None),
                        'body': getattr(comment, 'body', None),
                        'author': get_user_dict(comment.author),
                        'created': getattr(comment, 'created', None),
                        'updated': getattr(comment, 'updated', None)
                    } for comment in comments.comments
                ]
            # Helper function to process issue links
            def process_issue_links(issue_links):
                if not issue_links:
                    return []
                def process_issue_reference(issue_ref, direction):
                    if not hasattr(issue_ref, direction) or not getattr(issue_ref, direction):
                        return None
                    ref_issue = getattr(issue_ref, direction)
                    return {
                        'key': getattr(ref_issue, 'key', None),
                        'id': getattr(ref_issue, 'id', None),
                        'fields': {
                            'summary': getattr(ref_issue.fields, 'summary', None),
                            'status': get_object_attrs(ref_issue.fields.status, ['name']) if ref_issue.fields.status else None
                        }
                    }
                return [
                    {
                        'id': getattr(link, 'id', None),
                        'type': get_object_attrs(link.type, ['id', 'name', 'inward', 'outward']) if link.type else None,
                        'inwardIssue': process_issue_reference(link, 'inwardIssue'),
                        'outwardIssue': process_issue_reference(link, 'outwardIssue')
                    } for link in issue_links
                ]
            # Build response dictionary
            issue_dict = {
                'key': issue.key,
                'id': issue.id
            }
            # Determine which fields to process
            fields_to_process = fields if fields is not None else list(field_mappings.keys())
            # Process each field
            for field in fields_to_process:
                if field in ['key', 'id']:
                    continue  # Already handled
                field_value = safe_get_field(field_mappings.get(field, field))
                match field:
                    case 'summary' | 'description' | 'created' | 'updated' | 'resolutiondate' | 'duedate':
                        issue_dict[field] = field_value
                    case 'status' | 'issuetype' | 'priority':
                        issue_dict[field] = get_object_attrs(field_value, ['id', 'name', 'description'])
                    case 'project':
                        issue_dict[field] = get_object_attrs(field_value, ['key', 'name', 'id'])
                    case 'assignee' | 'reporter':
                        issue_dict[field] = get_user_dict(field_value)
                    case 'labels':
                        issue_dict[field] = list(field_value) if field_value else []
                    case 'components':
                        issue_dict[field] = [
                            get_object_attrs(comp, ['id', 'name', 'description']) 
                            for comp in (field_value or [])
                        ]
                    case 'attachments':
                        issue_dict[field] = process_attachments(field_value)
                    case 'comments':
                        issue_dict[field] = process_comments(field_value)
                    case 'issuelinks':
                        issue_dict[field] = process_issue_links(field_value)
                    case _:
                        # Handle unknown fields or custom fields
                        issue_dict[field] = field_value
            # logger.info(f"Retrieved JIRA issue: {issue_key}")
            return issue_dict
        except Exception as e:
            logger.error(f"Failed to get JIRA issue {issue_key}: {str(e)}")
            logger.traceback(e)
            return None

    def update_issue_summary(self, issue_key: str, new_summary: str) -> bool:
        """Update the summary of a JIRA issue.
        This method updates the summary field of an existing JIRA issue using the JIRA REST API.
        It validates the input parameters and handles errors gracefully with comprehensive logging.
        Parameters
        ----------
        issue_key : str
            The JIRA issue key to update (e.g., "PROJ-123")
        new_summary : str
            The new summary text to set for the issue
        Returns
        -------
        bool
            True if the summary was successfully updated, False if the operation failed.
            Returns None if an error occurs during the API request.
        Examples
        --------
        >>> handler = JiraHandler()
        >>> success = handler.update_issue_summary("PROJ-123", "Updated bug description")
        >>> print(success)
        True
        Notes
        -----
        - The issue key must be valid and accessible with current authentication
        - The new summary cannot be empty or None
        - Failed operations are logged as errors with relevant details
        - The method uses the JIRA client's update method for efficient API calls
        """
        try:
            # Validate input parameters
            if not issue_key or not issue_key.strip():
                logger.error("Issue key is required and cannot be empty")
                return False
            if not new_summary or not new_summary.strip():
                logger.error("New summary is required and cannot be empty")
                return False
            # Strip whitespace from inputs
            issue_key = issue_key.strip()
            new_summary = new_summary.strip()
            # logger.info(f"Updating summary for issue {issue_key}")
            # Get the issue object
            issue = self.client.issue(issue_key)
            if not issue:
                logger.error(f"Issue not found: {issue_key}")
                return False
            # Update the summary field
            issue.update(summary=new_summary)
            logger.info(f"Successfully updated summary for issue {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to update summary for issue {issue_key}: {str(e)}")
            logger.traceback(e)
            return False

    def _build_auth_headers(self, api_key: str = None, user: str = None, cookie: str = None) -> Dict[str, str]:
        """
        Build authentication headers for JIRA API requests.
        
        This method converts an API key to base64 format and creates the proper
        Authorization header, similar to how Postman generates it.
        
        Parameters
        ----------
        api_key : str, optional
            The JIRA API key. If not provided, uses the one from environment variables.
        user : str, optional
            The JIRA user email. If not provided, uses the one from environment variables.
        cookie : str, optional
            Additional cookie value to include in headers.
            
        Returns
        -------
        Dict[str, str]
            Dictionary containing the Authorization and Cookie headers.
            
        Examples
        --------
        >>> handler = JiraHandler()
        >>> headers = handler._build_auth_headers()
        >>> print(headers)
        {
            'Authorization': 'Basic eWFrdWIubW9oYW1tYWRAd25jby5jb206QVRBVFQzeEZmR0YwN29tcFRCcU9FVUxlXzJjWlFDbkJXb2ZTYS1xMW92YmYxYnBURC1URmppY3VFczVBUzFJMkdjaXcybHlNMEFaRjl1T19OSU0yR0tIMlZ6SkQtQ0JtLTV2T05RNHhnMEFKbzVoaWhtQjIxaHc3Zk54MUFicjFtTWx1R0M4cVJoVDIzUkZlQUlaMVk3UUd0UnBLQlFLOV9iV0hyWnhPOWlucURRVjh4ZC0wd2tNPTIyQTdDMjg1',
            'Cookie': 'atlassian.xsrf.token=9dd7b0ae95b82b138b9fd93e27a45a6fd01c548e_lin'
        }
        """
        try:
            # Use provided values or fall back to environment variables
            api_key = api_key or os.getenv('JIRA_API_KEY')
            user = user or os.getenv('JIRA_USER', 'yakub@arusatech.com')
            
            if not api_key:
                raise ValueError("API key is required")
            if not user:
                raise ValueError("User email is required")
            
            # Create the credentials string in format "user:api_key"
            credentials = f"{user}:{api_key}"
            
            # Encode to base64
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            
            # Build headers
            headers = {
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            # Add cookie if provided
            if cookie:
                headers['Cookie'] = cookie
                
            return headers
            
        except Exception as e:
            logger.error(f"Failed to build auth headers: {str(e)}")
            logger.traceback(e)
            raise

    def make_jira_request(self, jira_key: str, url: str, method: str = "GET", payload: Dict = None, 
                         api_key: str = None, user: str = None, cookie: str = None) -> Optional[Dict]:
        """
        Make a JIRA API request with proper authentication headers.
        
        This method builds the authentication headers (similar to Postman) and
        makes the request to the JIRA API.
        
        Parameters
        ----------
        jira_key : str
            The JIRA issue key
        method : str, optional
            HTTP method (GET, POST, PUT, DELETE). Defaults to "GET"
        payload : Dict, optional
            Request payload for POST/PUT requests
        api_key : str, optional
            The JIRA API key. If not provided, uses environment variable
        user : str, optional
            The JIRA user email. If not provided, uses environment variable
        cookie : str, optional
            Additional cookie value
            
        Returns
        -------
        Optional[Dict]
            The JSON response from the API, or None if the request fails
            
        Examples
        --------
        >>> handler = JiraHandler()
        >>> response = handler.make_jira_request(
        ...     url="https://arusa.atlassian.net/rest/api/2/issue/XSP1-543213456"
        ... )
        >>> print(response)
        {'id': '12345', 'key': 'XSP1-3456', ...}
        """
        try:
            if not jira_key:
                logger.error("JIRA issue key is required")
                return None
            
            url = f"{os.getenv('JIRA_SERVER')}/rest/api/2/issue/{jira_key}"
            if not url:
                logger.error("JIRA API endpoint URL is required")
                return None
            # Build authentication headers
            headers = self._build_auth_headers(api_key, user, cookie)
            
            # Make the request
            response = requests.request(method, url, headers=headers, data=payload)
            response.raise_for_status()
            
            # Return JSON response
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"JIRA API request failed: {str(e)}")
            logger.traceback(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in JIRA request: {str(e)}")
            logger.traceback(e)
            return None

    def download_jira_attachment_by_id(self, attachment_id: str, mime_type: str) -> Optional[Dict]:
        '''
        Download a JIRA attachment by its ID.
        '''
        try:
            # ATTACHMENT_URL = f"{os.getenv('JIRA_SERVER')}/rest/api/2/attachment/{attachment_id}"
            CONTENT_URL = f"{os.getenv('JIRA_SERVER')}/rest/api/2/attachment/content/{attachment_id}"
            if not CONTENT_URL:
                logger.error(f"No content URL found for attachment '{attachment_id}'")
                return None
            headers = self._build_auth_headers()
            download_response = requests.get(CONTENT_URL, headers=headers)
            download_response.raise_for_status()
            content = download_response.content
            #Process content based on type
            result = {
                'content': content,
                'mime_type': mime_type,
                'text_content': None,
                'json_content': None
            }
            
            # Handle text-based files
            if mime_type.startswith(('text/', 'application/json', 'application/xml' , 'json')):
                try:
                    text_content = content.decode('utf-8')
                    result['text_content'] = text_content
                    
                    # Try to parse as JSON
                    if mime_type == 'application/json':
                        try:
                            result['json_content'] = json.loads(text_content)
                        except json.JSONDecodeError:
                            pass
                except UnicodeDecodeError:
                    logger.error(f"Warning: Could not decode text content for {attachment_id}")
                    logger.traceback(e)
            
            return result
        except Exception as e:
            logger.error(f"Error downloading JIRA attachment: {str(e)}")
            logger.traceback(e)
            return None
        

class XrayGraphQL(JiraHandler):
    """A comprehensive client for interacting with Xray Cloud's GraphQL API.
    This class extends JiraHandler to provide specialized methods for interacting with
    Xray Cloud's GraphQL API for test management. It handles authentication, test plans,
    test executions, test runs, defects, evidence, and other Xray-related operations 
    through GraphQL queries and mutations.
    Inherits
    --------
    JiraHandler
        Base class providing JIRA client functionality and issue management
    Attributes
    ----------
    client_id : str
        The client ID for Xray authentication
    client_secret : str
        The client secret for Xray authentication
    xray_base_url : str
        Base URL for Xray Cloud API (defaults to 'https://us.xray.cloud.getxray.app')
    logger : Logger
        Logger instance for debugging and error tracking
    token : str
        Authentication token obtained from Xray
    Methods
    -------
    Authentication & Setup
    ---------------------
    __init__()
        Initialize XrayGraphQL client with authentication and configuration settings.
    _get_auth_token() -> Optional[str]
        Authenticate with Xray Cloud API and obtain an authentication token.
    _make_graphql_request(query: str, variables: Dict) -> Optional[Dict]
        Makes a GraphQL request to the Xray API with proper authentication.
    _parse_table(table_str: str) -> Dict[str, Union[List[int], List[float]]]
        Parse a string representation of a table into a dictionary of numeric values.
    Issue ID Management
    ------------------
    get_issue_id_from_jira_id(issue_key: str) -> Optional[str]
        Retrieves the internal Xray issue ID for a given JIRA issue key and type.
    Test Plan Operations
    -------------------
    get_tests_from_test_plan(test_plan: str) -> Optional[Dict[str, str]]
        Retrieves all tests associated with a given test plan.
    get_test_plan_data(test_plan: str) -> Optional[Dict[str, Union[List[int], List[float]]]]
        Retrieves and parses tabular data from a test plan's description.
    Test Set Operations
    ------------------
    get_tests_from_test_set(test_set: str) -> Optional[Dict[str, str]]
        Retrieves all tests associated with a given test set.
    filter_test_set_by_test_case(test_key: str) -> Optional[Dict[str, str]]
        Retrieves all test sets containing a specific test case.
    filter_tags_by_test_case(test_key: str) -> Optional[List[str]]
        Extracts and filters tags from test sets associated with a test case.
    Test Execution Operations
    ------------------------
    get_tests_from_test_execution(test_execution: str) -> Optional[Dict[str, str]]
        Retrieves all tests associated with a given test execution.
    get_test_execution(test_execution: str) -> Optional[Dict]
        Retrieve detailed information about a test execution from Xray.
    create_test_execution(test_issue_keys: List[str], project_key: Optional[str], 
                         summary: Optional[str], description: Optional[str]) -> Optional[Dict]
        Creates a new test execution with specified test cases.
    create_test_execution_from_test_plan(test_plan: str) -> Optional[Dict[str, Dict[str, str]]]
        Creates a test execution from a given test plan with all associated tests.
    add_test_execution_to_test_plan(test_plan: str, test_execution: str) -> Optional[Dict]
        Add a test execution to an existing test plan in Xray.
    Test Run Operations
    ------------------
    get_test_runstatus(test_case: str, test_execution: str) -> Optional[Tuple[str, str]]
        Retrieves the status of a test run for a specific test case.
    get_test_run_by_id(test_case_id: str, test_execution_id: str) -> Optional[Tuple[str, str]]
        Retrieves the test run ID and status using internal Xray IDs.
    update_test_run_status(test_run_id: str, test_run_status: str) -> bool
        Updates the status of a specific test run.
    update_test_run_comment(test_run_id: str, test_run_comment: str) -> bool
        Updates the comment of a specific test run.
    get_test_run_comment(test_run_id: str) -> Optional[str]
        Retrieve the comment of a specific test run from Xray.
    append_test_run_comment(test_run_id: str, test_run_comment: str) -> bool
        Append a comment to an existing test run comment.
    Evidence & Defect Management
    ---------------------------
    add_evidence_to_test_run(test_run_id: str, evidence_path: str) -> bool
        Add evidence (attachments) to a test run in Xray.
    create_defect_from_test_run(test_run_id: str, project_key: str, parent_issue_key: str,
                               defect_summary: str, defect_description: str) -> Optional[Dict]
        Create a defect from a test run and link it to the test run in Xray.
    Examples
    --------
    >>> client = XrayGraphQL()
    >>> test_plan_tests = client.get_tests_from_test_plan("TEST-123")
    >>> print(test_plan_tests)
    {'TEST-124': '10001', 'TEST-125': '10002'}
    >>> test_execution = client.create_test_execution_from_test_plan("TEST-123")
    >>> print(test_execution)
    {
        'TEST-124': {
            'test_run_id': '5f7c3',
            'test_execution_key': 'TEST-456',
            'test_plan_key': 'TEST-123'
        }
    }
    >>> # Update test run status
    >>> success = client.update_test_run_status("test_run_id", "PASS")
    >>> print(success)
    True
    >>> # Add evidence to test run
    >>> evidence_added = client.add_evidence_to_test_run("test_run_id", "/path/to/screenshot.png")
    >>> print(evidence_added)
    True
    Notes
    -----
    - Requires valid Xray Cloud credentials (client_id and client_secret)
    - Uses GraphQL for all API interactions
    - Implements automatic token refresh
    - Handles rate limiting and retries
    - All methods include comprehensive error handling and logging
    - Returns None for failed operations instead of raising exceptions
    - Supports various file types for evidence attachments
    - Integrates with JIRA for defect creation and issue management
    - Provides both synchronous and asynchronous operation patterns
    - Includes retry logic for transient failures
    """
    
    def __init__(self):
        """Initialize XrayGraphQL client with authentication and configuration settings.    
        This constructor sets up the XrayGraphQL client by:
        1. Loading environment variables from .env file
        2. Reading required environment variables for authentication
        3. Configuring the base URL for Xray Cloud
        4. Obtaining an authentication token
        Required Environment Variables
        ----------------------------
        XRAY_CLIENT_ID : str
            Client ID for Xray authentication
        XRAY_CLIENT_SECRET : str
            Client secret for Xray authentication
        XRAY_BASE_URL : str, optional
            Base URL for Xray Cloud API. Defaults to 'https://us.xray.cloud.getxray.app'
        Attributes
        ----------
        client_id : str
            Xray client ID from environment
        client_secret : str
            Xray client secret from environment
        xray_base_url : str
            Base URL for Xray Cloud API
        logger : Logger
            Logger instance for debugging and error tracking
        token : str
            Authentication token obtained from Xray
        Raises
        ------
        Exception
            If authentication fails or required environment variables are missing
        """
        super().__init__()
        try:
            # Load environment variables from .env file
            self.client_id = os.getenv('XRAY_CLIENT_ID')
            self.client_secret = os.getenv('XRAY_CLIENT_SECRET')
            self.xray_base_url = os.getenv('XRAY_BASE_URL', 'https://us.xray.cloud.getxray.app')
            self.logger = logger
            # Validate required environment variables
            if not self.client_id or self.client_id == '<CLIENT_ID>':
                raise ValueError("XRAY_CLIENT_ID environment variable is required")
            if not self.client_secret or self.client_secret == '<CLIENT_SECRET>':
                raise ValueError("XRAY_CLIENT_SECRET environment variable is required")
            # Get authentication token
            self.token = self._get_auth_token()
            if not self.token:
                logger.error("Failed to authenticate with Xray GraphQL")
                raise Exception("Failed to initialize XrayGraphQL: No authentication token")
        except Exception as e:
            logger.error(f"Error initializing XrayGraphQL: {e}")
            logger.traceback(e)
            raise e
    
    def _get_auth_token(self) -> Optional[str]:
        """Authenticate with Xray Cloud API and obtain an authentication token.
        Makes a POST request to the Xray authentication endpoint using the client credentials 
        to obtain a JWT token for subsequent API calls.
        Returns
        -------
        Optional[str]
            The authentication token if successful, None if authentication fails.
            The token is stripped of surrounding quotes before being returned.
        Raises
        ------
        requests.exceptions.RequestException
            If the HTTP request fails
        requests.exceptions.HTTPError
            If the server returns an error status code
        Notes
        -----
        - The token is obtained from the Xray Cloud API endpoint /api/v2/authenticate
        - The method uses client credentials stored in self.client_id and self.client_secret
        - Failed authentication attempts are logged as errors
        - Successful authentication is logged at debug level
        """
        try:
            auth_url = f"{self.xray_base_url}/api/v2/authenticate"
            auth_headers = {"Content-Type": "application/json"}
            auth_payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            # logger.debug("Attempting Xray authentication", "auth_start")
            logger.debug("Attempting Xray authentication... auth start")
            response = requests.post(auth_url, headers=auth_headers, json=auth_payload)
            response.raise_for_status()
            token = response.text.strip('"')
            # logger.info("Successfully authenticated with Xray", "auth_success")
            logger.debug("Successfully authenticated with Xray... auth success again")
            return token
        except Exception as e:
            # logger.error("Xray authentication failed", "auth_failed", error=e)
            logger.error("Xray authentication failed. auth failed")
            logger.traceback(e)
            return None
    
    def _parse_table(self, table_str: str) -> Dict[str, Union[List[int], List[float]]]:
        """Parse a string representation of a table into a dictionary of numeric values.
        Parameters
        ----------
        table_str : str
            A string containing the table data in markdown-like format.
            Example format::
                header1 || header2 || header3
                |row1   |value1    |[1, 2, 3]|
                |row2   |value2    |42       |
        Returns
        -------
        Dict[str, Union[List[int], List[float]]]
            A dictionary where:
            * Keys are strings derived from the first column (lowercase, underscores)
            * Values are either:
                * Lists of integers/floats (for array-like values in brackets)
                * Lists of individual numbers (for single numeric values)
            For non-array columns, duplicate values are removed and sorted.
            Returns None if parsing fails.
        Examples
        --------
        >>> table_str = '''header1 || header2
        ...                |temp   |[1, 2, 3]|
        ...                |value  |42       |'''
        >>> result = client._parse_table(table_str)
        >>> print(result)
        {
            'temp': [1, 2, 3],
            'value': [42]
        }
        """
        try:
            # Split the table into lines
            lines = table_str.strip().split('\n')
            # Process each data row
            result = {}
            for line in lines[1:]:
                if not line.startswith('|'):
                    continue
                # Split the row into columns
                columns = [col.strip() for col in line.split('|')[1:-1]]
                if not columns:
                    continue
                key = columns[0].replace(' ', '_').lower()
                values = []
                # Process each value column
                for col in columns[1:]:
                    # Handle list values
                    if col.startswith('[') and col.endswith(']'):
                        try:
                            # Clean and parse the list
                            list_str = col[1:-1].replace(',', ' ')
                            list_items = [item.strip() for item in list_str.split() if item.strip()]
                            num_list = [float(item) if '.' in item else int(item) for item in list_items]
                            values.append(num_list)
                        except (ValueError, SyntaxError):
                            pass
                    elif col.strip():  # Handle simple numeric values
                        try:
                            num = float(col) if '.' in col else int(col)
                            values.append(num)
                        except ValueError:
                            pass
                # Store in result
                if key:
                    if key in result:
                        result[key].extend(values)
                    else:
                        result[key] = values
            # For temperature (simple values), remove duplicates and sort
            for key in result:
                if all(not isinstance(v, list) for v in result[key]):
                    result[key] = sorted(list(set(result[key])))
            return result
        except Exception as e:
            logger.error(f"Error parsing table: {e}")
            logger.traceback(e)
            return None
    
    def _make_graphql_request(self, query: str, variables: Dict) -> Optional[Dict]:
        """
        Makes a GraphQL request to the Xray API with the provided query and variables.
        This internal method handles the execution of GraphQL queries against the Xray API,
        including proper authentication and error handling.
        Args:
            query (str): The GraphQL query or mutation to execute
            variables (Dict): Variables to be used in the GraphQL query/mutation
        Returns:
            Optional[Dict]: The 'data' field from the GraphQL response if successful,
                           None if the request fails or contains GraphQL errors
        Raises:
            No exceptions are raised - all errors are caught, logged, and return None
        Example:
            query = '''
                query GetTestPlan($id: String!) {
                    getTestPlan(issueId: $id) {
                        issueId
                    }
                }
            '''
            variables = {"id": "12345"}
            result = self._make_graphql_request(query, variables)
        Note:
            - Automatically includes authentication token in request headers
            - Logs errors if the request fails or if GraphQL errors are present
            - Returns None instead of raising exceptions to allow for graceful error handling
            - Only returns the 'data' portion of the GraphQL response
        """
        try:
            graphql_url = f"{self.xray_base_url}/api/v2/graphql"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            payload = {"query": query, "variables": variables}
            # logger.debug(f'Making GraphQL request "query": {query}, "variables": {variables} ')
            response = requests.post(graphql_url, headers=headers, json=payload)
            # jprint(response.json())

            response.raise_for_status()
            try:
                data = response.json()
                # jprint(data)
            except:
                data = response.text
                logger.debug(f"Response text: {data}")
            if 'errors' in data:
                logger.error(f'GraphQL request failed: {data["errors"]}')
                return None
            return data['data']
        except Exception as e:
            logger.error(f"GraphQL request failed due to {e} ")
            logger.traceback(e)
            return None
    
    def get_issue_id_from_jira_id(self, issue_key: str) -> Optional[str]:
        """
        Retrieves the internal JIRA issue ID for a given JIRA issue key.
        
        This method uses the JIRA API to fetch issue details and extract the internal
        issue ID. The internal ID is a numeric identifier used by JIRA internally,
        different from the human-readable issue key.
        
        Parameters
        ----------
        issue_key : str
            The JIRA issue key to retrieve the internal ID for (e.g., "PROJ-123")
            
        Returns
        -------
        Optional[str]
            The internal JIRA issue ID if found, None if:
            - The issue key doesn't exist
            - The JIRA API request fails
            - Any other error occurs during processing
            
        Examples
        --------
        >>> client.get_issue_id_from_jira_id("TEST-123")
        '10000'
        >>> client.get_issue_id_from_jira_id("INVALID-789")
        None
        
        Notes
        -----
        - The method uses the JIRA REST API via the get_issue() method
        - The internal ID is different from the issue key (e.g., "TEST-123" vs "10000")
        - Failed operations are logged as errors with relevant details
        - The method handles missing issues gracefully by returning None
        """
        try:
            issue = self.get_issue(issue_key)
            if isinstance(issue, dict):
                return(issue.get('id', None))
            return None
        except Exception as e:
            logger.error(f"Failed to get issue ID for {issue_key}")
            logger.traceback(e)
            return None
    
    def get_test_details(self, issue_key: str, issue_type: str) -> Optional[str]:
        """
        Retrieves the internal Xray issue ID for a given JIRA issue key and type.
        This method queries the Xray GraphQL API to find the internal issue ID corresponding
        to a JIRA issue key. It supports different types of Xray artifacts including test plans,
        test executions, test sets, and tests.
        Args:
            issue_key (str): The JIRA issue key (e.g., "PROJECT-123")
            issue_type (str): The type of Xray artifact. Supported values are:
                - "plan" or contains "plan": For Test Plans
                - "exec" or contains "exec": For Test Executions
                - "set" or contains "set": For Test Sets
                - "test" or contains "test": For Tests
                If not provided, defaults to "plan"
        Returns:
            Optional[str]: The internal Xray issue ID if found, None if:
                - The issue key doesn't exist
                - The GraphQL request fails
                - Any other error occurs during processing
        Examples:
            >>> client.get_issue_id_from_jira_id("TEST-123")
            '10000'
            >>> client.get_issue_id_from_jira_id("TEST-456")
            '10001'
            >>> client.get_issue_id_from_jira_id("INVALID-789")
            None
        Note:
            The method performs a case-insensitive comparison when matching issue keys.
            The project key is extracted from the issue_key (text before the hyphen)
            to filter results by project.
        """
        try:
            parse_project = issue_key.split("-")[0]
            function_name = "getTestPlans"
            if not issue_type:
                issue_type = "plan"
            if "plan" in issue_type.lower():
                function_name = "getTestPlans"
                jira_fields = [
                    "key", "summary", "description", "assignee", 
                    "status", "priority", "labels", "created", 
                    "updated", "dueDate", "components", "versions", 
                    "attachments", "comments"
                ]
                query = """
                    query GetDetails($limit: Int!, $jql: String!) {    
                        getTestPlans(limit: $limit, jql:$jql) {
                            results {
                                issueId
                                jira(fields: ["key"])
                            }
                        }
                    }
                    """
            if "exec" in issue_type.lower():
                function_name = "getTestExecutions"
                jira_fields = [
                    "key", "summary", "description", "assignee", 
                    "status", "priority", "labels", "created", 
                    "updated", "dueDate", "components", "versions", 
                    "attachments", "comments"
                ]
                query = """
                    query GetDetails($limit: Int!, $jql: String!) {    
                        getTestExecutions(limit: $limit, jql:$jql) {
                            results {
                                issueId
                                jira(fields: ["key"])
                            }
                        }
                    }
                    """
            if "set" in issue_type.lower():
                function_name = "getTestSets"
                jira_fields = [
                    "key", "summary", "description", "assignee", 
                    "status", "priority", "labels", "created", 
                    "updated", "dueDate", "components", "versions", 
                    "attachments", "comments"
                ]
                query = """
                    query GetDetails($limit: Int!, $jql: String!) {    
                        getTestSets(limit: $limit, jql:$jql) {
                            results {
                                issueId
                                jira(fields: ["key"])
                            }
                        }
                    }
                    """
            if "test" in issue_type.lower():
                function_name = "getTests"
                jira_fields = [
                    "key", "summary", "description", "assignee", 
                    "status", "priority", "labels", "created", 
                    "updated", "dueDate", "components", "versions", 
                    "attachments", "comments"
                ]
                query = """
                    query GetDetails($limit: Int!, $jql: String!, $jiraFields: [String!]!) {    
                        getTests(limit: $limit, jql:$jql) {
                            results {
                                issueId
                                jira(fields: $jiraFields)
                                steps {
                                    id
                                    action
                                    result
                                    attachments {
                                    id
                                    filename
                                    storedInJira
                                    downloadLink
                                    }
                                }
                                
                            }
                        }
                    }
                    """
            variables = {
                "limit": 10,
                "jql": f"project = '{parse_project}' AND key = '{issue_key}'",
                "jiraFields": jira_fields
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get issue ID for {issue_key}")
                return None
            for issue in data[function_name]['results']:
                if str(issue['jira']['key']).lower() == issue_key.lower():
                    return issue  # This now includes all metadata
            return None
        except Exception as e:
            logger.error(f"Failed to get issue ID for {issue_key}")
            logger.traceback(e)
            return None
    
    def get_tests_from_test_plan(self, test_plan: str) -> Optional[Dict[str, str]]:
        """
        Retrieves all tests associated with a given test plan from Xray.
        This method queries the Xray GraphQL API to fetch all tests that are part of the specified
        test plan. It first converts the JIRA test plan key to an internal Xray ID, then uses that
        ID to fetch the associated tests.
        Args:
            test_plan (str): The JIRA issue key of the test plan (e.g., "PROJECT-123")
        Returns:
            Optional[Dict[str, str]]: A dictionary mapping test JIRA keys to their Xray issue IDs,
                or None if the operation fails. For example:
                {
                    "PROJECT-124": "10001",
                    "PROJECT-125": "10002"
                }
                Returns None in the following cases:
                - Test plan ID cannot be found
                - GraphQL request fails
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> tests = client.get_tests_from_test_plan("PROJECT-123")
            >>> print(tests)
            {"PROJECT-124": "10001", "PROJECT-125": "10002"}
        Note:
            - The method is limited to retrieving 99999 tests per test plan
            - Test plan must exist in Xray and be accessible with current authentication
        """
        try:
            test_plan_id = self.get_issue_id_from_jira_id(test_plan)
            if not test_plan_id:
                logger.error(f"Failed to get test plan ID for {test_plan}")
                return None
            query = """
            query GetTestPlanTests($testPlanId: String!) {
                getTestPlan(issueId: $testPlanId) {
                    tests(limit: 100) {
                        results {   
                            issueId
                            jira(fields: ["key"])
                        }
                    }
                }
            }
            """
            variables = {"testPlanId": test_plan_id}
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get tests for plan {test_plan_id}")
                return None
            tests = {}
            for test in data['getTestPlan']['tests']['results']:
                tests[test['jira']['key']] = test['issueId']
            return tests
        except Exception as e:
            logger.error(f"Failed to get tests for plan {test_plan_id}")
            logger.traceback(e)
            return None
    
    def get_tests_from_test_set(self, test_set: str) -> Optional[Dict[str, str]]:
        """
        Retrieves all tests associated with a given test set from Xray.
        This method queries the Xray GraphQL API to fetch all tests that are part of the specified
        test set. It first converts the JIRA test set key to an internal Xray ID, then uses that
        ID to fetch the associated tests.
        Args:
            test_set (str): The JIRA issue key of the test set (e.g., "PROJECT-123")
        Returns:
            Optional[Dict[str, str]]: A dictionary mapping test JIRA keys to their Xray issue IDs,
                or None if the operation fails. For example:
                {
                    "PROJECT-124": "10001",
                    "PROJECT-125": "10002"
                }
                Returns None in the following cases:
                - Test set ID cannot be found
                - GraphQL request fails
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> tests = client.get_tests_from_test_set("PROJECT-123")
            >>> print(tests)
            {"PROJECT-124": "10001", "PROJECT-125": "10002"}
        Note:
            - The method is limited to retrieving 99999 tests per test set
            - Test set must exist in Xray and be accessible with current authentication
        """
        try:
            test_set_id = self.get_issue_id_from_jira_id(test_set)
            if not test_set_id:
                logger.error(f"Failed to get test set ID for {test_set}")
                return None
            query = """
            query GetTestSetTests($testSetId: String!) {
                getTestSet(issueId: $testSetId) {
                    tests(limit: 100) {
                        results {   
                            issueId
                            jira(fields: ["key"])
                        }
                    }
                }
            }
            """
            variables = {"testSetId": test_set_id}
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get tests for set {test_set_id}")
                return None
            tests = {}
            for test in data['getTestSet']['tests']['results']:
                tests[test['jira']['key']] = test['issueId']
            return tests
        except Exception as e:
            logger.error(f"Failed to get tests for set {test_set_id}")
            logger.traceback(e)
            return None
    
    def get_tests_from_test_execution(self, test_execution: str) -> Optional[Dict[str, str]]:
        """
        Retrieves all tests associated with a given test execution from Xray.
        This method queries the Xray GraphQL API to fetch all tests that are part of the specified
        test execution. It first converts the JIRA test execution key to an internal Xray ID, then uses that
        ID to fetch the associated tests.
        Args:
            test_execution (str): The JIRA issue key of the test execution (e.g., "PROJECT-123")
        Returns:
            Optional[Dict[str, str]]: A dictionary mapping test JIRA keys to their Xray issue IDs,
                or None if the operation fails. For example:
                {
                    "PROJECT-124": "10001",
                    "PROJECT-125": "10002"
                }
                Returns None in the following cases:
                - Test execution ID cannot be found
                - GraphQL request fails
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> tests = client.get_tests_from_test_execution("PROJECT-123")
            >>> print(tests)
            {"PROJECT-124": "10001", "PROJECT-125": "10002"}
        Note:
            - The method is limited to retrieving 99999 tests per test execution
            - Test execution must exist in Xray and be accessible with current authentication
        """
        try:
            test_execution_id = self.get_issue_id_from_jira_id(test_execution)
            if not test_execution_id:
                logger.error(f"Failed to get test execution ID for {test_execution}")
                return None
            query = """
            query GetTestExecutionTests($testExecutionId: String!) {
                getTestExecution(issueId: $testExecutionId) {
                    tests(limit: 100) {
                        results {   
                            issueId
                            jira(fields: ["key"])
                        }
                    }
                }
            }
            """
            variables = {"testExecutionId": test_execution_id}
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get tests for execution {test_execution_id}")
                return None
            tests = {}
            for test in data['getTestExecution']['tests']['results']:
                tests[test['jira']['key']] = test['issueId']
            return tests
        except Exception as e:
            logger.error(f"Failed to get tests for execution {test_execution_id}")
            logger.traceback(e)
            return None
    
    def get_test_plan_data(self, test_plan: str) -> Optional[Dict[str, Union[List[int], List[float]]]]:
        """
        Retrieve and parse tabular data from a test plan's description field in Xray.
        This method fetches a test plan's description from Xray and parses any tables found within it.
        The tables in the description are expected to be in a specific format that can be parsed by
        the _parse_table method. The parsed data is returned as a dictionary containing numeric values
        and lists extracted from the table.
        Args:
            test_plan (str): The JIRA issue key of the test plan (e.g., "PROJECT-123")
        Returns:
            Optional[Dict[str, Union[List[int], List[float]]]]: A dictionary containing the parsed table data
                where keys are derived from the first column of the table and values are lists of numeric
                values. Returns None if:
                - The test plan ID cannot be found
                - The GraphQL request fails
                - The description cannot be parsed
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> data = client.get_test_plan_data("TEST-123")
            >>> print(data)
            {
                'temperature': [20, 25, 30],
                'pressure': [1.0, 1.5, 2.0],
                'measurements': [[1, 2, 3], [4, 5, 6]]
            }
        Note:
            - The test plan must exist in Xray and be accessible with current authentication
            - The description must contain properly formatted tables for parsing
            - Table values are converted to numeric types (int or float) where possible
            - Lists in table cells should be formatted as [value1, value2, ...]
            - Failed operations are logged as errors with relevant details
        """
        try:
            test_plan_id = self.get_issue_id_from_jira_id(test_plan)
            if not test_plan_id:
                logger.error(f"Failed to get test plan ID for {test_plan}")
                return None
            query = """
            query GetTestPlanTests($testPlanId: String!) {
                getTestPlan(issueId: $testPlanId) {
                    issueId
                    jira(fields: ["key","description"])
                }
            }
            """
            variables = {"testPlanId": test_plan_id}
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get tests for plan {test_plan_id}")
                return None
            description = data['getTestPlan']['jira']['description']
            test_plan_data = self._parse_table(description)
            return test_plan_data            
        except Exception as e:
            logger.error(f"Failed to get tests for plan {test_plan_id}")
            logger.traceback(e)
            return None
    
    def filter_test_set_by_test_case(self, test_key: str) -> Optional[Dict[str, str]]:
        """
        Retrieves all test sets that contain a specific test case from Xray.
        This method queries the Xray GraphQL API to find all test sets that include the specified
        test case. It first converts the JIRA test case key to an internal Xray ID, then uses that
        ID to fetch all associated test sets.
        Args:
            test_key (str): The JIRA issue key of the test case (e.g., "PROJECT-123")
        Returns:
            Optional[Dict[str, str]]: A dictionary mapping test set JIRA keys to their summaries,
                or None if the operation fails. For example:
                {
                    "PROJECT-124": "Test Set for Feature A",
                    "PROJECT-125": "Regression Test Set"
                }
                Returns None in the following cases:
                - Test case ID cannot be found
                - GraphQL request fails
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> test_sets = client.filter_test_set_by_test_case("PROJECT-123")
            >>> print(test_sets)
            {"PROJECT-124": "Test Set for Feature A", "PROJECT-125": "Regression Test Set"}
        Note:
            - The method is limited to retrieving 99999 test sets per test case
            - Test case must exist in Xray and be accessible with current authentication
        """
        try:
            test_id = self.get_issue_id_from_jira_id(test_key)
            if not test_id:
                logger.error(f"Failed to get test ID for  Test Case ({test_key})")
                return None
            query = """
            query GetTestDetails($testId: String!) {
                getTest(issueId: $testId) {
                    testSets(limit: 100) {
                        results {   
                            issueId
                            jira(fields: ["key","summary"])
                        }
                    }
                }
            }   
            """
            variables = {
                "testId": test_id
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get tests for plan {test_id}")
                return None
            retDict = {}
            for test in data['getTest']['testSets']['results']:
                retDict[test['jira']['key']] = test['jira']['summary']
            return retDict
        except Exception as e:
            logger.error(f"Error in getting test set by test id: {e}")
            logger.traceback(e)
            return None 
    
    def filter_tags_by_test_case(self, test_key: str) -> Optional[List[str]]:
        """
        Extract and filter tags from test sets associated with a specific test case in Xray.
        This method queries the Xray GraphQL API to find all test sets associated with the given
        test case and extracts tags from their summaries. Tags are identified from test set summaries
        that start with either 'tag' or 'benchtype' prefixes.
        Args:
            test_key (str): The JIRA issue key of the test case (e.g., "PROJECT-123")
        Returns:
            Optional[List[str]]: A list of unique tags extracted from test set summaries,
                or None if no tags are found or an error occurs. Tags are:
                - Extracted from summaries starting with 'tag:' or 'benchtype:'
                - Split on commas, semicolons, double pipes, or whitespace
                - Converted to lowercase and stripped of whitespace
        Example:
            >>> client = XrayGraphQL()
            >>> tags = client.filter_tags_by_test_case("TEST-123")
            >>> print(tags)
            ['regression', 'smoke', 'performance']
        Note:
            - Test sets must have summaries in the format "tag: tag1, tag2" or "benchtype: type1, type2"
            - Tags are extracted only from summaries with the correct prefix
            - All tags are converted to lowercase for consistency
            - Duplicate tags are automatically removed via set conversion
            - Returns None if no valid tags are found or if an error occurs
        """
        try:
            test_id = self.get_issue_id_from_jira_id(test_key)
            if not test_id:
                logger.error(f"Failed to get test ID for  Test Case ({test_key})")
                return None
            query = """
            query GetTestDetails($testId: String!) {
                getTest(issueId: $testId) {
                    testSets(limit: 100) {
                        results {   
                            issueId
                            jira(fields: ["key","summary"])
                        }
                    }
                }
            }   
            """
            variables = {
                "testId": test_id
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get tests for plan {test_id}")
                return None
            tags = set()
            for test in data['getTest']['testSets']['results']:
                summary = str(test['jira']['summary']).strip().lower()
                if summary.startswith(('tag', 'benchtype')):
                    summary = summary.split(':', 1)[-1].strip()  # Split only once and take last part
                    tags.update(tag for tag in re.split(r'[,|;|\|\|]\s*|\s+', summary) if tag)
            if tags:
                return list(tags)
            else:
                return None
        except Exception as e:
            logger.error(f"Error in getting test set by test id: {e}")
            logger.traceback(e)
            return None 
    
    def get_test_runstatus(self, test_case: str, test_execution: str) -> Optional[Tuple[str, str]]:
        """
        Retrieve the status of a test run for a specific test case within a test execution.
        This method queries the Xray GraphQL API to get the current status of a test run,
        which represents the execution status of a specific test case within a test execution.
        It first converts both the test case and test execution JIRA keys to their internal
        Xray IDs, then uses these to fetch the test run status.
        Args:
            test_case (str): The JIRA issue key of the test case (e.g., "PROJECT-123")
            test_execution (str): The JIRA issue key of the test execution (e.g., "PROJECT-456")
        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing:
                - test_run_id: The unique identifier of the test run (or None if not found)
                - test_run_status: The current status of the test run (or None if not found)
                Returns (None, None) if any error occurs during the process.
        Example:
            >>> client = XrayGraphQL()
            >>> run_id, status = client.get_test_runstatus("TEST-123", "TEST-456")
            >>> print(f"Test Run ID: {run_id}, Status: {status}")
            Test Run ID: 10001, Status: PASS
        Note:
            - Both the test case and test execution must exist in Xray and be accessible
            - The test case must be associated with the test execution
            - The method performs two ID lookups before querying the test run status
            - Failed operations are logged as errors with relevant details
        """
        try:
            test_case_id = self.get_issue_id_from_jira_id(test_case)
            if not test_case_id:
                logger.error(f"Failed to get test ID for Test Case ({test_case})")
                return None
            test_exec_id = self.get_issue_id_from_jira_id(test_execution)
            if not test_exec_id:
                logger.error(f"Failed to get test execution ID for Test Execution ({test_execution})")
                return None
            query = """
            query GetTestRunStatus($testId: String!, $testExecutionId: String!) {
                getTestRun( testIssueId: $testId, testExecIssueId: $testExecutionId) {
                    id
                    status {
                        name
                    }
                }
            }
            """
            variables = {
                "testId": test_case_id,
                "testExecutionId": test_exec_id,
            }
            # Add debug loggerging
            logger.debug(f"Getting test run status for test {test_case_id} in execution {test_exec_id}")
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get test run status for test {test_case_id}")
                return None
            # jprint(data)
            test_run_id = data['getTestRun']['id']
            test_run_status = data['getTestRun']['status']['name']
            return (test_run_id, test_run_status)
        except Exception as e:
            logger.error(f"Error getting test run status: {str(e)}")
            logger.traceback(e)
            return (None, None)
    
    def get_test_run_by_id(self, test_case_id: str, test_execution_id: str) -> Optional[Tuple[str, str]]:
        """
        Retrieves the test run ID and status for a specific test case within a test execution using GraphQL.
        Args:
            test_case_id (str): The ID of the test case to query
            test_execution_id (str): The ID of the test execution containing the test run
        Returns:
            tuple[Optional[str], Optional[str]]: A tuple containing:
                - test_run_id: The ID of the test run if found, None if not found or on error
                - test_run_status: The status name of the test run if found, None if not found or on error
        Note:
            The function makes a GraphQL request to fetch the test run information. If the request fails
            or encounters any errors, it will log the error and return (None, None).
        """
        try:
            query = """
            query GetTestRunStatus($testId: String!, $testExecutionId: String!) {
                getTestRun( testIssueId: $testId, testExecIssueId: $testExecutionId) {
                    id
                    status {
                        name
                    }
                }
            }
            """
            variables = {
                "testId": test_case_id,
                "testExecutionId": test_execution_id,
            }
            # Add debug loggerging
            logger.debug(f"Getting test run status for test {test_case_id} in execution {test_execution_id}")
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get test run status for test {test_case_id}")
                return None
            test_run_id = data['getTestRun']['id']
            test_run_status = data['getTestRun']['status']['name']
            return (test_run_id, test_run_status)
        except Exception as e:
            logger.error(f"Error getting test run status: {str(e)}")
            logger.traceback(e)
            return (None, None)
    
    def get_test_execution(self, test_execution: str) -> Optional[Dict]:
        """
        Retrieve detailed information about a test execution from Xray.
        This method queries the Xray GraphQL API to fetch information about a specific test execution,
        including its ID and associated tests. It first converts the JIRA test execution key to an
        internal Xray ID, then uses that ID to fetch the execution details.
        Args:
            test_execution (str): The JIRA issue key of the test execution (e.g., "PROJECT-123")
        Returns:
            Optional[Dict]: A dictionary containing test execution details if successful, None if failed.
                The dictionary has the following structure:
                {
                    'id': str,          # The internal Xray ID of the test execution
                    'tests': {          # Dictionary mapping test keys to their IDs
                        'TEST-124': '10001',
                        'TEST-125': '10002',
                        ...
                    }
                }
                Returns None in the following cases:
                - Test execution ID cannot be found
                - GraphQL request fails
                - No test execution found with the given ID
                - No tests found in the test execution
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> execution = client.get_test_execution("TEST-123")
            >>> print(execution)
            {
                'id': '10000',
                'tests': {
                    'TEST-124': '10001',
                    'TEST-125': '10002'
                }
            }
        Note:
            - The method is limited to retrieving 99999 tests per test execution
            - Test execution must exist in Xray and be accessible with current authentication
            - Failed operations are logged with appropriate error or warning messages
        """
        try:
            test_execution_id = self.get_issue_id_from_jira_id(test_execution)
            if not test_execution_id:
                logger.error(f"Failed to get test execution ID for {test_execution}")
                return None
            query = """
            query GetTestExecution($testExecutionId: String!) {
                getTestExecution(issueId: $testExecutionId) {
                    issueId
                    projectId
                    jira(fields: ["key", "summary", "description", "status"])
                    tests(limit: 100) {
                        total
                        start
                        limit
                        results {
                            issueId
                            jira(fields: ["key"])
                        }
                    }
                }
            }
            """
            variables = {
                "testExecutionId": test_execution_id
            }
            # Add debug loggerging
            logger.debug(f"Getting test execution details for {test_execution_id}")
            data = self._make_graphql_request(query, variables)
            # jprint(data)
            if not data:
                logger.error(f"Failed to get test execution details for {test_execution_id}")
                return None
            test_execution = data.get('getTestExecution',{})
            if not test_execution:
                logger.warning(f"No test execution found with ID {test_execution_id}")
                return None
            tests = test_execution.get('tests',{})
            if not tests:
                logger.warning(f"No tests found for test execution {test_execution_id}")
                return None
            tests_details = dict()
            for test in tests['results']:
                tests_details[test['jira']['key']] = test['issueId']
            formatted_response = {
                'id': test_execution['issueId'],
                'tests': tests_details
            }
            return formatted_response
        except Exception as e:
            logger.error(f"Error getting test execution details: {str(e)}")
            logger.traceback(e)
            return None
    
    def add_test_execution_to_test_plan(self, test_plan: str, test_execution: str) -> Optional[Dict]:
        """
        Add a test execution to an existing test plan in Xray.
        This method associates a test execution with a test plan using the Xray GraphQL API.
        It first converts both the test plan and test execution JIRA keys to their internal
        Xray IDs, then creates the association between them.
        Args:
            test_plan (str): The JIRA issue key of the test plan (e.g., "PROJECT-123")
            test_execution (str): The JIRA issue key of the test execution to add (e.g., "PROJECT-456")
        Returns:
            Optional[Dict]: A dictionary containing the response data if successful, None if failed.
                The dictionary has the following structure:
                {
                    'addTestExecutionsToTestPlan': {
                        'addedTestExecutions': [str],  # List of added test execution IDs
                        'warning': str                 # Any warnings from the operation
                    }
                }
                Returns None in the following cases:
                - Test plan ID cannot be found
                - Test execution ID cannot be found
                - GraphQL request fails
                - Any other error occurs during processing
        Example:
            >>> client = XrayGraphQL()
            >>> result = client.add_test_execution_to_test_plan("TEST-123", "TEST-456")
            >>> print(result)
            {
                'addTestExecutionsToTestPlan': {
                    'addedTestExecutions': ['10001'],
                    'warning': None
                }
            }
        Note:
            - Both the test plan and test execution must exist in Xray and be accessible
            - The method performs two ID lookups before creating the association
            - Failed operations are logged as errors with relevant details
        """
        try:
            test_plan_id = self.get_issue_id_from_jira_id(test_plan)
            if not test_plan_id:
                logger.error(f"Test plan ID is required")
                return None
            test_exec_id = self.get_issue_id_from_jira_id(test_execution)
            if not test_exec_id:
                logger.error(f"Test execution ID is required")
                return None
            query = """
            mutation AddTestExecutionToTestPlan($testPlanId: String!, $testExecutionIds: [String!]!) {
                addTestExecutionsToTestPlan(issueId: $testPlanId, testExecIssueIds: $testExecutionIds) {
                    addedTestExecutions 
                    warning
                }
            }
            """
            variables = {
                "testPlanId": test_plan_id,
                "testExecutionIds": [test_exec_id]
            }
            data = self._make_graphql_request(query, variables)
            return data
        except Exception as e:
            logger.error(f"Error adding test execution to test plan: {str(e)}")
            logger.traceback(e)
            return None
    
    def create_test_execution(self, 
                            test_issue_keys: List[str], 
                            project_key: Optional[str] = None, 
                            summary: Optional[str] = None, 
                            description: Optional[str] = None) -> Optional[Dict]:
        """
        Create a new test execution in Xray with specified test cases.
        This method creates a test execution ticket in JIRA/Xray that includes the specified test cases.
        It handles validation of test issue keys, automatically derives project information if not provided,
        and creates appropriate default values for summary and description if not specified.
        Args:
            test_issue_keys (List[str]): List of JIRA issue keys for test cases to include in the execution
                (e.g., ["TEST-123", "TEST-124"])
            project_key (Optional[str]): The JIRA project key where the test execution should be created.
                If not provided, it will be derived from the first test issue key.
            summary (Optional[str]): The summary/title for the test execution ticket.
                If not provided, a default summary will be generated using the test issue keys.
            description (Optional[str]): The description for the test execution ticket.
                If not provided, a default description will be generated using the test issue keys.
        Returns:
            Optional[Dict]: A dictionary containing the created test execution details if successful,
                None if the creation fails. The dictionary has the following structure:
                {
                    'issueId': str,      # The internal Xray ID of the created test execution
                    'jira': {
                        'key': str       # The JIRA issue key of the created test execution
                    }
                }
        Example:
            >>> client = XrayGraphQL()
            >>> test_execution = client.create_test_execution(
            ...     test_issue_keys=["TEST-123", "TEST-124"],
            ...     project_key="TEST",
            ...     summary="Sprint 1 Regression Tests"
            ... )
            >>> print(test_execution)
            {'issueId': '10001', 'jira': {'key': 'TEST-125'}}
        Note:
            - Invalid test issue keys are logged as warnings but don't prevent execution creation
            - At least one valid test issue key is required
            - The method validates each test issue key before creating the execution
            - Project key is automatically derived from the first test issue key if not provided
        """
        try:
            invalid_keys = []
            test_issue_ids = []
            for key in test_issue_keys:
                test_issue_id = self.get_issue_id_from_jira_id(key)
                if test_issue_id:
                    test_issue_ids.append(test_issue_id)
                else:
                    invalid_keys.append(key)
            if len(test_issue_ids) == 0:
                logger.error(f"No valid test issue keys provided: {invalid_keys}")
                return None
            if len(invalid_keys) > 0:
                logger.warning(f"Invalid test issue keys: {invalid_keys}")
            if not project_key:
                project_key = test_issue_keys[0].split("-")[0]
            if not summary:
                summary = f"Test Execution for Test Plan {test_issue_keys}"
            if not description:
                description = f"Test Execution for Test Plan {test_issue_keys}"
            mutation = """
            mutation CreateTestExecutionForTestPlan(
                $testIssueId_list: [String!]!,
                $projectKey: String!,
                $summary: String!,
                $description: String
            ) {
                createTestExecution(
                    testIssueIds: $testIssueId_list,
                    jira: {
                        fields: {
                            project: { key: $projectKey },
                            summary: $summary,
                            description: $description,
                            issuetype: { name: "Test Execution" }
                        }
                    }
                ) {
                    testExecution {
                        issueId
                        jira(fields: ["key"])
                    }
                    warnings
                }
            }
            """
            variables = {
                "testIssueId_list": test_issue_ids,
                "projectKey": project_key,
                "summary": summary,
                "description": description
            }
            data = self._make_graphql_request(mutation, variables)
            if not data:
                return None
            execution_details = data['createTestExecution']['testExecution']
            # logger.info(f"Created test execution {execution_details['jira']['key']}")
            return execution_details
        except Exception as e:
            logger.error("Failed to create test execution : {e}")
            logger.traceback(e)
            return None
    
    def create_test_execution_from_test_plan(self, test_plan: str) -> Optional[Dict[str, Dict[str, str]]]:
        """Creates a test execution from a given test plan and associates all tests from the plan with the execution.
        This method performs several operations in sequence:
        1. Retrieves all tests from the specified test plan
        2. Creates a new test execution with those tests
        3. Associates the new test execution with the original test plan
        4. Creates test runs for each test in the execution
        Parameters
        ----------
        test_plan : str
            The JIRA issue key of the test plan (e.g., "PROJECT-123")
        Returns
        -------
        Optional[Dict[str, Dict[str, str]]]
            A dictionary mapping test case keys to their execution details, or None if the operation fails.
            The dictionary structure is::
                {
                    "TEST-123": {                    # Test case JIRA key
                        "test_run_id": "12345",      # Unique ID for this test run
                        "test_execution_key": "TEST-456",  # JIRA key of the created test execution
                        "test_plan_key": "TEST-789"  # Original test plan JIRA key
                    },
                    "TEST-124": {
                        ...
                    }
                }
            Returns None in the following cases:
            * Test plan parameter is empty or invalid
            * No tests found in the test plan
            * Test execution creation fails
            * API request fails
        Examples
        --------
        >>> client = XrayGraphQL()
        >>> result = client.create_test_execution_from_test_plan("TEST-123")
        >>> print(result)
        {
            "TEST-124": {
                "test_run_id": "5f7c3",
                "test_execution_key": "TEST-456",
                "test_plan_key": "TEST-123"
            },
            "TEST-125": {
                "test_run_id": "5f7c4",
                "test_execution_key": "TEST-456",
                "test_plan_key": "TEST-123"
            }
        }
        Notes
        -----
        - The test plan must exist and be accessible in Xray
        - All tests in the test plan must be valid and accessible
        - The method automatically generates a summary and description for the test execution
        - The created test execution is automatically linked back to the original test plan
        """
        try:
            if not test_plan:
                logger.error("Test plan is required [ jira key]")
                return None
            project_key = test_plan.split("-")[0]
            summary = f"Test Execution for Test Plan {test_plan}"
            retDict = dict()
            #Get tests from test plan
            tests = self.get_tests_from_test_plan(test_plan)
            retDict["tests"] = tests
            testIssueId_list = list(tests.values())
            # logger.info(f"Tests: {tests}")
            if not testIssueId_list:
                logger.error(f"No tests found for {test_plan}")
                return None
            description = f"Test Execution for {len(tests)} Test cases"
            # GraphQL mutation to create test execution
            query = """
                mutation CreateTestExecutionForTestPlan(
                    $testIssueId_list: [String!]!,
                    $projectKey: String!,
                    $summary: String!,
                    $description: String
                ) {
                    createTestExecution(
                        testIssueIds: $testIssueId_list,
                        jira: {
                            fields: {
                                project: { key: $projectKey },
                                summary: $summary,
                                description: $description,
                                issuetype: { name: "Test Execution" }
                            }
                        }
                    ) {
                        testExecution {
                            issueId
                            jira(fields: ["key"])
                            testRuns(limit: 100) {
                                results {
                                    id
                                    test {
                                        issueId
                                        jira(fields: ["key"])
                                    }
                                }
                            }
                        }
                        warnings
                    }
                }
            """
            variables = {
                "testIssueId_list": testIssueId_list,
                "projectKey": project_key,
                "summary": summary,
                "description": description or f"Test execution for total of {len(testIssueId_list)} test cases"
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                return None
            test_exec_key = data['createTestExecution']['testExecution']['jira']['key']
            test_exec_id = data['createTestExecution']['testExecution']['issueId']
            #Add Test execution to test plan
            test_exec_dict= self.add_test_execution_to_test_plan(test_plan, test_exec_key)
            #Get test runs for test execution
            test_runs = data['createTestExecution']['testExecution']['testRuns']['results']
            test_run_dict = dict()
            for test_run in test_runs:
                test_run_dict[test_run['test']['jira']['key']] = dict()
                test_run_dict[test_run['test']['jira']['key']]['test_run_id'] = test_run['id']
                # test_run_dict[test_run['test']['jira']['key']]['test_issue_id'] = test_run['test']['issueId']
                test_run_dict[test_run['test']['jira']['key']]['test_execution_key'] = test_exec_key
                # test_run_dict[test_run['test']['jira']['key']]['test_execution_id'] = test_exec_id
                test_run_dict[test_run['test']['jira']['key']]['test_plan_key'] = test_plan
            return test_run_dict
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating test execution: {e}")
            logger.traceback(e)
        return None
    
    def update_test_run_status(self, test_run_id: str, test_run_status: str) -> bool:
        """
        Update the status of a specific test run in Xray using the GraphQL API.
        This method allows updating the execution status of a test run identified by its ID.
        The status can be changed to reflect the current state of the test execution
        (e.g., "PASS", "FAIL", "TODO", etc.).
        Args:
            test_run_id (str): The unique identifier of the test run to update.
                This is the internal Xray ID for the test run, not the Jira issue key.
            test_run_status (str): The new status to set for the test run.
                Common values include: "PASS", "FAIL", "TODO", "EXECUTING", etc.
        Returns:
            bool: True if the status update was successful, False otherwise.
                Returns None if an error occurs during the API request.
        Example:
            >>> client = XrayGraphQL()
            >>> test_run_id = client.get_test_run_status("TEST-CASE-KEY", "TEST-EXEC-KEY")
            >>> success = client.update_test_run_status(test_run_id, "PASS")
            >>> print(success)
            True
        Note:
            - The test run ID must be valid and accessible with current authentication
            - The status value should be one of the valid status values configured in your Xray instance
            - Failed updates are logged as errors with details about the failure
        Raises:
            Exception: If there is an error making the GraphQL request or processing the response.
                The exception is caught and logged, and the method returns None.
        """
        try:
            query = """
            mutation UpdateTestRunStatus($testRunId: String!, $status: String!) {
                updateTestRunStatus(
                    id: $testRunId, 
                    status: $status 
                ) 
            }                       
            """
            variables = {
                "testRunId": test_run_id,
                "status": test_run_status
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get test run status for test {data}")
                return None
            # logger.info(f"Test run status updated: {data}")
            return data['updateTestRunStatus']
        except Exception as e:
            logger.error(f"Error updating test run status: {str(e)}")
            logger.traceback(e)
            return None
    
    def update_test_run_comment(self, test_run_id: str, test_run_comment: str) -> bool:
        """
        Update the comment of a specific test run in Xray using the GraphQL API.
        This method allows adding or updating the comment associated with a test run
        identified by its ID. The comment can provide additional context, test results,
        or any other relevant information about the test execution.
        Args:
            test_run_id (str): The unique identifier of the test run to update.
                This is the internal Xray ID for the test run, not the Jira issue key.
            test_run_comment (str): The new comment text to set for the test run.
                This will replace any existing comment on the test run.
        Returns:
            bool: True if the comment update was successful, False otherwise.
                Returns None if an error occurs during the API request.
        Example:
            >>> client = XrayGraphQL()
            >>> test_run_id = "67fcfd4b9e6d63d4c1d57b32"
            >>> success = client.update_test_run_comment(
            ...     test_run_id,
            ...     "Test passed with performance within expected range"
            ... )
            >>> print(success)
            True
        Note:
            - The test run ID must be valid and accessible with current authentication
            - The comment can include any text content, including newlines and special characters
            - Failed updates are logged as errors with details about the failure
            - This method will overwrite any existing comment on the test run
        Raises:
            Exception: If there is an error making the GraphQL request or processing the response.
                The exception is caught and logged, and the method returns None.
        """
        try:
            query = """
            mutation UpdateTestRunStatus($testRunId: String!, $comment: String!) {
                updateTestRunComment(
                    id: $testRunId, 
                    comment: $comment 
                ) 
            }                       
            """
            variables = {
                "testRunId": test_run_id,
                "comment": test_run_comment
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to get test run comment for test {data}")
                return None
            # jprint(data)
            return data['updateTestRunComment']
        except Exception as e:
            logger.error(f"Error updating test run comment: {str(e)}")
            logger.traceback(e)
            return None
    
    def add_evidence_to_test_run(self, test_run_id: str, evidence_path: str) -> bool:
        """Add evidence (attachments) to a test run in Xray.
        This method allows attaching files as evidence to a specific test run. The file is
        read, converted to base64, and uploaded to Xray with appropriate MIME type detection.
        Parameters
        ----------
        test_run_id : str
            The unique identifier of the test run to add evidence to
        evidence_path : str
            The local file system path to the evidence file to be attached
        Returns
        -------
        bool
            True if the evidence was successfully added, None if the operation failed.
            Returns None in the following cases:
            - Test run ID is not provided
            - Evidence path is not provided
            - Evidence file does not exist
            - GraphQL request fails
            - Any other error occurs during processing
        Examples
        --------
        >>> client = XrayGraphQL()
        >>> success = client.add_evidence_to_test_run(
        ...     test_run_id="10001",
        ...     evidence_path="/path/to/screenshot.png"
        ... )
        >>> print(success)
        True
        Notes
        -----
        - The evidence file must exist and be accessible
        - The file is automatically converted to base64 for upload
        - MIME type is automatically detected, defaults to "text/plain" if detection fails
        - The method supports various file types (images, documents, logs, etc.)
        - Failed operations are logged with appropriate error messages
        """
        try:
            if not test_run_id:
                logger.error("Test run ID is required")
                return None
            if not evidence_path:
                logger.error("Evidence path is required")
                return None
            if not os.path.exists(evidence_path):
                logger.error(f"Evidence file not found: {evidence_path}")
                return None
            #if file exists then read the file in base64
            evidence_base64 = None
            mime_type = None
            filename = os.path.basename(evidence_path)
            with open(evidence_path, "rb") as file:
                evidence_data = file.read()
                evidence_base64 = base64.b64encode(evidence_data).decode('utf-8')
                mime_type = mimetypes.guess_type(evidence_path)[0]
                logger.info(f"For loop -- Mime type: {mime_type}")
                if not mime_type:
                    mime_type = "text/plain"
            query = """
            mutation AddEvidenceToTestRun($testRunId: String!, $filename: String!, $mimeType: String!, $evidenceBase64: String!) {
                addEvidenceToTestRun(
                    id: $testRunId, 
                    evidence: [
                        {
                            filename : $filename,
                            mimeType : $mimeType,
                            data : $evidenceBase64
                        }
                    ]
                ) {
                    addedEvidence
                    warnings
                }
            }
            """
            variables = {
                "testRunId": test_run_id,
                "filename": filename,
                "mimeType": mime_type,
                "evidenceBase64": evidence_base64
            }
            data = self._make_graphql_request(query, variables) 
            if not data:
                logger.error(f"Failed to add evidence to test run: {data}")
                return None
            return data['addEvidenceToTestRun'] 
        except Exception as e:
            logger.error(f"Error adding evidence to test run: {str(e)}")
            logger.traceback(e)
            return None
    
    def create_defect_from_test_run(self, test_run_id: str, project_key: str, parent_issue_key: str, defect_summary: str, defect_description: str) -> Optional[Dict]:
        """Create a defect from a test run and link it to the test run in Xray.
        This method performs two main operations:
        1. Creates a new defect in JIRA with the specified summary and description
        2. Links the created defect to the specified test run in Xray
        Parameters
        ----------
        test_run_id : str
            The ID of the test run to create defect from
        project_key : str
            The JIRA project key where the defect should be created.
            If not provided, defaults to "EAGVAL"
        parent_issue_key : str
            The JIRA key of the parent issue to link the defect to
        defect_summary : str
            Summary/title of the defect.
            If not provided, defaults to "Please provide a summary for the defect"
        defect_description : str
            Description of the defect.
            If not provided, defaults to "Please provide a description for the defect"
        Returns
        -------
        Optional[Dict]
            Response data from the GraphQL API if successful, None if failed.
            The response includes:
            - addedDefects: List of added defects
            - warnings: Any warnings from the operation
        Examples
        --------
        >>> client = XrayGraphQL()
        >>> result = client.create_defect_from_test_run(
        ...     test_run_id="10001",
        ...     project_key="PROJ",
        ...     parent_issue_key="PROJ-456",
        ...     defect_summary="Test failure in login flow",
        ...     defect_description="The login button is not responding to clicks"
        ... )
        >>> print(result)
        {
            'addedDefects': ['PROJ-123'],
            'warnings': []
        }
        Notes
        -----
        - The project_key will be split on '-' and only the first part will be used
        - The defect will be created with issue type 'Bug'
        - The method handles missing parameters with default values
        - The parent issue must exist and be accessible to create the defect
        """
        try:
            if not project_key:
                project_key = "EAGVAL"
            if not defect_summary:
                defect_summary = "Please provide a summary for the defect"
            if not defect_description:
                defect_description = "Please provide a description for the defect"
            project_key = project_key.split("-")[0]
            # Fix: Correct parameter order for create_issue
            defect_key, defect_id = self.create_issue(
                project_key=project_key,
                parent_issue_key=parent_issue_key,
                summary=defect_summary,
                description=defect_description,
                issue_type='Bug'
            )
            if not defect_key:
                logger.error("Failed to create defect issue")
                return None
            # Then add the defect to the test run
            add_defect_mutation = """
            mutation AddDefectsToTestRun(
                $testRunId: String!,
                $defectKey: String!
            ) {
                addDefectsToTestRun( id: $testRunId, issues: [$defectKey]) {
                    addedDefects
                    warnings
                }
            }
            """
            variables = {
                "testRunId": test_run_id,
                "defectKey": defect_key
            }
            data = None
            retry_count = 0
            while retry_count < 3:
                data = self._make_graphql_request(add_defect_mutation, variables)
                if not data:
                    logger.error(f"Failed to add defect [{defect_key}] to test run - {test_run_id}.. retrying... {retry_count}")
                    retry_count += 1
                    time.sleep(1)
                else:
                    break
            return data
        except Exception as e:
            logger.error(f"Error creating defect from test run: {str(e)}")
            logger.traceback(e)
            return None
    
    def get_test_run_comment(self, test_run_id: str) -> Optional[str]:
        """
        Retrieve the comment of a specific test run from Xray using the GraphQL API.
        This method allows retrieving the comment associated with a test run
        identified by its ID. The comment can provide additional context, test results,
        or any other relevant information about the test execution.
        Args:
            test_run_id (str): The unique identifier of the test run to retrieve comment from.
                This is the internal Xray ID for the test run, not the Jira issue key.
        Returns:
            Optional[str]: The comment text of the test run if successful, None if:
                - The test run ID is not found
                - The GraphQL request fails
                - No comment exists for the test run
                - Any other error occurs during the API request
        Example:
            >>> client = XrayGraphQL()
            >>> test_run_id = "67fcfd4b9e6d63d4c1d57b32"
            >>> comment = client.get_test_run_comment(test_run_id)
            >>> print(comment)
            "Test passed with performance within expected range"
        Note:
            - The test run ID must be valid and accessible with current authentication
            - If no comment exists for the test run, the method will return None
            - Failed requests are logged as errors with details about the failure
            - The method returns the raw comment text as stored in Xray
        Raises:
            Exception: If there is an error making the GraphQL request or processing the response.
                The exception is caught and logged, and the method returns None.
        """
        try:
            # Try the direct ID approach first
            query = """
            query GetTestRunComment($testRunId: String!) {
                getTestRunById(id: $testRunId) {
                    id
                    comment
                    status {
                        name
                    }
                }
            }                       
            """
            variables = {
                "testRunId": test_run_id
            }
            data = self._make_graphql_request(query, variables)
            # jprint(data)
            if not data:
                logger.error(f"Failed to get test run comment for test run {test_run_id}")
                return None
            test_run = data.get('getTestRunById', {})
            if not test_run:
                logger.warning(f"No test run found with ID {test_run_id}")
                return None
            comment = test_run.get('comment')
            return comment
        except Exception as e:
            logger.error(f"Error getting test run comment: {str(e)}")
            logger.traceback(e)
            return None
    
    def append_test_run_comment(self, test_run_id: str, test_run_comment: str) -> bool:
        """
        Append the comment of a specific test run in Xray using the GraphQL API.
        This method allows appending the comment associated with a test run
        identified by its ID. The comment can provide additional context, test results,
        or any other relevant information about the test execution.
        Args:
            test_run_id (str): The unique identifier of the test run to update.
                This is the internal Xray ID for the test run, not the Jira issue key.
            test_run_comment (str): The comment text to append to the test run.
                This will be added to any existing comment on the test run with proper formatting.
        Returns:
            bool: True if the comment update was successful, False otherwise.
                Returns None if an error occurs during the API request.
        Example:
            >>> client = XrayGraphQL()
            >>> test_run_id = "67fcfd4b9e6d63d4c1d57b32"
            >>> success = client.append_test_run_comment(
            ...     test_run_id,
            ...     "Test passed with performance within expected range"
            ... )
            >>> print(success)
            True
        Note:
            - The test run ID must be valid and accessible with current authentication
            - The comment can include any text content, including newlines and special characters
            - Failed updates are logged as errors with details about the failure
            - This method will append to existing comments with proper line breaks
            - If no existing comment exists, the new comment will be set as the initial comment
        Raises:
            Exception: If there is an error making the GraphQL request or processing the response.
                The exception is caught and logged, and the method returns None.
        """
        try:
            # Get existing comment
            existing_comment = self.get_test_run_comment(test_run_id)
            # Prepare the combined comment with proper formatting
            if existing_comment:
                # If there's an existing comment, append with double newline for proper separation
                combined_comment = f"{existing_comment}\n{test_run_comment}"
            else:
                # If no existing comment, use the new comment as is
                combined_comment = test_run_comment
                logger.debug(f"No existing comment found for test run {test_run_id}, setting initial comment")
            query = """
            mutation UpdateTestRunComment($testRunId: String!, $comment: String!) {
                updateTestRunComment(
                    id: $testRunId, 
                    comment: $comment 
                ) 
            }                       
            """
            variables = {
                "testRunId": test_run_id,
                "comment": combined_comment
            }
            data = self._make_graphql_request(query, variables)
            if not data:
                logger.error(f"Failed to update test run comment for test run {test_run_id}")
                return None
            return data['updateTestRunComment']
        except Exception as e:
            logger.error(f"Error updating test run comment: {str(e)}")
            logger.traceback(e)
            return None

    def download_attachment_by_extension(self, jira_key: str, file_extension: str) -> Optional[Dict]:
        """
        Download JIRA attachments by file extension.
        
        Retrieves all attachments from a JIRA issue that match the specified file extension
        and downloads their content. This method searches through all attachments on the
        issue and filters by filename ending with the provided extension.
        
        Args:
            jira_key (str): The JIRA issue key (e.g., 'PROJ-123')
            file_extension (str): The file extension to search for (e.g., '.json', '.txt')
                                 Should include the dot prefix
                                 
        Returns:
            Optional[Dict]: A list of dictionaries containing attachment data, where each
                           dictionary has filename as key and attachment content as value.
                           Returns None if:
                           - Issue cannot be retrieved
                           - No attachments found with the specified extension
                           - Error occurs during download
                           
        Example:
            >>> client = XrayGraphQL()
            >>> attachments = client.download_attachment_by_extension('PROJ-123', '.json')
            >>> # Returns: [{'document.json': {'content': b'...', 'mime_type': 'application/json'}}]
            
        Raises:
            Exception: Logged and handled internally, returns None on any error
        """
        try:
            response = self.make_jira_request(jira_key, 'GET')
            
            if not response or 'fields' not in response:
                logger.error(f"Error: Could not retrieve issue {jira_key}")
                return None
            
            # Find attachment by filename
            attachments = response.get('fields', {}).get('attachment', [])
            target_attachment = [att for att in attachments if att.get('filename').endswith(file_extension)]
            if not target_attachment:
                logger.error(f"No attachment found for {jira_key} with extension {file_extension}")
                return None
            
            combined_attachment = []
            fileDetails = dict()
            for attachment in target_attachment:
                attachment_id = attachment.get('id')
                mime_type = attachment.get('mimeType', '')
                fileDetails[attachment.get('filename')] = self.download_jira_attachment_by_id(attachment_id, mime_type)
                combined_attachment.append(fileDetails)
            
            return combined_attachment
        except Exception as e:
            logger.error(f"Error downloading JIRA attachment: {str(e)}")
            logger.traceback(e)
            return None
        
    def download_attachment_by_name(self, jira_key: str, file_name: str) -> Optional[Dict]:
        """
        Download JIRA attachments by filename prefix.
        
        Retrieves all attachments from a JIRA issue whose filenames start with the
        specified name (case-insensitive). This method searches through all attachments
        on the issue and filters by filename starting with the provided name.
        
        Args:
            jira_key (str): The JIRA issue key (e.g., 'PROJ-123')
            file_name (str): The filename prefix to search for (e.g., 'report', 'test')
                            Case-insensitive matching is performed
                            
        Returns:
            Optional[Dict]: A list of dictionaries containing attachment data, where each
                           dictionary has filename as key and attachment content as value.
                           Returns None if:
                           - Issue cannot be retrieved
                           - No attachments found with the specified filename prefix
                           - Error occurs during download
                           
        Example:
            >>> client = XrayGraphQL()
            >>> attachments = client.download_attachment_by_name('PROJ-123', 'report')
            >>> # Returns: [{'report_v1.json': {'content': b'...', 'mime_type': 'application/json'}},
            >>> #          {'report_v2.json': {'content': b'...', 'mime_type': 'application/json'}}]
            
        Raises:
            Exception: Logged and handled internally, returns None on any error
        """
        try:
            response = self.make_jira_request(jira_key, 'GET')
            
            if not response or 'fields' not in response:
                logger.error(f"Error: Could not retrieve issue {jira_key}")
                return None
            
            # Find attachment by filename
            attachments = response.get('fields', {}).get('attachment', [])
            target_attachment = [att for att in attachments if att.get('filename').lower().startswith(file_name.lower())]
            if not target_attachment:
                logger.error(f"No attachment found for {jira_key} with extension {file_name}")
                return None
            
            combined_attachment = []
            fileDetails = dict()
            for attachment in target_attachment:
                attachment_id = attachment.get('id')
                mime_type = attachment.get('mimeType', '')
                fileDetails[attachment.get('filename')] = self.download_jira_attachment_by_id(attachment_id, mime_type)
                combined_attachment.append(fileDetails)
            
            return combined_attachment
        except Exception as e:
            logger.error(f"Error downloading JIRA attachment: {str(e)}")
            logger.traceback(e)
            return None

    def generate_json_from_sentence(self, sentence, template_schema, debug=False):
        """Extract information using template schema and spaCy components"""
        def _ensure_spacy_model():
            """Ensure spaCy model is available, download if needed"""
            try:
                nlp = spacy.load("en_core_web_md")
                return nlp
            except OSError:
                import subprocess
                import sys
                logger.info("Downloading required spaCy model...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "spacy", "download", "en_core_web_md"
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return spacy.load("en_core_web_md")
                except subprocess.CalledProcessError:
                    raise RuntimeError(
                        "Failed to download spaCy model. Please run manually: "
                        "python -m spacy download en_core_web_md"
                    )

        def analyze_model_components(nlp):
            """Analyze the loaded model's components and capabilities"""
            logger.info("=== Model Analysis ===")
            logger.info(f"Model: {nlp.meta['name']}")
            logger.info(f"Version: {nlp.meta['version']}")
            logger.info(f"Pipeline: {nlp.pipe_names}")
            logger.info(f"Components: {list(nlp.pipeline)}")
            
        def parse_template_pattern(pattern_value):
            """Parse template pattern to extract structure and placeholders"""
            if not isinstance(pattern_value, str):
                return None
            
            # Extract placeholders like <string> from the pattern
            placeholders = re.findall(r'<(\w+)>', pattern_value)
            
            # Create a regex pattern by replacing placeholders with capture groups
            regex_pattern = pattern_value
            for placeholder in placeholders:
                # Replace <string> with a regex that captures word characters
                regex_pattern = regex_pattern.replace(f'<{placeholder}>', r'(\w+)')
            
            return {
                'original': pattern_value,
                'placeholders': placeholders,
                'regex_pattern': regex_pattern,
                'regex': re.compile(regex_pattern, re.IGNORECASE)
            }

        def match_pattern_from_template(pattern_value, doc, debug=False):
            """Match a pattern based on template value and return the matched text"""
            
            if isinstance(pattern_value, list):
                # Handle list of exact values (for environment, region)
                for value in pattern_value:
                    for token in doc:
                        if token.text.lower() == value.lower():
                            if debug:
                                logger.info(f"✓ Matched list value '{value}' -> {token.text}")
                            return token.text
                return None
            
            elif isinstance(pattern_value, str):
                # Parse the template pattern dynamically
                pattern_info = parse_template_pattern(pattern_value)
                if not pattern_info:
                    return None
                
                if debug:
                    logger.info(f"Parsed pattern: {pattern_info['original']}")
                    logger.info(f"Regex pattern: {pattern_info['regex_pattern']}")
                
                # Look for tokens that match the pattern
                for token in doc:
                    if pattern_info['regex'].match(token.text):
                        if debug:
                            logger.info(f"✓ Matched template pattern '{pattern_value}' -> {token.text}")
                        return token.text
                
                return None

        try:
            if not sentence:
                logger.error("Sentence is required")
                return None
            if not template_schema or not isinstance(template_schema, dict):
                logger.error("Template schema is required")
                return None
            if not debug:
                debug = False
            
            # Fix: Initialize result with all template schema keys
            result = {key: None for key in template_schema.keys()}
            result["sentences"] = []  # Initialize as empty list instead of string
            
        except Exception as e:
            logger.error(f"Error generating JSON from sentence: {str(e)}")
            logger.traceback(e)
            return None
        
        # Only add debug fields if debug mode is enabled
        if debug:
            result.update({
                "tokens_analysis": [],
                "entities": [],
                "dependencies": []
            })
        
        try:
            nlp = _ensure_spacy_model()
            if not nlp:
                logger.error("Failed to load spaCy model")
                return None
            if debug:
                # Analyze model capabilities
                analyze_model_components(nlp)
            doc = nlp(sentence)

            # Fix: Ensure sentences list exists before appending
            if "sentences" not in result:
                result["sentences"] = []
                
            for sent in doc.sents:
                result["sentences"].append(sent.text.strip())
            
            # 2. Tokenize and analyze each token with spaCy components (only in debug mode)
            if debug:
                for token in doc:
                    token_info = {
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "tag": token.tag_,
                        "dep": token.dep_,
                        "head": token.head.text,
                        "is_alpha": token.is_alpha,
                        "is_digit": token.is_digit,
                        "is_punct": token.is_punct,
                        "shape": token.shape_,
                        "is_stop": token.is_stop
                    }
                    result["tokens_analysis"].append(token_info)
            
            # 3. Dynamic pattern matching based on template schema values
            for pattern_key, pattern_value in template_schema.items():
                if not result[pattern_key]:  # Only search if not already found
                    matched_value = match_pattern_from_template(pattern_value, doc, debug)
                    if matched_value:
                        result[pattern_key] = matched_value
            
            # 4. Use NER (Named Entity Recognition) component (only in debug mode)
            if debug:
                for ent in doc.ents:
                    entity_info = {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char
                    }
                    result["entities"].append(entity_info)
                    logger.info(f"✓ NER Entity: {ent.text} - {ent.label_}")
            
            # 5. Use dependency parsing to find relationships (only in debug mode)
            if debug:
                for token in doc:
                    dep_info = {
                        "token": token.text,
                        "head": token.head.text,
                        "dependency": token.dep_,
                        "children": [child.text for child in token.children]
                    }
                    result["dependencies"].append(dep_info)
            
            # 6. Use lemmatizer to find action verbs and their objects
            for token in doc:
                if token.lemma_ in ["verify", "validate", "check", "test"]:
                    if debug:
                        logger.info(f"✓ Found action verb: {token.text} (lemma: {token.lemma_})")
                    # Find what's being verified/validated
                    for child in token.children:
                        if child.dep_ in ["dobj", "pobj"]:
                            if debug:
                                logger.info(f"✓ Found verification target: {child.text}")
            
            return result
        except Exception as e:
            logger.error(f"Error extracting information from document: {str(e)}")
            logger.traceback(e)
            return None

        
        

