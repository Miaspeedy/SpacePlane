from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import sdl3 as sdl

if TYPE_CHECKING:
    # 仅用于类型提示，避免循环导入
    from Game import Game

class Scene(ABC):
    def __init__(self, game: "Game") -> None:
        self.game: "Game" = game

    @abstractmethod
    def init(self) -> None:
        """场景初始化：加载资源、重置状态等。"""
        ...

    @abstractmethod
    def update(self, deltatime: float) -> None:
        """逻辑更新:deltatime 为tick """
        ...

    @abstractmethod
    def render(self) -> None:
        """渲染："""
        ...

    @abstractmethod
    def clean(self) -> None:
        """清理资源：在场景退出/切换时调用。"""
        ...

    @abstractmethod
    def handle_event(self, event: sdl.SDL_Event) -> None:
        """事件处理：把 pygame 的单个事件分发到场景。"""
        ...
