"""
Enums definitions
"""

from enum import Enum, EnumMeta

class MetaEnum(EnumMeta):
    """
    MetaEnum class
    """
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(Enum, metaclass=MetaEnum):
    """
    BaseEnum class
    """
    pass


class Table(BaseEnum):
    """
    Table name
    """
    DOCUMENTS_TABLE = " documetns"

