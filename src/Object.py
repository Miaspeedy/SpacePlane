from typing import Optional

import sdl3 as sdl

class Player:
    def __init__(self):
        self.texture:Optional[sdl.SDL_Texture] = None
        self.position:Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0,0)
        self.width = 0
        self.height = 0
        self.speed = 400
        self.coolDown = 0.05 * 1e9  # 0.05秒转为ns
        self.lastShootTime = 0

class ProjectilePlayer:
    def __init__(self):
        self.texture:Optional[sdl.SDL_Texture] = None
        self.position:Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0,0)
        self.width = 0
        self.height = 0
        self.speed = 600