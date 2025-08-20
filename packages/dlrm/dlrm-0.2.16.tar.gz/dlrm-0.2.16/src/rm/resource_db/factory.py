from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Type

from rm.memo.memo import FileMemo
from rm.resource_db.base_model import AutoSavingModel



# from .property_manager import PropertyManager
from ..memo import MemoFactory
from ..dirdb.dirdb import ID, NAME
from ..dirdb.factory import DirDBFactory
from .record import ResourceRecord
from .db import ResourceDB
from .view import DBView


from typing import TypeVar, Generic, Type

CONFIG_MANAGER = TypeVar('CONFIG_MANAGER', bound=AutoSavingModel)
RESOURCE_RECORD = TypeVar('RESOURCE_RECORD', bound=ResourceRecord)
RESOURCE_DB = TypeVar('RESOURCE_DB', bound=ResourceDB)
DB_VIEW = TypeVar('DB_VIEW', bound=DBView)

@dataclass
class ResourceDBFactory(Generic[CONFIG_MANAGER, RESOURCE_RECORD, RESOURCE_DB, DB_VIEW]):
    dir_path: Path # 리소스들이 저장될 디렉토리 경로
    CONFIG_MANAGER_CLASS:Type[CONFIG_MANAGER]
    RECORD_CLASS:Type[RESOURCE_RECORD]
    DB_CLASS:Type[RESOURCE_DB]
    VIEW_CLASS:Type[DB_VIEW]
    PROPERTY_NAME:str = field(default="property")

    @cached_property
    def dir_db_factory(self)->DirDBFactory:
        return DirDBFactory()
    
    @cached_property
    def memo_factory(self)->MemoFactory:
        return MemoFactory()

    def memo(self, dir_path:Path)->FileMemo:
        return self.memo_factory.make_file_memo(dir_path/self.PROPERTY_NAME)

    @cached_property
    def db(self)->RESOURCE_DB:
        return self.DB_CLASS(self.dir_db_factory.make_dirdb(self.dir_path), self, self.RECORD_CLASS)

    def make_config_manager(self, dir_path:Path)->CONFIG_MANAGER:

        return self.CONFIG_MANAGER_CLASS.load(self.memo(dir_path))
        # return self.CONFIG_MANAGER_CLASS(dir_path, self.memo_factory, CONFIG_NAME=self.PROPERTY_NAME)
    
    def make_record(self, id:ID, name:NAME, dir_path:Path)->RESOURCE_RECORD:
        return self.RECORD_CLASS(id, name, dir_path, self.make_config_manager(dir_path))

    @cached_property
    def view(self)->DB_VIEW:
        return self.VIEW_CLASS(self.db)