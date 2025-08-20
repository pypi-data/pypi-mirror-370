# from dataclasses import dataclass, field
# from enum import Enum, auto
# from typing import Callable, Dict, Generic, List, TypeVar, final
# from rm.hook.hook import Hook, Callback
# from rm.tree.tree import TreeNode

# NodeType = TypeVar('NodeType', bound='HookingTreeNode')

# class HookEvent(Enum):
#     BEFORE_NODE_CREATE = auto()
#     AFTER_NODE_CREATE = auto()

#     BEFORE_NODE_UPDATE = auto()
#     AFTER_NODE_UPDATE = auto()

#     BEFORE_NODE_REMOVE = auto()
#     AFTER_NODE_REMOVE = auto()


# class CustomHook(Hook, Generic[NodeType]):

#     Parent_Child_Callback = Callable[[NodeType, NodeType], None]

#     NodeCallback = Callable[[NodeType], None]

#     # def register___before_node_create(self, BeforeNodeCreateCallback)->None:
#     #     self.register(HookEvent.BEFORE_NODE_CREATE, BeforeNodeCreateCallback)

#     # def trigger___before_node_create(self, parent:NodeType, child:NodeType)->None:
#     #     self.trigger(HookEvent.BEFORE_NODE_CREATE, parent, child)

#     def register___after_node_create(self, callback:NodeCallback)->None:
#         self.register(HookEvent.AFTER_NODE_CREATE, callback)

#     def trigger___after_node_create(self, target_node:NodeType)->None:
#         self.trigger(HookEvent.AFTER_NODE_CREATE, target_node)

    

#     def register___after_node_removed(self, callback:NodeCallback)->None:
#         self.register(HookEvent.AFTER_NODE_REMOVE, callback)
    
#     def trigger___after_node_removed(self, target_node:NodeType)->None:
#         self.trigger(HookEvent.AFTER_NODE_REMOVE, target_node)

# @dataclass(kw_only=True)
# class HookingTreeNode(Generic[NodeType], TreeNode[NodeType]):
#     # 기존에 _func을 __func로 변경하고 _func는 hook을 심고 __func 호출출
#     hook:CustomHook[NodeType] = field(default_factory=CustomHook)

#     @final
#     def _create_child_with_hook(self, name:str)->NodeType:
#         child = super()._create_child_with_hook(name)
#         self.hook.trigger___after_node_create(child)
#         return child

#     @final
#     def _remove_child_with_hook(self)->None:
#         super()._remove_child_with_hook()
#         self.hook.trigger___after_node_removed(self)