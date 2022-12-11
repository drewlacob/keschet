class engine():
    def __init__(self, gameBoard):
        #TODO refactor and comment this out
        # refactor move calculations if possible 
        #then move to factoring out game board display from gameBoard.py
        self.gameBoard = gameBoard 
        self.rows = 10
        self.columns = 10
        self.size = 60 #size is 60 pixels by when game is initialized
        self.white_images = {} #images for player one
        self.black_images = {} #images for player two
        self.reset() #reset parts of board that differ for each game

    def handleClick(self, r, c):
        if self.awaitingDeployClick: #handle deployment click to board once piece selected
            if self.matrix[r][c] != '-' or (self.turn == 1 and r < 7) or (self.turn == 2 and r > 2): #if square occupied or outside of deployment bounds
                return
            self.matrix[r][c] = ('w' + self.deployingPieceType) if self.turn == 1 else ('b' + self.deployingPieceType)
            x0 = (c * self.size) + int(self.size/2)
            y0 = (r * self.size) + int(self.size/2)
            imageIdentifier = self.deployingPieceType + '.png'
            images = self.gameBoard.white_images if self.turn == 1 else self.gameBoard.black_images
            self.gameBoard.canvas.create_image(x0, y0, image = images[imageIdentifier], tags=(self.matrix[r][c], 'piece'))
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
            if piecesDeployed == 2: #TODO: change back to 26
                self.awaitingDeployClick = False
                self.gameBoard.sideWidget.clear()
                self.gameBoard.redrawBoard()
                self.gameBoard.beginPlay()
                self.gameBoard.redrawPieces()
                return

            self.gameBoard.sideWidget.updateAfterDeploy()
            self.awaitingDeployClick = False
            self.gameBoard.redrawBoard()
            self.gameBoard.redrawPieces()
        
        #move click
        if self.playPhaseStarted and not self.isGameOver:
            print(r, c)
            pieceColor = 'w' if self.turn == 1 else 'b'
            if self.awaitingThiefStealDeployment: #piece from thief capture is being deployed #REFACTOR
                if (self.turn == 1 and r >= 7 and self.matrix[r][c] == '-') or (self.turn == 2 and r <= 2 and self.matrix[r][c] == '-'):
                    self.matrix[r][c] = self.awaitingThiefStealDeployment
                    self.awaitingThiefStealDeployment = None
                    self.gameBoard.redrawPieces()
                    self.gameBoard.redrawBoard()
                    self.gameBoard.sideWidget.updateAfterDeploy()

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
                    self.gameBoard.redrawBoard()
                    self.colorDeployableSquares()
                else:    #general case, move piece
                    self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'

                #update turn text
                if not self.awaitingThiefStealDeployment: #REFACTOR: make the following display updates into a function
                    self.turn = 2 if self.turn == 1 else 1
                    self.turnCount += 1
                    self.gameBoard.sideWidget.updateTurnDisplay()

                #redraw board and clean up for next turn
                self.gameBoard.redrawPieces()
                if not self.awaitingThiefStealDeployment:
                    self.gameBoard.redrawBoard()

                #move was made, clear the selected piece
                self.checkGameOver()
                if self.isGameOver:
                    self.gameBoard.sideWidget.handleGameOver()
                    return
                self.gameBoard.colorEmpPurpleIfAttacked()
                self.pieceToMove = None
                self.allowedMoves.clear()
            elif self.matrix[r][c][0] == pieceColor: #selected a piece of your color, calculate moves and draw board with moves
                if (r, c) == self.pieceToMove:
                    self.pieceToMove = None
                    self.allowedMoves.clear()
                    self.gameBoard.redrawBoard()
                    self.gameBoard.colorEmpPurpleIfAttacked()
                    return
                self.pieceToMove = (r, c)
                self.allowedMoves.clear()
                self.allowedMoves = self.calcAllowedMoves(r, c)
                self.gameBoard.redrawBoard()
                self.gameBoard.colorPieceAndPossibleMoves(r, c)
                self.gameBoard.colorEmpPurpleIfAttacked()

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
        
        enemyProtectedSquares = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
        for square in enemyProtectedSquares:
            if square in moves: moves.remove(square)

        return moves

    def isOnBoard(self, r, c):
        if r >= 0 and r < self.rows and c >= 0 and c < self.columns:
            return True
        else:
            return False

    def checkGameOver(self):
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

    def reset(self):
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