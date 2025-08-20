from pathlib import Path
import shutil


class FileSystemManager:        
    @classmethod
    def is_empty(cls, path:Path)->bool:        
        return not any(path.iterdir())
    
    @classmethod
    def remove_empty_parents_recursively(cls, path:Path):
        parents = list(path.parents)
        for parent in parents[:-1]:
            if cls.is_empty(parent):
                shutil.rmtree(parent)
            else:
                break
    
    @classmethod
    def remove_dir(cls, path:Path):
        shutil.rmtree(path)