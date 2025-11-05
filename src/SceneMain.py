from __future__ import annotations
from typing import TYPE_CHECKING
import sdl3 as sdl
from sdl3 import SDL_image as img
from ctypes import c_float, byref
import random
import secrets  # 用于获取高质量随机种子
import math

from Logger import GameLogger as log
from Scene import Scene
from Object import Player, ProjectilePlayer, Enemy, ProjectileEnemy, Explosion

if TYPE_CHECKING:
    # 避免循环导入
    from Game import Game

class SceneMain(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        seed = secrets.randbits(64)
        self.rng = random.Random(seed)
        self.player = Player()  
        self.isDead = False    
        self.projectilePlayerTemplate = ProjectilePlayer()
        self.projectileEnemyTemplate = ProjectileEnemy()
        self.enemyTemplate = Enemy()
        self.explosionTemplate = Explosion()
        self.projectilesPlayer = []
        self.enemies = []
        self.projectilesEnemy = []
        self.explosions = []

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

        self.projectileEnemyTemplate.texture = img.IMG_LoadTexture(self.game.getRenderer(), b"D:/PyProjects/SpacePlane/assets/image/bullet-1.png")
        ok = sdl.SDL_GetTextureSize(self.projectileEnemyTemplate.texture, byref(w), byref(h))
        self.projectileEnemyTemplate.width = int(int(w.value) / 4)
        self.projectileEnemyTemplate.height = int(int(h.value) / 4)

        self.explosionTemplate.texture = img.IMG_LoadTexture(
            self.game.getRenderer(),
            b"D:/PyProjects/SpacePlane/assets/effect/explosion.png",
        )
        ok = sdl.SDL_GetTextureSize(self.explosionTemplate.texture, byref(w), byref(h))
        self.explosionTemplate.width = int(w.value)
        self.explosionTemplate.height = int(h.value)
        self.explosionTemplate.totalFrame = (
            self.explosionTemplate.width / self.explosionTemplate.height
        )
        self.explosionTemplate.width = self.explosionTemplate.height

    def update(self, deltaTime: float) -> None:
        self.keyboardControl(deltaTime)
        self.updatePlayerProjectiles(deltaTime)
        self.updateEnemyProjectiles(deltaTime)
        self.spawEnemy()
        self.updateEnemies(deltaTime)
        self.updatePlayer(deltaTime)
        self.updateExplosions(deltaTime)

    def render(self) -> None:
        # 渲染玩家子弹
        self.renderPlayerProjectiles()
        # 渲染敌机子弹
        self.renderEnemyProjectiles()

        # 渲染玩家
        if not self.isDead:            
            playerRect = sdl.SDL_FRect(self.player.position.x, self.player.position.y,
                        self.player.width, self.player.height)
            sdl.SDL_RenderTexture(self.game.getRenderer(), self.player.texture, None, playerRect)

        # 渲染敌人
        self.renderEnemies()

        # 渲染爆炸效果
        self.renderExplosions()

    def clean(self) -> None:
        if self.player.texture is not None:
            sdl.SDL_DestroyTexture(self.player.texture)

        # 清理模板
        if self.projectilePlayerTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.projectilePlayerTemplate.texture)
        if self.enemyTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.enemyTemplate.texture)
        if self.projectileEnemyTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.projectileEnemyTemplate.texture)
        if self.explosionTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.explosionTemplate.texture)

        for projectile in self.projectilesPlayer:
            if projectile.texture is not None:
                sdl.SDL_DestroyTexture(projectile.texture)
        self.projectilesPlayer.clear()

        for enemy in self.enemies:
            if enemy.texture is not None:
                sdl.SDL_DestroyTexture(enemy.texture)
        self.enemies.clear()

        for projectile in self.projectilesEnemy:
            if projectile.texture is not None:
                sdl.SDL_DestroyTexture(projectile.texture)
        self.projectilesEnemy.clear()

        for explosion in self.explosions:
            if explosion.texture is not None:
                sdl.SDL_DestroyTexture(explosion.texture)
        self.explosions.clear()

    def handle_event(self, event: sdl.SDL_Event) -> None:
        pass

    def keyboardControl(self, deltaTime: float) -> None:
        if self.isDead:
            return

        keyboardState = sdl.SDL_GetKeyboardState(None)

        if keyboardState[sdl.SDL_SCANCODE_W]:
            self.player.position.y -= deltaTime * self.player.speed

        if keyboardState[sdl.SDL_SCANCODE_S]:
            self.player.position.y += deltaTime * self.player.speed 

        if keyboardState[sdl.SDL_SCANCODE_A]:
            self.player.position.x -= deltaTime * self.player.speed

        if keyboardState[sdl.SDL_SCANCODE_D]:
            self.player.position.x += deltaTime * self.player.speed

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
                self.playerShoot()
                self.player.lastShootTime = currentTime

    def updatePlayer(self, deltaTime: float) -> None:
        if self.isDead:
            return
        if self.player.currentHealth <= 0:
            # todo Game Over
            currentTime = sdl.SDL_GetTicksNS()
            self.isDead = True
            explosion = Explosion()
            explosion.texture = self.explosionTemplate.texture
            explosion.width = self.explosionTemplate.width
            explosion.height = self.explosionTemplate.height
            explosion.totalFrame = self.explosionTemplate.totalFrame
            explosion.position.x = self.player.position.x + self.player.width / 2 - explosion.width / 2
            explosion.position.y = self.player.position.y + self.player.height / 2 - explosion.height / 2
            explosion.startTime = currentTime
            self.explosions.append(explosion)
            return

        for enemy in self.enemies:
            enemyRect = sdl.SDL_Rect(int(enemy.position.x), int(enemy.position.y), 
                                    enemy.width, enemy.height)

            playerRect = sdl.SDL_Rect(int(self.player.position.x), int(self.player.position.y), 
                                    self.player.width, self.player.height)
            # 碰撞检测成功
            if sdl.SDL_HasRectIntersection(enemyRect, playerRect):
                self.player.currentHealth -= 1
                enemy.currentHealth = 0

    def playerShoot(self) -> None:
        # 发射子弹
        projectile = ProjectilePlayer() 
        projectile.texture = self.projectilePlayerTemplate.texture
        projectile.width = self.projectilePlayerTemplate.width
        projectile.height = self.projectilePlayerTemplate.height
        projectile.speed = self.projectilePlayerTemplate.speed

        projectile.position.x = self.player.position.x + self.player.width / 2 - projectile.width / 2
        projectile.position.y = self.player.position.y
        self.projectilesPlayer.append(projectile)

    def updatePlayerProjectiles(self, deltaTime: float) -> None:
        margin = 32  # 子弹超出屏幕外边界的距离
        for i in range(len(self.projectilesPlayer) - 1, -1, -1):
            p = self.projectilesPlayer[i]
            p.position.y -= p.speed * deltaTime
            if p.position.y + margin < 0:
                self.projectilesPlayer.pop(i)
            else:
                # 检测与敌机的碰撞
                for j in range(len(self.enemies) - 1, -1, -1):
                    enemyRect = sdl.SDL_Rect(int(self.enemies[j].position.x), int(self.enemies[j].position.y), 
                                            self.enemies[j].width, self.enemies[j].height)

                    projectileRect = sdl.SDL_Rect(int(p.position.x), int(p.position.y), 
                                            p.width, p.height)
                    # 碰撞检测成功
                    if sdl.SDL_HasRectIntersection(enemyRect, projectileRect):
                        self.enemies[j].currentHealth -= p.damage
                        self.projectilesPlayer.pop(i)
                        break

    def renderPlayerProjectiles(self) -> None:
        for projectile in self.projectilesPlayer:
            projectileRect = sdl.SDL_FRect(int(projectile.position.x),int(projectile.position.y), 
                                                        projectile.width, projectile.height)
            sdl.SDL_RenderTexture(self.game.getRenderer(), projectile.texture, None, projectileRect)

    def spawEnemy(self) -> None:
        if self.rng.random() > 1 / self.game.GlobalSettings.SpawnEnemyStep:
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

    def updateEnemies(self, deltaTime: float) -> None:
        currentTime = sdl.SDL_GetTicksNS()
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]
            enemy.position.y += enemy.speed * deltaTime
            if enemy.position.y > self.game.getWindowHeight():
                self.enemies.pop(i)
            else:
                # 敌机射击
                if (currentTime - enemy.lastShootTime > enemy.coolDown) and (not self.isDead):
                    self.enemyShoot(enemy)
                    enemy.lastShootTime = currentTime

                if enemy.currentHealth <= 0:
                    self.enemyExplode(enemy)
                    self.enemies.pop(i)

    def renderEnemies(self) -> None:
        for enemy in self.enemies:
            enemyRect = sdl.SDL_FRect(int(enemy.position.x),int(enemy.position.y), 
                                                        enemy.width, enemy.height)
            sdl.SDL_RenderTexture(self.game.getRenderer(), enemy.texture, None, enemyRect)

    def updateEnemyProjectiles(self, deltaTime: float) -> None:
        margin = 32  # 子弹超出屏幕外边界的距离
        for i in range(len(self.projectilesEnemy) - 1, -1, -1):
            projectile = self.projectilesEnemy[i]
            projectile.position.x += (
                projectile.speed * projectile.direction.x * deltaTime
            )
            projectile.position.y += (
                projectile.speed * projectile.direction.y * deltaTime
            )
            if (
                (projectile.position.x > self.game.getWindowWidth() + margin)
                or (projectile.position.x < -margin)
                or (projectile.position.y < -margin)
                or (projectile.position.x > self.game.getWindowWidth() + margin)
            ):
                self.projectilesEnemy.pop(i)
            else:
                # 检测与玩家的碰撞
                projectileRect = sdl.SDL_Rect(
                    int(projectile.position.x),
                    int(projectile.position.y),
                    projectile.width,
                    projectile.height,
                )

                playerRect = sdl.SDL_Rect(
                    int(self.player.position.x),
                    int(self.player.position.y),
                    self.player.width,
                    self.player.height,
                )

                # 碰撞检测成功
                if sdl.SDL_HasRectIntersection(projectileRect, playerRect):
                    self.player.currentHealth -= projectile.damage
                    self.projectilesEnemy.pop(i)

    def renderEnemyProjectiles(self) -> None:
        for projectile in self.projectilesEnemy:
            projectileRect = sdl.SDL_FRect(int(projectile.position.x),int(projectile.position.y), 
                                                        projectile.width, projectile.height)
            angle = math.degrees(math.atan2(projectile.direction.y, projectile.direction.x)) - 90
            sdl.SDL_RenderTextureRotated(
                self.game.getRenderer(),
                projectile.texture,
                None,
                projectileRect,
                angle,
                None,
                False
            )

    def enemyShoot(self, enemy: Enemy) -> None:
        projectile = ProjectileEnemy()
        projectile.texture = self.projectileEnemyTemplate.texture
        projectile.width = self.projectileEnemyTemplate.width
        projectile.height = self.projectileEnemyTemplate.height
        projectile.speed = self.projectileEnemyTemplate.speed
        projectile.position.x = enemy.position.x + enemy.width / 2 - projectile.width / 2
        projectile.position.y = enemy.position.y + enemy.height / 2 - projectile.height / 2
        projectile.direction = self.getDirection(enemy)
        self.projectilesEnemy.append(projectile)

    def getDirection(self, enemy: Enemy) -> sdl.SDL_FPoint:
        x = (self.player.position.x + self.player.width / 2) - (enemy.position.x + enemy.width / 2)
        y = (self.player.position.y + self.player.height / 2) - (enemy.position.y + enemy.height / 2)
        length = math.sqrt(x * x + y * y)
        x /= length
        y /= length
        return sdl.SDL_FPoint(x, y)

    def enemyExplode(self, enemy: Enemy) -> None:
        currentTime = sdl.SDL_GetTicksNS()
        explosion = Explosion()
        explosion.texture = self.explosionTemplate.texture
        explosion.width = self.explosionTemplate.width
        explosion.height = self.explosionTemplate.height
        explosion.totalFrame = self.explosionTemplate.totalFrame
        explosion.position.x = enemy.position.x + enemy.width / 2 - explosion.width / 2
        explosion.position.y = (enemy.position.y + enemy.height / 2 - explosion.height / 2)
        explosion.startTime = currentTime
        self.explosions.append(explosion)

    def updateExplosions(self, deltaTime: float) -> None:
        currentTime = sdl.SDL_GetTicksNS()
        for i in range(len(self.explosions) - 1, -1, -1):
            explosion = self.explosions[i]
            explosion.currentFrame = (currentTime - explosion.startTime) * explosion.FPS / 1e9
            if explosion.currentFrame >= explosion.totalFrame:
                self.explosions.pop(i)

    def renderExplosions(self) -> None:
        for explosion in self.explosions:
            srcRect = sdl.SDL_FRect(
                int(explosion.currentFrame) * explosion.width,0,
                explosion.width,
                explosion.height
            )
            destRect = sdl.SDL_FRect(
                int(explosion.position.x),
                int(explosion.position.y),
                explosion.width,
                explosion.height,
            )
            sdl.SDL_RenderTexture(
                self.game.getRenderer(),
                explosion.texture,
                srcRect,
                destRect,
            )
