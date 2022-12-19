import tkinter as tk
from tkinter import font
import os, sys
from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage
from constants import PIECE_SELECTED_COLOR, POSSIBLE_MOVE_COLOR, KILL_PIECE_COLOR, PROTECT_PIECE_COLOR, EMPEROR_ATTACKED_COLOR, BASE_WIDTH, BASE_HEIGHT, BOARD_ONE_COLOR, BOARD_TWO_COLOR

class boardDisplay(tk.Frame):
    def __init__(self, gameController, canvas):
        self.rows = 10
        self.columns = 10
        self.size = 60
        self.white_images = {}
        self.black_images = {}
        
        self.gameController = gameController #hold a reference to the parent controller
        self.gameEngine = gameController.gameEngine #hold a reference to the engine

        self.canvas = canvas
        self.canvas.bind("<Configure>", self.refresh)
        self.canvas.bind('<Button 1>', self.getorigin)
    
    def colorDeployableSquares(self):
        squares = self.canvas.find_withtag('square')
        for square in squares:
            coords = self.canvas.coords(square)
            r = int(coords[1] // self.size)
            c = int(coords[0] // self.size)
            if self.gameEngine.turn == 1 and r >= 7 and self.gameEngine.matrix[r][c] == '-':
                self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)
            if self.gameEngine.turn == 2 and r <= 2 and self.gameEngine.matrix[r][c] == '-':
                self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)

    def getorigin(self, eventorigin):
        c = eventorigin.x // self.size
        r = eventorigin.y // self.size
        print(r, c)
        self.gameEngine.handleClick(r, c)

    def clear(self):
        widgets = self.canvas.find_withtag('piece')
        for widget in widgets:
            self.canvas.delete(widget)

    def colorEmpPurpleIfAttacked(self):
        pieceColor = 'w' if self.gameEngine.turn == 1 else 'b'
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.gameEngine.matrix[r1][c1] == pieceColor + 'E':
                    emperorR = r1
                    emperorC = c1
        
        attackedSquares = self.gameEngine.calcSquaresThatEnemyAttacksOrDefends()
        if (emperorR, emperorC) in attackedSquares:
            squares = self.canvas.find_withtag('square')
            for square in squares:
                coords = self.canvas.coords(square)
                r = int(coords[1] // self.size)
                c = int(coords[0] // self.size)
                if r == emperorR and c == emperorC:
                    self.canvas.itemconfigure(square, fill=EMPEROR_ATTACKED_COLOR)

    def colorPieceAndPossibleMoves(self, r0, c0):
        pieceColor = self.gameEngine.matrix[r0][c0][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        squares = self.canvas.find_withtag('square')
        for square in squares:
            coords = self.canvas.coords(square)
            r = int(coords[1] // self.size)
            c = int(coords[0] // self.size)
            if r == r0 and c == c0:
                self.canvas.itemconfigure(square, fill=PIECE_SELECTED_COLOR)
            if (r, c) in self.gameEngine.allowedMoves:
                if self.gameEngine.matrix[r][c] == '-':
                    self.canvas.itemconfigure(square, fill=POSSIBLE_MOVE_COLOR)
                elif self.gameEngine.matrix[r][c][0] == enemyColor:
                    self.canvas.itemconfigure(square, fill=KILL_PIECE_COLOR)
                elif self.gameEngine.matrix[r][c][0] == pieceColor:
                    self.canvas.itemconfigure(square, fill=PROTECT_PIECE_COLOR)

    def redrawBoard(self):
        self.canvas.delete("square")
        color = BOARD_TWO_COLOR
        for row in range(self.rows):
            color = BOARD_ONE_COLOR if color == BOARD_TWO_COLOR else BOARD_TWO_COLOR
            if self.gameEngine.awaitingDeployClick:
                if self.gameEngine.turn == 1 and row >= 7:
                    color = POSSIBLE_MOVE_COLOR
                elif self.gameEngine.turn == 2 and row <= 2:
                    color = POSSIBLE_MOVE_COLOR
            for col in range(self.columns):
                x1 = (col * self.size)
                y1 = (row * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                if (row, col) in self.gameEngine.whiteProtectedSquares or (row, col) in self.gameEngine.blackProtectedSquares: #if protected square, color protected
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=PROTECT_PIECE_COLOR, tags="square")
                else: #else normal color
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = BOARD_ONE_COLOR if color == BOARD_TWO_COLOR else BOARD_TWO_COLOR
                if self.gameEngine.awaitingDeployClick:
                    if self.gameEngine.turn == 1 and row >= 7:
                        color = POSSIBLE_MOVE_COLOR
                    elif self.gameEngine.turn == 2 and row <= 2:
                        color = POSSIBLE_MOVE_COLOR
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def redrawPieces(self):
        self.canvas.delete('piece')
        for r in range(self.rows):
            for c in range(self.columns):
                if self.gameEngine.matrix[r][c] != '-':
                    pieceToRender = self.gameEngine.matrix[r][c]
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

    def refresh(self, event=None):
        '''Redraw the board, possibly in response to window being resized'''
        print(event.width, event.height)
        xsize = int((event.width-1) / self.columns) #if event else int((BASE_WIDTH-1) / self.columns)
        ysize = int((event.height-1) / self.rows) #if event else int((BASE_HEIGHT-1) / self.columns)
        self.size = min(xsize, ysize)
        self.redrawBoard()
        self.redrawPieces()

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
    
    def getWindowImage(self):
        return self.black_images['G.png']

    def placePiece(self, x0, y0, image):
        images = self.white_images if self.gameEngine.turn == 1 else self.black_images
        self.canvas.create_image(x0, y0, image = images[image], tags=('piece'))