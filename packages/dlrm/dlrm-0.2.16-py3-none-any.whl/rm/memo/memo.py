
from pathlib import Path

from rm.wrapper_tool import Wrapper
from .file_io import CONTENT_TYPE, FileIO
import yaml
import pandas as pd
import json
from dataclasses import dataclass, field
from typing import ClassVar, Any, Generic, List, TypeVar, cast
from typing import Callable
from abc import ABC

class Memo(ABC):
    # File과 Memory에 관계 없이 데이터를 다루는 객체
    # 확장에 따라 file, memory 또는 둘 다 동시에 저장할 수도 있음
    
    def get(self)->Any: # 데이터를 전부 반환
        raise NotImplementedError("Not Implemented")
    
    def set(self, data)->None: # 데이터를 전부 저장
        raise NotImplementedError("Not Implemented")

    def clear(self):
        raise NotImplementedError("Not Implemented")
    
    def create(self):
        raise NotImplementedError("Not Implemented")

# class HookManager:
#     def __init__(self):
#         self._hooks = {}

#     def register(self, event_name: str, func):
#         self._hooks.setdefault(event_name, []).append(func)

#     def trigger(self, event_name: str, *args, **kwargs):
#         for func in self._hooks.get(event_name, []):
#             func(*args, **kwargs)


@dataclass
class FileMemo(Memo):
    # 간단한 데이터를 파일에 get, set 하는 객체
    # 데이터 읽기는 캐시하며, 수정 발생 시 파일 업데이트트

    file_path:Path
    file_io:FileIO
    # content: CONTENT_TYPE

    def __post_init__(self):
        if not self.file_path.exists():       
            self.file_io.create(self.file_path)
        self.content = self.file_io.read(self.file_path)

    def get(self)->Any: # 데이터를 통으로 반환 (캐싱됌)
        return self.content
    
    def set(self, data)->None: # 데이터를 통으로 저장
        self.content = data
        self.file_io.write(self.file_path, self.content)

    def remove(self):
        self.content = None
        if self.file_path.exists():
            self.file_io.remove(self.file_path)

# @dataclass
# class FileMemoHookName:
#     AFTER_LOAD_FILE:str = "after_load_file"
#     BEFORE_SAVE_FILE:str = "before_save_file"


# INNER_TYPE = TypeVar("INNER_TYPE")

# class Wrapper(Generic[INNER_TYPE]):
#     @staticmethod
#     def make(INNER_TYPE)->"INNER_TYPE":
#         return Wrapper(INNER_TYPE)

# cast


# class HookMemoDeco



from rm.hook.hook import Hook

class HookEvent:
    AFTER_LOAD_FILE:str = "after_get" # 값을 받아온 뒤
    BEFORE_SAVE_FILE:str = "before_set" # 값을 저장하기 전


Callback = Callable[[Any], Any]

class MemoHook(Hook):
    def register(self, event_name:HookEvent, callback:Callback):
        super().register(event_name, callback)
    
    def trigger(self, event_name:HookEvent, data:Any)->Any:
        for callback in self._hooks.get(event_name, []):
            data = callback(data)
        return data

@dataclass(kw_only=True)
class HookMemo(Wrapper[Memo]):
    hook:MemoHook = field(default_factory=MemoHook, init=False)

    def get(self)->Any:
        data = self.inner_obj.get()
        return self.hook.trigger(HookEvent.AFTER_LOAD_FILE, data)

    def set(self, data)->None:
        data = self.inner_obj.set(data)
        self.hook.trigger(HookEvent.BEFORE_SAVE_FILE, data)