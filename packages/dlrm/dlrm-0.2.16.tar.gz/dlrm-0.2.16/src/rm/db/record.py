
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Generic, Type
from typing_extensions import Self

from rm.db.db_tree import DBTreeNode
from rm.memo.factory import MemoFactory
from rm.memo.property_memo import PropertyMemo, PropertyType


if TYPE_CHECKING:
    from rm.db.db import FileSystemDB

class ElementType(Enum):
    FILE = "file"
    DIR = "dir"
    
@dataclass
class FileSystemRecord(ABC):
    # 단일 데이터 셋, 모델 또는 작업을 관리한다.
    # 리소스에 맞게 확장된 클래스를 사용한 것으로 기대대 
    
    def __post_init__(self):
        if self.element_type is None:
            raise ValueError("FileSystemRecord의 상속 클래스에서 element_type을 설정해야 합니다.")

        if self.element_type != self.db.element_type:
            raise ValueError(f"element_type({self.element_type}) is not equal to db.element_type({self.db.element_type})")

    db:'FileSystemDB[Self]'
    root_dir_path:Path
    id:int
    # path:Path
    element:DBTreeNode
    element_type:ElementType = field(default=None, init=False)

    @property
    def path(self)->Path:
        return self.root_dir_path/self.element.path

    @property
    def name(self)->str:
        # root_dir 부터 id 전까지 경로 텍스트트
        
        path = self.element.path.parent/self.element.name
        rel_path = path.relative_to(Path(self.element.root.name))
        name = rel_path.as_posix()
        return "___".join(name.split("___")[:-1])

    @property
    def ext(self)->str:
        return self.element.ext

@dataclass
class FileRecord(FileSystemRecord):
    element_type:ElementType = field(default=ElementType.FILE, init=False)

@dataclass
class DirRecord(FileSystemRecord):
    element_type:ElementType = field(default=ElementType.DIR, init=False)

@dataclass
class PropertyRecord(DirRecord, Generic[PropertyType]):
    property_class:Type[PropertyType]

    @property
    def __property_path(self)->Path:
        return self.path / "property"

    @property
    def __property_memo(self)->PropertyMemo[PropertyType]:
        return MemoFactory().make_property_memo(self.__property_path, self.property_class)

    @property
    def prop(self)->PropertyType:
        return self.__property_memo.get()
    
    @prop.setter
    def prop(self, property:PropertyType)->None:
        self.__property_memo.set(property)


