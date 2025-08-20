from enum import Flag


class StiUserAccessPrivileges(Flag):
    """Enumeration describes possible user access privileges to the pdf document. User access privileges are managed by the user password.
    Owner with the correct owner password has all possible privileges for the content of the pdf document and a rule for setting document permissions."""

    NONE = 0
    """User password allows only opening the pdf document, decrypt it, and display it on the screen."""
    
    PRINT_DOCUMENT = 1
    """User password allows opening the pdf document, decrypt it, display it on the screen and print its content."""
    
    MODIFY_CONTENTS = 2
    """User password allows modifying the content of the pdf document."""
    
    COPY_TEXT_AND_GRAPHICS = 4
    """User password allows copying text and graphics objects from the content of the pdf document."""
    
    ADD_OR_MODIFY_TEXT_ANNOTATIONS = 8
    """User password allows adding or modifying text annotations in the content of the pdf document."""
    
    ALL = 15
    """User password allows all modifications on the content of the pdf document."""