from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import sdl3 as sdl
from sdl3 import SDL_image as img
from sdl3 import SDL_mixer as mix
from sdl3 import SDL_ttf as ttf
from ctypes import c_float, byref
import random
import secrets  # 用于获取高质量随机种子
import math

from Logger import GameLogger as log
from Scene import Scene
from Object import Player, ProjectilePlayer, Enemy, ProjectileEnemy, Explosion, ItemType, Item

if TYPE_CHECKING:
    # 避免循环导入
    from Game import Game

class SceneMain(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        seed = secrets.randbits(64)
        self.rng = random.Random(seed)
        self.uiHealth = None
        self.scoreFont = None
        self.score:Optional[int] = 0
        self.player = Player()  
        self.isDead = False    
        self.projectilePlayerTemplate = ProjectilePlayer()
        self.projectileEnemyTemplate = ProjectileEnemy()
        self.enemyTemplate = Enemy()
        self.explosionTemplate = Explosion()
        self.itemLifeTemplate = Item()
        self.projectilesPlayer = []
        self.enemies = []
        self.projectilesEnemy = []
        self.explosions = []
        self.items = []
        self.sounds = {}

    def init(self) -> None:

        # 读取音频文件
        self.initMusic()

        # 播放背景音乐
        self.playSoundByName("bgm")

        # 初始化UI
        self.uiHealth = img.IMG_LoadTexture(
            self.game.getRenderer(),
            b"D:/PyProjects/SpacePlane/assets/image/Health_UI_Black.png",
        )

        # 载入字体
        self.scoreFont = ttf.TTF_OpenFont(b"D:/PyProjects/SpacePlane/assets/font/VonwaonBitmap-12px.ttf", 24)

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

        self.itemLifeTemplate.texture = sdl.IMG_LoadTexture(
            self.game.getRenderer(),
            b"D:/PyProjects/SpacePlane/assets/image/bonus_life.png",
        )
        ok = sdl.SDL_GetTextureSize(self.itemLifeTemplate.texture, byref(w), byref(h))
        self.itemLifeTemplate.width = int(w.value / 4)
        self.itemLifeTemplate.height = int(h.value / 4)

    def update(self, deltaTime: float) -> None:
        self.keyboardControl(deltaTime)
        self.updatePlayerProjectiles(deltaTime)
        self.updateEnemyProjectiles(deltaTime)
        self.spawEnemy()
        self.updateEnemies(deltaTime)
        self.updatePlayer(deltaTime)
        self.updateExplosions(deltaTime)
        self.updateItems(deltaTime)

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

        # 渲染物品
        self.renderItems()

        # 渲染爆炸效果
        self.renderExplosions()

        # 渲染UI
        self.renderUI()

    def clean(self) -> None:
        if self.player.texture is not None:
            sdl.SDL_DestroyTexture(self.player.texture)

        if self.uiHealth is not None:
            sdl.SDL_DestroyTexture(self.uiHealth)

        if self.scoreFont is not None:
            ttf.TTF_CloseFont(self.scoreFont)

        # 清理模板
        if self.projectilePlayerTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.projectilePlayerTemplate.texture)
        if self.enemyTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.enemyTemplate.texture)
        if self.projectileEnemyTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.projectileEnemyTemplate.texture)
        if self.explosionTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.explosionTemplate.texture)
        if self.itemLifeTemplate.texture is not None:
            sdl.SDL_DestroyTexture(self.itemLifeTemplate.texture)

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

        for item in self.items:
            if item.texture is not None:
                sdl.SDL_DestroyTexture(item.texture)
        self.items.clear()

        for sound in self.sounds.values():
            mix.MIX_DestroyAudio(sound)
        self.sounds.clear()

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
            self.playSoundByName("player_explode")
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
        self.playSoundByName("player_shoot")

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
                        self.playSoundByName("hit")
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
                    self.playSoundByName("hit")

    def renderEnemyProjectiles(self) -> None:
        for projectile in self.projectilesEnemy:
            projectileRect = sdl.SDL_FRect(int(projectile.position.x),int(projectile.position.y), 
                                                        projectile.width, projectile.height)
            angle = math.degrees(math.atan2(projectile.direction.y, projectile.direction.x)) - 90
            sdl.SDL_RenderTextureRotated(self.game.getRenderer(),projectile.texture,
                None,projectileRect,angle,None,False)

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
        self.playSoundByName("enemy_shoot")

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

        self.score += 10

        self.playSoundByName("enemy_explode")

        # 随机生成物品
        if self.rng.random() < self.game.GlobalSettings.LifeItemRate:
            self.dropItem(enemy)

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

    def dropItem(self, enemy: Enemy) -> None:
        item = Item()
        item.texture = self.itemLifeTemplate.texture
        item.width = self.itemLifeTemplate.width
        item.height = self.itemLifeTemplate.height
        item.speed = self.itemLifeTemplate.speed
        item.position.x = enemy.position.x + enemy.width / 2 - item.width / 2
        item.position.y = enemy.position.y + enemy.height / 2 - item.height / 2
        angle = self.rng.random() * 2.0 * math.pi
        item.direction.x = math.cos(angle)
        item.direction.y = math.sin(angle)
        self.items.append(item)

    def updateItems(self, deltaTime: float) -> None:
        for i in range(len(self.items) - 1, -1, -1):
            item = self.items[i]
            # 更新位置
            item.position.x += item.speed * item.direction.x * deltaTime
            item.position.y += item.speed * item.direction.y * deltaTime

            # 处理屏幕边缘反弹
            if item.position.x < 0 and item.bounceCount > 0:
                item.direction.x = -item.direction.x
                item.bounceCount -= 1

            if item.position.x + item.width > self.game.getWindowWidth() and item.bounceCount > 0:
                item.direction.x = -item.direction.x
                item.bounceCount -= 1

            if item.position.y < 0 and item.bounceCount > 0:
                item.direction.y = -item.direction.y
                item.bounceCount -= 1

            if item.position.y + item.height > self.game.getWindowHeight() and item.bounceCount > 0:
                item.direction.y = -item.direction.y
                item.bounceCount -= 1

            # 超出屏幕范围则删除
            if (item.position.x + item.width < 0) or (item.position.x > self.game.getWindowWidth()) or \
               (item.position.y + item.height < 0) or (item.position.y > self.game.getWindowHeight()):
                self.items.pop(i)
            else:
                # 检测与玩家的碰撞
                itemRect = sdl.SDL_Rect(int(item.position.x),int(item.position.y),
                    item.width,item.height)

                playerRect = sdl.SDL_Rect(
                    int(self.player.position.x),
                    int(self.player.position.y),
                    self.player.width,
                    self.player.height,
                )

                # 碰撞检测成功
                if sdl.SDL_HasRectIntersection(itemRect, playerRect) and (not self.isDead):
                    self.playerGetItem(item)
                    self.items.pop(i)
                    self.playSoundByName("get_item")

    def playerGetItem(self, item: Item) -> None:
        self.score += 5
        if item.type == ItemType.Life:
            self.player.currentHealth += 1
            if self.player.currentHealth > self.player.maxHealth:
                self.player.currentHealth = self.player.maxHealth

    def renderItems(self) -> None:
        for item in self.items:
            itemRect = sdl.SDL_FRect(int(item.position.x),int(item.position.y), 
                                                        item.width, item.height)
            sdl.SDL_RenderTexture(self.game.getRenderer(), item.texture, None, itemRect)

    def initMusic(self) -> None:
        self.sounds["bgm"] = sdl.MIX_LoadAudio(self.game.getMixer(), 
                                                f"D:/PyProjects/SpacePlane/assets/music/03_Racing_Through_Asteroids_Loop.ogg".encode(),False)
        self.sounds["player_shoot"] = sdl.MIX_LoadAudio( self.game.getMixer(), 
                                                b"D:/PyProjects/SpacePlane/assets/sound/laser_shoot4.wav",False)
        self.sounds["enemy_shoot"] = sdl.MIX_LoadAudio( self.game.getMixer(), 
                                                b"D:/PyProjects/SpacePlane/assets/sound/xs_laser.wav",False)
        self.sounds["player_explode"] = sdl.MIX_LoadAudio(self.game.getMixer(),
                                                b"D:/PyProjects/SpacePlane/assets/sound/explosion1.wav",False)
        self.sounds["enemy_explode"] = sdl.MIX_LoadAudio(self.game.getMixer(),
                                                b"D:/PyProjects/SpacePlane/assets/sound/explosion3.wav",False)
        self.sounds["hit"] = sdl.MIX_LoadAudio( self.game.getMixer(), 
                                                b"D:/PyProjects/SpacePlane/assets/sound/eff11.wav",False)
        self.sounds["get_item"] = sdl.MIX_LoadAudio( self.game.getMixer(), 
                                                b"D:/PyProjects/SpacePlane/assets/sound/eff5.wav",False)

    def playSoundByName(self, name: str) -> None:
        if name not in self.sounds:
            log.error("Sound {} not found!", name)
            return

        sound = self.sounds[name]
        if name == "bgm":
            props = sdl.SDL_CreateProperties()
            ok = sdl.SDL_SetNumberProperty(props, mix.MIX_PROP_PLAY_LOOPS_NUMBER, -1) # 无限循环
            if not ok:
                log.error("Failed to set property for sound {}: {}", name, sdl.SDL_GetError())

            mix.MIX_SetTrackAudio(self.game.getBGMTrack(), sound)
            isPlayBack = sdl.MIX_PlayTrack(self.game.getBGMTrack(), props)
            if not isPlayBack:
                log.error("Failed to play sound {}: {}", name, sdl.SDL_GetError())

        else:
            mix.MIX_SetTrackAudio(self.game.getMusicTrack(), sound)
            isPlayBack = sdl.MIX_PlayTrack(self.game.getMusicTrack(), 0)
            if not isPlayBack:
                log.error("Failed to play sound {}: {}", name, sdl.SDL_GetError())

    def renderUI(self) -> None:
        # 渲染血量
        x = 10
        y = 10
        size = 32
        offset = 40
        sdl.SDL_SetTextureColorMod(self.uiHealth, 100, 100, 100) #颜色减淡
        for i in range(self.player.maxHealth):        
            BackRect = sdl.SDL_FRect(x + i * offset, y, size, size)
            sdl.SDL_RenderTexture(self.game.getRenderer(), self.uiHealth, None, BackRect)

        sdl.SDL_SetTextureColorMod(self.uiHealth, 255, 255, 255) #当前剩余血量
        for i in range(self.player.currentHealth): 
            currentRect = sdl.SDL_FRect(x + i * offset, y, size, size)
            sdl.SDL_RenderTexture(self.game.getRenderer(), self.uiHealth, None, currentRect)

        # 渲染分数
        text = f"Score: {self.score}"
        scoreColor = sdl.SDL_Color(255, 255, 255, 255)
        surface = ttf.TTF_RenderText_Solid(self.scoreFont, text.encode("utf-8"),len(text.encode("utf-8")), scoreColor)
        surfaceRect = sdl.SDL_Rect()
        sdl.SDL_GetSurfaceClipRect(surface,surfaceRect)
        scoreTexture = sdl.SDL_CreateTextureFromSurface(self.game.getRenderer(), surface)
        scoreRect = sdl.SDL_FRect(
            self.game.getWindowWidth() - 10 - surfaceRect.w, 10,
            surfaceRect.w,surfaceRect.h)
        sdl.SDL_RenderTexture(self.game.getRenderer(), scoreTexture, None, scoreRect)
        sdl.SDL_DestroySurface(surface)
        sdl.SDL_DestroyTexture(scoreTexture)
