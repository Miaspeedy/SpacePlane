from __future__ import annotations
from typing import TYPE_CHECKING
import sdl3 as sdl
from sdl3 import SDL_image as img
from ctypes import c_float, byref
import random
import secrets  # 用于获取高质量随机种子

from Logger import GameLogger as log
from Scene import Scene
from Object import Player, ProjectilePlayer, Enemy

if TYPE_CHECKING:
    # 避免循环导入
    from Game import Game

class SceneMain(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        seed = secrets.randbits(64)
        self.rng = random.Random(seed)
        self.player = Player()  
        self.player = Player()      
        self.projectilePlayerTemplate = ProjectilePlayer()
        self.enemyTemplate = Enemy()
        self.projectilesPlayer = []
        self.enemies = []

    def init(self) -> None:

        # todo 改为相对位置
        self.player.texture = img.IMG_LoadTexture(self.game.getRenderer(), b"D:/PyProjects/SpacePlane/assets/image/SpaceShip.png")

        if self.player.texture is None:
            log.error("Failed to load player texture: {}",sdl.SDL_GetError())
        
        w = c_float()
        h = c_float()
        ok = sdl.SDL_GetTextureSize(self.player.texture, byref(w), byref(h))
        if not ok:
            log.error("Failed to get player texture size: {}", sdl.SDL_GetError())

        self.player.width = int(int(w.value) / 4)
        self.player.height = int(int(h.value) / 4)

        self.player.position.x = self.game.getWindowWidth() / 2 - self.player.width / 2
        self.player.position.y = self.game.getWindowHeight() - self.player.height

        # 初始化模版
        self.projectilePlayerTemplate.texture = img.IMG_LoadTexture(self.game.getRenderer(), b"D:/PyProjects/SpacePlane/assets/image/laser-1.png")
        ok = sdl.SDL_GetTextureSize(self.projectilePlayerTemplate.texture, byref(w), byref(h))
        self.projectilePlayerTemplate.width = int(int(w.value) / 4)
        self.projectilePlayerTemplate.height = int(int(h.value) / 4)

        self.enemyTemplate.texture = img.IMG_LoadTexture(self.game.getRenderer(), b"D:/PyProjects/SpacePlane/assets/image/insect-2.png")
        ok = sdl.SDL_GetTextureSize(self.enemyTemplate.texture, byref(w), byref(h))
        self.enemyTemplate.width = int(int(w.value) / 4)
        self.enemyTemplate.height = int(int(h.value) / 4)

    def update(self, deltatime: float) -> None:
        self.keyboardControl(deltatime)
        self.updatePlayerProjectiles(deltatime)
        self.spawEnemy()
        self.updateEnemies(deltatime)

    def render(self) -> None:
        # 渲染玩家子弹
        self.renderPlayerProjectiles()

        #渲染玩家
        playerRect = sdl.SDL_FRect(self.player.position.x, self.player.position.y,
                        self.player.width, self.player.height)
        sdl.SDL_RenderTexture(self.game.getRenderer(), self.player.texture, None, playerRect)

        # 渲染敌人
        self.renderEnemies()

    def clean(self) -> None:
        if self.player.texture is not None:
            sdl.SDL_DestroyTexture(self.player.texture)
        
        # 清理模板
        if self.projectilePlayerTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.projectilePlayerTemplate.texture)
        if self.enemyTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.enemyTemplate.texture)

        for projectile in self.projectilesPlayer:
            if projectile.texture is not None:
                sdl.SDL_DestroyTexture(projectile.texture)
        self.projectilesPlayer.clear()

        for enemy in self.enemies:
            if enemy.texture is not None:
                sdl.SDL_DestroyTexture(enemy.texture)
        self.enemies.clear()

    def handle_event(self, event: sdl.SDL_Event) -> None:
        pass

    def keyboardControl(self, deltatime: float) -> None:
        keyboardState = sdl.SDL_GetKeyboardState(None)

        if keyboardState[sdl.SDL_SCANCODE_W]:
            self.player.position.y -= deltatime * self.player.speed
    
        if keyboardState[sdl.SDL_SCANCODE_S]:
            self.player.position.y += deltatime * self.player.speed 
        
        if keyboardState[sdl.SDL_SCANCODE_A]:
            self.player.position.x -= deltatime * self.player.speed
    
        if keyboardState[sdl.SDL_SCANCODE_D]:
            self.player.position.x += deltatime * self.player.speed
   
        # 限制飞机的移动范围
        if self.player.position.x < 0:
            self.player.position.x = 0
        
        if self.player.position.x > self.game.getWindowWidth() - self.player.width:
            self.player.position.x = self.game.getWindowWidth() - self.player.width
    
        if self.player.position.y < 0:
            self.player.position.y = 0
    
        if self.player.position.y > self.game.getWindowHeight() - self.player.height:
            self.player.position.y = self.game.getWindowHeight() - self.player.height
    
        # 控制子弹发射
        if keyboardState[sdl.SDL_SCANCODE_J]:
            currentTime = sdl.SDL_GetTicksNS()
            if currentTime - self.player.lastShootTime > self.player.coolDown:
                self.Playershoot()
                self.player.lastShootTime = currentTime
            
    def Playershoot(self) -> None:
        # 发射子弹
        projectile = ProjectilePlayer() 
        projectile.texture = self.projectilePlayerTemplate.texture
        projectile.width = self.projectilePlayerTemplate.width
        projectile.height = self.projectilePlayerTemplate.height
        projectile.speed = self.projectilePlayerTemplate.speed

        projectile.position.x = self.player.position.x + self.player.width / 2 - projectile.width / 2
        projectile.position.y = self.player.position.y
        self.projectilesPlayer.append(projectile)

    def updatePlayerProjectiles(self, deltatime: float) -> None:
        margin = 32  # 子弹超出屏幕外边界的距离
        for i in range(len(self.projectilesPlayer) - 1, -1, -1):
            p = self.projectilesPlayer[i]
            p.position.y -= p.speed * deltatime
            if p.position.y + margin < 0:
                self.projectilesPlayer.pop(i)

    def renderPlayerProjectiles(self) -> None:
        for projectile in self.projectilesPlayer:
            projectileRect = sdl.SDL_FRect(int(projectile.position.x),int(projectile.position.y), 
                                                        projectile.width, projectile.height)
            sdl.SDL_RenderTexture(self.game.getRenderer(), projectile.texture, None, projectileRect)
        

    def spawEnemy(self) -> None:
        if self.rng.random() > 1 / 60.0:
            return
        # 间隔时间随机生成敌人
        enemy = Enemy()        
        enemy.texture = self.enemyTemplate.texture
        enemy.width = self.enemyTemplate.width
        enemy.height = self.enemyTemplate.height
        enemy.speed = self.enemyTemplate.speed
        enemy.position.x = self.rng.random() * (self.game.getWindowWidth() - enemy.width)
        enemy.position.y = - enemy.height
        self.enemies.append(enemy)

    def updateEnemies(self, deltatime: float) -> None:
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]
            enemy.position.y += enemy.speed * deltatime
            if enemy.position.y > self.game.getWindowHeight():
                self.enemies.pop(i)

    def renderEnemies(self) -> None:
        for enemy in self.enemies:
            enemyRect = sdl.SDL_FRect(int(enemy.position.x),int(enemy.position.y), 
                                                        enemy.width, enemy.height)
            sdl.SDL_RenderTexture(self.game.getRenderer(), enemy.texture, None, enemyRect)