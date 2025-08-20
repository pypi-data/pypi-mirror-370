
from functools import cached_property
from pathlib import Path
from rm.dirdb.dirdb import DirDB, DirTreeFactory, FileDB

import os



class DirDBFactory:
    @cached_property
    def dir_tree_factory(self)->DirTreeFactory: return DirTreeFactory()

    def make_dirdb(self, dir_path:Path)->DirDB: return DirDB(path=dir_path, factory=self.dir_tree_factory)



    def make_filedb(self, file_path:Path, ext:str)->FileDB: return FileDB(path=file_path, factory=self.dir_tree_factory, ext=ext)
    