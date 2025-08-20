from typing import List
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path, PurePath
from typing import Callable
from abc import ABC, abstractmethod

TerminalCheker = Callable[[PurePath], bool]

@dataclass
class TreeDB(ABC):
    path: Path
    terminal_checker: TerminalCheker
    depth: int = 0
    
    """    
    디렉터리가 하나의 노드에 해당하며, 터미널 여부는 특정 조건에 따라 결정되는 트리 객체
    터미널 노드의 하위 디렉터리는 무시
    터미널 노드의 상위 디렉터리는 모드 경로 디렉터리로 간주
    경로 디렉터리는 반드시 하나 이상의 터미널 또는 경로 디렉터리를 가지고 있어야 한다.
    """

    def __post_init__(self):
        chidren, violating_paths = self._find_children()
        self.children: List['DirTree'] = chidren
        self.violating_paths: List[Path] = violating_paths # 탐색과정에서 발견된 규칙 위반 경로들을 모아두는 곳

    @cached_property
    def is_terminal(self)->bool:
        return self.terminal_checker(self.path)

    @cached_property
    def is_path_node(self)->bool:
        return len(self.children) > 0

    @cached_property
    def is_root(self)->bool:
        return self.depth == 0


    @abstractmethod
    def _find_children(self)->tuple[List['DirTree'], List[Path]]:
        pass

    
    @cached_property
    def terminal_nodes(self):
        if (self.is_root is not True) and self.is_terminal:
            return [self]
        else:
            terminal_nodes: List[DirTree] = []
            for child in self.children:
                terminal_nodes.extend(child.terminal_nodes)
            return terminal_nodes

    @cached_property
    def all_violating_paths(self)->List[Path]:
        """
        탐색 과정에서 발견된 규칙 위반 경로들을 모아두는 곳
        """
        if self.is_terminal:
            return self.violating_paths
        else:
            all_violationg_paths:List[Path] = []
            all_violationg_paths.extend(self.violating_paths)
            for child in self.children:
                all_violationg_paths.extend(child.all_violating_paths)
        return all_violationg_paths

@dataclass
class DirTree(TreeDB):

    def _find_children(self)->tuple[List['DirTree'], List[Path]]:
        children: List[DirTree] = []
        violating_paths: List[Path] = []
        
        if (self.is_root) or (not self.is_terminal):
            
            # dir path를 구하며 file인 path는 룰 위반 경로로 수집
            sub_dir_paths: List[Path] = []
            for sub_path in self.path.iterdir():
                if sub_path.is_dir():
                    sub_dir_paths.append(sub_path)
                else:
                    violating_paths.append(sub_path)

                    
            # dir_path 정렬
            sub_dir_paths.sort()

            
            # 하위 트리를 생성하며 룰 위반 경로 수집
            for sub_dir_path in sub_dir_paths:
                sub_tree = DirTree(sub_dir_path, self.terminal_checker, self.depth + 1)
                if sub_tree.is_terminal or sub_tree.is_path_node:
                    children.append(sub_tree)
                else:
                    violating_paths.append(sub_dir_path)
                    
        return children, violating_paths


@dataclass
class FileTree(TreeDB):            
    
    def _find_children(self)->tuple[List['DirTree'], List[Path]]:
        children: List[DirTree] = []
        violating_paths: List[Path] = []
        
        if (self.is_root) or (not self.is_terminal):
            
            if self.path.is_file():
                return [], []

            sub_dir_paths = list(self.path.iterdir())
                    
            # dir_path 정렬
            sub_dir_paths.sort()

            
            # 하위 트리를 생성하며 룰 위반 경로 수집
            for sub_dir_path in sub_dir_paths:
                sub_tree = FileTree(sub_dir_path, self.terminal_checker, self.depth + 1)
                if sub_tree.is_terminal or sub_tree.is_path_node:
                    children.append(sub_tree)
                else:
                    violating_paths.append(sub_dir_path)
                    
        return children, violating_paths
