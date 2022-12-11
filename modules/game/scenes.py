import pygame
from components.button import Button
from components.image import Image
from components.scene import Scene, SceneManager
from components.panel import Panel
from modules.game.logic import GameLogic, GameMode
from utils.enum_types import MouseEvent, MouseEventContext
from utils.json_reader import JsonReader
import utils.constants as constants
from utils.logger import Logger

class GameScene(Scene):
    CONFIG_FILE = "conf/game/GameScene.json"

    RES_PATH = "res/game/"

    IMAGE_SUFFIX = ".png"

    logger = Logger(__name__).getInstance()

    def __init__(self, mode: GameMode) -> None:
        self.conf = JsonReader.load(GameScene.CONFIG_FILE)

        self.logic = GameLogic(mode)
        self.mode = mode
        self.boardPanel = Panel(conf=self.conf["boardPanel"])
        self.boardPanel.addEventHandler(MouseEvent.ON_TOUCH_END, self.onBoardClick)

        self.endGamePanel: Panel = Panel(conf=self.conf["endGamePanel"])
        self.returnBtn: Button = self.endGamePanel.getChild("returnBtn")
    
        self.isRunning = True

        self.init()

    def init(self) -> None:
        self.sceneMgr = SceneManager.getInstance()

        self.returnBtn.addEventListener(MouseEvent.ON_TOUCH_END, self.onReturnClick)

        width, height = self.boardPanel.getSize()
        self.cellWidth, self.cellHeight = width // GameLogic.COLS, height // GameLogic.ROWS

    def draw(self, screen: pygame.surface.Surface) -> None:
        screen.fill(constants.BACKGROUND_COLOR)

        self.boardPanel.draw(screen)
        self.endGamePanel.draw(screen)

    def onBoardClick(self, context: MouseEventContext) -> None:
        if not self.isRunning: return

        if not self.logic.isPlayerTurn(): return

        localX, localY = self.boardPanel.getLocalPosition(context["x"], context["y"])
        col, row = localX // self.cellWidth, localY // self.cellHeight
        self.updateBoard(row, col)
            
        self.logic.changeTurn()

        if self.mode == GameMode.PVB: 
            row, col = self.logic.getBotMove()
            self.logger.info("GameScene.onBoardClick. row={} col={}".format(row, col))
            if not self.logic.isValidCell(row, col): return
            self.updateBoard(row, col)
            self.logic.changeTurn()

    def updateBoard(self, row: int, col: int) -> None:
        if not self.logic.isValidCell(row, col):
            return 
        currentTurn = self.logic.getCurrentTurn()
        self.logger.info("GameLogic.updateBoard. row={} col={} currentTurn={}".format(row, col, currentTurn))
        self.boardPanel.addChild(f"cell_{row}_{col}", Image({'x': col * self.cellWidth, 'y': row * self.cellHeight, 
            'src': f"{GameScene.RES_PATH}{currentTurn.value}{GameScene.IMAGE_SUFFIX}", 'width': self.cellWidth, 'height': self.cellHeight}))
        self.logic.setCell(self.logic.getCurrentTurn(), row, col, False)
        if self.logic.isEndGame():
            self.isRunning = False
            self.showEndGame()
            return

    def onReturnClick(self, _: MouseEventContext) -> None:
        self.sceneMgr.clear()
        from modules.lobby.scenes import StartScene
        self.sceneMgr.push(StartScene())

    def showEndGame(self) -> None: 
        lines = self.logic.getWinLines()
        for line in lines:
            self.boardPanel.getChild(f"line{line}").setVisible(True)
        self.endGamePanel.setVisible(True)