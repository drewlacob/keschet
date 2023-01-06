#include "ai.h"
#include <iostream>

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

ai::ai(std::string boardAsString) {
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
        m_Board.push_back({});
        for (int c = 0; c < 10; c++) {
            string piece = boardAsString.substr(index, 2);
            char pieceType = piece.at(1);
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
}