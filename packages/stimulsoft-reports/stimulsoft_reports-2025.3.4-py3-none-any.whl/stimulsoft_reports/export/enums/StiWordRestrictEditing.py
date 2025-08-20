from enum import Enum


class StiWordRestrictEditing(Enum):
    """Enumeration for setting modes of restrict editing."""

    NO = 1
    """No restrictions."""

    EXCEPT_EDITABLE_FIELDS = 2
    """Except Editable fields."""
    
    YES = 3
    """Yes."""
