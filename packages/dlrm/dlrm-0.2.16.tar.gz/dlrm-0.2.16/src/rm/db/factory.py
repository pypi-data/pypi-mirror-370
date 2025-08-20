

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type

from rm.memo.property_memo import Property
from .db import ElementType, FileSystemDB
from .record import FileRecord, PropertyRecord, PropertyType

class CustomProperty(Property):
    name:str = "no_name"
    age:int = 0
    option:Optional[str] = None

@dataclass
class CustomRecord(PropertyRecord[CustomProperty]):
    property_class:Type[PropertyType] = CustomProperty

@dataclass
class CustomPropertyDB(FileSystemDB[CustomRecord]):
    RecordClass:Type[FileSystemDB] = CustomRecord
    element_type:ElementType = ElementType.DIR

@dataclass
class CustomFileDB(FileSystemDB[FileRecord]):
    RecordClass:Type[FileSystemDB] = FileRecord
    element_type:ElementType = ElementType.FILE


@dataclass
class FileSystemDBFactory:
    root_dir_path:Path

    @property
    def dir_db(self)->CustomPropertyDB:
        return CustomPropertyDB(root_dir_path=self.root_dir_path)

    @property
    def file_db(self)->CustomFileDB:
        return CustomFileDB(root_dir_path=self.root_dir_path)


