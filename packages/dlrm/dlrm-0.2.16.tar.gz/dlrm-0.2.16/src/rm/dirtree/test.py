from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import re
import shutil
from collections import defaultdict


@dataclass
class TreeNode:
    """트리 노드를 나타내는 클래스"""
    name: str
    id: int
    path: Path
    parent: Optional['TreeNode'] = None
    children: List['TreeNode'] = field(default_factory=list)
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    @property
    def is_leaf(self) -> bool:
        """터미널 노드인지 확인"""
        return len(self.children) == 0
    
    @property
    def full_name(self) -> str:
        """ID가 포함된 전체 이름"""
        return f"{self.name}___id_{self.id}"
    
    @property
    def dir_name(self) -> str:
        """디렉토리 이름 (ID 포함)"""
        return self.full_name
    
    def add_child(self, child: 'TreeNode'):
        """자식 노드 추가"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'TreeNode'):
        """자식 노드 제거"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
    
    def get_all_children(self) -> List['TreeNode']:
        """모든 하위 노드 반환 (재귀적)"""
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.get_all_children())
        return result
    
    def find_by_id(self, target_id: int) -> Optional['TreeNode']:
        """ID로 노드 찾기"""
        if self.id == target_id:
            return self
        for child in self.children:
            result = child.find_by_id(target_id)
            if result:
                return result
        return None
    
    def find_by_name(self, target_name: str) -> Optional['TreeNode']:
        """이름으로 노드 찾기"""
        if self.name == target_name:
            return self
        for child in self.children:
            result = child.find_by_name(target_name)
            if result:
                return result
        return None


class TreeManager:
    """파일 시스템 기반 트리 구조 관리자"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.root_node: Optional[TreeNode] = None
        self.id_counter: int = 0
        self.used_ids: Set[int] = set()
        self.name_id_mapping: Dict[str, int] = {}
        
        # 루트 디렉토리가 없으면 생성
        if not self.root_path.exists():
            self.root_path.mkdir(parents=True, exist_ok=True)
        
        # 기존 트리 구조 로드
        self._load_tree()
    
    def _load_tree(self):
        """기존 트리 구조를 로드"""
        self.root_node = TreeNode("root", 0, self.root_path)
        self.used_ids.add(0)
        self.name_id_mapping["root"] = 0
        
        # 루트 디렉토리의 모든 하위 디렉토리 탐색
        self._load_children(self.root_node)
        
        # 사용된 ID 중 최대값 찾기
        if self.used_ids:
            self.id_counter = max(self.used_ids) + 1
    
    def _load_children(self, parent_node: TreeNode):
        """재귀적으로 자식 노드들을 로드"""
        try:
            for item in parent_node.path.iterdir():
                if item.is_dir():
                    # ID 패턴 매칭: name___id_숫자
                    match = re.match(r'^(.+)___id_(\d+)$', item.name)
                    if match:
                        name = match.group(1)
                        node_id = int(match.group(2))
                        
                        # 중복 ID 체크
                        if node_id in self.used_ids:
                            print(f"Warning: Duplicate ID {node_id} found in {item}")
                            continue
                        
                        child_node = TreeNode(name, node_id, item, parent_node)
                        parent_node.add_child(child_node)
                        self.used_ids.add(node_id)
                        self.name_id_mapping[name] = node_id
                        
                        # 재귀적으로 자식 로드
                        self._load_children(child_node)
                    else:
                        print(f"Warning: Directory {item.name} doesn't follow naming convention")
        except PermissionError:
            print(f"Permission denied accessing {parent_node.path}")
    
    def _generate_unique_id(self) -> int:
        """고유한 ID 생성"""
        while self.id_counter in self.used_ids:
            self.id_counter += 1
        return self.id_counter
    
    def _validate_name(self, name: str) -> bool:
        """이름 유효성 검사"""
        if not name or name.strip() == "":
            return False
        if "___id_" in name:
            return False
        return True
    
    def create_node(self, name: str, parent_path: Optional[Path] = None) -> TreeNode:
        """새로운 노드 생성"""
        if not self._validate_name(name):
            raise ValueError(f"Invalid name: {name}")
        
        # 부모 노드 찾기
        if parent_path is None:
            parent_node = self.root_node
        else:
            parent_node = self._find_node_by_path(parent_path)
            if parent_node is None:
                raise ValueError(f"Parent path not found: {parent_path}")
        
        # 고유 ID 생성
        node_id = self._generate_unique_id()
        
        # 디렉토리 생성
        new_dir_name = f"{name}___id_{node_id}"
        new_dir_path = parent_node.path / new_dir_name
        new_dir_path.mkdir(parents=True, exist_ok=True)
        
        # 노드 생성
        new_node = TreeNode(name, node_id, new_dir_path, parent_node)
        parent_node.add_child(new_node)
        
        # 매핑 업데이트
        self.used_ids.add(node_id)
        self.name_id_mapping[name] = node_id
        
        return new_node
    
    def delete_node(self, node_id: int) -> bool:
        """노드 삭제"""
        node = self.find_by_id(node_id)
        if node is None:
            return False
        
        # 루트 노드는 삭제 불가
        if node == self.root_node:
            raise ValueError("Cannot delete root node")
        
        # 모든 하위 노드 삭제
        all_children = node.get_all_children()
        for child in all_children:
            self.used_ids.discard(child.id)
            if child.name in self.name_id_mapping:
                del self.name_id_mapping[child.name]
        
        # 현재 노드 정리
        self.used_ids.discard(node.id)
        if node.name in self.name_id_mapping:
            del self.name_id_mapping[node.name]
        
        # 부모에서 제거
        if node.parent:
            node.parent.remove_child(node)
        
        # 디렉토리 삭제
        try:
            shutil.rmtree(node.path)
        except OSError as e:
            print(f"Error deleting directory {node.path}: {e}")
        
        return True
    
    def rename_node(self, node_id: int, new_name: str) -> bool:
        """노드 이름 변경"""
        if not self._validate_name(new_name):
            raise ValueError(f"Invalid name: {new_name}")
        
        node = self.find_by_id(node_id)
        if node is None:
            return False
        
        # 루트 노드는 이름 변경 불가
        if node == self.root_node:
            raise ValueError("Cannot rename root node")
        
        # 새 이름이 이미 사용 중인지 확인
        if new_name in self.name_id_mapping and self.name_id_mapping[new_name] != node_id:
            raise ValueError(f"Name {new_name} is already in use")
        
        # 기존 이름 매핑 제거
        if node.name in self.name_id_mapping:
            del self.name_id_mapping[node.name]
        
        # 새 디렉토리 이름
        new_dir_name = f"{new_name}___id_{node.id}"
        new_dir_path = node.parent.path / new_dir_name
        
        # 디렉토리 이름 변경
        try:
            node.path.rename(new_dir_path)
            node.path = new_dir_path
            node.name = new_name
            self.name_id_mapping[new_name] = node.id
        except OSError as e:
            print(f"Error renaming directory: {e}")
            return False
        
        return True
    
    def move_node(self, node_id: int, new_parent_path: Path) -> bool:
        """노드를 다른 부모로 이동"""
        node = self.find_by_id(node_id)
        if node is None:
            return False
        
        new_parent = self._find_node_by_path(new_parent_path)
        if new_parent is None:
            return False
        
        # 루트 노드는 이동 불가
        if node == self.root_node:
            raise ValueError("Cannot move root node")
        
        # 자기 자신이나 하위 노드로는 이동 불가
        if new_parent == node or new_parent in node.get_all_children():
            raise ValueError("Cannot move node to itself or its descendant")
        
        # 기존 부모에서 제거
        if node.parent:
            node.parent.remove_child(node)
        
        # 새 위치로 이동
        new_path = new_parent.path / node.dir_name
        try:
            node.path.rename(new_path)
            node.path = new_path
            node.parent = new_parent
            new_parent.add_child(node)
        except OSError as e:
            print(f"Error moving directory: {e}")
            return False
        
        return True
    
    def find_by_id(self, node_id: int) -> Optional[TreeNode]:
        """ID로 노드 찾기"""
        return self.root_node.find_by_id(node_id)
    
    def find_by_name(self, name: str) -> Optional[TreeNode]:
        """이름으로 노드 찾기"""
        return self.root_node.find_by_name(name)
    
    def find_by_path(self, path: Path) -> Optional[TreeNode]:
        """경로로 노드 찾기"""
        return self._find_node_by_path(path)
    
    def _find_node_by_path(self, path: Path) -> Optional[TreeNode]:
        """경로로 노드 찾기 (내부 메서드)"""
        if not path.exists():
            return None
        
        # 루트부터 시작해서 경로 따라가기
        current_node = self.root_node
        relative_path = path.relative_to(self.root_path)
        
        for part in relative_path.parts:
            found = False
            for child in current_node.children:
                if child.path.name == part:
                    current_node = child
                    found = True
                    break
            if not found:
                return None
        
        return current_node
    
    def get_all_nodes(self) -> List[TreeNode]:
        """모든 노드 반환"""
        if self.root_node is None:
            return []
        return [self.root_node] + self.root_node.get_all_children()
    
    def get_leaf_nodes(self) -> List[TreeNode]:
        """터미널 노드들만 반환"""
        all_nodes = self.get_all_nodes()
        return [node for node in all_nodes if node.is_leaf]
    
    def print_tree(self, node: Optional[TreeNode] = None, level: int = 0):
        """트리 구조 출력"""
        if node is None:
            node = self.root_node
        
        indent = "  " * level
        print(f"{indent}{node.full_name}")
        
        for child in node.children:
            self.print_tree(child, level + 1)
    
    def get_statistics(self) -> Dict:
        """트리 통계 정보"""
        all_nodes = self.get_all_nodes()
        leaf_nodes = self.get_leaf_nodes()
        
        return {
            "total_nodes": len(all_nodes),
            "leaf_nodes": len(leaf_nodes),
            "max_depth": self._get_max_depth(self.root_node),
            "used_ids": len(self.used_ids),
            "next_id": self.id_counter
        }
    
    def _get_max_depth(self, node: TreeNode, current_depth: int = 0) -> int:
        """최대 깊이 계산"""
        if not node.children:
            return current_depth
        
        max_depth = current_depth
        for child in node.children:
            depth = self._get_max_depth(child, current_depth + 1)
            max_depth = max(max_depth, depth)
        
        return max_depth

