import tkinter as tk
import os, sys
from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage

POSSIBLE_MOVE_COLOR = '#42e340'
BASE_WIDTH = 771
BASE_HEIGHT = 771
BASE_SIDEWIDGET_WIDTH = 360

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

        tk.Frame.__init__(self, parent)
        
        self.canvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_WIDTH, height = BASE_HEIGHT, background = 'grey')
        self.canvas.pack(side="left", fill="both", expand=True)

        self.sideWidgetCanvas = tk.Canvas(self, borderwidth = 0, highlightthickness = 0, width = BASE_SIDEWIDGET_WIDTH, height = BASE_HEIGHT, background = 'black')
        self.textX = (columns * size) // 2
        self.textY = (rows * size) // 2
        self.sideWidgetCanvas.create_text(self.textX, self.textY, text='Welcome to Keschet!', fill='white', tag='sideWidgetText')
        self.startButton = tk.Button(self.sideWidgetCanvas, text='Start Deployment', command=self.startDeploymentPhase)
        self.startButton.configure(width=15,  activebackground = "#33B5E5", relief = 'flat')
        #add quick deploy button <---- NEXT UP
        self.sideWidgetCanvas.create_window(self.textX, self.textY + size, window=self.startButton)
        self.sideWidgetCanvas.pack(side='right', fill='both', expand=True)

        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind('<Button 1>', self.getorigin)
        self.sideWidgetCanvas.bind("<Configure>", self.redrawSideWidget)

    def startDeploymentPhase(self):
        self.startButton.destroy()
        self.sideWidgetCanvas.delete('sideWidgetText')

        self.sideWidgetCanvas.create_text(self.textX, self.size, text='Deploy Pieces', fill='white', tag='sideWidgetText')
        turnText = 'Player ' + str(self.turn) + '\'s Turn' 
        self.playersTurnTextID = self.sideWidgetCanvas.create_text(self.textX, self.size*2, text=turnText, fill='white', tag='playersTurnTextID')

        #place emperor button
        placeEmperorText = 'Place Emperor | 1 Remaining'
        self.placeEmperorButton = tk.Button(self.sideWidgetCanvas, text=placeEmperorText, command=lambda : self.placePieceHelper('E'))
        self.placeEmperorButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*3, window=self.placeEmperorButton)

        #place pawn button
        placePawnText = 'Place Man-at-Arms | 8 Remaining'
        self.placePawnButton = tk.Button(self.sideWidgetCanvas, text=placePawnText, command=lambda : self.placePieceHelper('P'))
        self.placePawnButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*3.75, window=self.placePawnButton)

        #place archer button
        placeArcherText = 'Place Archer | 6 Remaining'
        self.placeArcherButton = tk.Button(self.sideWidgetCanvas, text=placeArcherText, command=lambda : self.placePieceHelper('A'))
        self.placeArcherButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*4.5, window=self.placeArcherButton)

        #place lancer button
        placeLancerText = 'Place Lancer | 4 Remaining'
        self.placeLancerButton = tk.Button(self.sideWidgetCanvas, text=placeLancerText, command=lambda : self.placePieceHelper('L'))
        self.placeLancerButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*5.25, window=self.placeLancerButton)

        #place merchant button
        placeMerchantText = 'Place Merchant | 2 Remaining'
        self.placeMerchantButton = tk.Button(self.sideWidgetCanvas, text=placeMerchantText, command=lambda : self.placePieceHelper('M'))
        self.placeMerchantButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*6, window=self.placeMerchantButton)

        #place merchant button
        placeGeneralText = 'Place General | 1 Remaining'
        self.placeGeneralButton = tk.Button(self.sideWidgetCanvas, text=placeGeneralText, command=lambda : self.placePieceHelper('G'))
        self.placeGeneralButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*6.75, window=self.placeGeneralButton)

        #place merchant button
        placeScholarText = 'Place Scholar | 1 Remaining'
        self.placeScholarButton = tk.Button(self.sideWidgetCanvas, text=placeScholarText, command=lambda : self.placePieceHelper('S'))
        self.placeScholarButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*7.5, window=self.placeScholarButton)

        #place merchant button
        placeThiefText = 'Place Thief | 3 Remaining'
        self.placeThiefButton = tk.Button(self.sideWidgetCanvas, text=placeThiefText, command=lambda : self.placePieceHelper('T'))
        self.placeThiefButton.configure(width=30,  activebackground = "#33B5E5", relief = 'flat')
        self.sideWidgetCanvas.create_window(self.textX, self.size*8.25, window=self.placeThiefButton)

        #start button?

    def placePieceHelper(self, pieceType):
        print('Player ' + str(self.turn) + ' is attempting to place a ' + pieceType)
        squares = self.canvas.find_withtag('square')
        for square in squares:
            coords = self.canvas.coords(square)
            c = int(coords[1] // self.size)
            r = int(coords[0] // self.size)
            # print(r, c)
            if self.turn == 1 and c >= 7 and self.matrix[c][r] == '-':
                self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)
            if self.turn == 2 and c <= 2 and self.matrix[c][r] == '-':
                self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)
        self.deployingPieceType = pieceType
        self.awaitingDeployClick = True

    def getorigin(self, eventorigin):
        self.mouseX = eventorigin.x
        self.mouseY = eventorigin.y

        if self.awaitingDeployClick: #handle deployment click to board once piece selected
            c = self.mouseX // self.size
            r = self.mouseY // self.size
            print('deploy click to ', r, c)
            if self.matrix[r][c] != '-': #if square already occupied, stop
                print('square already deployed to')
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

            if self.turn == 1: #if white is next to deploy, update deployment buttons
                deployedEmperors = self.white_pieces.get('E', 0)
                deployedPawns = self.white_pieces.get('P', 0)
                deployedLancers = self.white_pieces.get('L', 0)
                deployedMerchants = self.white_pieces.get('M', 0)
                deployedArchers = self.white_pieces.get('A', 0)
                deployedGenerals = self.white_pieces.get('G', 0)
                deployedScholars = self.white_pieces.get('S', 0)
                deployedThieves = self.white_pieces.get('T', 0)
            else:
                deployedEmperors = self.black_pieces.get('E', 0)
                deployedPawns = self.black_pieces.get('P', 0)
                deployedLancers = self.black_pieces.get('L', 0)
                deployedMerchants = self.black_pieces.get('M', 0)
                deployedArchers = self.black_pieces.get('A', 0)
                deployedGenerals = self.black_pieces.get('G', 0)
                deployedScholars = self.black_pieces.get('S', 0)
                deployedThieves = self.black_pieces.get('T', 0)

            self.updateDeployButton('E', self.placeEmperorButton, deployedEmperors)
            self.updateDeployButton('P', self.placePawnButton, deployedPawns)
            self.updateDeployButton('L', self.placeLancerButton, deployedLancers)
            self.updateDeployButton('M', self.placeMerchantButton, deployedMerchants)
            self.updateDeployButton('A', self.placeArcherButton, deployedArchers)
            self.updateDeployButton('G', self.placeGeneralButton, deployedGenerals)
            self.updateDeployButton('S', self.placeScholarButton, deployedScholars)
            self.updateDeployButton('T', self.placeThiefButton, deployedThieves)

            self.awaitingDeployClick = False
            self.redrawBoard()
            # print(self.matrix)

    def updateDeployButton(self, pieceType, deployButton, deployedCount):
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

        deployButton.config(text=newText)
        if remainingPiecesToDeploy:
            deployButton['state'] = 'normal'
        else:
            deployButton['state'] = 'disabled'

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
        # print(event.width, event.height)
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