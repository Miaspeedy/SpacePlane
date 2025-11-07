import sdl3 as sdl
from sdl3 import SDL_ttf as ttf
from sdl3 import SDL_mixer as mix
from typing import Optional
from ctypes import c_float, byref

from Logger import GameLogger as log
from Scene import Scene
from SceneMain import SceneMain
from Object import GlobalObject,Background

class Game:
    def __init__(self):
        self.GlobalSettings = GlobalObject()
        self.windowWidth = self.GlobalSettings.windowWidth
        self.windowHeight = self.GlobalSettings.windowHeight
        self.FPS = self.GlobalSettings.FPS
        self.frameTime = 0.0   
        self.deltaTime = 0.0  
        self.currentScene: Optional[Scene] = None
        self.isRunning = True
        self.window:Optional[sdl.SDL_Window] = None
        self.renderer:Optional[sdl.SDL_Renderer] = None
        self.mixer:Optional[sdl.MIX_Mixer] = None
        self.bgmTrack: Optional[sdl.MIX_Track] = None
        self.musicTrack: Optional[sdl.MIX_Track] = None
        self.nearStars = None
        self.farStars = None

    def init(self):
        # 初始化 logger
        log.set_level("Debug")
        log.set_detailed(False)

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
        self.renderer = sdl.SDL_CreateRenderer(self.window, b"opengl")
        if not self.renderer:
            self.isRunning = False
            log.error("SDL_CreateRenderer failed")     

        # 初始化SDL_mixer
        if not mix.MIX_Init():
            self.isRunning = False
            log.error("SDL_mixer initialization failed")

        # 选用默认播放设备 音频规格用默认值
        self.mixer = sdl.MIX_CreateMixerDevice(
            sdl.SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, None 
        )  
        if not self.mixer:
            self.isRunning = False
            log.error("SDL_mixer initialization failed")

        # 创建track
        self.bgmTrack = sdl.MIX_CreateTrack(self.mixer)
        if not self.bgmTrack:
            self.isRunning = False
            log.error("SDL_mixer could not initialize! SDL_mixer Error: {}", mix.Mix_GetError())

        self.musicTrack = sdl.MIX_CreateTrack(self.mixer)
        if not self.musicTrack:
            self.isRunning = False
            log.error("SDL_mixer could not initialize! SDL_mixer Error: {}", mix.Mix_GetError())

        # 设置整体音量
        sdl.MIX_SetMasterGain(self.mixer, 0.2)
        sdl.MIX_SetTrackGain(self.bgmTrack, 0.5)
        sdl.MIX_SetTrackGain(self.musicTrack, 0.4)

        # 初始化背景卷轴
        w = c_float()
        h = c_float()
        self.nearStars = Background()
        self.nearStars.texture = sdl.IMG_LoadTexture(self.getRenderer(),b"D:/PyProjects/SpacePlane/assets/image/Stars-A.png")
        sdl.SDL_GetTextureSize(self.nearStars.texture, byref(w), byref(h))
        self.nearStars.width = int(w.value / 2)
        self.nearStars.height = int(h.value / 2)

        self.farStars = Background()
        self.farStars.texture = sdl.IMG_LoadTexture(self.getRenderer(),b"D:/PyProjects/SpacePlane/assets/image/Stars-B.png")
        sdl.SDL_GetTextureSize(self.farStars.texture, byref(w), byref(h))
        self.farStars.width = int(w.value / 2)
        self.farStars.height = int(h.value / 2)
        self.farStars.speed = 20

        self.currentScene = SceneMain(self)
        self.currentScene.init()

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

        sdl.MIX_DestroyTrack(self.bgmTrack)
        sdl.MIX_DestroyTrack(self.musicTrack)
        sdl.MIX_DestroyMixer(self.mixer)
        sdl.MIX_Quit()

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

    def handleEvent(self,event : sdl.SDL_Event):
        while sdl.SDL_PollEvent(event):
            if event.type == sdl.SDL_EVENT_QUIT:
                self.isRunning = False
            self.currentScene.handle_event(event)

    def update(self, deltaTime : float):
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
        
