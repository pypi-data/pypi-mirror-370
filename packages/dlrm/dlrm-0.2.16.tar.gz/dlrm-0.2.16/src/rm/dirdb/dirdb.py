from functools import cached_property
import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union, Set
from dataclasses import dataclass, field

from rm.dirtree.file_name_id_manager import Linked_File_Name_ID_Manager

from ..dirtree.dir_name_id_manager import ID, NAME, Linked_Name_ID_Manager
from ..dirtree.dir_tree import DirTree, FileTree
from ..dirtree.factory import DirTreeFactory
from ..dirdb.metadata import MetaData

from collections import Counter

def find_duplicates(lst:List[Any])->List[Any]:
    counter = Counter(lst)
    return [item for item, count in counter.items() if count > 1]

@dataclass(kw_only=True)
class DirDB:
    """
    특정 dir 
    ID 기반 폴더 관리 시스템
    폴더 경로를 받아서 자동으로 고유 ID를 할당하고 관리합니다.
    ID는 0부터 시작하며, 최근 ID는 루트 디렉터리에 저장됩니다.


    지금부터 name은 dir_path를 포함하면 full_name, 포함하지 않으면 core_name으로 판단한다.
    별도의 언급이 없으면 core_name이다.
    """
    path: Path
    factory: DirTreeFactory

    violating_elements_check:bool = field(default=True)
    id_duplication_check:bool = field(default=True)

    def __post_init__(self):
        self.validate_dir_path()
        self.dir_tree: DirTree = self.factory.get_dir_tree(self.path)
        self.metadata: MetaData = MetaData(self.path, "db_metadata.json")
        
        
        if self.violating_elements_check:
            self.validate_violating_paths()


        if self.id_duplication_check:
            self.validate_key_duplication()

    def validate_dir_path(self):
        # 디렉터리가 존재하지 않으면 생성
        if not self.path.exists():
            print(f"Directory {self.path} does not exist")
            print(f"Creating directory {self.path}")
            self.path.mkdir(parents=True, exist_ok=True)


    def validate_violating_paths(self):
        print("***violating paths***")
        for path in self.dir_tree.all_violating_paths:
            print(f"Warning: {path} is violating the rules")

    def validate_key_duplication(self):
        duplicated_ids = find_duplicates(self.ids)
        if duplicated_ids:
            for id in duplicated_ids:
                print(f"ID {id} 중복 오류")
            raise ValueError("ID 중복 오류")

    @cached_property
    def name_managers(self)->List[Linked_Name_ID_Manager]:
        return [self.factory.dir_linked_id_name_manager(node.path) for node in self.dir_tree.terminal_nodes]

    @cached_property
    def id_name_dict(self)->Dict[ID, NAME]:
        return {m.id: self.to_core_name(m.name) for m in self.name_managers}

    @cached_property
    def name_id_dict(self)->Dict[NAME, ID]:
        return {self.to_core_name(m.name): m.id for m in self.name_managers}

    @property
    def ids(self)->List[ID]:
        return [m.id for m in self.name_managers]

    @property
    def names(self)->List[NAME]:
        return [self.to_core_name(m.name) for m in self.name_managers]
    
    @cached_property
    def id_manager_dict(self)->Dict[ID, Linked_Name_ID_Manager]:
        return {m.id: m for m in self.name_managers}

    def exist(self, query:ID|NAME)->bool:
        if isinstance(query, ID):
            return query in self.id_manager_dict
        elif isinstance(query, NAME):
            return query in self.name_id_dict
        else:
            raise ValueError(f"Invalid query: {query}")

    def get(self, query:ID|NAME)->Tuple[ID, NAME, Path]:
        if isinstance(query, ID):
            if query not in self.id_manager_dict:
                raise ValueError(f"ID {query} not found")
            manager = self.id_manager_dict[query]
        elif isinstance(query, NAME):
            if query not in self.name_id_dict:
                raise ValueError(f"NAME {query} not found")
            id = self.name_id_dict[query]
            manager = self.id_manager_dict[id]
        else:
            raise ValueError(f"Invalid query: {query}")

        name = self.to_core_name(manager.name)
        return (manager.id, name, manager.path)

    def relative_path(self, path:Path)->Path:
        return path.relative_to(self.path)


    def to_core_name(self, name:NAME)->NAME:
        return NAME(self.relative_path(Path(name)))
    
    def to_full_name(self, name:NAME)->NAME:
        return NAME(self.path/name)


    def create_new(self, name:Optional[str] = None) -> ID:
        name = name or f"no_name"
        new_id = self.metadata.get_next_id_increasing_1()
        manager = self.factory.dir_linked_id_name_manager(Path(self.to_full_name(name)))
        manager.create()
        manager.id = new_id
        self.name_managers.append(manager)
        self.id_manager_dict[new_id] = manager
        self.id_name_dict[new_id] = name
        self.name_id_dict[name] = new_id
        self.ids.append(new_id)
        # self.names.append(name)
    
        # ID 출력
        print(f"🆕 새로운 ID 생성: {new_id}")
        
        return new_id


@dataclass(kw_only=True)
class FileDB(DirDB):
    """
    특정 dir 
    ID 기반 폴더 관리 시스템
    폴더 경로를 받아서 자동으로 고유 ID를 할당하고 관리합니다.
    ID는 0부터 시작하며, 최근 ID는 루트 디렉터리에 저장됩니다.


    지금부터 name은 dir_path를 포함하면 full_name, 포함하지 않으면 core_name으로 판단한다.
    별도의 언급이 없으면 core_name이다.
    """
    ext: str

    def __post_init__(self):
        self.validate_dir_path()
        self.dir_tree: FileTree = self.factory.get_file_tree(self.path)
        self.metadata: MetaData = MetaData(self.path, "db_metadata.json")
        self.validate_violating_paths()
        self.validate_key_duplication()



    @cached_property
    def name_managers(self)->List[Linked_File_Name_ID_Manager]:
        return [self.factory.file_linked_id_name_manager(node.path) for node in self.dir_tree.terminal_nodes]

    
    @cached_property
    def id_manager_dict(self)->Dict[ID, Linked_Name_ID_Manager]:
        return {m.id: m for m in self.name_managers}


    def create_new(self, name:Optional[str] = None) -> ID:
        new_id = super().create_new(name)
        self.id_manager_dict[new_id].ext = self.ext
        return new_id


