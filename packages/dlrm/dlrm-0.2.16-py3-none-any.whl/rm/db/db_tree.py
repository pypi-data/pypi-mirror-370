from dataclasses import dataclass, field
from pathlib import Path
from typing_extensions import Self

from rm.dirtree.file_name_id_manager import File_Name_ID_Parser
from rm.tree.path_tree import PathTreeNode


@dataclass
class DBTreeNode(PathTreeNode):
    # root_dir:Path
    name_id_parser:File_Name_ID_Parser = field(default=File_Name_ID_Parser(), init=False)

    # @property
    # def path(self)->Path:
    #     return self.root_dir/super().path

    def terminal_nodes(self)->list[Self]:
        if self.is_terminal:
            if self.is_root:
                return []
            else:
                return [self]
        else:
            return sum([child.terminal_nodes() for child in self.children], [])


    def _create_root_node(self, name:str)->Self:
        return self.__class__(name=name, _init_file_system_sync_on=self.file_system_sync_on)

    @property
    def __db_id(self)->int|None:
        id, name, ext =self.name_id_parser.split(self.path)
        return id
    
    @property
    def is_empty(self)->bool:
        return super().is_empty and (not self.__is_db_element)

    @property
    def __is_db_element(self)->bool:
        return self.__db_id is not None
    

    def pruning(self): # 빈 노드 제거
        for child in self.children:
            child.pruning()

        if self.is_root: return # root는 대상이 되지 않음 

        if self.is_empty:
            self.delete()