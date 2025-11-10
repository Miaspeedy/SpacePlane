from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import sdl3 as sdl

from Logger import GameLogger as log
from Scene import Scene

if TYPE_CHECKING:
    # 避免循环导入
    from Game import Game

class SceneEnd(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.isTyping = True
        self.name = []

    def init(self) -> None:
        # 载入并播放背景音乐
        if sdl.SDL_TextInputActive(self.game.getWindow()) == False:
            sdl.SDL_StartTextInput(self.game.getWindow())

        if sdl.SDL_TextInputActive(self.game.getWindow()) == False:
            log.error("Failed to start text input:{}", sdl.SDL_GetError())

    def update(self, deltaTime: float) -> None:
        pass

    def render(self) -> None:
        if self.isTyping:
            self.renderPhase1()
        else:
            self.renderPhase2()

    def clean(self) -> None:
        pass

    def handle_event(self, event : sdl.SDL_Event) -> None:
        if self.isTyping:
            if event.type == sdl.SDL_EVENT_TEXT_INPUT:
                s = event.text.text.decode('utf-8') # bytes -> str
                for ch in s:
                    self.name.append(ch)              # list[str]
            if event.type == sdl.SDL_EVENT_KEY_DOWN:
                if event.key.scancode == sdl.SDL_SCANCODE_RETURN:
                    self.isTyping = False
                    sdl.SDL_StopTextInput(self.game.getWindow())
                if event.key.scancode == sdl.SDL_SCANCODE_BACKSPACE:
                    if self.name:
                        self.name.pop()

    def renderPhase1(self) -> None:
        score = self.game.getFinalScore()
        scoreText = f"Your Score is: " + str(score)  # 你的得分是:
        gameOver = f"Game Over"
        instrutionText = f"Please enter your name,"  # 请输入你的名字,
        instrutionText1 = f"and press the Enter key to confirm: "  # 按回车键确认:
        self.game.renderTextCentered(scoreText, 0.1, False)
        self.game.renderTextCentered(gameOver, 0.4, True)
        self.game.renderTextCentered(instrutionText, 0.6, False)
        self.game.renderTextCentered(instrutionText1, 0.7, False)       

        if len(self.name) != 0:
            textname = "".join(self.name)
            self.game.renderTextCentered(textname, 0.8, False)

    def renderPhase2(self) -> None:
        pass
