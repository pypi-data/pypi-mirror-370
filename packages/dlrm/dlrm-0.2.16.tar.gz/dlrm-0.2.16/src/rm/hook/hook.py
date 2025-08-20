from typing import Any, Callable, Dict, List


Callback = Callable[..., Any]

class Hook:
    def __init__(self):
        self._hooks: Dict[str, List[Callback]] = {}

    def register(self, event: str, callback: Callback) -> None:
        """특정 이벤트에 콜백 함수를 등록"""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    def trigger(self, event: str, *args, **kwargs) -> None:
        """등록된 콜백을 모두 실행"""
        for callback in self._hooks.get(event, []):
            callback(*args, **kwargs)

    def clear(self, event: str) -> None:
        """특정 이벤트의 모든 콜백 제거"""
        self._hooks[event] = []

    def clear_all(self) -> None:
        """모든 이벤트의 콜백 제거"""
        self._hooks.clear()