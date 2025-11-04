import sdl3 as sdl
from sdl3 import SDL_image as img
from typing import Optional

from Logger import GameLogger as log
from Scene import Scene
from SceneMain import SceneMain


class Game:
    def __init__(self):
      self.windowWidth = 600
      self.windowHeight = 800
      self.FPS = 60
      self.frameTime = 0.0   
      self.deltaTime = 0.0  
      self.currentScene: Optional[Scene] = None
      self.isRunning = True
      self.window:Optional[sdl.SDL_Window] = None
      self.renderer:Optional[sdl.SDL_Renderer] = None

    def init(self):
        #初始化 logger
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

        self.currentScene = SceneMain(self)
        self.currentScene.init()
        

    def clean(self):
        if self.currentScene is not None:
          self.currentScene.clean()
          self.currentScene = None
        
        
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

            #log.debug("FPS: {} ", 1 / self.deltaTime)
        
    def handleEvent(self,event : sdl.SDL_Event):
        while sdl.SDL_PollEvent(event):
            if event.type == sdl.SDL_EVENT_QUIT:
              self.isRunning = False
            self.currentScene.handle_event(event)

    def update(self, deltaTime : float):
        self.currentScene.update(deltaTime)

    def render(self):
        sdl.SDL_RenderClear(self.renderer)
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