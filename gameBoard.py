import tkinter as tk
from tkinter import font
from constants import BASE_WIDTH, BASE_HEIGHT
from sideWidget import sideWidget
from engine import engine
from boardDisplay import boardDisplay

class GameBoard(tk.Frame):
    def __init__(self, parent):
        self.gameEngine = engine(self) #create the engine, must be initialized first

        tk.Frame.__init__(self, parent)
        canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_WIDTH, height = BASE_HEIGHT, background = 'grey')
        canvas.pack(side="left", fill="both", expand=True)
        self.boardDisplay = boardDisplay(self, canvas) #create the display for the game

        self.sideWidget = sideWidget(self) #create the menu on the right hand side

    def quickDeploy(self):
        self.sideWidget.clear()
        self.gameEngine.matrix = [['-', 'bT', 'bE', 'bG', 'bS', 'bT', '-', 'bP', 'bP', 'bT'],
                       ['-', 'bM', 'bL', 'bA', '-', 'bA', 'bA', 'bM', 'bA', 'bL'],
                       ['bA', 'bP', 'bP', 'bP', 'bL', 'bL', 'bP', 'bP', 'bP', 'bA'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['wA', 'wP', 'wP', 'wP', 'wL', 'wL', 'wP', 'wP', 'wP', 'wA'],
                       ['wL', 'wA', 'wM', 'wA', 'wA', '-', 'wA', 'wL', 'wM', '-'],
                       ['wT', 'wP', 'wP', '-', 'wT', 'wS', 'wG', 'wE', 'wT', '-']]
        self.boardDisplay.redrawPieces()
        self.beginPlay()

    def beginPlay(self):
        self.gameEngine.playPhaseStarted = True
        self.gameEngine.turnCount = 1
        self.sideWidget.startPlayPhase()
    
    def placePieceHelper(self, pieceType):
        self.boardDisplay.colorDeployableSquares()
        self.gameEngine.deployingPieceType = pieceType #abstract into game engine
        # self.gameEngine.awaitingDeployClick = True

    def restartGameHelper(self):
        self.restartGame()
        self.sideWidget.sideWidgetCanvas.destroy() #TODO: fix this I don't like it
        self.sideWidget = sideWidget(self)

    def restartGame(self):
        self.sideWidget.clear()
        self.boardDisplay.clear()
        self.gameEngine.reset()

    def redrawBoard(self):
        self.boardDisplay.redrawBoard()

    def redrawPieces(self):
        self.boardDisplay.redrawPieces()

    def colorPieceAndPossibleMoves(self, r, c):
        self.boardDisplay.colorPieceAndPossibleMoves(r, c)

    def colorEmpPurpleIfAttacked(self):
        self.boardDisplay.colorEmpPurpleIfAttacked()

    def colorDeployableSquares(self):
        self.boardDisplay.colorDeployableSquares()

    def placePiece(self, x0, y0, image):
        self.boardDisplay.placePiece(x0, y0, image)