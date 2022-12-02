import tkinter as tk
import os, sys
from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage

PIECE_SELECTED_COLOR = '#42e340'
POSSIBLE_MOVE_COLOR = '#92c74e'
KILL_PIECE_COLOR = '#f2463d'
PROTECT_PIECE_COLOR = '#4ca6f5'
BASE_WIDTH = 771
BASE_HEIGHT = 771
BASE_SIDEWIDGET_WIDTH = 360
DEPLOY_BUTTON_TEXTS = {'E' : 'Place Emperor | 1 Remaining', 'G' : 'Place General | 1 Remaining', 'M' : 'Place Merchant | 2 Remaining',
                       'P' : 'Place Man-at-Arms | 8 Remaining', 'T' : 'Place Thief | 3 Remaining', 'A': 'Place Archer | 6 Remaining',
                       'S': 'Place Scholar | 1 Remaining', 'L' : 'Place Lancer | 4 Remaining' }

#TODO:
#clone a scholar
#end game when emperor killed
#turn counter during movement phase
#add start button when deployment phase finished
#add move descriptions to before game start and during move phase
#add board flip button to move phase
#implement check mechanic?
class GameBoard(tk.Frame):
    def __init__(self, parent, rows=10, columns=10, size=60, color1="#f9b46c", color2="#432d09"):
        self.rows = rows
        self.columns = columns
        self.size = size
        self.color1 = color1
        self.color2 = color2
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
        self.mouseX = 0
        self.mouseY = 0
        self.white_pieces = {}
        self.black_pieces = {}
        self.deployButtons = {}
        self.allowedMoves = set()
        self.whiteProtectedSquares = None
        self.blackProtectedSquares = None
        self.pieceToDeployFromThief = None
        self.awaitingThiefStealDeployment = None

        tk.Frame.__init__(self, parent)
        
        self.canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_WIDTH, height = BASE_HEIGHT, background = 'grey')
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sideWidgetCanvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_SIDEWIDGET_WIDTH, height = BASE_HEIGHT, background = 'black')
        self.textX = (columns * size) // 2
        self.textY = (rows * size) // 2
        self.sideWidgetCanvas.create_text(self.textX, self.textY, text='Welcome to Keschet!', fill='white', tag='sideWidgetText')

        self.startButton = tk.Button(self.sideWidgetCanvas, text='Start Deployment', command=self.startDeploymentPhase)
        self.startButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.textY + size, window=self.startButton)

        self.quickDeployButton = tk.Button(self.sideWidgetCanvas, text='Quick Deploy', command=self.quickDeploy)
        self.quickDeployButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.textY + size, window=self.quickDeployButton)
        
        self.sideWidgetCanvas.pack(side='right', fill='both', expand=True)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind('<Button 1>', self.getorigin)
        self.sideWidgetCanvas.bind("<Configure>", self.redrawSideWidget)

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
        turnText = 'White To Move' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText, fill='white', tag='playersTurnTextID')        

    def startDeploymentPhase(self):
        self.startButton.destroy()
        self.quickDeployButton.destroy()
        self.sideWidgetCanvas.delete('sideWidgetText')

        self.sideWidgetCanvas.create_text(self.textX, self.size, text='Deploy Pieces', fill='white', tag='sideWidgetText')
        turnText = 'Player ' + str(self.turn) + '\'s Turn' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText, fill='white', tag='playersTurnTextID')

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
        #REFACTOR, maybe combine the if statements for player 1 and 2
        if self.awaitingDeployClick: #handle deployment click to board once piece selected
            if self.matrix[r][c] != '-': #if square already occupied, stop
                return
            if self.turn == 1: #player 1 is deploying
                if r < 7:
                    return
                self.matrix[r][c] = 'w' + self.deployingPieceType
                x0 = (c * self.size) + int(self.size/2)
                y0 = (r * self.size) + int(self.size/2)
                imageIdentifier = self.deployingPieceType + '.png'
                self.canvas.create_image(x0, y0, image = self.white_images[imageIdentifier], tags=(self.matrix[r][c], 'piece'))
                self.turn = 2
                if self.deployingPieceType not in self.white_pieces:
                    self.white_pieces[self.deployingPieceType] = 1
                else:
                    self.white_pieces[self.deployingPieceType] += 1
            else: #player 2 is deploying
                if r > 2:
                    return
                self.matrix[r][c] = 'b' + self.deployingPieceType
                x0 = (c * self.size) + int(self.size/2)
                y0 = (r * self.size) + int(self.size/2)
                imageIdentifier = self.deployingPieceType + '.png'
                self.canvas.create_image(x0, y0, image = self.black_images[imageIdentifier], tags=(self.matrix[r][c], 'piece'))
                self.turn = 1
                if self.deployingPieceType not in self.black_pieces:
                    self.black_pieces[self.deployingPieceType] = 1
                else:
                    self.black_pieces[self.deployingPieceType] += 1

            turnText = 'Player ' + str(self.turn) + '\'s Turn' 
            self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
            self.updateDeployButton('E')
            self.updateDeployButton('P')
            self.updateDeployButton('L')
            self.updateDeployButton('M')
            self.updateDeployButton('A')
            self.updateDeployButton('G')
            self.updateDeployButton('S')
            self.updateDeployButton('T')

            self.awaitingDeployClick = False
            self.redrawBoard()
        
        #move click
        if self.playPhaseStarted: #REFACTOR, this is so bad
            print(r, c)
            if self.awaitingThiefStealDeployment: #piece from thief capture is being deployed #REFACTOR
                if self.turn == 1 and r >= 7 and self.matrix[r][c] == '-':
                    self.matrix[r][c] = self.awaitingThiefStealDeployment
                    self.awaitingThiefStealDeployment = None
                    self.redrawPieces()
                    self.redrawBoard()
                    self.turn = 2
                    turnText = 'Black to Move' 
                    self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
                elif self.turn == 2 and r <= 2 and self.matrix[r][c] == '-':
                    self.matrix[r][c] = self.awaitingThiefStealDeployment
                    self.awaitingThiefStealDeployment = None
                    self.redrawPieces()
                    self.redrawBoard()
                    self.turn = 1
                    turnText = 'White to Move' 
                    self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)
            elif self.turn == 1: #white move
                if self.pieceToMove and (r, c) in self.allowedMoves:#if a piece is currently selected and the new selection is a place to move
                    selectedPiece = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    
                     #if scholar is being moved or piece moves out of protection, then remove protection from square
                    if selectedPiece[1] == 'S' or self.whiteProtectedSquares == (self.pieceToMove[0], self.pieceToMove[1]):
                        self.whiteProtectedSquares = None

                    if self.matrix[r][c] == 'bS': #if killing enemy scholar, remove that scholars protected square
                        self.blackProtectedSquares = None
                    #if scholar is selected piece and clicking on same color piece to protect
                    if selectedPiece[1] == 'S' and self.matrix[r][c][0] == selectedPiece[0]:
                        self.whiteProtectedSquares = (r, c)
                    
                    #if theif is capturing an enemy piece
                    elif selectedPiece[1] == 'T' and self.matrix[r][c][0] == 'b':
                        self.awaitingThiefStealDeployment = 'w' + self.matrix[r][c][1]
                        self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                        self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'
                        self.redrawBoard()
                        self.colorDeployableSquares()
                    else:    #general case, move piece
                        self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                        self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'

                    #update turn text
                    if not self.awaitingThiefStealDeployment:
                        self.turn = 2
                        turnText = 'Black to Move' 
                        self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)

                    #redraw board and clean up for next turn
                    self.redrawPieces()
                    if not self.awaitingThiefStealDeployment:
                        self.redrawBoard()
                    self.pieceToMove = None
                    self.allowedMoves.clear()
                elif self.matrix[r][c][0] == 'w': #selected a piece of your color
                    self.pieceToMove = (r, c)
                    self.calcAllowedMoves()
                    self.redrawBoard()
                    self.colorPieceAndPossibleMoves(r, c)
            else: #black move
                if self.pieceToMove and (r, c) in self.allowedMoves:#if a piece is currently selected and the new selection is a place to move
                    selectedPiece = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    #if scholar is being moved or piece moves out of protection, then remove protection from square
                    if selectedPiece[1] == 'S' or self.blackProtectedSquares == (self.pieceToMove[0], self.pieceToMove[1]): 
                        self.blackProtectedSquares = None
                    
                    if self.matrix[r][c] == 'wS': #if killing enemy scholar, remove that scholars protected square
                        self.whiteProtectedSquares = None
                    #if scholar is selected piece and clicking on same color piece to protect
                    if selectedPiece[1] == 'S' and self.matrix[r][c][0] == selectedPiece[0]:
                        self.blackProtectedSquares = (r, c)
                    #if theif is capturing an enemy piece
                    elif selectedPiece[1] == 'T' and self.matrix[r][c][0] == 'w':
                        self.awaitingThiefStealDeployment = 'b' + self.matrix[r][c][1]
                        self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                        self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'
                        self.redrawBoard()
                        self.colorDeployableSquares()
                    else:    #general case, move piece
                        self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                        self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'

                    #update turn text
                    if not self.awaitingThiefStealDeployment:
                        self.turn = 1
                        turnText = 'White to Move' 
                        self.sideWidgetCanvas.itemconfigure(self.playersTurnTextID, text=turnText)

                    #redraw board and clean up for next turn
                    self.redrawPieces()
                    if not self.awaitingThiefStealDeployment:
                        self.redrawBoard()
                    self.pieceToMove = None
                    self.allowedMoves.clear()
                elif self.matrix[r][c][0] == 'b': #selected a piece of your color
                    self.pieceToMove = (r, c)
                    self.calcAllowedMoves()
                    self.redrawBoard()
                    self.colorPieceAndPossibleMoves(r, c)

    def calcAllowedMoves(self):
        r = self.pieceToMove[0]
        c = self.pieceToMove[1]
        pieceType = self.matrix[r][c][1]
        self.allowedMoves.clear()
        if pieceType == 'P':
            self.calcHorizontalorVerticalMoves(r, c, 2)
            print(self.allowedMoves)
        elif pieceType == 'A':
            self.calcHorizontalorVerticalMoves(r, c, 6)
        elif pieceType == 'G':
            self.calcHorizontalorVerticalMoves(r, c, 9)
            self.calcDiagonalMoves(r, c, 9)
        elif pieceType == 'L':
            self.calcDiagonalMoves(r, c, 9)
        elif pieceType == 'M':
            self.calcHorizontalorVerticalMoves(r, c, 2)
            self.calcDiagonalMoves(r, c, 2)
            self.checkEmperorTeleportMoves(r, c)
        elif pieceType == 'S':
            self.calcHorizontalorVerticalMoves(r, c, 2)
            self.calcDiagonalMoves(r, c, 2)
            self.calcScholarProtectMoves(r, c)
        elif pieceType == 'T':
            self.calcHorizontalorVerticalMoves(r, c, 1)
            self.calcDiagonalMoves(r, c, 1)
            #deal with thief capturing and deployment of new piece
        elif pieceType == 'E':
            self.calcHorizontalorVerticalMoves(r, c, 1)
            self.calcDiagonalMoves(r, c, 1)
            #calc so emperor cannot put itself into line of fire

    def calcScholarProtectMoves(self, r, c):
        pieceColor = self.matrix[r][c][0]
        #REFACTOR WITH EMPEROR
        protectedSquares = self.whiteProtectedSquares if pieceColor == 'w' else self.blackProtectedSquares
        for rVal in range(-1, 2):
            for cVal in range(-1, 2):
                if rVal == 0 and cVal == 0: continue
                if self.isOnBoard(r + rVal, c + cVal):
                    if self.matrix[r + rVal][c + cVal] != '-' and self.matrix[r+rVal][c+cVal][0] == pieceColor and (r+rVal, c+cVal) != protectedSquares:
                        self.allowedMoves.add((r+rVal, c+cVal))

    def checkEmperorTeleportMoves(self, r, c):
        pieceColor = self.matrix[r][c][0]
        #find the emperor of the current team
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1] == pieceColor + 'E':
                    emperorR = r1
                    emperorC = c1
        #check for empty squares adjacent to the emperor
        #REFACTOR WITH SCHOLAR
        for rVal in range(-1, 2):
            for cVal in range(-1, 2):
                if rVal == 0 and cVal == 0: continue
                if self.isOnBoard(emperorR + rVal, emperorC + cVal):
                    if self.matrix[emperorR + rVal][emperorC + cVal] == '-':
                        self.allowedMoves.add((emperorR+rVal, emperorC+cVal))

    def calcDiagonalMoves(self, r, c, distance):
        pieceColor = self.matrix[r][c][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        #REFACTOR
        for i in range(1, distance + 1): #up left
            rMove, cMove = r - i, c - i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    self.allowedMoves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((rMove, cMove))
        for i in range(1, distance + 1): #up right
            rMove, cMove = r - i, c + i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    self.allowedMoves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((rMove, cMove))
        for i in range(1, distance + 1): #down left
            rMove, cMove = r + i, c - i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    self.allowedMoves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((rMove, cMove))
        for i in range(1, distance + 1): #down right
            rMove, cMove = r + i, c + i
            if self.isOnBoard(rMove, cMove):
                if self.matrix[rMove][cMove][0] == enemyColor:
                    self.allowedMoves.add((rMove, cMove))
                    break
                elif self.matrix[rMove][cMove][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((rMove, cMove))

        #remove enemy protected square if it was listed as a possible move
        
        enemyProtectedSquare = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
        print('enemyProtectedSquare', enemyProtectedSquare)
        print(self.allowedMoves)
        if enemyProtectedSquare in self.allowedMoves: self.allowedMoves.remove(enemyProtectedSquare)

    def calcHorizontalorVerticalMoves(self, r, c, distance):
        pieceColor = self.matrix[r][c][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        #REFACTOR
        for i in range(1, distance + 1): #moves to left
            if self.isOnBoard(r, c - i):
                if self.matrix[r][c-i][0] == enemyColor:
                    self.allowedMoves.add((r, c-i))
                    break
                elif self.matrix[r][c-i][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((r, c-i))
        for i in range(1, distance + 1): #moves to right
            if self.isOnBoard(r, c + i):
                if self.matrix[r][c+i][0] == enemyColor:
                    self.allowedMoves.add((r, c+i))
                    break
                elif self.matrix[r][c+i][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((r, c+i))
        for i in range(1, distance + 1): #moves down
            if self.isOnBoard(r + i, c):
                if self.matrix[r+i][c][0] == enemyColor:
                    self.allowedMoves.add((r+i, c))
                    break
                elif self.matrix[r+i][c][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((r+i, c))
        for i in range(1, distance + 1): #moves up
            if self.isOnBoard(r - i, c):
                if self.matrix[r-i][c][0] == enemyColor:
                    self.allowedMoves.add((r-i, c))
                    break
                elif self.matrix[r-i][c][0] == pieceColor:
                    break
                else:
                    self.allowedMoves.add((r-i, c))

        enemyProtectedSquare = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
        if enemyProtectedSquare in self.allowedMoves: self.allowedMoves.remove(enemyProtectedSquare)

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
                if (row, col) == self.whiteProtectedSquares or (row, col) == self.blackProtectedSquares: #if protected square, color protected
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
        
    def refresh(self, event):
        '''Redraw the board, possibly in response to window being resized'''
        print(event.width, event.height)
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
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

    def redrawSideWidget(self, event):
        self.textX = event.width // 2
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