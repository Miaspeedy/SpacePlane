from __future__ import annotations
from typing import TYPE_CHECKING
import sdl3 as sdl
from sdl3 import SDL_image as img
from ctypes import c_float, byref

from Logger import GameLogger as log
from Scene import Scene
from Object import Player

if TYPE_CHECKING:
    # 避免循环导入
    from Game import Game

class SceneMain(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.player = Player()      

    def init(self) -> None:
        # todo 改为相对位置
        self.player.texture = img.IMG_LoadTexture(self.game.getrenderer(), b"D:/PyProjects/SpacePlane/assets/image/SpaceShip.png")

        if self.player.texture is None:
            log.error("Failed to load player texture: {}",sdl.SDL_GetError())
        
        w = c_float(); h = c_float()
        ok = sdl.SDL_GetTextureSize(self.player.texture, byref(w), byref(h))
        if not ok:
            log.error("Failed to get player texture size: {}", sdl.SDL_GetError())

        self.player.width = int(int(w.value) / 4)
        self.player.height = int(int(h.value) / 4)

        self.player.position.x = self.game.getWindowWidth() / 2 - self.player.width / 2
        self.player.position.y = self.game.getWindowHeight() - self.player.height

    def update(self, delta_time: float) -> None:
        self.keyboardControl()

    def render(self) -> None:
       playerRect = sdl.SDL_FRect(self.player.position.x, self.player.position.y,
                     self.player.width, self.player.height)
       sdl.SDL_RenderTexture(self.game.getrenderer(), self.player.texture, None, playerRect)

    def clean(self) -> None:
        if self.player.texture is not None:
            sdl.SDL_DestroyTexture(self.player.texture)

    def handle_event(self, event: sdl.SDL_Event) -> None:
        pass

    def keyboardControl(self) -> None:
        keyboardState = sdl.SDL_GetKeyboardState(None)

        if keyboardState[sdl.SDL_SCANCODE_W]:
            self.player.position.y -= 1
    
        if keyboardState[sdl.SDL_SCANCODE_S]:
            self.player.position.y += 1; 
        
        if keyboardState[sdl.SDL_SCANCODE_A]:
            self.player.position.x -= 1
    
        if keyboardState[sdl.SDL_SCANCODE_D]:
            self.player.position.x += 1
   
        # 限制飞机的移动范围
        if self.player.position.x < 0:
            self.player.position.x = 0
        
        if self.player.position.x > self.game.getWindowWidth() - self.player.width:
            self.player.position.x = self.game.getWindowWidth() - self.player.width
    
        if self.player.position.y < 0:
            self.player.position.y = 0
    
        if self.player.position.y > self.game.getWindowHeight() - self.player.height:
            self.player.position.y = self.game.getWindowHeight() - self.player.height
    