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
      self.currentScene: Optional[Scene] = None
      self.isRunning = True
      self.window:Optional[sdl.SDL_Window] = None
      self.renderer:Optional[sdl.SDL_Renderer] = None

    def init(self):
        #初始化 logger
        log.set_level("INFO")
        log.set_detailed(False)
        log.error("SDL_Init failed")
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
            event = sdl.SDL_Event()
            self.handleEvent(event)
            self.update()
            self.render()

    def handleEvent(self,event : sdl.SDL_Event):
        while sdl.SDL_PollEvent(event):
            if event.type == sdl.SDL_QuitEvent():
              self.isRunning = False
            self.currentScene.handle_event(event)

    def update(self):
        self.currentScene.update(1)

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


    def getrenderer(self):
        return self.renderer

    def getWindowWidth(self):
        return self.windowWidth
    
    def getWindowHeight(self):
        return self.windowHeight