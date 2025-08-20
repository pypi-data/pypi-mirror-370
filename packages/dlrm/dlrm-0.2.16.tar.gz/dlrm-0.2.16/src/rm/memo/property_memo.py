
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, Type, TypeVar

from pydantic import BaseModel
from rm.memo.memo import HookEvent, HookMemo



class Property(BaseModel):
    pass

PropertyType = TypeVar('PropertyType', bound=Property)

@dataclass(kw_only=True)
class PropertyMemo(HookMemo, Generic[PropertyType]):
    property_class:Type[PropertyType]
    # 자동 변환 훅을 심는다.
    # BaseModel로 자동 변환

    def __post_init__(self):
        self.hook.register(HookEvent.AFTER_LOAD_FILE, self.after_load_file)
        self.hook.register(HookEvent.BEFORE_SAVE_FILE, self.before_save_file)

    @classmethod
    def after_load_file(cls, data:Any)->Any:
        return data
    
    @staticmethod
    def before_save_file(data:Any)->Any:
        return data
    
    def get(self)->PropertyType:
        data = super().get()
        return self.property_class(**data)
    
    def set(self, data:PropertyType)->None:
        super().set(data.model_dump(mode="json"))