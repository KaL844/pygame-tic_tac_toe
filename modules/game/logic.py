from enum import Enum

from utils.logger import Logger


class GameMode(Enum):
    PVP = 0
    PVB = 1

class GameCellType(Enum):
    X = 'x'
    O = 'o'
    NULL = ''
    
class GameLogic:
    ROWS = 3
    COLS = 3
    START_PLAYER = GameCellType.X
    BOT_PLAYER = GameCellType.O

    WIN_SCORE = 3
    MAX_MOVE = 9
    NUM_WIN_POSSIBILITY = 8

    SCORE_DIAGNONAL_1_INDEX = 6
    SCORE_DIAGNONAL_2_INDEX = 7

    MIN_SCORE = -10
    MAX_SCORE = 10
    
    SCORE = {
        BOT_PLAYER: 1,
        START_PLAYER: -1,
        GameCellType.NULL: 0
    }

    logger = Logger(__name__).getInstance()

    def __init__(self, mode: GameMode) -> None:
        self.mode = mode

        self.board = self.initBoard()
        self.currentTurn = GameLogic.START_PLAYER
        self.playerScore = {
            GameCellType.X: [0] * GameLogic.NUM_WIN_POSSIBILITY,
            GameCellType.O: [0] * GameLogic.NUM_WIN_POSSIBILITY,
            GameCellType.NULL: [0] * GameLogic.NUM_WIN_POSSIBILITY
        }
        self.moves = 0
        self.result = GameCellType.NULL

    def initBoard(self) -> list[list[GameCellType]]:
        return [[GameCellType.NULL for _ in range(GameLogic.COLS)] for _ in range(GameLogic.ROWS)]

    def setCell(self, turn: GameCellType, row: int, col: int, isReverse: bool) -> None:
        if row >= len(self.board) or col >= len(self.board[row]):
            return
        value = 1 if not isReverse else -1
        self.board[row][col] = turn if not isReverse else GameCellType.NULL
        self.playerScore[turn][row] += value
        self.playerScore[turn][col + GameLogic.ROWS] += value
        if row == col: self.playerScore[turn][GameLogic.SCORE_DIAGNONAL_1_INDEX] += value
        if row == GameLogic.ROWS - 1 - col: self.playerScore[turn][GameLogic.SCORE_DIAGNONAL_2_INDEX] += value
        self.moves += value

    def isValidCell(self, row: int, col: int) -> bool:
        return self.board[row][col] == GameCellType.NULL

    def changeTurn(self) -> None:
        if self.currentTurn == GameCellType.O: 
            self.currentTurn = GameCellType.X
            return
        self.currentTurn = GameCellType.O

    def getCurrentTurn(self) -> GameCellType:
        return self.currentTurn

    def isPlayerTurn(self) -> bool:
        return self.mode == GameMode.PVP or (self.mode == GameMode.PVB and self.currentTurn == GameLogic.START_PLAYER)

    def getBotMove(self) -> tuple[int, int]:
        bestScore = GameLogic.MIN_SCORE
        bestMove = (-1, -1)
        count = 0
        for i in range(GameLogic.ROWS):
            for j in range(GameLogic.COLS):
                if self.board[i][j] != GameCellType.NULL: continue
                self.setCell(GameLogic.BOT_PLAYER, i, j, False)
                score = self.minimax(0, False)
                self.setCell(GameLogic.BOT_PLAYER, i, j, True)
                if score > bestScore:
                    bestScore = score
                    bestMove = (i, j)
        return bestMove

    def isEndGame(self) -> bool:
        for player, score in self.playerScore.items():
            if GameLogic.WIN_SCORE in score:
                self.result = player
                return True
        if self.moves >= GameLogic.MAX_MOVE:
            self.result = GameCellType.NULL
            return True
        return False

    def getWinLines(self) -> list[int]:
        return [i for i, x in enumerate(self.playerScore[self.result]) if x == GameLogic.WIN_SCORE]

    def minimax(self, depth: int, isBotTurn: bool) -> int:
        if self.isEndGame():
            return GameLogic.SCORE[self.result]

        bestScore = GameLogic.MIN_SCORE if isBotTurn else GameLogic.MAX_SCORE
        for i in range(GameLogic.ROWS):
            for j in range(GameLogic.COLS):
                if self.board[i][j] != GameCellType.NULL: continue
                if isBotTurn: 
                    self.setCell(GameLogic.BOT_PLAYER, i, j, False)
                    score = self.minimax(depth + 1, False)
                    self.setCell(GameLogic.BOT_PLAYER, i, j, True)
                    bestScore = max(score, bestScore)
                else:
                    self.setCell(GameLogic.START_PLAYER, i, j, False)
                    score = self.minimax(depth + 1, True)
                    self.setCell(GameLogic.START_PLAYER, i, j, True)
                    bestScore = min(score, bestScore)

        return bestScore