
from dataclasses import dataclass, field
import enum
from pathlib import Path, PurePath
import shutil
from typing import Generic, List, TypeVar

from typing_extensions import Self

# from rm.tree.hooking_tree import HookingTreeNode
from .tree import ExtendedTreeNode


def ensure_str_list(name:Path|List[str]|str)->List[str]:
    if isinstance(name, Path|PurePath):
        return list(name.parts)
    elif isinstance(name, str):
        return [name]   
    else:
        return name

@dataclass(kw_only=True)
class PurePathTreeNode(ExtendedTreeNode):
    # 각 노드를 의미 있는 폴더로 보고 중간에 있는 노드는 

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.name, Path):
            self.name = self.name.as_posix()

    @property
    def path(self)->Path:
        if self.is_root: return Path(self.name)
        return self._parent.path / self.name


    def create(self, path:Path|str):
        name = ensure_str_list(path)
        return super().create(name)

    def has(self, path:Path|str)->bool:
        name = ensure_str_list(path)
        return super().has(name)

    # def unlink_child(self, name:str)->None:
    #     child = super().unlink_child(name)
    #     self.unlink_empty()
    #     return child

    # def unlink_empty(self):
    #     if self.is_root: return # root는 대상이 되지 않음 
    #     if self.is_empty: # 비어있는 노드라면 부모 노드에서 제거
    #         parent = self._parent
    #         parent.unlink(self.name) # 나를 지우고
    #         self.clear()
    #         parent.unlink_empty() # 부모에게도 recursive 호출

    def delete(self): # 노드 삭제 (다른 노드와의 관계 제거 & 내용 제거거)
        if not self.is_root:
            self.parent.unlink(self.name)

    @property
    def is_empty(self)->bool:
        # 노드 안에 어떤 컨텐츠도 없는가?
        return self.is_terminal # 경로만 계산하는 경우에는 terminal 노드라면 빈 디렉터리임임



def remove_path(path: str | Path)->None:
    p = Path(path)
    if not p.exists():
        return  # 존재하지 않으면 무시

    if p.is_file() or p.is_symlink():
        p.unlink()  # 파일 또는 심볼릭 링크
    elif p.is_dir():
        shutil.rmtree(p)  # 디렉토리 전체 삭제


@dataclass(kw_only=True)
class PathTreeNode(PurePathTreeNode):
    # 각 노드를 실제파일 시스템의 경로로 보며
    # CRUD 연산에 실제 파일 경로로 변경 지원
    # 경로 노드는 모두 디렉터리로 존재하며 터미널 노드는 DIR, FilE 중 지정 가능
    
    """
        file_system과의 연동은 on/off 가능하며
        off인 경우 실제 파일 시스템에 대한 연동은 없음
        on으로 바꾸는 경우 현재까지 만들어진 노드 정보에 대해 한번에 파일 시스템에 생성
        이후부터는 연동됌됌
    """

    _init_file_system_sync_on: int = field(repr=False, default=True)
    __file_system_sync_on:bool = field(default=None, init=False)


    def __post_init__(self):
        super().__post_init__()
        self.__file_system_sync_on = self._init_file_system_sync_on
        self.ensure_file_exist() # 노드 생성시 파일시스템에도 실제로 생성

    @property
    def file_system_sync_on(self)->bool:
        return self.__file_system_sync_on

    @file_system_sync_on.setter
    def file_system_sync_on(self, value:bool):
        self.__file_system_sync_on = value
        self.ensure_file_exist()

        for child in self.children:
            child.file_system_sync_on = value

    def rename(self, new_name:str)->Self:
        if self.file_system_sync_on:
            origin_path = self.path
            super().rename(new_name)
            new_path = self.path
            new_path.parent.mkdir(parents=True, exist_ok=True)
            origin_path.rename(new_path)
        else:
            super().rename(new_name)

        return self


    @property
    def is_empty(self)->bool: # 자식 노드 뿐만 아니라 실제 파일 시스템에 하위 디렉터리와 파일 존재까지 고려려
        if not self.is_terminal: return False # 1차로 터미널이 아니면 False
        
        return (self.path.is_dir()) and not any(self.path.iterdir()) # 


    def ensure_file_exist(self): # 노드의 경로가 파일시스템에 실제로 존재하도록 보장장
        if not self.__file_system_sync_on: return
        
        if self.path.exists():
            return
        
        self.path.mkdir(parents=True, exist_ok=True)


    def delete(self): # 노드 정보에서도 삭제하며 실제 파일 시스템에서도 삭제
        # if not self.is_root:
        #     self.parent.unlink(self.name)
        if self.file_system_sync_on:
            if not self.is_root:
                self.rename("@@@") # 파일 unlink시 이름이 겹칠 수 있으니 임의로 변경 후 제거
            super().delete()
            self.clear()        
        else:
            super().delete()

    def clear(self): # 파일시스템에 있는 내용 삭제
        if not self.file_system_sync_on:
            raise ValueError("clear is can be called in file_system_sync_on == True")

        if self.path.is_dir():
            shutil.rmtree(self.path)
        else:
            self.path.unlink()

    @property
    def exists(self)->bool: # 노드의 경로가 파일 시스템에 실제로 존재하는가?
        return self.path.exists()

    def unlink_child(self, name:str)->Self:
        if self.__file_system_sync_on:
            # 노드 연결 관계가 수정되면 실제 파일도 변경
            origin_path = self.get_child(name).path
            child = super().unlink_child(name)
            new_path = child.path
            new_path.parent.mkdir(parents=True, exist_ok=True)
            origin_path.rename(new_path)
        else:
            child = super().unlink_child(name)

        return child


    def link_child(self, child:Self)->Self:
        if self.__file_system_sync_on:
            # 노드 연결 관계가 수정되면 실제 파일도 변경
            origin_path = child.path
            super().link_child(child)
            new_path = child.path
            new_path.parent.mkdir(parents=True, exist_ok=True)
            origin_path.rename(new_path)
        else:
            child = super().link_child(child)
        return child

    def _create_root_node(self, name:str)->Self:
        return self.__class__(name=name, _init_file_system_sync_on=self.file_system_sync_on)
