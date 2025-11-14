import sdl3 as sdl
from sdl3 import SDL_ttf as ttf
from sdl3 import SDL_mixer as mix
from typing import Optional
from ctypes import c_float, byref
from pathlib import Path

from Logger import GameLogger as log
from Scene import Scene
from SceneTitle import SceneTitle
from Object import GlobalObject,Background

class Game:
    def __init__(self):
        self.GlobalSettings = GlobalObject()
        self.windowWidth = self.GlobalSettings.windowWidth
        self.windowHeight = self.GlobalSettings.windowHeight
        self.FPS = self.GlobalSettings.FPS
        self.Version = self.GlobalSettings.Version
        self.frameTime = 0.0   
        self.deltaTime = 0.0  
        self.finalScore: Optional[int] = 0
        self.currentScene: Optional[Scene] = None
        self.isRunning = True
        self.isPause = False
        self.isFullScreen = False
        self.currentLanguage = "zh"
        self.window:Optional[sdl.SDL_Window] = None
        self.renderer:Optional[sdl.SDL_Renderer] = None
        self.mixer:Optional[sdl.MIX_Mixer] = None
        self.bgmTrack: Optional[sdl.MIX_Track] = None
        self.musicTrack: Optional[sdl.MIX_Track] = None
        self.nearStars = None
        self.farStars = None
        self.titleFont: Optional[sdl.TTF_Font] = None
        self.textFont: Optional[sdl.TTF_Font] = None
        self.leaderBoard = {}
        self.language = ["en","zh"]
        self.localizeLib = {}

    def init(self):
        # 初始化 logger
        log.set_level("Debug")
        log.set_detailed(False)

        # 初始化本地化
        self.initLocalizer()

        self.frameTime = 1000000000.0 / self.FPS

        # 初始化视频子系统
        if not sdl.SDL_Init(sdl.SDL_INIT_VIDEO):
            log.error("SDL_Init failed")

        # 创建窗口
        self.window = sdl.SDL_CreateWindow(b"Space Plane",self.windowWidth, self.windowHeight, 
                                      sdl.SDL_WINDOW_RESIZABLE | sdl.SDL_WINDOW_HIGH_PIXEL_DENSITY)
        if not self.window:
            self.isRunning = False
            log.error("SDL_CreateWindow failed")

        # 创建 2D 渲染器
        self.renderer = sdl.SDL_CreateRenderer(self.window, None)
        if not self.renderer:
            self.isRunning = False
            log.error("SDL_CreateRenderer failed")     

        # 设置逻辑分辨率 不管屏幕分辨率 不管屏幕大小
        sdl.SDL_SetRenderLogicalPresentation(self.getRenderer(),self.windowWidth,self.windowHeight,
                                             sdl.SDL_LOGICAL_PRESENTATION_INTEGER_SCALE)

        # 初始化SDL_mixer
        if not mix.MIX_Init():
            self.isRunning = False
            log.error("SDL_mixer initialization failed")

        # 选用默认播放设备 音频规格用默认值
        self.mixer = sdl.MIX_CreateMixerDevice(sdl.SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, None)  
        if not self.mixer:
            self.isRunning = False
            log.error("SDL_mixer initialization failed")

        # 创建track
        self.bgmTrack = sdl.MIX_CreateTrack(self.mixer)
        if not self.bgmTrack:
            self.isRunning = False
            log.error("SDL_mixer could not initialize! SDL_mixer Error: {}", sdl.SDL_GetError())

        self.musicTrack = sdl.MIX_CreateTrack(self.mixer)
        if not self.musicTrack:
            self.isRunning = False
            log.error("SDL_mixer could not initialize! SDL_mixer Error: {}", sdl.SDL_GetError())

        # 设置整体音量
        sdl.MIX_SetMasterGain(self.mixer, 0.2)
        sdl.MIX_SetTrackGain(self.bgmTrack, 0.5)
        sdl.MIX_SetTrackGain(self.musicTrack, 0.4)

        # 初始化SDL_ttf
        if ttf.TTF_Init() == -1:
            self.isRunning = False
            log.error("SDL_ttf could not initialize! SDL_ttf Error: {}", sdl.SDL_GetError())

        # 初始化背景卷轴
        w = c_float()
        h = c_float()
        self.nearStars = Background()
        self.nearStars.texture = sdl.IMG_LoadTexture(self.getRenderer(),self.to_abs_path("assets/image/Stars-A.png").encode())
        if self.nearStars.texture is None:
            self.isRunning = False
            log.error("SDL_image could not initialize! SDL_image Error:: {}", sdl.SDL_GetError())

        sdl.SDL_GetTextureSize(self.nearStars.texture, byref(w), byref(h))
        self.nearStars.width = int(w.value / 2)
        self.nearStars.height = int(h.value / 2)

        self.farStars = Background()
        self.farStars.texture = sdl.IMG_LoadTexture(self.getRenderer(),self.to_abs_path("assets/image/Stars-B.png").encode())
        if self.farStars.texture is None:
            self.isRunning = False
            log.error("SDL_image could not initialize! SDL_image Error:: {}", sdl.SDL_GetError())

        sdl.SDL_GetTextureSize(self.farStars.texture, byref(w), byref(h))
        self.farStars.width = int(w.value / 2)
        self.farStars.height = int(h.value / 2)
        self.farStars.speed = 20

        # 载入标题场景字体
        self.titleFont = ttf.TTF_OpenFont(self.to_abs_path("assets/font/VonwaonBitmap-16px.ttf").encode(), 64)
        self.textFont = ttf.TTF_OpenFont(self.to_abs_path("assets/font/VonwaonBitmap-16px.ttf").encode(), 32)
        if self.titleFont is None or self.textFont is None:
            self.isRunning = False
            log.error("SDL_ttf could not initialize! SDL_ttf Error:: {}", sdl.SDL_GetError())        

        self.currentScene = SceneTitle(self)
        self.currentScene.init()

        self.loadData()

    def clean(self):
        if self.currentScene is not None:
            self.currentScene.clean()
            self.currentScene = None

        if self.nearStars is not None:
            sdl.SDL_DestroyTexture(self.nearStars.texture)
            self.nearStars = None
        if self.farStars is not None:
            sdl.SDL_DestroyTexture(self.farStars.texture)
            self.farStars = None

        if self.titleFont is not None:
            ttf.TTF_CloseFont(self.titleFont)

        if self.textFont is not None:
            ttf.TTF_CloseFont(self.textFont)

        sdl.MIX_DestroyTrack(self.bgmTrack)
        sdl.MIX_DestroyTrack(self.musicTrack)
        sdl.MIX_DestroyMixer(self.mixer)
        sdl.MIX_Quit()

        sdl.TTF_Quit()

        sdl.SDL_DestroyRenderer(self.renderer)
        sdl.SDL_DestroyWindow(self.window)
        sdl.SDL_Quit()

    def run(self):
        while self.isRunning:
            frameStart = sdl.SDL_GetTicksNS()
            event = sdl.SDL_Event()
            self.handleEvent(event)
            self.update(self.deltaTime)
            self.render()
            frameEnd = sdl.SDL_GetTicksNS()
            diff = frameEnd - frameStart  # nanoseconds
            if diff < self.frameTime:
                # 需要睡眠剩余时间以控制帧率，计算为毫秒并使用 SDL_Delay
                sleep_ns = int(self.frameTime - diff)
                sleep_ms = int(sleep_ns / 1000000)
                if sleep_ms > 0:
                    sdl.SDL_Delay(sleep_ms)     
                # 使用目标帧时间作为 delta（秒）
                self.deltaTime = self.frameTime / 1.0e9
            else:
                # 使用实际耗时（秒）
                self.deltaTime = diff / 1.0e9

            # 保护性约束：防止 deltaTime 为 0 或异常巨大
            if self.deltaTime <= 0:
                self.deltaTime = 1.0 / self.FPS
            max_dt = 0.5
            if self.deltaTime > max_dt:
                self.deltaTime = max_dt

            # log.debug("FPS: {} ", 1 / self.deltaTime)
        self.saveData()

    def handleEvent(self,event : sdl.SDL_Event):
        while sdl.SDL_PollEvent(event):
            if event.type == sdl.SDL_EVENT_QUIT:
                self.isRunning = False
            if event.type == sdl.SDL_EVENT_KEY_DOWN:
                if event.key.scancode == sdl.SDL_SCANCODE_F11:
                    self.isFullScreen = not self.isFullScreen
                    if self.isFullScreen:
                        sdl.SDL_SetWindowFullscreen(self.window, sdl.SDL_WINDOW_FULLSCREEN)
                    else:
                        sdl.SDL_SetWindowFullscreen(self.window, 0)
            self.currentScene.handle_event(event)

    def update(self, deltaTime : float):
        if self.isPause:
            deltaTime = 0.0

        self.backgroundUpdate(deltaTime)
        self.currentScene.update(deltaTime)

    def render(self):
        sdl.SDL_RenderClear(self.renderer)
        self.renderBackground()    
        self.currentScene.render()
        sdl.SDL_RenderPresent(self.renderer)

    def changeScene(self, scene):
        if self.currentScene is scene:
            return
        if self.currentScene is not None:
            self.currentScene.clean()
        self.currentScene = scene
        if self.currentScene is not None:
            self.currentScene.init()

    def getRenderer(self):
        return self.renderer

    def getWindow(self):
        return self.window

    def getWindowWidth(self):
        return self.windowWidth

    def getWindowHeight(self):
        return self.windowHeight

    def getMixer(self):
        return self.mixer

    def getBGMTrack(self):
        return self.bgmTrack

    def getMusicTrack(self):
        return self.musicTrack

    def setFinalScore(self, score: int):
        self.finalScore = score

    def getFinalScore(self) -> int:
        return self.finalScore

    def getLeaderBoard(self):
        return self.leaderBoard

    def togglePause(self):
        self.isPause = not self.isPause

    def getCurrentLanguage(self):
        return self.currentLanguage

    def switchLanguage(self):
        try:
            i = self.language.index(self.currentLanguage)
            self.currentLanguage = self.language[(i + 1) % len(self.language)]
        except ValueError:
            return

    def backgroundUpdate(self, deltaTime : float):
        self.nearStars.offset += self.nearStars.speed * deltaTime
        if self.nearStars.offset >= 0:  
            self.nearStars.offset -= self.nearStars.height

        self.farStars.offset += self.farStars.speed * deltaTime
        if self.farStars.offset >= 0:
            self.farStars.offset -= self.farStars.height

    def renderBackground(self):
        # 渲染远处的星星
        for posY in range(int(self.farStars.offset), self.getWindowHeight(), int(self.farStars.height)):
            for posX in range(0, self.getWindowWidth(), int(self.farStars.width)):
                dstRect = sdl.SDL_FRect(posX, posY, self.farStars.width, self.farStars.height)
                sdl.SDL_RenderTexture(self.getRenderer(), self.farStars.texture, None, dstRect)

        # 渲染近处的星星
        for posY in range(int(self.nearStars.offset), self.getWindowHeight(), int(self.nearStars.height)):
            for posX in range(0, self.getWindowWidth(), int(self.nearStars.width)):
                dstRect = sdl.SDL_FRect(posX, posY, self.nearStars.width, self.nearStars.height)
                sdl.SDL_RenderTexture(self.getRenderer(), self.nearStars.texture, None, dstRect)      

    def renderTextCentered(self, text:str, posY:float, isTitle: bool):
        color = sdl.SDL_Color(255, 255, 255, 255)
        surface = None
        if isTitle:
            surface = ttf.TTF_RenderText_Solid(self.titleFont, text.encode("utf-8"), len(text.encode("utf-8")), color)
        else:
            surface = ttf.TTF_RenderText_Solid(self.textFont, text.encode("utf-8"), len(text.encode("utf-8")), color)

        surfaceRect = sdl.SDL_Rect()
        sdl.SDL_GetSurfaceClipRect(surface, surfaceRect)
        texture = sdl.SDL_CreateTextureFromSurface(self.getRenderer(), surface)
        y = int((self.getWindowHeight() - surfaceRect.h) * posY)
        scoreRect = sdl.SDL_FRect(self.getWindowWidth() / 2 - surfaceRect.w / 2, y, surfaceRect.w,surfaceRect.h)
        sdl.SDL_RenderTexture(self.getRenderer(), texture, None, scoreRect)
        sdl.SDL_DestroySurface(surface)
        sdl.SDL_DestroyTexture(texture)
        return sdl.SDL_Point(int(scoreRect.x) + int(scoreRect.w), y)

    def renderTextPos(self, text: str, posX: int, posY: int, isLeft: bool):  
        color = sdl.SDL_Color(255, 255, 255, 255)
        surface = ttf.TTF_RenderText_Solid(self.textFont, text.encode("utf-8"), len(text.encode("utf-8")), color)
        texture = sdl.SDL_CreateTextureFromSurface(self.getRenderer(), surface)
        surfaceRect = sdl.SDL_Rect()
        sdl.SDL_GetSurfaceClipRect(surface, surfaceRect)   
        finalRect = sdl.SDL_FRect()
        if isLeft:           
            finalRect = sdl.SDL_FRect(posX, posY, surfaceRect.w, surfaceRect.h)
        else:
            finalRect = sdl.SDL_FRect(self.getWindowWidth() - posX - surfaceRect.w, posY, surfaceRect.w, surfaceRect.h)

        sdl.SDL_RenderTexture(self.getRenderer(), texture, None, finalRect)
        sdl.SDL_DestroySurface(surface)
        sdl.SDL_DestroyTexture(texture)

    def renderTextAtPercent(self, text: str, fontSize: float, posX: float, posY: float, isLeft: bool, isTitle: bool = False):
        """
        posX, posY 使用百分比: 0.0~1.0(左上为 0,0;右下为 1,1)
        isLeft=True  → 以左侧为基准; x = W*posX
        isLeft=False → 以右侧为基准;x = W*(1-posX) - text_w
        """
        color = sdl.SDL_Color(255, 255, 255, 255)
        b = text.encode("utf-8")
        Orisize = ttf.TTF_GetFontSize(self.textFont)
        ttf.TTF_SetFontSize(self.textFont, fontSize * Orisize)

        surface = (ttf.TTF_RenderText_Solid(self.titleFont if isTitle else self.textFont, b, len(b), color))
        surfaceRect = sdl.SDL_Rect()
        sdl.SDL_GetSurfaceClipRect(surface, surfaceRect)
        texture = sdl.SDL_CreateTextureFromSurface(self.getRenderer(), surface)

        W = float(self.getWindowWidth())
        H = float(self.getWindowHeight())

        # 百分比 → 像素
        y = H * float(posY)
        if isLeft:
            x = W * float(posX)
        else:
            x = W * (1.0 - float(posX)) - float(surfaceRect.w)

        dst = sdl.SDL_FRect(float(int(x)), float(int(y)),
                            float(surfaceRect.w), float(surfaceRect.h))
        sdl.SDL_RenderTexture(self.getRenderer(), texture, None, dst)

        sdl.SDL_DestroySurface(surface)
        sdl.SDL_DestroyTexture(texture)
        ttf.TTF_SetFontSize(self.textFont, Orisize)

    def insertLeaderBoard(self, score: int, name: str):
        self.leaderBoard[score] = name
        if len(self.leaderBoard) > 8:
            self.leaderBoard.pop()

    def saveData(self):
        path = self._save_path("save.dat")
        try:
            with path.open("w", encoding="utf-8", newline="\n") as f:
                for score, name in sorted(self.leaderBoard.items()):
                    f.write(f"{score} {name}\n")
        except OSError as e:
            log.error("[saveData] Failed to open save file: {}", e)

    def loadData(self):
        path = self._save_path("save.dat")  
        if not path.exists():
            log.info("[loadData] Failed to open save file")
            return

        self.leaderBoard.clear()
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(maxsplit=1)
                    if len(parts) != 2:
                        continue
                    score_str, name = parts
                    try:
                        score = int(score_str)
                    except ValueError:
                        continue

                    if score not in self.leaderBoard:
                        self.leaderBoard[score] = name
        except OSError as e:
            log.error("[loadData] Failed to read save file: {}",e)

    def to_abs_path(self, rel_path: str) -> str:
        # 把相对路径转为绝对路径(基于当前源码文件所在目录)
        # 若传入本就是绝对路径，则直接返回标准化后的绝对路径
        import sys
        p = Path(rel_path)
        if p.is_absolute():
            return str(p.resolve())

        # 冻结态(PyInstaller)
        if getattr(sys, "frozen", False):
            base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        else:
            # 开发态：Game.py 在 src/<pkg>/ 里，资源在项目根的 assets/
            base = Path(__file__).resolve().parent.parent

        return str((base / p).resolve())

    def _app_dir(self):
        # 返回 EXE 所在目录 开发态则返回项目根(src 的上一层)
        import sys

        if getattr(sys, "frozen", False):
            return Path(sys.executable).parent
        # Game.py 位于 src/<pkg>/Game.py，上一层是 src，再上一层是项目根
        return Path(__file__).resolve().parent.parent

    def _save_path(self, filename="save.dat"):
        p = self._app_dir() / filename
        # 确保目录存在
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def initLocalizer(self):
        self.localizeLib.clear()
        self.localizeLib["gameName"] = {"zh":"太空战机","en":"Space Plane"}
        self.localizeLib["titleStart"] = {"zh": "按 空格 键开始游戏","en":"Press SPACE key to Start Game"}
        self.localizeLib["titleChangeLang"] = {"zh": "按 TAB 键切换语言","en":"Press TAB key to change Language"}
        self.localizeLib["endScore"] = {"zh": "你的得分是: ", "en": "Your Score is: "}
        self.localizeLib["gameOver"] = {"zh": "游戏结束", "en": "Game Over"}
        self.localizeLib["inputName"] = {"zh": "请输入你的名字", "en": "Please enter your name,"}
        self.localizeLib["ensureName"] = {"zh": "并按回车键确认:", "en": "and press the Enter key to confirm: "}
        self.localizeLib["scoreList"] = {"zh": "得分榜", "en": "Score List"}
        self.localizeLib["restartGame"] = {"zh": "按 J 键重新开始游戏", "en": "Press the J key to restart game"}
        self.localizeLib["score"] = {"zh": "得分: ", "en": "Score: "}
        self.localizeLib["pause"] = {"zh": "已暂停", "en": "Pause"}
        self.localizeLib["pauseMove"] = {"zh": "移动: WASD", "en": "Move: WASD"}
        self.localizeLib["pauseAttack"] = {"zh": "射击: J", "en": "Shoot: J"}
        self.localizeLib["pauseShield"] = {"zh": "使用护盾: K", "en": "Use Shield: K"}
        self.localizeLib["pauseInvincible"] = {"zh": "使用无敌: L", "en": "Invincible: L"}
        self.localizeLib["pausePause"] = {"zh": "暂停: P", "en": "Pause: P"}
        self.localizeLib["version"] = {"zh": "版本: ", "en": "Version: "}
        self.localizeLib["fullScreen"] = {"zh": "全屏: F11", "en": "Fullscreen: F11"}

    def localizer(self, key:str) -> str:
        enter = self.localizeLib.get(key)
        if not enter:
            return key

        return self.localizeLib[key][self.currentLanguage]
