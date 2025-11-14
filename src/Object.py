from typing import Optional
from enum import Enum, auto

import sdl3 as sdl


class GlobalObject:
    def __init__(self):
        self.windowWidth = 600
        self.windowHeight = 800
        self.FPS = 60
        self.Version = "0.1.0"
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
        self.shield = 0
        self.isShielded = False
        self.shieldTime = 5.0 * 1e9
        self.shieldCurrentTime = self.shieldTime
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

    @classmethod
    def from_ProjectilePlayer(cls, src: "ProjectilePlayer") -> "ProjectilePlayer":
        e = cls()
        e.texture = src.texture
        e.position = (sdl.SDL_FPoint(src.position.x, src.position.y)
                      if src.position is not None else None)
        e.width = src.width
        e.height = src.height
        e.speed = src.speed
        e.damage = src.damage
        return e

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

    @classmethod
    def from_Enemy(cls, src: "Enemy") -> "Enemy":
        e = cls()
        e.texture = src.texture
        e.position = (sdl.SDL_FPoint(src.position.x, src.position.y)
                      if src.position is not None else None)
        e.width = src.width
        e.height = src.height
        e.currentHealth = src.currentHealth
        e.speed = src.speed
        e.coolDown = src.coolDown
        e.lastShootTime = src.lastShootTime
        return e


class ProjectileEnemy:
    def __init__(self):
        self.texture: Optional[sdl.SDL_Texture] = None
        self.position: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.direction: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.width = 0
        self.height = 0
        self.speed = 300
        self.damage = 1

    @classmethod
    def from_ProjectileEnemy(cls, src: "ProjectileEnemy") -> "ProjectileEnemy":
        e = cls()
        e.texture = src.texture
        e.position = (sdl.SDL_FPoint(src.position.x, src.position.y)
                      if src.position is not None else None)
        e.width = src.width
        e.height = src.height
        e.speed = src.speed
        e.damage = src.damage
        return e


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

    @classmethod
    def from_Explosion(cls, src: "Explosion") -> "Explosion":
        e = cls()
        e.texture = src.texture
        e.position = (sdl.SDL_FPoint(src.position.x, src.position.y)
                      if src.position is not None else None)
        e.width = src.width
        e.height = src.height
        e.currentFrame = src.currentFrame
        e.totalFrame = src.totalFrame
        e.startTime = src.startTime
        e.FPS = src.FPS
        return e


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

    @classmethod
    def from_Item(cls, src: "Item") -> "Item":
        e = cls()
        e.texture = src.texture
        e.position = (sdl.SDL_FPoint(src.position.x, src.position.y)
                      if src.position is not None else None)
        e.direction = (sdl.SDL_FPoint(src.direction.x, src.direction.y)
                      if src.direction is not None else None)
        e.width = src.width
        e.height = src.height
        e.speed = src.speed
        e.bounceCount = src.bounceCount
        e.type = src.type
        return e

class Shield:
    def __init__(self):
        self.texture: Optional[sdl.SDL_Texture] = None
        self.position: Optional[sdl.SDL_FPoint] = sdl.SDL_FPoint(0, 0)
        self.width = 0
        self.height = 0
