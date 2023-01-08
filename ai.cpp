#include "ai.h"
#include <iostream>

Move::Move(int sRow, int sCol, int eRow, int eCol){
    m_startRow = sRow;
    m_startCol = sCol;
    m_endRow = eRow;
    m_endCol = eCol;
}

ProtectedSquare::ProtectedSquare(int row, int col) {
    m_row = row;
    m_col = col;
}

void ProtectedSquare::printPSquare(){
    cout << "Protected square: " << m_row << " " << m_col << "\n";
}

Piece::Piece() {
    m_type = "--";
    m_row = -1;
    m_col = -1;
}

Piece::Piece(string pieceType, int r0, int c0) {
    m_type = pieceType;
    m_row = r0;
    m_col = c0;
}

vector<string> Piece::getMoves() {
    vector<string> moves;
    return moves;
}

bool ai::isOnBoard(int r, int c) {
    if (r >= 0 && r < m_Board.size() && c >= 0 && c < m_Board[0].size())
        return true;
    else
    {
        return false;
    }
    
}

vector<Move> ai::calcDiagonalMoves(int r, int c, int distance, bool addDefendingMoves) {
    char pieceColor = m_Board[r][c]->m_type[0];
    char enemyColor;
    if (pieceColor == 'w') {
        enemyColor = 'b';
    } else {
        enemyColor = 'w';
    }

    vector<Move> moves;

    for (int i = 0; i < distance + 1; i++){
        int rMove = r - i;
        int cMove = c - i;
        if (isOnBoard(rMove, cMove)) {
            Move possibleMove(r, c, rMove, cMove);
            if (m_Board[rMove][cMove]->m_type[0] == enemyColor){   
                moves.push_back(possibleMove);
                break;
            } 
            else if (m_Board[rMove][cMove]->m_type[0] == pieceColor){
                if (addDefendingMoves) {
                    moves.push_back(possibleMove);
                }
                break;
            }
            else {
                moves.push_back(possibleMove);
            }
        } 
    }
    for (int i = 0; i < distance + 1; i++){
        int rMove = r - i;
        int cMove = c + i;
        if (isOnBoard(rMove, cMove)) {
            Move possibleMove(r, c, rMove, cMove);
            if (m_Board[rMove][cMove]->m_type[0] == enemyColor){   
                moves.push_back(possibleMove);
                break;
            } 
            else if (m_Board[rMove][cMove]->m_type[0] == pieceColor){
                if (addDefendingMoves) {
                    moves.push_back(possibleMove);
                }
                break;
            }
            else {
                moves.push_back(possibleMove);
            }
        } 
    }
    for (int i = 0; i < distance + 1; i++){
        int rMove = r + i;
        int cMove = c - i;
        if (isOnBoard(rMove, cMove)) {
            Move possibleMove(r, c, rMove, cMove);
            if (m_Board[rMove][cMove]->m_type[0] == enemyColor){   
                moves.push_back(possibleMove);
                break;
            } 
            else if (m_Board[rMove][cMove]->m_type[0] == pieceColor){
                if (addDefendingMoves) {
                    moves.push_back(possibleMove);
                }
                break;
            }
            else {
                moves.push_back(possibleMove);
            }
        } 
    }
    for (int i = 0; i < distance + 1; i++){
        int rMove = r + i;
        int cMove = c + i;
        if (isOnBoard(rMove, cMove)) {
            Move possibleMove(r, c, rMove, cMove);
            if (m_Board[rMove][cMove]->m_type[0] == enemyColor){   
                moves.push_back(possibleMove);
                break;
            } 
            else if (m_Board[rMove][cMove]->m_type[0] == pieceColor){
                if (addDefendingMoves) {
                    moves.push_back(possibleMove);
                }
                break;
            }
            else {
                moves.push_back(possibleMove);
            }
        } 
    }

    //TODO: pass protected squares to AI and deal with that
// enemyProtectedSquares = self.whiteProtectedSquares if pieceColor == 'b' else self.blackProtectedSquares
//         for square in enemyProtectedSquares: #remove all squares as possible captures if the enemy scholar protects that piece
//             if square in moves: moves.remove(square)
    for (int i = 0; i < moves.size(); i++){

    }
    return moves;
}

ai::ai(std::string boardAsString) {
    cout << "received string of: " << boardAsString << "\n";
    loadBoard(boardAsString);
    findBestMove();
    cout << "best move found: " << m_bestMove << "\n";
}

ai::~ai() {
    for (int i = 0; i < m_Board.size(); i++){
        for (int j = 0; j < m_Board[i].size(); j++){
            delete m_Board[i][j];
        }
    }
}

void ai::findBestMove() {
    //find the best move and leave it in m_bestMove as a string

    //for now we will find a random move for black and return that
    vector<string> allPossibleMoves;
    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 10; c++) {
            vector<string> possibleMoves = getPossibleMoves(r, c);
            allPossibleMoves.insert(allPossibleMoves.end(), possibleMoves.begin(), possibleMoves.end());
        }
    }

    // random_shuffle(allPossibleMoves.begin(), allPossibleMoves.end());
    // m_bestMove = allPossibleMoves.begin();
    m_bestMove = allPossibleMoves[0];
}

vector<string> ai::getPossibleMoves(int r, int c) {
    vector<string> moves;
    moves.push_back("3,4,3,5");
    return moves;
}

void ai::loadBoard(std::string boardAsString) {
    int index = 0;
    for (int r = 0; r < 10; r++) {
        vector<Piece *> nextRow;
        m_Board.push_back(nextRow);
        for (int c = 0; c < 10; c++) {
            string piece = boardAsString.substr(index, 2);
            char pieceType = piece.at(1);
            char pieceColor = piece.at(0);
            if (pieceColor == 'W' || pieceColor == 'B'){ //handle protected squares, denoted by capital color
                ProtectedSquare pSquare(r, c);
                m_ProtectedSquares.insert(pSquare);
                piece[0] = tolower(piece[0]);
            }
            switch (pieceType) {
                case 'P': m_Board[r].push_back(new Pawn(piece, r, c)); break;
                case 'A': m_Board[r].push_back(new Archer(piece, r, c)); break;
                case 'G': m_Board[r].push_back(new General(piece, r, c)); break;
                case 'L': m_Board[r].push_back(new Lancer(piece, r, c)); break;
                case 'M': m_Board[r].push_back(new Merchant(piece, r, c)); break;
                case 'S': m_Board[r].push_back(new Scholar(piece, r, c)); break;
                case 'T': m_Board[r].push_back(new Thief(piece, r, c)); break;
                case 'E': m_Board[r].push_back(new Emperor(piece, r, c)); break;
                default:
                    m_Board[r].push_back(new Piece(piece, r, c));
            }
            index += 2;
        }
    }
    std::cout << "board loaded!";
    printBoard();
}

void ai::printBoard(){
         for (int r = 0; r < 10; r++) {
            std::cout << "\n";
            for (int c = 0; c < 10; c++) {
                std::cout << m_Board[r][c]->m_type << " ";
        }
     }
     std::cout << "\n";
     for (auto itr = m_ProtectedSquares.begin(); itr != m_ProtectedSquares.end(); ++itr) {
         ProtectedSquare square = *itr;
         square.printPSquare();
     }
     //TODO: avoid using unordered set, waste some memory and use a big vector i guess
     // maybe just leave the things capitalized in the cpp version
     // and dont event worry about it except whenever accessing color just use a lower()
}