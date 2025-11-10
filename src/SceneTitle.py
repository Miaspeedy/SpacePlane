from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import sdl3 as sdl
from sdl3 import SDL_mixer as mix
from ctypes import byref

from Logger import GameLogger as log
from Scene import Scene
from SceneMain import SceneMain

if TYPE_CHECKING:
    # 避免循环导入
    from Game import Game

class SceneTitle(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.bgm = None
        self.timer = 0.0

    def init(self) -> None:
        # 载入并播放背景音乐
        self.bgm = sdl.MIX_LoadAudio(self.game.getMixer(), self.game.to_abs_path("assets/music/06_Battle_in_Space_Intro.ogg").encode(), False)
        props = sdl.SDL_CreateProperties()
        ok = sdl.SDL_SetNumberProperty(props, mix.MIX_PROP_PLAY_LOOPS_NUMBER, -1) # 无限循环
        if not ok:
            log.error("Failed to set property for sound TitleBGM: {}", sdl.SDL_GetError())

        mix.MIX_SetTrackAudio(self.game.getBGMTrack(), self.bgm)
        isPlayBack = sdl.MIX_PlayTrack(self.game.getBGMTrack(), props)
        if not isPlayBack:
            log.error("Failed to play sound TitleBGM: {}", sdl.SDL_GetError())

    def update(self, deltaTime: float) -> None:
        self.timer += deltaTime
        if self.timer > 1.0:
            self.timer -= 1.0

    def render(self) -> None:
        # 渲染标题文字
        titleText = f"Space Plane"#太空战机
        self.game.renderTextCentered(titleText, 0.4, True)

        # 渲染普通文字
        if self.timer < 0.5:
            instructions = f"Press SPACE key to Start Game"  # 按 空格 键开始游戏
            self.game.renderTextCentered(instructions, 0.8, False)

    def clean(self) -> None:
        if self.bgm is not None:
            mix.MIX_DestroyAudio(self.bgm)

    def handle_event(self, event : sdl.SDL_Event) -> None:
        if event.type == sdl.SDL_EVENT_KEY_DOWN:
            if event.key.scancode == sdl.SDL_SCANCODE_SPACE:
                sceneMain = SceneMain(self.game)
                self.game.changeScene(sceneMain)
