from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel, PrivateAttr

# from rm.resource_db.record import RESOURCE_CONFIG_MANAGER

from ..memo import MemoFactory, FileMemo
import os

@dataclass
class PropertyManager:
    # 데이터를 통째로 로드/저장하는 객체를 확장하여
    # 
    # 필요한 값들에 대해 세부적으로 불러오는 것은 Record에 따라 확장해서 사용

    dir_path:Path
    memo_factory:MemoFactory
    PROPERTY_NAME:str = field(default="property")

    def __post_init__(self):
        self.file_memo:FileMemo = self.memo_factory.make_file_memo(self.memo_file_path)

    @cached_property
    def memo_file_path(self)->Path:
        return self.dir_path / self.PROPERTY_NAME

    # @cached_property
    # def config_memo(self)->FileMemo:
    #     return self.memo_factory.make_file_json_file_memo(self.config_file_path)

    def get(self, key:str)->Any:
        return self.content[key]


    def set(self, key:str, value:Any)->None:
        config = self.content
        config[key] = value
        self.content = config


    @property
    def content(self)->Dict[str, Any]:
        return self.file_memo.get()

    @content.setter
    def content(self, config:Dict[str, Any])->None:
        self.file_memo.set(config)

@dataclass
class PathHandling_PropertyManager(PropertyManager):
    # 경로 property에 대해 항상 상대 경로로 저장하고 절대 경로로 불러오는 기능 지원원

    def as_relative_path(self, path:Path)->Path:
        return path.relative_to(self.dir_path)

    def as_absolute_path(self, path:Path)->Path:
        path = self.dir_path / path
        path = Path(os.path.normpath(path))
        return path

    def get_as_absolute_path(self, key:str)->Path:
        return self.as_absolute_path(self.get(key))

    def set_as_relative_path(self, key:str, value:Path)->None:
        self.set(key, self.as_relative_path(value).as_posix())


