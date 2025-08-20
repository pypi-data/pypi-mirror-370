import re
from pathlib import PurePath, Path
import shutil
from typing import Callable, Generic, Optional, Protocol, Type
from dataclasses import dataclass, field
from typing import TypeVar

from rm.tool import FileSystemManager
from rm.wrapper_tool import Wrapper

ID = Optional[int]
NAME = str

PATH = TypeVar('PATH', bound=PurePath)


class Name_ID_Parser(Protocol):
    def split(self, path:PurePath)->tuple[ID, NAME]:
        ...
    def merge(self, id:ID, name:NAME)->PurePath:
        ...

@dataclass
class Dir_Name_ID_Parser(Name_ID_Parser):
    # path로 부터 id와 name 추출
    ID_PATTERN: str = field(default=r'___id_(\d+)$')

    def split(self, path:PurePath)->tuple[ID, NAME]:
        # path name으로 부터
        path_str = path.as_posix()
        match = re.search(self.ID_PATTERN, path_str)
        id = int(match.group(1)) if match else None
        name = path_str.replace(f"___id_{id}", "")
        return (id, name)

    def merge(self, id:ID, name:NAME)->PurePath:
        # id와 name을 merge하여 path name으로 반환환
        if id is None:
            return PurePath(name)
        else:
            return PurePath(f"{name}___id_{id}")


class Name_ID_Manager(Protocol):
    def id_name(self)->tuple[ID, NAME]:
        ...
    def id(self)->ID:
        ...
    def name(self)->NAME:
        ...
    def path(self)->PurePath:
        ...


class DIR_Name_ID_Manager(Name_ID_Manager):
    # path를 관리하며 id와 name 계산 및 조작

    def __init__(self, path:PurePath, parser: Dir_Name_ID_Parser):
        self.parser = parser
        self._id: ID = None
        self._name: NAME = ""
        self.path = path


    @property
    def id_name(self)->tuple[ID, NAME]:
        return (self._id, self._name)
    
    @property
    def id(self)->ID:
        return self._id
    
    @property
    def name(self)->NAME:
        return self._name
    
    @property
    def has_id(self)->bool:
        return self._id is not None

    @property
    def path(self)->PurePath:
        return self.parser.merge(self._id, self._name)

    @id.setter
    def id(self, id:ID):
        if id is None:
            raise ValueError("For assign id, id must not be None. But it is None.")
        self._id = id

    @name.setter
    def name(self, name:NAME):
        self._name = name
        
    @path.setter
    def path(self, path:PurePath):
        """
        path를 설정하면 id와 name을 자동으로 추출하여 설정합니다.
        """
        id, name = self.parser.split(path)
        self._id = id
        self._name = name

class Linked_Name_ID_Manager(Wrapper[Name_ID_Manager]):
    # 실제 폴더에 연결되어 경로로 조작 가능
    @property
    def path(self)->Path:
        return Path(self.inner_obj.path)

    @path.setter
    def path(self, path: Path):
        self.inner_obj.path = PurePath(path)

    def _rename(self, callback:Callable[[], None])->None:
        old_path = self.path
        callback()
        new_path = self.path
        if old_path != new_path:
            old_path.rename(new_path)
            FileSystemManager.remove_empty_parents_recursively(old_path)
    
    @property
    def id(self)->ID:
        return self.inner_obj.id

    @id.setter
    def id(self, id:ID):
        if id is None:
            raise ValueError("For assign id, id bust not be None. But it is None.")
        def callback():
            self.inner_obj.id = id
        self._rename(callback)

    @property
    def name(self)->NAME:
        return self.inner_obj.name

    @name.setter
    def name(self, name:NAME):
        def callback():
            self.inner_obj.name = name
        self._rename(callback)

    def remove(self)->None:
        if self.exists:
            FileSystemManager.remove_dir(self.path)
            FileSystemManager.remove_empty_parents_recursively(self.path)
            
    def create(self)->None:
        self.path.mkdir(parents=True, exist_ok=True)

    @property
    def exists(self)->bool:
        return self.path.exists() # type: ignore

    
# class Linked_Name_ID_Manager(DIR_Name_ID_Manager):
#     # 실제 폴더에 연결되어 경로로 조작 가능
#     @property
#     def path(self)->Path:
#         return Path(super().path)

#     @path.setter
#     def path(self, path: Path):
#         DIR_Name_ID_Manager.path.fset(self, path)
#         # super(Linked_ID_Name_Manager, Linked_ID_Name_Manager).path.__set__(self, path)

#     @property
#     def exists(self)->bool:
#         return self.path.exists() # type: ignore

#     def _rename(self, callback:Callable[[], None])->None:
#         old_path = self.path
#         callback()
#         new_path = self.path
#         if old_path != new_path:
#             old_path.rename(new_path)
#             FileSystemManager.remove_empty_parents_recursively(old_path)
    
#     @property
#     def id(self)->ID:
#         return self._id

#     @id.setter
#     def id(self, id:ID):
#         if id is None:
#             raise ValueError("For assign id, id bust not be None. But it is None.")
#         def callback():
#             self._id = id
#         self._rename(callback)

#     @property
#     def name(self)->NAME:
#         return self._name

#     @name.setter
#     def name(self, name:NAME):
#         def callback():
#             self._name = name
#         self._rename(callback)

#     def remove(self)->None:
#         if self.exists:
#             FileSystemManager.remove_dir(self.path)
#             FileSystemManager.remove_empty_parents_recursively(self.path)
            
#     def create(self)->None:
#         self.path.mkdir(parents=True, exist_ok=True)


