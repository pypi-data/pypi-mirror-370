


from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Dict, Generic, Type, TypeVar

from ..dirdb.dirdb import ID, NAME, DirDB
from .record import PropertyManager, ResourceRecord
import pandas as pd

if TYPE_CHECKING:
    from .factory import ResourceDBFactory


RESOURCE_RECORD = TypeVar('RECORD_CLASS', bound=ResourceRecord)


@dataclass
class ResourceDB(Generic[RESOURCE_RECORD]):
    # DIR_DB는 공유한 name 보장 x
    # ResourceDB는 고유한 name 보장

    dir_db: DirDB
    factory: 'ResourceDBFactory'
    RECORD_CLASS: Type[RESOURCE_RECORD]


    def all_ids(self)->list[ID]:
        return self.dir_db.ids

    def get(self, query: ID | NAME) -> RESOURCE_RECORD:
        id, name, dir_path = self.dir_db.get(query)
        return self.factory.make_record(id, name, dir_path)

    def get_unique_name(self, name:NAME)->NAME:
        i = 1
        origin_name = name
        while True:
            if not self.exist(name):
                return name
            name = f"{origin_name}_{i}"
            i += 1

    def create(self, name: NAME) -> RESOURCE_RECORD:
        name = self.get_unique_name(name)
        id = self.dir_db.create_new(name)
        return self.get(id)



    
    def exist(self, query: ID | NAME)->bool:
        return self.dir_db.exist(query)
    
