import re
from pathlib import PurePath, Path
import shutil
from typing import Callable, Generic, Optional, Type
from dataclasses import dataclass, field
from typing import TypeVar

from rm.tool import FileSystemManager

from .dir_name_id_manager import NAME, ID, Dir_Name_ID_Parser
from rm.wrapper_tool import Wrapper

EXT = str

@dataclass
class File_Name_ID_Parser(Dir_Name_ID_Parser):
    # path로 부터 id와 name 추출
    ID_PATTERN: str = field(default=r'___id_(\d+)$')

    def split(self, path: PurePath) -> tuple[ID, NAME, EXT]:
        path_str = path.as_posix()


        # 확장자 분리
        tokens = path_str.split(".")
        if len(tokens) == 1:
            name_id = tokens[0]
            ext = None
        else:
            name_id = ".".join(tokens[:-1])
            ext = tokens[-1]
        
        id, name = super().split(PurePath(name_id))

        return (id, name, ext)

    def merge(self, id:ID, name:NAME, ext:str)->PurePath:
        # id와 name을 merge하여 path name으로 반환환
       
        path = super().merge(id, name)

        if ext is not None:
            path = path.with_suffix(f".{ext}")

        return path

class File_Name_ID_Manager:
    # path를 관리하며 id와 name 계산 및 조작

    def __init__(self, path:PurePath, parser: File_Name_ID_Parser):
        self.parser = parser
        self._id: ID = None
        self._name: NAME = None
        self._ext: EXT = None
        self.path = path

    # id
    @property
    def id(self)->ID:
        return self._id
    
    @id.setter
    def id(self, id:ID):
        if id is None:
            raise ValueError("For assign id, id must not be None. But it is None.")
        self._id = id

    @property
    def has_id(self)->bool:
        return self._id is not None

    # name
    @property
    def name(self)->NAME:
        return self._name
    
    @name.setter
    def name(self, name:NAME):
        self._name = name

    @property
    def has_name(self)->bool:
        return self._name is not None


    # ext
    @property
    def ext(self)->EXT:
        return self._ext

    @ext.setter
    def ext(self, ext:EXT):
        self._ext = ext

    @property
    def has_ext(self)->bool:
        return self._ext is not None


    @property
    def path(self)->PurePath:
        return self.parser.merge(self._id, self._name, self._ext)

    @path.setter
    def path(self, path:PurePath):
        """
        path를 설정하면 id와 name을 자동으로 추출하여 설정합니다.
        """
        self._id, self._name, self._ext = self.parser.split(path)

class Linked_File_Name_ID_Manager(Wrapper[File_Name_ID_Manager]):
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
        print(f"old_path: {old_path}, new_path: {new_path}")
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

    @property
    def ext(self)->EXT:
        return self.inner_obj.ext

    @ext.setter
    def ext(self, ext:EXT):
        def callback():
            self.inner_obj.ext = ext
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

      