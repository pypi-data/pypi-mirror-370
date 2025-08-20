from pathlib import Path
from typing import Type

from .file_io import YamlFileIO
from .memo import FileMemo, HookMemo
from .property_memo import PropertyMemo, PropertyType

class MemoFactory:
    def make_file_memo(self, file_path:Path)->FileMemo:
        return FileMemo(file_path.with_suffix(".yaml"), YamlFileIO())

    def make_hook_memo(self, file_path:Path)->HookMemo:
        return HookMemo(inner_obj=self.make_file_memo(file_path))

    def make_property_memo(self, file_path:Path, property_class:Type[PropertyType])->PropertyMemo:
        return PropertyMemo(inner_obj=self.make_file_memo(file_path), property_class=property_class)

    # def make_file_memo(self, file_path:Path)->FileMemo:
    #     return FileMemo(file_path.with_suffix(".json"), JsonFileIO())




