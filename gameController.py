import tkinter as tk
from tkinter import font
from constants import BASE_WIDTH, BASE_HEIGHT
from sideWidget import sideWidget
from engine import engine
from boardDisplay import boardDisplay

class gameController(tk.Frame):
    def __init__(self, parent):
        self.gameEngine = engine(self) #create the engine, must be initialized first

        tk.Frame.__init__(self, parent)
        canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_WIDTH, height = BASE_HEIGHT, background = 'grey')
        canvas.pack(side="left", fill="both", expand=True)
        self.boardDisplay = boardDisplay(self, canvas) #create the display for the game

        self.sideWidget = sideWidget(self) #create the menu on the right hand side

    def quickDeploy(self) -> None:
        self.sideWidget.clear()
        self.gameEngine.setQuickDeployBoard()
        self.boardDisplay.redrawPieces()
        self.beginPlay()

    def startAIGame(self) -> None:
        self.quickDeploy()
        self.gameEngine.playingAI = True

    def beginPlay(self) -> None:
        self.gameEngine.playPhaseStarted = True
        self.gameEngine.turnCount = 1
        self.sideWidget.startPlayPhase()
    
    def placePieceHelper(self, pieceType: str) -> None:
        self.boardDisplay.colorDeployableSquares()
        self.gameEngine.deployingPieceType = pieceType

    def restartGameHelper(self) -> None:
        self.restartGame()
        self.sideWidget.sideWidgetCanvas.destroy()
        self.sideWidget = sideWidget(self)

    def restartGame(self) -> None:
        self.sideWidget.clear()
        self.boardDisplay.clear()
        self.gameEngine.reset()

    def redrawBoard(self) -> None:
        self.boardDisplay.redrawBoard()

    def redrawPieces(self) -> None:
        self.boardDisplay.redrawPieces()

    def colorPieceAndPossibleMoves(self, r: int, c: int) -> None:
        self.boardDisplay.colorPieceAndPossibleMoves(r, c)

    def colorEmpPurpleIfAttacked(self) -> None:
        self.boardDisplay.colorEmpPurpleIfAttacked()

    def colorDeployableSquares(self) -> None:
        self.boardDisplay.colorDeployableSquares()

    def placePiece(self, x0: int, y0: int, image: str) -> None:
        self.boardDisplay.placePiece(x0, y0, image)