import pygame
from components.scene import Scene, SceneManager
from components.button import Button
from modules.game.logic import GameMode
from modules.game.scenes import GameScene
from utils.enum_types import MouseEvent, MouseEventContext
from utils.json_reader import JsonReader
import utils.constants as constants


class StartScene(Scene):
    CONFIG_FILE = "conf/lobby/StartScene.json"

    def __init__(self) -> None:
        self.sceneMgr = None

        self.conf = JsonReader.load(StartScene.CONFIG_FILE)

        self.startPvPBtn: Button = Button(conf=self.conf["startPvPBtn"])
        self.startPvBBtn: Button = Button(conf=self.conf["startPvBBtn"])

        self.init()

    def init(self) -> None:
        self.sceneMgr = SceneManager.getInstance()

        self.startPvPBtn.addEventListener(MouseEvent.ON_TOUCH_END, self.onStartPvPClick)
        self.startPvBBtn.addEventListener(MouseEvent.ON_TOUCH_END, self.onStartPvBClick)

    def draw(self, screen: pygame.surface.Surface) -> None:
        screen.fill(constants.BACKGROUND_COLOR)
        self.startPvBBtn.draw(screen)
        self.startPvPBtn.draw(screen)

    def onStartPvPClick(self, _: MouseEventContext) -> None:
        self.sceneMgr.push(GameScene(GameMode.PVP))

    def onStartPvBClick(self, _: MouseEventContext) -> None:
        self.sceneMgr.push(GameScene(GameMode.PVB))