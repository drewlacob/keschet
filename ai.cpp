#include "ai.h"
#include <iostream>
#include <cctype>
#include <cstdlib>

Move::Move(int sRow, int sCol, int eRow, int eCol){
    m_startRow = sRow;
    m_startCol = sCol;
    m_endRow = eRow;
    m_endCol = eCol;
}

Move::Move(){
    m_startRow = -1;
    m_startCol = -1;
    m_endRow = -1;
    m_endCol = -1;
}

// ProtectedSquare::ProtectedSquare(int row, int col) {
//     m_row = row;
//     m_col = col;
// }

Piece::Piece() {
    m_type = "--";
    m_row = -1;
    m_col = -1;
    m_ai = nullptr;
}

Piece::Piece(string pieceType, int r0, int c0, ai * aiParent) {//, ai * aiCreator
    m_type = pieceType;
    m_row = r0;
    m_col = c0;
    m_ai = aiParent;
}

vector<Move> Piece::getMoves() {
    cout << "piece get moves function" << endl;
    vector<Move> moves;
    Move dummyMove(-1, -1, -1, -1);
    moves.push_back(dummyMove);
    return moves;
}

vector<Move> Pawn::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 2, false);
    cout << "Found moves for pawn on: " << m_row << " " << m_col << ":" << endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> Archer::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 6, false);
    cout << "Found moves for Archer on: " << m_row << " " << m_col << ":"<< endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> Lancer::getMoves(){
    vector<Move> moves = m_ai->calcDiagonalMoves(m_row, m_col, 9, false);
    cout << "Found moves for Lancer on: " << m_row << " " << m_col << ":"<< endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> Emperor::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 1, false);
    vector<Move> diagonalMoves = m_ai->calcDiagonalMoves(m_row, m_col, 1, false);
    moves.insert(moves.end(), diagonalMoves.begin(), diagonalMoves.end());
    cout << "Found moves for Emperor on: " << m_row << " " << m_col << ":"<< endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> Merchant::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 2, false);
    vector<Move> diagonalMoves = m_ai->calcDiagonalMoves(m_row, m_col, 2, false);
    moves.insert(moves.end(), diagonalMoves.begin(), diagonalMoves.end());
    cout << "Found moves for Merchant on: " << m_row << " " << m_col << ":";
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> Scholar::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 2, false);
    vector<Move> diagonalMoves = m_ai->calcDiagonalMoves(m_row, m_col, 2, false);
    moves.insert(moves.end(), diagonalMoves.begin(), diagonalMoves.end());
    cout << "Found moves for Scholar on: " << m_row << " " << m_col << ":"<< endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> Thief::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 1, false);
    vector<Move> diagonalMoves = m_ai->calcDiagonalMoves(m_row, m_col, 1, false);
    moves.insert(moves.end(), diagonalMoves.begin(), diagonalMoves.end());
    cout << "Found moves for Thief on: " << m_row << " " << m_col << ":"<< endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}
vector<Move> General::getMoves(){
    vector<Move> moves = m_ai->calcHorizontalOrVerticalMoves(m_row, m_col, 9, false);
    vector<Move> diagonalMoves = m_ai->calcDiagonalMoves(m_row, m_col, 9, false);
    moves.insert(moves.end(), diagonalMoves.begin(), diagonalMoves.end());
    cout << "Found moves for General on: " << m_row << " " << m_col << ":"<< endl;
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}

bool ai::isOnBoard(int r, int c) {
    if (r >= 0 && r < m_Board.size() && c >= 0 && c < m_Board[0].size())
        return true;
    else
        return false;
}

void ai::calcSlidingMovesHelper(int rowMult, int colMult, int distance, int r, int c, bool addDefendingMoves, char pieceColor, char enemyColor, vector<Move>& moves){
    // cout << "sliding moves helper with rMove: " << rowMult << " and cMove: " << colMult << endl;
    for (int i = 1; i < distance + 1; i++){
        int rMove = r + (rowMult * i);
        int cMove = c + (colMult * i);
        // cout << "rMove " << rMove << " cMove " << cMove << endl;
        if (isOnBoard(rMove, cMove)) {
            // cout << "on board" << endl;
            Move possibleMove(r, c, rMove, cMove);
            if (m_Board[rMove][cMove]->m_type[0] == enemyColor){   
                moves.push_back(possibleMove);
                // cout << "enemycolor" << endl;
                break;
            } 
            else if (m_Board[rMove][cMove]->m_type[0] == pieceColor){
                // cout << "same color" << endl;
                if (addDefendingMoves) {
                    moves.push_back(possibleMove);
                }
                break;
            }
            else if (m_Board[rMove][cMove]->m_type[0] == '-') {
                // cout << "empty square" << endl;
                moves.push_back(possibleMove);
            }
        } 
    }
    //TODO FIX IF STATEMENT BUG ABOVE
    // cout << "sliding moves" << endl;
    // for (Move i : moves) {
    //     cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    // }
}

vector<Move> ai::calcDiagonalMoves(int r, int c, int distance, bool addDefendingMoves) {
    char pieceColor = tolower(m_Board[r][c]->m_type[0]);
    char enemyColor;
    if (pieceColor == 'w') {
        enemyColor = 'b';
    } else {
        enemyColor = 'w';
    }

    vector<Move> moves;
    calcSlidingMovesHelper(-1, -1, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    calcSlidingMovesHelper(1, -1, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    calcSlidingMovesHelper(-1, 1, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    calcSlidingMovesHelper(1, 1, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
   //NOTE: may not need to remove moves that are protected, just check when adding them to the move list that the color is lowercase
    return moves;
}

vector<Move> ai::calcHorizontalOrVerticalMoves(int r, int c, int distance, bool addDefendingMoves){
    char pieceColor = tolower(m_Board[r][c]->m_type[0]);
    char enemyColor;
    if (pieceColor == 'w') {
        enemyColor = 'b';
    } else {
        enemyColor = 'w';
    }

    vector<Move> moves;
    calcSlidingMovesHelper(0, 1, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    calcSlidingMovesHelper(0, -1, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    calcSlidingMovesHelper(1, 0, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    calcSlidingMovesHelper(-1, 0, distance, r, c, addDefendingMoves, pieceColor, enemyColor, moves);
    for (Move i : moves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    return moves;
}

ai::ai(std::string boardAsString) {
    cout << "received string of: " << boardAsString << "\n";
    loadBoard(boardAsString);
    findBestMove();
    cout << "BMF: " << m_bestMove.m_startRow <<  " " << m_bestMove.m_startCol << " to " << m_bestMove.m_endRow << " " << m_bestMove.m_endCol << "\n";
}

ai::~ai() {
    for (int i = 0; i < m_Board.size(); i++){
        for (int j = 0; j < m_Board[i].size(); j++){
            delete m_Board[i][j];
        }
    }
}

void ai::findBestMove() {
    char pieceColor = 'b';
    //find the best move and leave it in m_bestMove as a string

    //for now we will find a random move for black and return that
    vector<Move> allPossibleMoves;
    for (int r = 0; r < 10; r++) {
        for (int c = 0; c < 10; c++) {
            if (tolower(m_Board[r][c]->m_type[0]) == pieceColor && (m_Board[r][c]->m_type[0] == 'b' || m_Board[r][c]->m_type[0] == 'B')) {
                
                // cout << "Calculating moves for " << r << " " << c << " type " << m_Board[r][c]->m_type[1] << endl;
                vector<Move> possibleMoves = m_Board[r][c]->getMoves();
                // cout << "cpp sucks" << endl;
                allPossibleMoves.insert(allPossibleMoves.end(), possibleMoves.begin(), possibleMoves.end());
            }
        }
    }
    cout << allPossibleMoves.size() << " total moves found:" << endl;
    for (Move i : allPossibleMoves) {
        cout << i.m_startRow << " " << i.m_startCol << " to " << i.m_endRow << " " << i.m_endCol << "\n";
    }
    int numMoves = allPossibleMoves.size();
    srand(time(NULL));
    int movePicked = rand() % numMoves;
    cout << "picking move " << movePicked << endl;

    m_bestMove = allPossibleMoves[movePicked];
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
            // if (pieceColor == 'W' || pieceColor == 'B'){ //handle protected squares, denoted by capital color
            //     // ProtectedSquare pSquare(r, c);
            //     m_ProtectedSquares.insert(make_pair(r, c));
            //     piece[0] = tolower(piece[0]);
            // }
            switch (pieceType) {
                case 'P': m_Board[r].push_back(new Pawn(piece, r, c, this)); break;
                case 'A': m_Board[r].push_back(new Archer(piece, r, c, this)); break;
                case 'G': m_Board[r].push_back(new General(piece, r, c, this)); break;
                case 'L': m_Board[r].push_back(new Lancer(piece, r, c, this)); break;
                case 'M': m_Board[r].push_back(new Merchant(piece, r, c, this)); break;
                case 'S': m_Board[r].push_back(new Scholar(piece, r, c, this)); break;
                case 'T': m_Board[r].push_back(new Thief(piece, r, c, this)); break;
                case 'E': m_Board[r].push_back(new Emperor(piece, r, c, this)); break;
                default:
                    m_Board[r].push_back(new Piece(piece, r, c, this));
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

    for (int r = 0; r < 10; r++) {
            for (int c = 0; c < 10; c++) {
                if (m_Board[r][c]->m_type[0] == 'W' || m_Board[r][c]->m_type[0] == 'B'){
                    std::cout << "Protected Square: " << r << " " << c << "\n";
                }
                
        }
     }

}