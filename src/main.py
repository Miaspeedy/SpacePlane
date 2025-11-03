import sdl3 as sdl

def main():
    # 初始化视频子系统
    if not sdl.SDL_Init(sdl.SDL_INIT_VIDEO):
        raise SystemExit("SDL_Init failed")

    # 创建窗口(注意：标题要 bytes)
    window = sdl.SDL_CreateWindow(
        b"PySDL3 Test",
        800, 600,
        sdl.SDL_WINDOW_RESIZABLE | sdl.SDL_WINDOW_HIGH_PIXEL_DENSITY
    )
    if not window:
        sdl.SDL_Quit()
        raise SystemExit("SDL_CreateWindow failed")

    # 创建 2D 渲染器
    renderer = sdl.SDL_CreateRenderer(window, None)
    if not renderer:
        sdl.SDL_DestroyWindow(window)
        sdl.SDL_Quit()
        raise SystemExit("SDL_CreateRenderer failed")

    running = True
    event = sdl.SDL_Event()

    while running:
        # 事件轮询
        while sdl.SDL_PollEvent(event):
            if event.type == sdl.SDL_EVENT_QUIT:
                running = False

        # 清屏（深灰）
        sdl.SDL_SetRenderDrawColor(renderer, 30, 30, 40, 255)
        sdl.SDL_RenderClear(renderer)

        # 画一个浅红矩形
        rect = sdl.SDL_FRect(100.0, 100.0, 200.0, 100.0)
        sdl.SDL_SetRenderDrawColor(renderer, 200, 80, 80, 255)
        sdl.SDL_RenderRect(renderer, rect)

        # 显示到屏幕
        sdl.SDL_RenderPresent(renderer)

        # 限帧 ~60FPS
        sdl.SDL_Delay(16)

    # 清理
    sdl.SDL_DestroyRenderer(renderer)
    sdl.SDL_DestroyWindow(window)
    sdl.SDL_Quit()

if __name__ == "__main__":
    main()