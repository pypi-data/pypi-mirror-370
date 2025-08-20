from enum import Enum


class StiEngineType(Enum):
    
    CLIENT_JS = 1
    """The report is built and exported on the client side in a browser window."""

    SERVER_NODE_JS = 2
    """The report is built and exported on the server side using Node.js"""
