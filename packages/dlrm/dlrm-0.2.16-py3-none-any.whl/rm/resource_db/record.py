from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

from rm.dirdb.dirdb import ID, NAME
from rm.resource_db.base_model import AutoSavingModel
from rm.property_manager.property_manager import PropertyManager

# PROPERTY_MANAGER = TypeVar('PROPERTY_MANAGER_CLASS', bound=PropertyManager)
PROPERTY_MANAGER = TypeVar('PROPERTY_MANAGER_CLASS', bound=AutoSavingModel)

@dataclass
class ResourceRecord(Generic[PROPERTY_MANAGER]):
    # 단일 데이터 셋, 모델 또는 작업을 관리한다.
    # 리소스에 맞게 확장된 클래스를 사용한 것으로 기대대 
    id:ID
    name:NAME
    dir_path:Path
    property_manager:PROPERTY_MANAGER


