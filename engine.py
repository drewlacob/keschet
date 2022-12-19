class engine():
    def __init__(self, gameBoard) -> None:
        self.gameBoard = gameBoard #hold a reference to game instance which created the engine
        self.rows = 10
        self.columns = 10
        self.size = 60 #size of each square is 60 pixels by when default game is initialized
        self.white_images = {} #images for player one
        self.black_images = {} #images for player two
        self.reset() #reset parts of board that differ for each game

    def handleClick(self, r: int, c: int) -> None:
        if self.deployingPieceType and not self.playPhaseStarted: #handle deployment click to board once piece selected
            if self.matrix[r][c] != '-' or (self.turnCount % 2 == 1 and r < 7) or (self.turnCount % 2 == 0 and r > 2): #if square occupied or outside of deployment bounds
                return
            self.matrix[r][c] = ('w' + self.deployingPieceType) if self.turnCount % 2 == 1 else ('b' + self.deployingPieceType) #update the board with the deployment
            x0, y0 = (c * self.size) + int(self.size/2), (r * self.size) + int(self.size/2) #find position to place image
            imageIdentifier = self.deployingPieceType + '.png'
            self.gameBoard.placePiece(x0, y0, imageIdentifier)

            #increment our count of how many of this piece type have been deployed
            curPieces = self.white_pieces if self.turnCount % 2 == 1 else self.black_pieces
            if self.deployingPieceType not in curPieces:
                curPieces[self.deployingPieceType] = 1
            else:
                curPieces[self.deployingPieceType] += 1

            # self.turn = 2 if self.turn == 1 else 1
            self.turnCount += 1

            piecesDeployed = 0 #count how many black pieces are deployed since they are second to place
            for piece in self.black_pieces:
                piecesDeployed += self.black_pieces[piece]

            if piecesDeployed == 25: #deploy phase has ended, clean up and begin play
                self.deployingPieceType = None
                self.gameBoard.sideWidget.clear()
                self.gameBoard.redrawBoard()
                self.gameBoard.beginPlay()
                self.gameBoard.redrawPieces()
                return

            #else update the side widget and redraw everything to render the piece correctly and remove the deploy highlighting
            self.gameBoard.sideWidget.updateAfterDeploy()
            self.deployingPieceType = None
            self.gameBoard.redrawBoard()
            self.gameBoard.redrawPieces()
        
        #handle click during play phase: piece selection, moving pieces, deploying pieces from thief capture
        if self.playPhaseStarted and not self.isGameOver:
            pieceColor = 'w' if self.turnCount % 2 == 1 else 'b'
            if self.deployingPieceType: #piece from thief capture is being deployed
                if (self.turnCount % 2 == 1 and r >= 7 and self.matrix[r][c] == '-') or (self.turnCount % 2 == 0 and r <= 2 and self.matrix[r][c] == '-'):
                    self.matrix[r][c] = self.deployingPieceType
                    self.deployingPieceType = None
                    self.gameBoard.redrawPieces()
                    self.gameBoard.redrawBoard()
                    self.turnCount += 1
                    self.gameBoard.sideWidget.updateTurnDisplay()

            #handle normal move during play phase
            elif self.pieceToMove and (r, c) in self.allowedMoves: #if a piece is currently selected and the new selection is a place to move
                selectedPiece = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]

                #if scholar is being moved or piece moves out of protection, then remove protection from square
                myProtectedSquares = self.whiteProtectedSquares if self.turnCount % 2 == 1 else self.blackProtectedSquares
                if selectedPiece[1] == 'S' or (self.pieceToMove[0], self.pieceToMove[1]) in myProtectedSquares:
                    myProtectedSquares.clear()
                
                #if killing enemy scholar, remove that scholars protected square
                enemyColor = 'b' if pieceColor == 'w' else 'w'
                enemyProtectedSquares = self.blackProtectedSquares if self.turnCount % 2 == 1 else self.whiteProtectedSquares
                if self.matrix[r][c] == enemyColor + 'S': 
                    enemyProtectedSquares.clear()

                #if scholar is selected piece and clicking on same color piece to protect
                if selectedPiece[1] == 'S' and self.matrix[r][c][0] == pieceColor:
                    myProtectedSquares.add((r, c)) #scholar position, protected position

                #if thief is capturing an enemy piece
                elif selectedPiece[1] == 'T' and self.matrix[r][c][0] == enemyColor:
                    self.deployingPieceType = pieceColor + self.matrix[r][c][1]
                    self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'
                    self.gameBoard.redrawBoard()
                    self.gameBoard.colorDeployableSquares()
                else:    #general case, move piece
                    self.matrix[r][c] = self.matrix[self.pieceToMove[0]][self.pieceToMove[1]]
                    self.matrix[self.pieceToMove[0]][self.pieceToMove[1]] = '-'

                #update turn text
                if not self.deployingPieceType:
                    self.turnCount += 1
                    self.gameBoard.sideWidget.updateTurnDisplay()

                #redraw board and clean up for next turn
                self.gameBoard.redrawPieces()
                if not self.deployingPieceType:
                    self.gameBoard.redrawBoard()

                #check if the game is over and handle that
                self.checkGameOver()
                if self.isGameOver:
                    self.gameBoard.sideWidget.handleGameOver()
                    return

                # clear the selected piece/moves, color emperor if in check
                self.gameBoard.colorEmpPurpleIfAttacked()
                self.pieceToMove = None
                self.allowedMoves.clear()
            elif self.matrix[r][c][0] == pieceColor: #selected a piece of your color, calculate moves and draw board with moves
                if (r, c) == self.pieceToMove: #deselect the piece currently selected
                    self.pieceToMove = None
                    self.allowedMoves.clear()
                    self.gameBoard.redrawBoard()
                    self.gameBoard.colorEmpPurpleIfAttacked()
                    return
                
                # handle the selection of a piece to move
                self.pieceToMove = (r, c)
                self.allowedMoves = self.calcAllowedMoves(r, c)
                self.gameBoard.redrawBoard()
                self.gameBoard.colorPieceAndPossibleMoves(r, c)
                self.gameBoard.colorEmpPurpleIfAttacked()

    def calcAllowedMoves(self, r: int, c: int, defended: bool=False) -> set(): #defended = True will also return squares that piece is defending 
        # defended squares are defined as squares it could move to if there is an allied piece there and that allied piece on the square was captured
        pieceType = self.matrix[r][c][1]
        if pieceType == 'P': #pawn moves
            return self.calcHorizontalorVerticalMoves(r, c, 2, defended)
        elif pieceType == 'A': #archer moves
            return self.calcHorizontalorVerticalMoves(r, c, 6, defended)
        elif pieceType == 'G': #general moves
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 9, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 9, defended)
            return rcMoves.union(diagMoves)
        elif pieceType == 'L': #lancer moves
            return self.calcDiagonalMoves(r, c, 9, defended)
        elif pieceType == 'M': #merchant moves
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 2, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 2, defended)
            tpMoves = self.checkEmperorTeleportMoves(r, c)
            return tpMoves.union(rcMoves.union(diagMoves))
        elif pieceType == 'S': #scholar moves
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 2, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 2, defended)
            spMoves = self.calcScholarProtectMoves(r, c)
            return spMoves.union(rcMoves.union(diagMoves))
        elif pieceType == 'T': #thief moves
            rcMoves = self.calcHorizontalorVerticalMoves(r, c, 1, defended)
            diagMoves = self.calcDiagonalMoves(r, c, 1, defended)
            return rcMoves.union(diagMoves)
        elif pieceType == 'E': #emperor moves
            return self.calcEmperorMoves(r, c, defended)

    def calcEmperorMoves(self, r: int, c: int, defended: bool) -> set():
        rcMoves = self.calcHorizontalorVerticalMoves(r, c, 1, defended)
        diagMoves = self.calcDiagonalMoves(r, c, 1, defended)
        possibleEmperorMoves = rcMoves.union(diagMoves) #now have the normal moves
        t = self.matrix[r][c]
        self.matrix[r][c] = '-'
        attackedOrDefendedSquares = self.calcSquaresThatEnemyAttacksOrDefends() #get squares attacked by opponent, emperor cannot move there
        self.matrix[r][c] = t
        return possibleEmperorMoves.difference(attackedOrDefendedSquares)

    def calcSquaresThatEnemyAttacksOrDefends(self) -> set(): #change to attacks or defends
        squares = set()
        enemyColor = 'w' if self.turnCount % 2 == 0 else 'b'
        #for each enemy piece, calculate its moves and add them to the set
        for r1 in range(0, self.rows):
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1][0] == enemyColor and self.matrix[r1][c1][1] != 'E':
                    moves = self.calcAllowedMoves(r1, c1, True)
                    squares = squares.union(moves)
        return squares

    def calcScholarProtectMoves(self, r: int, c: int) -> set():
        pieceColor = self.matrix[r][c][0]
        moves = set()
        protectedSquares = self.whiteProtectedSquares if pieceColor == 'w' else self.blackProtectedSquares
        #check squares adjacent to the scholar; allow protection if friendly piece that is not already protected
        for rVal in range(-1, 2):
            for cVal in range(-1, 2):
                if rVal == 0 and cVal == 0: continue
                if self.isOnBoard(r + rVal, c + cVal):
                    if self.matrix[r + rVal][c + cVal] != '-' and self.matrix[r+rVal][c+cVal][0] == pieceColor and (r+rVal, c+cVal) not in protectedSquares:
                        moves.add((r+rVal, c+cVal))
        return moves
        
    def checkEmperorTeleportMoves(self, r: int, c: int) -> set():
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

    def calcDiagonalMoves(self, r: int, c: int, distance: int, addDefendingMoves: bool) -> set():
        pieceColor = self.matrix[r][c][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        moves = set()

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
        for square in enemyProtectedSquares: #remove all squares as possible captures if the enemy scholar protects that piece
            if square in moves: moves.remove(square)

        return moves

    def calcHorizontalorVerticalMoves(self, r: int, c: int, distance: int, addDefendingMoves: bool) -> set():
        pieceColor = self.matrix[r][c][0]
        enemyColor = 'w' if pieceColor == 'b' else 'b'
        moves = set()

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
        for square in enemyProtectedSquares: #remove all squares as possible captures if the enemy scholar protects that piece
            if square in moves: moves.remove(square)

        return moves

    def isOnBoard(self, r: int, c: int) -> bool:
        if r >= 0 and r < self.rows and c >= 0 and c < self.columns:
            return True
        else:
            return False

    def checkGameOver(self) -> bool:
        wEmpFound = False
        bEmpFound = False
        for r1 in range(0, self.rows): #search the board for the emperors
            for c1 in range(0, self.columns):
                if self.matrix[r1][c1] == 'wE': wEmpFound = True
                if self.matrix[r1][c1] == 'bE': bEmpFound = True

        if not wEmpFound or not bEmpFound: #if one of the team's emperor has been captured
            self.isGameOver = True
            return True
        return False

    def setQuickDeployBoard(self) -> None:
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

    def reset(self) -> None:
        self.deployingPieceType = None #holds the piece waiting to be deployed
        self.playPhaseStarted = False
        self.matrix = [['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], #initialize the game board to all empty squares
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                       ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-']]
        self.white_pieces = {} #holds the white pieces deployed during the deployment phase #could be changed to only use one set such as deployedPieces = {}
        self.black_pieces = {} #holds the black pieces deployed during the deployment phase
        self.pieceToMove = None #holds the piece waiting to be moved
        self.allowedMoves = set() #holds the moves allowed for the current piece we are attempting to move
        self.whiteProtectedSquares = set() #holds squares protected by the white team #could be changed to just protectedSquares = {}
        self.blackProtectedSquares = set() #holds squares protected by the black team
        self.turnCount = 1 #count of the turns that have passed during the play phase
        self.isGameOver = False