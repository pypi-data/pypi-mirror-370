from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, Optional, Type, TypeVar
from pydantic import BaseModel, PrivateAttr, ValidationInfo, field_serializer, field_validator
from ..memo import FileMemo
import os

MODEL = TypeVar("MODEL", bound="AutoSavingModel")

class AutoSavingModel(BaseModel):
    _memo: FileMemo = PrivateAttr()
    _suspend_sync: bool = PrivateAttr(default=False)


    model_config = {
        "validate_assignment": True  # ← 이게 있어야 setattr 계열 동작에 훅이 걸림
    }

    def __init__(self, **data):
        memo = data.pop("_memo")
        super().__init__(**data)
        self._memo = memo
        self._save()

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if not name.startswith("_") and not self._suspend_sync:
            self._save()

    def _save(self):
        self._memo.set(self.model_dump())

    @classmethod
    def load(cls: Type[MODEL], memo: FileMemo) -> MODEL:
        content = memo.get()
        return cls(_memo=memo, **content)

    @cached_property
    def dir_path(self)->Path:
        return self._memo.file_path.parent

    def to_absolute_path(self, path:Path)->Path:
        path = self.dir_path / path
        return Path(os.path.normpath(path))

    def to_relative_path(self, path:Path)->Path:
        return path.relative_to(self.dir_path)

    @field_serializer("*", check_fields=False)
    def serialize_all_paths(self, value: Any):
        if isinstance(value, Path):
            # value = self.to_absolute_path(value)
            value = value.as_posix()
        return value
    
    def to_absolute_path(self, path:Path)->Path:
        return Path(os.path.normpath(self.dir_path / path))
        
    def to_relative_path(self, path:Path)->Path:
        return path.relative_to(self.dir_path)

    # # # @classmethod
    # # @field_validator("*", mode="before")
    # # def parse_paths(self, value: Any, info: ValidationInfo) -> Any:
    # #     if info.field_name.endswith("_path") and isinstance(value, str):
    # #         value = self.to_absolute_path(value)
    # #         return Path(value)
    # #     return value

    
    # def __pydantic_setattr__(self, name, value):
    #     print(name, value, 111111111111)
    #     # "_path"로 끝나는 필드이면 자동 변환
    #     if name.endswith('_path') and isinstance(value, str|Path):
    #         value = self.to_absolute_path(Path(value))
    #     super().__pydantic_setattr__(name, value)



# PROPERTY_MANAGER_CLASS = TypeVar('PROPERTY_MANAGER_CLASS', bound=AutoSavingModel)
# @dataclass
# class ReferedPropertyManager(Generic[PROPERTY_MANAGER_CLASS]):
#     refer: 'ReferedPropertyManager'
#     main: PROPERTY_MANAGER_CLASS

#     def get(self, key:str)->Any:
#         if self.refer is None:
#             return getattr(self.main, key)
        
#         value = getattr(self.main, key)
#         if value == None:
#             value = getattr(self.refer, key)
#         return value