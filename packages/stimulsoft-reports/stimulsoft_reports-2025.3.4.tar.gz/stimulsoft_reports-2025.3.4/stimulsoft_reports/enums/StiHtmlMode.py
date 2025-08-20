from enum import Enum


class StiHtmlMode(Enum):
    
    SCRIPTS = 0
    """Renders only JavaScript code to insert into JavaScript block on an HTML page."""

    HTML_SCRIPTS = 1
    """Renders the full JavaScript code and the necessary HTML tags to insert into the HTML page inside the BODY."""
    
    HTML_PAGE = 2
    """Renders a fully HTML page with all scripts and tags to return as a response instead of an HTML template."""
