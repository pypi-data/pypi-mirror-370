from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Protocol, Type, TypeVar

import yaml

CONTENT_TYPE = TypeVar("CONTENT_TYPE", dict, list, str, int, float, bool)

class FileIO(Protocol):
    def write(self, file_path:Path, content:CONTENT_TYPE)->None:
        pass
        
    def read(self, file_path:Path):
        pass

    def remove(self, file_path:Path)->None:
        if file_path.exists():
            file_path.unlink()

    def create(self, file_path:Path)->None:
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

class DictFileIO(FileIO):
    def make_empty_data(self)->Any:
        return {}

    def create(self, file_path:Path)->None:
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            self.write(file_path, self.make_empty_data())

@dataclass
class YamlFileIO(DictFileIO):
    encoding:str = "utf-8-sig"
    
    def write(self, file_path:Path, data:CONTENT_TYPE)->None:
        with open(file_path, 'w', encoding=self.encoding) as f:
            yaml.dump(data, f, allow_unicode=True)
        
    def read(self, file_path:Path):
        with open(file_path, 'r', encoding=self.encoding) as f:
            return yaml.safe_load(f) or {}



@dataclass
class JsonFileIO(DictFileIO):
    encoding:str = "utf-8-sig"
    
    def write(self, file_path:Path, data:Any)->None:
        with open(file_path, 'w', encoding=self.encoding) as f:
            json.dump(data, f, ensure_ascii=False)
    
    def read(self, file_path:Path):
        with open(file_path, 'r', encoding=self.encoding) as f:
            return json.load(f)

    # def make_empty_data(self)->Any:
    #     return {}

    # def create(self, file_path:Path)->None:
    #     if not file_path.exists():
    #         file_path.parent.mkdir(parents=True, exist_ok=True)
    #         self.write(file_path, self.make_empty_data())