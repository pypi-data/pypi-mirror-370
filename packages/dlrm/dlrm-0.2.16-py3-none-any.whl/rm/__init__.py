"""
Resource Manager Package
리소스 관리를 위한 패키지
"""

__version__ = "1.0.0"
__author__ = "Resource Manager Team"

from rm.db.db import DirDB, ElementType, FileDB, FileSystemDB, FileSystemRecord
from rm.db.record import DirRecord, FileRecord, PropertyRecord
from rm.memo.property_memo import Property

from .property_manager.property_manager import PropertyManager
# from .resource_db.db import ResourceDB
# from .resource_db.factory import ResourceDBFactory
# from .resource_db.record import ResourceRecord
# from .dirdb.dirdb import ID, NAME
# from .resource_db.view import DBView

# FileSystemDB
# ElementType

DirDB
FileDB

DirRecord
FileRecord

Property
PropertyRecord


__all__ = [
    "Property",
    "FileSystemDB",
    "ElementType",
    "FileSystemRecord",
    "PropertyRecord",
]

