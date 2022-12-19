import tkinter as tk
from tkinter import font
from constants import BASE_SIDEWIDGET_WIDTH, BASE_HEIGHT, DEPLOY_BUTTON_TEXTS

class sideWidget(tk.Frame):
    def __init__(self, gameBoard, width=BASE_SIDEWIDGET_WIDTH, height=BASE_HEIGHT, size=60, rows=10):
        self.BOLD_FONT = font.Font(family='freemono', size=18, weight="bold")
        self.textX = width // 2
        self.textY = (rows * size) // 2
        self.gameBoard = gameBoard
        self.size = size
        self.deployButtons = {}
        self.gameEngine = gameBoard.gameEngine

        self.sideWidgetCanvas = tk.Canvas(self.gameBoard, borderwidth = 0, highlightthickness = 0, width = BASE_SIDEWIDGET_WIDTH, height = BASE_HEIGHT, background = 'black')
        
        self.sideWidgetCanvas.create_text(self.textX, size, font=self.BOLD_FONT, text='Welcome to Keschet!', fill='white', tag='sideWidgetText')
        self.startButton = tk.Button(self.sideWidgetCanvas, text='Start Deployment', command=self.startDeploymentPhase)
        self.startButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, size * 2, window=self.startButton)

        self.quickDeployButton = tk.Button(self.sideWidgetCanvas, text='Quick Deploy', command=self.gameBoard.quickDeploy)
        self.quickDeployButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, size * 3, window=self.quickDeployButton)
        
        self.sideWidgetCanvas.pack(side='right', fill='both', expand=True)
        self.sideWidgetCanvas.bind("<Configure>", self.redraw)
    
    def startPlayPhase(self):
        self.clear()
        turnText = 'White To Move' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText, font=self.BOLD_FONT, fill='white', tag='playersTurnTextID')        
        turnCountText = 'Turn 1' 
        self.turnCountText = self.sideWidgetCanvas.create_text(self.textX, self.size, text=turnCountText, font=self.BOLD_FONT, fill='white', tag='turnCountText')

    def createDeployButton(self, pieceType, yPosition):
        self.deployButtons[pieceType] = tk.Button(self.sideWidgetCanvas, text=DEPLOY_BUTTON_TEXTS[pieceType], command=lambda : self.gameBoard.placePieceHelper(pieceType))
        self.deployButtons[pieceType].configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*yPosition, window=self.deployButtons[pieceType])

    def startDeploymentPhase(self):
        print('starting deploy phase')
        self.startButton.destroy()
        self.quickDeployButton.destroy()
        self.sideWidgetCanvas.delete('sideWidgetText')

        self.sideWidgetCanvas.create_text(self.textX, self.size, text='Deploy Pieces', font=self.BOLD_FONT, fill='white', tag='sideWidgetText')
        turnText = 'Player ' + str(self.gameEngine.turn) + '\'s Turn' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText,font=self.BOLD_FONT, fill='white', tag='playersTurnTextID')

        self.createDeployButton('E', 3)
        self.createDeployButton('P', 3.75)
        self.createDeployButton('A', 4.5)
        self.createDeployButton('L', 5.25)
        self.createDeployButton('M', 6)
        self.createDeployButton('G', 6.75)
        self.createDeployButton('S', 7.5)
        self.createDeployButton('T', 8.25)

    def updateDeployButton(self, pieceType):
        if not self.gameEngine.awaitingDeployClick: return
        if self.gameEngine.turn == 1:
            deployedCount = self.gameEngine.white_pieces.get(pieceType, 0)
        else:
            deployedCount = self.gameEngine.black_pieces.get(pieceType, 0)
        if pieceType == 'E':
            remainingPiecesToDeploy = 1 - deployedCount
            newText = 'Place Emperor | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'P':
            remainingPiecesToDeploy = 8 - deployedCount
            newText = 'Place Man-at-Arms | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'L':
            remainingPiecesToDeploy = 4 - deployedCount
            newText = 'Place Lancer | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'M':
            remainingPiecesToDeploy = 2 - deployedCount
            newText = 'Place Merchant | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'A':
            remainingPiecesToDeploy = 6 - deployedCount
            newText = 'Place Archer | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'G':
            remainingPiecesToDeploy = 1 - deployedCount
            newText = 'Place General | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'S':
            remainingPiecesToDeploy = 1 - deployedCount
            newText = 'Place Scholar | ' + str(remainingPiecesToDeploy) + ' Remaining'
        elif pieceType == 'T':
            remainingPiecesToDeploy = 3 - deployedCount
            newText = 'Place Thief | ' + str(remainingPiecesToDeploy) + ' Remaining'

        self.deployButtons[pieceType].config(text=newText)
        if remainingPiecesToDeploy:
            self.deployButtons[pieceType]['state'] = 'normal'
        else:
            self.deployButtons[pieceType]['state'] = 'disabled'

    def handleGameOver(self):
        self.clear()
        winText = 'White was victorious!' if self.gameEngine.turn == 2 else 'Black was victorious!' 
        self.winText = self.sideWidgetCanvas.create_text(self.textX, self.size, text=winText, font=self.BOLD_FONT, fill='white', tag='turnCountText') 
        self.startButton = tk.Button(self.sideWidgetCanvas, text='Back To Menu', command=self.gameBoard.restartGameHelper)
        self.startButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size * 2, window=self.startButton)

    def updateTurnDisplay(self):
        turnText = 'Black to Move' if self.gameEngine.turn == 2 else 'White to Move'
        self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
        turnCountText = 'Turn ' + str(self.gameEngine.turnCount)
        self.sideWidgetCanvas.itemconfigure(self.turnCountText, text=turnCountText)

    def updateAfterDeploy(self):
            turnText = 'Player ' + str(self.gameEngine.turn) + '\'s Turn' 
            self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
            self.updateDeployButton('E')
            self.updateDeployButton('P')
            self.updateDeployButton('L')
            self.updateDeployButton('M')
            self.updateDeployButton('A')
            self.updateDeployButton('G')
            self.updateDeployButton('S')
            self.updateDeployButton('T')

    def clear(self):
        widgets = self.sideWidgetCanvas.find_all()
        for widget in widgets:
            self.sideWidgetCanvas.delete(widget)

    def redraw(self, event=None):
        if event:
            self.sideWidgetX = event.width
        self.textX = event.width // 2 if event else BASE_SIDEWIDGET_WIDTH // 2
        self.textY = self.size 
        sideWidgetItems = self.sideWidgetCanvas.find_all()
        curY = self.textY
        for widget in sideWidgetItems:
            self.sideWidgetCanvas.coords(widget, self.textX, curY)
            curY += self.size
