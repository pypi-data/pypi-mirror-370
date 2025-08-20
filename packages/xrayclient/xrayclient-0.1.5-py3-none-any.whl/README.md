# XrayClient

A comprehensive Python client for interacting with Xray Cloud's GraphQL API for test management in Jira. This library provides a robust interface for managing test plans, test executions, test runs, defects, evidence, and other Xray-related operations through GraphQL queries and mutations.

## 📚 Documentation

- **HTML Documentation**: [View Online](https://github.com/arusatech/xrayclient/tree/main/docs/html)
- **API Reference**: [API Docs](https://github.com/arusatech/xrayclient/tree/main/docs/html/xrayclient.html)

## ✨ Features

- **Jira Integration**: Full Jira REST API support for issue management
- **Xray GraphQL API**: Complete Xray Cloud GraphQL API integration
- **Test Management**: Create and manage test plans, test executions, and test runs
- **Evidence Management**: Add attachments and evidence to test runs
- **Defect Management**: Create defects from failed test runs
- **Authentication**: Secure authentication with both Jira and Xray Cloud
- **Error Handling**: Comprehensive error handling and logging
- **Type Hints**: Full type annotation support for better development experience
- **Table Parsing**: Automatic parsing of tabular data from test plan descriptions
- **File Operations**: Download attachments by extension or name
- **Natural Language Processing**: Generate JSON from natural language sentences

## 🚀 Installation

```bash
pip install xrayclient
```

Or install from source:

```bash
git clone https://github.com/arusatech/xrayclient.git
cd xrayclient
pip install -e .
```

## ⚡ Quick Start

### Basic Setup

```python
from xrayclient.xray_client import XrayGraphQL

# Initialize the client
client = XrayGraphQL()
```

### Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Jira Configuration
JIRA_SERVER=https://your-instance.atlassian.net
JIRA_USER=your-email@company.com
JIRA_API_KEY=your-jira-api-key

# Xray Cloud Configuration
XRAY_CLIENT_ID=your-xray-client-id
XRAY_CLIENT_SECRET=your-xray-client-secret
XRAY_BASE_URL=https://us.xray.cloud.getxray.app
```

## 📖 Usage Examples

### Test Plan Operations

```python
# Get all tests from a test plan
test_plan_tests = client.get_tests_from_test_plan("TEST-123")
print(test_plan_tests)
# Output: {'TEST-124': '10001', 'TEST-125': '10002'}

# Get test plan data with parsed tables
test_plan_data = client.get_test_plan_data("TEST-123")
print(test_plan_data)
# Output: {'column1': [1, 2, 3], 'column2': [4.5, 6.7, 8.9]}
```

### Test Execution Management

```python
# Create a test execution from a test plan
test_execution = client.create_test_execution_from_test_plan("TEST-123")
print(test_execution)
# Output: {
#     'TEST-124': {
#         'test_run_id': '5f7c3',
#         'test_execution_key': 'TEST-456',
#         'test_plan_key': 'TEST-123'
#     }
# }

# Create a test execution with specific tests
test_execution = client.create_test_execution(
    test_issue_keys=["TEST-124", "TEST-125"],
    project_key="PROJ",
    summary="Regression Test Execution",
    description="Testing critical features"
)
```

### Test Run Operations

```python
# Get test run status
status, run_id = client.get_test_runstatus("TEST-124", "TEST-456")
print(f"Status: {status}, Run ID: {run_id}")

# Update test run status
success = client.update_test_run_status("test_run_id", "PASS")
print(success)  # True

# Update test run comment
success = client.update_test_run_comment("test_run_id", "Test passed successfully")
print(success)  # True

# Append to existing comment
success = client.append_test_run_comment("test_run_id", "Additional notes")
print(success)  # True
```

### Evidence and Defect Management

```python
# Add evidence to a test run
evidence_added = client.add_evidence_to_test_run("test_run_id", "/path/to/screenshot.png")
print(evidence_added)  # True

# Create a defect from a failed test run
defect = client.create_defect_from_test_run(
    test_run_id="test_run_id",
    project_key="PROJ",
    parent_issue_key="TEST-456",
    defect_summary="Login functionality broken",
    defect_description="Users cannot log in with valid credentials"
)
print(defect)
```

### Test Set Operations

```python
# Get tests from a test set
test_set_tests = client.get_tests_from_test_set("TESTSET-123")
print(test_set_tests)

# Filter test sets by test case
test_sets = client.filter_test_set_by_test_case("TEST-124")
print(test_sets)

# Get tags for a test case
tags = client.filter_tags_by_test_case("TEST-124")
print(tags)
```

### Jira Issue Management

```python
# Create a new Jira issue
issue_key, issue_id = client.create_issue(
    project_key="PROJ",
    summary="New feature implementation",
    description="Implement new login flow",
    issue_type="Story",
    priority="High",
    labels=["feature", "login"],
    attachments=["/path/to/screenshot.png"]
)
print(f"Created issue {issue_key} with ID {issue_id}")

# Get issue details
issue = client.get_issue("PROJ-123", fields=["summary", "status", "assignee"])
print(f"Issue: {issue['summary']} - Status: {issue['status']['name']}")

# Update issue summary
success = client.update_issue_summary("PROJ-123", "Updated summary")
print(success)  # True
```

### Advanced Features

```python
# Download attachments by extension
attachments = client.download_attachment_by_extension("PROJ-123", ".png")

# Download attachments by name
attachments = client.download_attachment_by_name("PROJ-123", "screenshot")

# Generate JSON from natural language
json_data = client.generate_json_from_sentence("Create a test with priority high and assign to john")
print(json_data)
```

## 🔧 API Reference

### JiraHandler Class

The base class providing Jira REST API functionality.

#### Methods

- `create_issue(project_key, summary, description, **kwargs)` - Create a new Jira issue
- `get_issue(issue_key, fields=None)` - Retrieve a Jira issue
- `update_issue_summary(issue_key, new_summary)` - Update issue summary
- `make_jira_request(jira_key, url, method, payload, **kwargs)` - Make custom Jira requests
- `download_jira_attachment_by_id(attachment_id, mime_type)` - Download attachments

### XrayGraphQL Class

Extends JiraHandler to provide Xray Cloud GraphQL API functionality.

#### Authentication & Setup
- `__init__()` - Initialize XrayGraphQL client
- `_get_auth_token()` - Authenticate with Xray Cloud API
- `_make_graphql_request(query, variables)` - Make GraphQL requests

#### Test Plan Operations
- `get_tests_from_test_plan(test_plan)` - Get tests from test plan
- `get_test_plan_data(test_plan)` - Get parsed test plan data

#### Test Set Operations
- `get_tests_from_test_set(test_set)` - Get tests from test set
- `filter_test_set_by_test_case(test_key)` - Filter test sets by test case
- `filter_tags_by_test_case(test_key)` - Get tags for test case

#### Test Execution Operations
- `get_tests_from_test_execution(test_execution)` - Get tests from test execution
- `get_test_execution(test_execution)` - Get detailed test execution info
- `create_test_execution(test_issue_keys, project_key, summary, description)` - Create test execution
- `create_test_execution_from_test_plan(test_plan)` - Create test execution from plan
- `add_test_execution_to_test_plan(test_plan, test_execution)` - Add execution to plan

#### Test Run Operations
- `get_test_runstatus(test_case, test_execution)` - Get test run status
- `get_test_run_by_id(test_case_id, test_execution_id)` - Get test run by ID
- `update_test_run_status(test_run_id, test_run_status)` - Update test run status
- `update_test_run_comment(test_run_id, test_run_comment)` - Update test run comment
- `get_test_run_comment(test_run_id)` - Get test run comment
- `append_test_run_comment(test_run_id, test_run_comment)` - Append to comment

#### Evidence & Defect Management
- `add_evidence_to_test_run(test_run_id, evidence_path)` - Add evidence
- `create_defect_from_test_run(test_run_id, project_key, parent_issue_key, defect_summary, defect_description)` - Create defect

#### File Operations
- `download_attachment_by_extension(issue_key, extension)` - Download attachments by file extension
- `download_attachment_by_name(issue_key, filename)` - Download attachments by filename

#### Natural Language Processing
- `generate_json_from_sentence(sentence)` - Generate JSON from natural language

## 📋 Requirements

- Python >= 3.12
- jira >= 3.10.5, < 4.0.0
- jsonpath-nz >= 1.0.6, < 2.0.0
- requests >= 2.31.0, < 3.0.0
- spacy >= 3.8.7, < 4.0.0

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/arusatech/xrayclient.git
cd xrayclient
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xrayclient --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m slow
```

### Code Quality

The project uses:
- **pytest** for testing
- **pytest-cov** for coverage reporting
- **pytest-mock** for mocking in tests
- **Type hints** for better code documentation

## 🔒 Error Handling

The library implements comprehensive error handling:

- All methods return `None` for failed operations instead of raising exceptions
- Detailed logging for debugging and error tracking
- Automatic retry logic for transient failures
- Graceful handling of authentication failures

## 🔐 Security

- Uses environment variables for sensitive configuration
- Supports API key authentication for both Jira and Xray
- Implements proper token management and refresh
- Handles secure file uploads for evidence

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: yakub@arusatech.com

## 📝 Changelog

### Version 0.1.5
- Added spacy dependency for natural language processing
- Enhanced table parsing capabilities
- Improved error handling and logging
- Added file download operations
- Enhanced documentation

### Version 0.1.2
- Initial release
- Jira REST API integration
- Xray Cloud GraphQL API integration
- Complete test management functionality
- Evidence and defect management
- Comprehensive error handling and logging
