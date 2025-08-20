
from dataclasses import dataclass, field
import enum
from pathlib import Path
from typing import Any, Dict, Generic, List, TypeVar
from typing_extensions import Self


def ensure_list(value:str|Path|List[str]|None)->List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Path):
        return list(value.parts)
    
    return value


@dataclass(kw_only=True)
class TreeNode:
    # 자식 노드에 대해 다룰 수 있는 원시적인 기능 지원
    # 노드를 직접 만들고 등록하는 방식
    # 연산마다다 노드를 반환하여 연속 호출 지원
    # 자식 노드를 추가 삭제 할 수 있으나, 추가 삭제 시 속성값들의 유기적인 연결은 고려하지 않음

    name: str
    _name_children: Dict[str, Self] = field(default_factory=dict, init=False)

    

    @property
    def children(self)->List[Self]:
        return list(self._name_children.values())

    def has_child(self, name:str)->bool:
        return name in self._name_children

    def get_child(self, name:str)->Self:
        if not self.has_child(name):
            raise ValueError(f"Child with name {name} not found")
        return self._name_children[name]

    def remove_child(self, name:str)->Self:
        child = self.get_child(name)
        del self._name_children[name]
        return child
        
    def append_child(self, child:Self)->Self:
        if self.has_child(child.name):
            raise ValueError(f"Child with name {child.name} already exists")
        self._name_children[child.name] = child
        return child

    def rename(self, new_name:str)->Self:
        self.name = new_name
        return self

    @property
    def child_num(self)->int:
        return len(self._name_children)

    @property
    def size(self)->int:
        return sum([child.size for child in self.children], 0) + 1


    
    def print_tree(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(prefix + connector + self.name)

        # 다음 레벨의 prefix 생성
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            child.print_tree(prefix=new_prefix, is_last=is_last_child)   



@dataclass(kw_only=True)
class LikableTreeNode(TreeNode):
    # 자식노드에 대한 연산에 대해 부모 자식간 유기적 연결 고려

    __root: Self = field(default=None, init=False)
    _parent: Self = field(default=None, init=False)
    _depth: int = field(default=0, init=False) # 루트로부터 떨어진 깊이

    @property
    def root(self)->Self: return self.__root

    @property
    def parent(self)->Self: return self._parent

    @property
    def depth(self)->int: return self._depth

    def __post_init__(self):
        if self.__root is None:
            self.__root = self

    def rename(self, new_name:str)->Self:
        self.parent.remove_child(self.name)
        super().rename(new_name)
        self.parent.append_child(self)
        return self

    @property
    def is_root(self)->bool:
        return self.__root is self

    @property
    def is_terminal(self)->bool:
        return len(self._name_children) == 0  

    # 부모 자식간 유기적인 연결 기능 지원원

    def link_child(self, child:Self)->Self:
        if not child.is_root:
            raise ValueError("The target not of linking must be root node, But current target is not a root")
        
        if self.has_child(child.name):
            raise ValueError(f"Child with name {child.name} already exists")
        self.append_child(child)
        child._parent = self
        child._depth = self._depth + 1
        child.__root = self.__root
        return child



    def unlink_child(self, name:str)->Self:
        # 자식 노드를 분리하여 root 노드로 만들고 반환
        child = self.remove_child(name)
        child._parent = None
        child._depth = 0
        child.__root = child
        return child


    def create_child(self, name:str)->Self:
        # 자식 노드의 생성과 연결을 한번에 처리
        child = self._create_root_node(name)
        self.link_child(child)
        return child


    def _create_root_node(self, name)->Self:
        return self.__class__(name=name)


class ExtendedTreeNode(LikableTreeNode):
    # 자식에 대한 연산을 자손 단위로 확장장

    def has(self, names:str|List[str])->bool:
        names = ensure_list(names)
        if len(names) == 0: return True
        first_name, other_names = names[0], names[1:]
        return self.has_child(first_name) and self.get_child(first_name).has(other_names)

    def get(self, names:str|List[str])->Self:
        names = ensure_list(names)
        if len(names) == 0: return self
        
        first_name, other_names = names[0], names[1:]
        return self.get_child(first_name).get(other_names)

    def create(self, names:str|List[str])->Self:
        names = ensure_list(names)

        
        if len(names) == 0:
            return self
        
        first_name, other_names = names[0], names[1:]
        
        if not self.has_child(first_name):
            self.create_child(first_name)
            

        return self.get_child(first_name).create(other_names)



    def unlink(self, names:str|List[str])->Self:
        removed_node =self.get(names)
        return removed_node.parent.unlink_child(removed_node.name)

