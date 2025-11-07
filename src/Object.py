from typing import Optional
from enum import Enum, auto

import sdl3 as sdl


class GlobalObject:
    def __init__(self):
        self.windowWidth = 600
        self.windowHeight = 800
        self.FPS = 60
        self.SpawnEnemyStep = 60
        self.LifeItemRate = 0.5  # 生命道具掉落概率


class Player:
    def __init__(self):
        self.texture:Optional[sdl.SDL_Texture] = None
        self.position:Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0,0)
        self.width = 0
        self.height = 0
        self.currentHealth = 3
        self.maxHealth = 3
        self.speed = 400
        self.coolDown = 0.3 * 1e9  # 0.05秒转为ns
        self.lastShootTime = 0

class ProjectilePlayer:
    def __init__(self):
        self.texture:Optional[sdl.SDL_Texture] = None
        self.position:Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0,0)
        self.width = 0
        self.height = 0
        self.speed = 600
        self.damage = 1

class Enemy:
    def __init__(self):
        self.texture:Optional[sdl.SDL_Texture] = None
        self.position:Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0,0)
        self.width = 0
        self.height = 0
        self.currentHealth = 1
        self.speed = 300
        self.coolDown = 1.0 * 1e9  # 转为ns
        self.lastShootTime = 0

class ProjectileEnemy:
    def __init__(self):
        self.texture: Optional[sdl.SDL_Texture] = None
        self.position: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.direction: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.width = 0
        self.height = 0
        self.speed = 300
        self.damage = 1

class Background:
    def __init__(self):
        self.texture: Optional[sdl.SDL_Texture] = None
        self.position: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.width = 0
        self.height = 0
        self.offset = 0
        self.speed = 100

class Explosion:
    def __init__(self):
        self.texture: Optional[sdl.SDL_Texture] = None
        self.position: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.width = 0
        self.height = 0
        self.currentFrame = 0
        self.totalFrame = 0
        self.startTime = 0
        self.FPS = 10

class ItemType(Enum):
    Life = auto()
    Shield = auto()
    Time = auto()

class Item:
    def __init__(self):
        self.texture: Optional[sdl.SDL_Texture] = None
        self.position: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.direction: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.width = 0
        self.height = 0
        self.speed = 200
        self.bounceCount = 3
        self.type: Optional[ItemType] = ItemType.Life
