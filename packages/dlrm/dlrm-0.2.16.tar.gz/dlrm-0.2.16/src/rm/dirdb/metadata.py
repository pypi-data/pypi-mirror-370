"""
메타데이터 관리 모듈
ID 기반 폴더 시스템의 메타데이터 파일 관리를 담당
"""

from functools import cached_property
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class JsonFile:
    """
    JSON 파일 관리 클래스
    파일이 항상 존재하도록 보장하고 content property로 직접 접근 가능
    """
    file_path: Path
    
    def __post_init__(self):
        """초기화 후 파일 존재 보장"""
        self._ensure_file_exists()
        self._content = self.load_content()
    
    def _ensure_file_exists(self):
        """파일이 존재하지 않으면 기본 데이터로 생성"""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
    
    def load_content(self)->Dict[str, Any]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    def content(self) -> Dict[str, Any]:
        return self._content
    
    @content.setter
    def content(self, data: Dict[str, Any]):
        self._content = data
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        if key not in self.content:
            self.set(key, default)
        
        return self.content[key]

    
    def set(self, key: str, value: Any):
        """
        JSON 파일의 특정 키에 값을 설정
        
        Args:
            key: 설정할 키
            value: 설정할 값
        """
        current_data = self.content
        current_data[key] = value
        self.content = current_data
    
    def update(self, data: Dict[str, Any]):
        """
        JSON 파일의 여러 키-값을 한번에 업데이트
        
        Args:
            data: 업데이트할 키-값 딕셔너리
        """
        current_data = self.content
        current_data.update(data)
        self.content = current_data
    
    def __repr__(self):
        """JsonFile 객체의 문자열 표현"""
        return f"JsonFile(file_path={self.file_path})"


@dataclass
class MetaData:
    """
    메타데이터 파일 관리 클래스
    meta.json 파일을 통해 최대 ID 값과 기타 메타정보를 관리
    """
    dir_path: Path
    meta_filename: str = 'meta.json'

    @cached_property
    def meta_file_path(self)->Path:
        return self.dir_path / self.meta_filename

    @cached_property
    def meta_data(self)->JsonFile:
        return JsonFile(self.meta_file_path)

    @property
    def last_id(self)->int:
        return self.meta_data.get('last_id', -1)
        
    @last_id.setter
    def last_id(self, value: int):
        self.meta_data.set('last_id', value)
    
    def get_next_id_increasing_1(self)->int:
        self.last_id += 1
        id = self.last_id
        return id