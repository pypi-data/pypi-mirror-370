"""
XrayClient - Python Client for Xray Test Management for Jira

A comprehensive Python client for interacting with Xray Cloud's GraphQL API
for test management in Jira.
"""

from .xray_client import JiraHandler, XrayGraphQL

__version__ = "0.1.6"
__author__ = "yakub@arusatech.com"
__all__ = ["JiraHandler", "XrayGraphQL"] 