import tkinter as tk
from tkinter import font
import os, sys
from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage

PIECE_SELECTED_COLOR = '#42e340'
POSSIBLE_MOVE_COLOR = '#92c74e'
KILL_PIECE_COLOR = '#f2463d'
PROTECT_PIECE_COLOR = '#4ca6f5'
EMPEROR_ATTACKED_COLOR = '#8b4df7'
BASE_WIDTH = 771
BASE_HEIGHT = 771
BASE_SIDEWIDGET_WIDTH = 360
DEPLOY_BUTTON_TEXTS = {'E' : 'Place Emperor | 1 Remaining', 'G' : 'Place General | 1 Remaining', 'M' : 'Place Merchant | 2 Remaining',
                       'P' : 'Place Man-at-Arms | 8 Remaining', 'T' : 'Place Thief | 3 Remaining', 'A': 'Place Archer | 6 Remaining',
                       'S': 'Place Scholar | 1 Remaining', 'L' : 'Place Lancer | 4 Remaining' }

#TODO:
#add move descriptions to before game start and during move phase
#add board flip button to move phase
class GameBoard(tk.Frame):
    def __init__(self, parent):
        self.rows = 10
        self.columns = 10
        self.size = 60
        self.color1 = "#f9b46c"
        self.color2 = "#432d09"
        self.white_images = {}
        self.black_images = {}
        self.awaitingDeployClick = False
        self.playPhaseStarted = False
        self.pieceToMove = None
        self.turn = 1
        self.deployingPieceType = None
        self.matrix = [['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-']]
        self.white_pieces = {}
        self.black_pieces = {}
        self.deployButtons = {}
        self.allowedMoves = set()
        self.whiteProtectedSquares = set()
        self.blackProtectedSquares = set()
        self.pieceToDeployFromThief = None
        self.awaitingThiefStealDeployment = None
        self.turnCount = 1
        self.isGameOver = False
        self.sideWidgetX = BASE_SIDEWIDGET_WIDTH

        tk.Frame.__init__(self, parent)
        self.BOLD_FONT = font.Font(family='freemono', size=18, weight="bold")
        
        self.canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_WIDTH, height = BASE_HEIGHT, background = 'grey')
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sideWidgetCanvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_SIDEWIDGET_WIDTH, height = BASE_HEIGHT, background = 'black')
        self.initSideCanvas()

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind('<Button 1>', self.getorigin)
        self.sideWidgetCanvas.bind("<Configure>", self.redrawSideWidget)

    def initSideCanvas(self):
        self.textX = self.sideWidgetX // 2 #(self.columns * self.size) // 2
        self.textY = (self.rows * self.size) // 2
        # BOLD_FONT = font.Font(family='freemono', size=18, weight="bold")
        self.sideWidgetCanvas.create_text(self.textX, self.size, font=self.BOLD_FONT, text='Welcome to Keschet!', fill='white', tag='sideWidgetText')

        self.startButton = tk.Button(self.sideWidgetCanvas, text='Start Deployment', command=self.startDeploymentPhase)
        self.startButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size * 2, window=self.startButton)

        self.quickDeployButton = tk.Button(self.sideWidgetCanvas, text='Quick Deploy', command=self.quickDeploy)
        self.quickDeployButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size * 3, window=self.quickDeployButton)
        
        self.sideWidgetCanvas.pack(side='right', fill='both', expand=True)
    def quickDeploy(self):
        widgets = self.sideWidgetCanvas.find_all()
        for widget in widgets:
            self.sideWidgetCanvas.delete(widget)

        self.matrix = [['-', 'bT', 'bE', 'bG', 'bS', 'bT', '-', 'bP', 'bP', 'bT'],
                       ['-', 'bM', 'bL', 'bA', '-', 'bA', 'bA', 'bM', 'bA', 'bL'],
                       ['bA', 'bP', 'bP', 'bP', 'bL', 'bL', 'bP', 'bP', 'bP', 'bA'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['wA', 'wP', 'wP', 'wP', 'wL', 'wL', 'wP', 'wP', 'wP', 'wA'],
                       ['wL', 'wA', 'wM', 'wA', 'wA', '-', 'wA', 'wL', 'wM', '-'],
                       ['wT', 'wP', 'wP', '-', 'wT', 'wS', 'wG', 'wE', 'wT', '-']]
        
        self.redrawPieces()
        #move to begin play + player turn + turn counter + move descriptions 
        self.beginPlay()
        return

    def beginPlay(self):
        self.playPhaseStarted = True
        self.turn = 1
        # BOLD_FONT = font.Font(family='freemono', size=18, weight="bold")
        turnText = 'White To Move' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText, font=self.BOLD_FONT, fill='white', tag='playersTurnTextID')        
        turnCountText = 'Turn 1' 
        self.turnCountText = self.sideWidgetCanvas.create_text(self.textX, self.size, text=turnCountText, font=self.BOLD_FONT, fill='white', tag='turnCountText') 

    def startDeploymentPhase(self):
        print('starting deploy phase')
        self.startButton.destroy()
        self.quickDeployButton.destroy()
        self.sideWidgetCanvas.delete('sideWidgetText')

        # BOLD_FONT = font.Font(family='freemono', size=18, weight="bold")
        self.sideWidgetCanvas.create_text(self.textX, self.size, text='Deploy Pieces', font=self.BOLD_FONT, fill='white', tag='sideWidgetText')
        turnText = 'Player ' + str(self.turn) + '\'s Turn' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText,font=self.BOLD_FONT, fill='white', tag='playersTurnTextID')

        self.createDeployButton('E', 3)
        self.createDeployButton('P', 3.75)
        self.createDeployButton('A', 4.5)
        self.createDeployButton('L', 5.25)
        self.createDeployButton('M', 6)
        self.createDeployButton('G', 6.75)
        self.createDeployButton('S', 7.5)
        self.createDeployButton('T', 8.25)

    def createDeployButton(self, pieceType, yPosition):
        self.deployButtons[pieceType] = tk.Button(self.sideWidgetCanvas, text=DEPLOY_BUTTON_TEXTS[pieceType], command=lambda : self.placePieceHelper(pieceType))
        self.deployButtons[pieceType].configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*yPosition, window=self.deployButtons[pieceType])

    def placePieceHelper(self, pieceType):
        self.colorDeployableSquares()
        self.deployingPieceType = pieceType
        self.awaitingDeployClick = True

    def colorDeployableSquares(self):
        squares = self.canvas.find_withtag('square')
        for square in squares:
            coords = self.canvas.coords(square)
            r = int(coords[1] // self.size)
            c = int(coords[0] // self.size)
            if self.turn == 1 and r >= 7 and self.matrix[r][c] == '-':
                self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)
            if self.turn == 2 and r <= 2 and self.matrix[r][c] == '-':
                self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)

    def getorigin(self, eventorigin):
        c = eventorigin.x // self.size
        r = eventorigin.y // self.size
        if self.awaitingDeployClick: #handle deployment click to board once piece selected
            if self.matrix[r][c] != '-' or (self.turn == 1 and r < 7) or (self.turn == 2 and r > 2): #if square occupied or outside of deployment bounds
                return
            self.matrix[r][c] = ('w' + self.deployingPieceType) if self.turn == 1 else ('b' + self.deployingPieceType)
            x0 = (c * self.size) + int(self.size/2)
            y0 = (r * self.size) + int(self.size/2)
            imageIdentifier = self.deployingPieceType + '.png'
            images = self.white_images if self.turn == 1 else self.black_images
            self.canvas.create_image(x0, y0, image = images[imageIdentifier], tags=(self.matrix[r][c], 'piece'))
            curPieces = self.white_pieces if self.turn == 1 else self.black_pieces
            if self.deployingPieceType not in curPieces:
                curPieces[self.deployingPieceType] = 1
            else:
                curPieces[self.deployingPieceType] += 1
            self.turn = 2 if self.turn == 1 else 1

            piecesDeployed = 0
            for r1 in range(0, self.rows):
                for c1 in range(0, self.columns):
                    if self.matrix[r1][c1][0] == 'b': piecesDeployed += 1
            if piecesDeployed == 26:
                self.awaitingDeployClick = False
                widgets = self.sideWidgetCanvas.find_all()
                for widget in widgets:
                    self.sideWidgetCanvas.delete(widget)
                self.redrawBoard()
                self.beginPlay()
                return

            turnText = 'Player ' + str(self.turn) + '\'s Turn' 
            self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
            # self.turnCount += 1
            # turnCountText = 'Turn ' + str(self.turnCount)
            # self.sideWidgetCanvas.itemconfigure(self.turnCountText, text=turnCountText)

            self.updateDeployButton('E')
            self.updateDeployButton('P')
            self.updateDeployButton('L')
            self.updateDeployButton('M')
            self.updateDeployButton('A')
            self.updateDeployButton('G')
            self.updateDeployButton('S')
            self.updateDeployButton('T')
            print('here')
            self.awaitingDeployClick = False
            self.redrawBoard()
        
        #move click
        if self.playPhaseStarted and not self.isGameOver:
            print(r, c)
            pieceColor = 'w' if self.turn == 1 else 'b'
            if self.awaitingThiefStealDeployment: #piece from thief capture is being deployed #REFACTOR
                if (self.turn == 1 and r >= 7 and self.matrix[r][c] == '-') or (self.turn == 2 and r <= 2 and self.matrix[r][c] == '-'):
                    self.matrix[r][c] = self.awaitingThiefStealDeployment
                    self.awaitingThiefStealDeployment = None
                    self.redrawPieces()
                    self.redrawBoard()
                    turnText = 'Black to Move' if self.turn == 1 else 'White to Move'
                    self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
                    self.turn = 2 if self.turn == 1 else 1
                    self.turnCount += 1
                    turnCountText = 'Turn ' + str(self.turnCount)
                    self.sideWidgetCanvas.itemconfigure(self.turnCountText, text=turnCountText)

            #handle normal move during play phase
            elif self.pieceToMove and (r, c) in self.allowedMoves: #if a piece is currently selected and the new selection is a place to move
                selectedPiece = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                
                #if scholar is being moved or piece moves out of protection, then remove protection from square
                myProtectedSquares = self.whiteProtectedSquares if self.turn == 1 else self.blackProtectedSquares
                if selectedPiece[1] == 'S' or (self.pieceToMove[0], self.pieceToMove[1]) in myProtectedSquares:
                    myProtectedSquares.clear()
                
                enemyColor = 'b' if pieceColor == 'w' else 'w'
                enemyProtectedSquares = self.blackProtectedSquares if self.turn == 1 else self.whiteProtectedSquares
                if self.matrix[r][c] == enemyColor + 'S': #if killing enemy scholar, remove that scholars protected square
                    enemyProtectedSquares.clear()

                #if scholar is selected piece and clicking on same color piece to protect
                if selectedPiece[1] == 'S' and self.matrix[r][c][0] == pieceColor:
                    myProtectedSquares.add((r, c)) #scholar position, protected position
                #if thief is capturing an enemy piece
                elif selectedPiece[1] == 'T' and self.matrix[r][c][0] == enemyColor:
                    self.awaitingThiefStealDeployment = pieceColor + self.matrix[r][c][1]
                    self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'
                    self.redrawBoard()
                    self.colorDeployableSquares()
                else:    #general case, move piece
                    self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'

                #update turn text
                if not self.awaitingThiefStealDeployment: #REFACTOR: make the following display updates into a function
                    self.turn = 2 if self.turn == 1 else 1
                    turnText = 'Black to Move' if self.turn == 2 else 'White to Move'
                    self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
                    self.turnCount += 1
                    turnCountText = 'Turn ' + str(self.turnCount)
                    self.sideWidgetCanvas.itemconfigure(self.turnCountText, text=turnCountText)

                #redraw board and clean up for next turn
                self.redrawPieces()
                if not self.awaitingThiefStealDeployment:
                    self.redrawBoard()

                #move was made, clear the selected piece
                self.checkGameOver()
                if self.isGameOver:
                    self.handleGameOver()
                    return
                self.colorEmpPurpleIfAttacked()
                self.pieceToMove = None
                self.allowedMoves.clear()
            elif self.matrix[r][c][0] == pieceColor: #selected a piece of your color, calculate moves and draw board with moves
                if (r, c) == self.pieceToMove:
                    self.pieceToMove = None
                    self.allowedMoves.clear()
                    self.redrawBoard()
                    self.colorEmpPurpleIfAttacked()
                    return
                self.pieceToMove = (r, c)
                self.allowedMoves.clear()
                self.allowedMoves = self.calcAllowedMoves(r, c)
                self.redrawBoard()
                self.colorPieceAndPossibleMoves(r, c)
                self.colorEmpPurpleIfAttacked()

    def handleGameOver(self):
        widgets = self.sideWidgetCanvas.find_all()
        for widget in widgets:
            self.sideWidgetCanvas.delete(widget)
        
        # BOLD_FONT = font.Font(family='freemono', size=18, weight="bold")
        winText = 'White was victorious!' if self.turn == 2 else 'Black was victorious!' 
        self.winText = self.sideWidgetCanvas.create_text(self.textX, self.size, text=winText, font=self.BOLD_FONT, fill='white', tag='turnCountText') 

        self.startButton = tk.Button(self.sideWidgetCanvas, text='Back To Menu', command=self.restartGameHelper)
        self.startButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size * 2, window=self.startButton)

    def restartGameHelper(self):
        self.restartGame()
        self.initSideCanvas()

    def restartGame(self):
        print('restart the gamemmeme')
        widgets = self.sideWidgetCanvas.find_all()
        for widget in widgets:
            self.sideWidgetCanvas.delete(widget)

        widgets = self.canvas.find_withtag('piece')
        for widget in widgets:
            self.canvas.delete(widget)

        self.resetGameBoard()
        # self.canvas.pack_forget()
        # self.sideWidgetCanvas.pack_forget()
        # self.canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_WIDTH, height = BASE_HEIGHT, background = 'grey')
        # self.canvas.pack(side="left", fill="both", expand=True)
        
        # self.sideWidgetCanvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_SIDEWIDGET_WIDTH, height = BASE_HEIGHT, background = 'black')
        
        # self.initSideCanvas()
        # self.canvas.event_generate("<Configure>")
        #fix side widget text wrong on game reset        


        # self.refresh()

    def resetGameBoard(self):
        self.awaitingDeployClick = False
        self.playPhaseStarted = False
        self.pieceToMove = None
        self.turn = 1
        self.deployingPieceType = None
        self.matrix = [['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-']]
        self.white_pieces = {}
        self.black_pieces = {}
        self.deployButtons = {}
        self.allowedMoves = set()
        self.whiteProtectedSquares = set()
        self.blackProtectedSquares = set()
        self.pieceToDeployFromThief = None
        self.awaitingThiefStealDeployment = None
        self.turnCount = 1
        self.isGameOver = False

    def checkGameOver(self):
        # print('checking if game over')
        wEmpFound = False
        bEmpFound = False
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1] == 'wE': wEmpFound = True
                if self.matrix[r1][c1] == 'bE': bEmpFound = True

        if not wEmpFound or not bEmpFound:
            self.isGameOver = True
            return True
        return False

    def colorEmpPurpleIfAttacked(self):
        pieceColor = 'w' if self.turn == 1 else 'b'
        #find the emperor of the current team
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1] == pieceColor + 'E':
                    emperorR = r1
                    emperorC = c1
        
        attackedSquares = self.calcSquaresThatEnemyAttacksOrDefends()
        if (emperorR, emperorC) in attackedSquares:
            squares = self.canvas.find_withtag('square')
            for square in squares:
                coords = self.canvas.coords(square)
                r = int(coords[1] // self.size)
                c = int(coords[0] // self.size)
                if r == emperorR and c == emperorC:
                    self.canvas.itemconfigure(square, fill=EMPEROR_ATTACKED_COLOR)

    def calcAllowedMoves(self, r, c, defended=False): #defended = True will also return squares that piece is defending 
        #(allied squares it could move to if that allied piece was attacked)
        pieceType = self.matrix[r][c][1]
        if pieceType == 'P':
            return self.calcHorizontalorVerticalMoves(r, c, 2, defended)
        elif pieceType == 'A':
            return self.calcHorizontalorVerticalMoves(r, c, 6, defended)
        elif pieceType == 'G':
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 9, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 9, defended)
            return rcMoves.union(diagMoves)
        elif pieceType == 'L':
            return self.calcDiagonalMoves(r, c, 9, defended)
        elif pieceType == 'M':
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 2, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 2, defended)
            tpMoves = self.checkEmperorTeleportMoves(r, c)
            return tpMoves.union(rcMoves.union(diagMoves))
        elif pieceType == 'S':
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 2, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 2, defended)
            spMoves = self.calcScholarProtectMoves(r, c)
            return spMoves.union(rcMoves.union(diagMoves))
        elif pieceType == 'T':
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 1, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 1, defended)
            return rcMoves.union(diagMoves)
        elif pieceType == 'E':
            return self.calcEmperorMoves(r, c, defended)

    def calcEmperorMoves(self, r, c, defended):
        rcMoves = self.calcHorizontalorVerticalMoves(r, c, 1, defended)
        diagMoves = self.calcDiagonalMoves(r, c, 1, defended)
        possibleEmperorMoves = rcMoves.union(diagMoves)
        t = self.matrix[r][c]
        self.matrix[r][c] = '-'
        attackedOrDefendedSquares = self.calcSquaresThatEnemyAttacksOrDefends()
        self.matrix[r][c] = t
        return possibleEmperorMoves.difference(attackedOrDefendedSquares)

    def calcSquaresThatEnemyAttacksOrDefends(self): #change to attacks or defends
        squares = set()
        enemyColor = 'b' if self.turn == 1 else 'w'
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1][0] == enemyColor and self.matrix[r1][c1][1] != 'E':
                    moves = self.calcAllowedMoves(r1, c1, True)
                    squares = squares.union(moves)
        return squares

    def calcScholarProtectMoves(self, r, c):
        pieceColor = self.matrix[r][c][0]
        moves = set()
        protectedSquares = self.whiteProtectedSquares if pieceColor == 'w' else self.blackProtectedSquares
        for rVal in range(-1, 2):
            for cVal in range(-1, 2):
                if rVal == 0 and cVal == 0: continue
                if self.isOnBoard(r + rVal, c + cVal):
                    if self.matrix[r + rVal][c + cVal] != '-' and self.matrix[r+rVal][c+cVal][0] == pieceColor and (r+rVal, c+cVal) not in protectedSquares:
                        moves.add((r+rVal, c+cVal))

        return moves
    def checkEmperorTeleportMoves(self, r, c):
        pieceColor = self.matrix[r][c][0]
        #find the emperor of the current team
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1] == pieceColor + 'E':
                    emperorR = r1
                    emperorC = c1
        #check for empty squares adjacent to the emperor
        moves = set()
        for rVal in range(-1, 2):
            for cVal in range(-1, 2):
                if rVal == 0 and cVal == 0: continue
                if self.isOnBoard(emperorR + rVal, emperorC + cVal):
                    if self.matrix[emperorR + rVal][emperorC + cVal] == '-':
                        moves.add((emperorR+rVal, emperorC+cVal))
        return moves

    def calcDiagonalMoves(self, r, c, distance, addDefendingMoves):
        pieceColor = self.matrix[r][c][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        moves = set()
        #REFACTOR
        for i in range(1, distance + 1): #up left
            rMove, cMove = r - i, c - i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    moves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((rMove, cMove))
                    break
                else:
                    moves.add((rMove, cMove))
        for i in range(1, distance + 1): #up right
            rMove, cMove = r - i, c + i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    moves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((rMove, cMove))
                    break
                else:
                    moves.add((rMove, cMove))
        for i in range(1, distance + 1): #down left
            rMove, cMove = r + i, c - i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    moves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((rMove, cMove))
                    break
                else:
                    moves.add((rMove, cMove))
        for i in range(1, distance + 1): #down right
            rMove, cMove = r + i, c + i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    moves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((rMove, cMove))
                    break
                else:
                    moves.add((rMove, cMove))

        enemyProtectedSquares = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
        for square in enemyProtectedSquares:
            if square in moves: moves.remove(square)

        return moves

    def calcHorizontalorVerticalMoves(self, r, c, distance, addDefendingMoves):
        pieceColor = self.matrix[r][c][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        moves = set()
        #REFACTOR
        for i in range(1, distance + 1): #moves to left
            if self.isOnBoard(r, c - i):
                if self.matrix[r][c-i][0] == enemyColor:
                    moves.add((r, c-i))
                    break
                elif self.matrix[r][c-i][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((r, c-i))
                    break
                else:
                    moves.add((r, c-i))
        for i in range(1, distance + 1): #moves to right
            if self.isOnBoard(r, c + i):
                if self.matrix[r][c+i][0] == enemyColor:
                    moves.add((r, c+i))
                    break
                elif self.matrix[r][c+i][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((r, c+i))
                    break
                else:
                    moves.add((r, c+i))
        for i in range(1, distance + 1): #moves down
            if self.isOnBoard(r + i, c):
                if self.matrix[r+i][c][0] == enemyColor:
                    moves.add((r+i, c))
                    break
                elif self.matrix[r+i][c][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((r+i, c))
                    break
                else:
                    moves.add((r+i, c))
        for i in range(1, distance + 1): #moves up
            if self.isOnBoard(r - i, c):
                if self.matrix[r-i][c][0] == enemyColor:
                    moves.add((r-i, c))
                    break
                elif self.matrix[r-i][c][0] == pieceColor:
                    if addDefendingMoves:
                        moves.add((r-i, c))
                    break
                else:
                    moves.add((r-i, c))
        
        # enemyProtectedSquare = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
        # if enemyProtectedSquare in self.allowedMoves: self.allowedMoves.remove(enemyProtectedSquare)
        enemyProtectedSquares = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
        # print('enemyProtectedSquare', enemyProtectedSquares)
        # print(self.allowedMoves)
        for square in enemyProtectedSquares:
            if square in moves: moves.remove(square)

        return moves

    def isOnBoard(self, r, c):
        if r >= 0 and r < self.rows and c >= 0 and c < self.columns:
            return True
        else:
            return False

    def colorPieceAndPossibleMoves(self, r0, c0):
        pieceColor = self.matrix[r0][c0][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        squares = self.canvas.find_withtag('square')
        for square in squares:
            coords = self.canvas.coords(square)
            r = int(coords[1] // self.size)
            c = int(coords[0] // self.size)
            if r == r0 and c == c0:
                self.canvas.itemconfigure(square, fill=PIECE_SELECTED_COLOR)
            if (r, c) in self.allowedMoves:
                if self.matrix[r][c] == '-':
                    self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)
                elif self.matrix[r][c][0] == enemyColor:
                    self.canvas.itemconfigure(square, fill=KILL_PIECE_COLOR)
                elif self.matrix[r][c][0] == pieceColor:
                    self.canvas.itemconfigure(square, fill=PROTECT_PIECE_COLOR)

    def updateDeployButton(self, pieceType):
        if self.turn == 1:
            deployedCount = self.white_pieces.get(pieceType, 0)
        else:
            deployedCount = self.black_pieces.get(pieceType, 0)
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

    def redrawBoard(self):
        self.canvas.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            if self.awaitingDeployClick:
                if self.turn == 1 and row >= 7:
                    color = POSSIBLE_MOVE_COLOR
                elif self.turn == 2 and row <= 2:
                    color = POSSIBLE_MOVE_COLOR
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                if (row, col) in self.whiteProtectedSquares or (row, col) in self.blackProtectedSquares: #if protected square, color protected
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=PROTECT_PIECE_COLOR, tags="square")
                else: #else normal color
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
                if self.awaitingDeployClick:
                    if self.turn == 1 and row >= 7:
                        color = POSSIBLE_MOVE_COLOR
                    elif self.turn == 2 and row <= 2:
                        color = POSSIBLE_MOVE_COLOR
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")
        
    def refresh(self, event=None):
        '''Redraw the board, possibly in response to window being resized'''
        print(event.width, event.height)
        xsize = int((event.width-1) / self.columns) #if event else int((BASE_WIDTH-1) / self.columns)
        ysize = int((event.height-1) / self.rows) #if event else int((BASE_HEIGHT-1) / self.columns)
        self.size = min(xsize, ysize)
        self.redrawBoard()
        self.redrawPieces()

    def redrawPieces(self):
        self.canvas.delete('piece')
        for r in range(self.rows):
            for c in range(self.columns):
                if self.matrix[r][c] != '-':
                    pieceToRender = self.matrix[r][c]
                    if pieceToRender[0] == 'b':
                        imageIdentifier = pieceToRender[1] + '.png'
                        x0 = (c * self.size) + int(self.size/2)
                        y0 = (r * self.size) + int(self.size/2)
                        self.canvas.create_image(x0, y0, image = self.black_images[imageIdentifier], tags=(pieceToRender, 'piece'))
                    else:
                        imageIdentifier = pieceToRender[1] + '.png'
                        x0 = (c * self.size) + int(self.size/2)
                        y0 = (r * self.size) + int(self.size/2)
                        self.canvas.create_image(x0, y0, image = self.white_images[imageIdentifier], tags=(pieceToRender, 'piece'))
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def redrawSideWidget(self, event=None):
        if event:
            self.sideWidgetX = event.width
        self.textX = event.width // 2 if event else BASE_SIDEWIDGET_WIDTH // 2
        self.textY = self.size #(self.rows * self.size) // 2
        sideWidgetItems = self.sideWidgetCanvas.find_all()
        curY = self.textY #- (self.size * 2)
        for widget in sideWidgetItems:
            self.sideWidgetCanvas.coords(widget, self.textX, curY)
            curY += self.size

    def import_pieces(self): #opens and stores images of pieces and prepares the pieces for the game for both sides
        path = os.path.join(os.path.dirname(__file__), "white") #stores white pieces images into dicts
        w_dirs = os.listdir(path)
        for file in w_dirs:
            if file == '.DS_Store':
                continue
            img = Image.open(path+"/"+file)
            img = img.resize((60,60), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(image=img)
            self.white_images.setdefault(file, img)

        path = os.path.join(os.path.dirname(__file__), "black") #stores black pieces images into dicts
        b_dirs = os.listdir(path)
        for file in b_dirs:
            if file == '.DS_Store':
                continue
            img = Image.open(path+"/"+file)
            img = img.resize((60,60), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(image=img)
            self.black_images.setdefault(file, img)

root = tk.Tk()
board = GameBoard(root)
board.pack(side="top", fill="both", expand="true")
board.import_pieces()
root.mainloop()