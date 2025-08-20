from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Generic, Type, TypeVar
from typing_extensions import Self

from rm.db.db_tree import DBTreeNode
from rm.dirtree.file_name_id_manager import File_Name_ID_Parser
import re

def find_db_element_paths(base_dir: Path)->list[Path]:
    # DB의 항목에 해당하는 모든 경로 반환환
    pattern = re.compile(r'^.+___id_\d+(?:\.[\w\d_-]+)?$')
    matched_paths = []

    if not base_dir.exists():
        return []

    def _walk(current_dir: Path):
        for entry in current_dir.iterdir():
            if pattern.match(entry.name):
                matched_paths.append(entry)
                # 폴더인 경우 하위 탐색 생략
                continue
            if entry.is_dir():
                _walk(entry)

    _walk(base_dir)
    return matched_paths

from rm.db.record import DirRecord, ElementType, FileRecord, FileSystemRecord

RecordType = TypeVar("RecordType", bound=FileSystemRecord)

from collections import Counter

def dup_counts(xs):
    return {v: c for v, c in Counter(xs).items() if c > 1}




@dataclass
class FileSystemDB(Generic[RecordType]):
    # 내부적으로 tree를 이용하며, terminal node를 하나의 항목으로 다루는 클래스
    root_dir_path:Path
    RecordClass:Type[RecordType]
    element_type:ElementType

    name_id_parser:File_Name_ID_Parser = field(default=File_Name_ID_Parser(), init=False)
    __record_cache:dict[int, RecordType] = field(default_factory=dict, init=False)    
    
    def __post_init__(self):
        paths = find_db_element_paths(self.root_dir_path)
        self.__tree = DBTreeNode(name=self.root_dir_path, _init_file_system_sync_on=False)
        for path in paths:
            self.__tree.create(path.relative_to(self.root_dir_path))
        self.__tree.file_system_sync_on = True
        self.ids

    @property
    def id_list(self)->list[int]:
        return list(self.__id_elements.keys())


    @property
    def __elements(self)->list[DBTreeNode]:
        return self.__tree.terminal_nodes()
    
    def has_branch(self, name:Path)->bool:
        return self.__tree.has(name)

    def branch(self, name:Path)->Self:
        if self.__tree.has(name):
            return self.__class__(root_dir_path=self.root_dir_path/name, RecordClass=self.RecordClass, element_type=self.element_type)
        else:
            raise ValueError(f"Branch {name} not found")

    @property
    def __new_id(self)->int: return max(self.ids, default=0) + 1

    @property
    def __id_elements(self)->dict[int, DBTreeNode]:
        result = {}
        for element in self.__elements:
            id, name, ext = self.name_id_parser.split(element.path)
            if id in result:
                raise ValueError(f"ID {id} is duplicated")
            result[id] = element
        return result

    def __get_element(self, id:int)->DBTreeNode:
        return self.__id_elements[id]

    def __contains__(self, name_or_id:int|str|Path)->bool:
        try:
            id = self.ensure_id(name_or_id)
            return id in self.ids
        except:
            return False

    @property
    def records(self)->list[RecordType]:
        return [self.get_record(id) for id in self.ids]
        
    @property
    def name_id_dict(self)->dict[str, int]:
        return {record.name:record.id for record in self.records}


    def ensure_id(self, id_or_name:int|str|Path)->int:
        if isinstance(id_or_name, int):
            return id_or_name
        elif isinstance(id_or_name, str):
            return self.name_id_dict[id_or_name]
        elif isinstance(id_or_name, Path):
            return self.name_id_dict[id_or_name.as_posix()]
        else:
            raise ValueError(f"Invalid type: {type(id_or_name)}")

    @property
    def ids(self)->list[str]:
        return list(self.__id_elements.keys())
    
    def get_record(self, name_or_id:int|str|Path)->RecordType:
        id = self.ensure_id(name_or_id)
        if id not in self.__record_cache:
            element = self.__get_element(id)
            self.__record_cache[id] = self.RecordClass(db=self, id=id, element=element, root_dir_path=self.root_dir_path)
        return self.__record_cache[id]
    
    def create(self, name:str, ext:str=None)->RecordType:
        new_id = self.__new_id
        new_path = self.name_id_parser.merge(new_id, name, ext)
        node = self.__tree.create(new_path)

        if self.element_type == ElementType.FILE:
            node.clear() # 폴더 데이터를 지우고 파일로 변환
            node.path.touch()

        return self.get_record(new_id)
    
    def remove(self, id:int)->Self:
        element = self.__get_element(id)
        element.parent.unlink(element.name).clear() # 자식 노드를 분리하고 삭제
        # self.root.pruning() # 빈 노드 제거


    def copy(self, id:int)->RecordType:
        target_work = self.get_record(id)
        name = target_work.name+"_copy"
        if self.element_type == ElementType.FILE:
            new_work = self.create(name, ext=target_work.ext)
        else:
            new_work = self.create(name)

        return new_work


    @property
    def size(self)->int: return len(self.__elements)

    def pruning(self): self.__tree.pruning()

    def print_tree(self):
        self.__tree.print_tree()

FileRecordType = TypeVar("FileRecordType", bound=FileRecord)
DirRecordType = TypeVar("DirRecordType", bound=DirRecord)


@dataclass
class DirDB(Generic[DirRecordType], FileSystemDB[DirRecordType]):
    element_type:ElementType = ElementType.DIR

@dataclass
class FileDB(Generic[FileRecordType], FileSystemDB[FileRecordType]):
    element_type:ElementType = ElementType.FILE
    
    # @property
    # def table(self)->pd.DataFrame:
    #     id_tokens_dict:Dict[ID, list[NAME]] = {k: v.split("/") for k, v in self.db.dir_db.id_name_dict.items()}
    #     max_len = max([len(v) for v in id_tokens_dict.values()], default=0)

    #     for k, v in id_tokens_dict.items():
    #         for i in range(max_len-len(v)):
    #             v.append("")
        
    #     df = pd.DataFrame(id_tokens_dict).T.reset_index()
    #     df.rename(columns={"index": "id"}, inplace=True)

    #     return df