from functools import cached_property
from pathlib import Path, PurePath
from typing import Type

from rm.dirtree.file_name_id_manager import File_Name_ID_Manager, File_Name_ID_Parser, Linked_File_Name_ID_Manager
from .dir_tree import DirTree, FileTree, TerminalCheker
from .dir_name_id_manager import DIR_Name_ID_Manager, Linked_Name_ID_Manager, Dir_Name_ID_Parser


class DirTreeFactory:


    @cached_property
    def dir_name_id_parser(self)->Dir_Name_ID_Parser:
        return Dir_Name_ID_Parser()

    @cached_property
    def file_name_id_parser(self)->File_Name_ID_Parser:
        return File_Name_ID_Parser()

    def dir_id_name_manager(self, path:PurePath)->DIR_Name_ID_Manager:
        return DIR_Name_ID_Manager(path, self.dir_name_id_parser)

    def file_id_name_manager(self, path:PurePath)->File_Name_ID_Manager:
        return File_Name_ID_Manager(path, self.file_name_id_parser)

    def dir_linked_id_name_manager(self, path:Path)->Linked_Name_ID_Manager:
        return Linked_Name_ID_Manager(self.dir_id_name_manager(path))
        # return Linked_Name_ID_Manager(path, self.dir_name_id_parser)

    def file_linked_id_name_manager(self, path:Path)->Linked_File_Name_ID_Manager:
        return Linked_File_Name_ID_Manager(self.file_id_name_manager(path))

    @cached_property
    def dir_terminal_checker(self)->TerminalCheker:
        f = self.dir_name_id_parser.split
        return lambda path : f(path)[0] is not None

    @cached_property
    def file_terminal_checker(self)->TerminalCheker:
        f = self.file_name_id_parser.split
        return lambda path : f(path)[0] is not None

    def get_dir_tree(self, dir_path:Path)->DirTree:
        return DirTree(dir_path, self.dir_terminal_checker)

    def get_file_tree(self, file_path:Path)->FileTree:
        return FileTree(file_path, self.file_terminal_checker)
