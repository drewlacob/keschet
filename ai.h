#include <stdio.h>
#include <string>
#include <vector>
#include <unordered_set>

using namespace std;

class Piece {
    public:
        string m_type;
        int m_row;
        int m_col;

        Piece();
        Piece(string pieceType, int r0, int c0);
        vector<string> getMoves();
};

class Move {
    public:
        int m_startRow;
        int m_startCol;
        int m_endRow;
        int m_endCol;

        Move(int sRow, int sCol, int eRow, int eCol);
};

class ProtectedSquare {
    public:
        int m_row;
        int m_col;
        ProtectedSquare(int row, int col);
        void printPSquare();
};

class Pawn: public Piece {
    public:
        Pawn(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class Archer: public Piece {
    public:
        Archer(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class General: public Piece {
    public:
        General(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class Lancer: public Piece {
    public:
        Lancer(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class Merchant: public Piece {
    public:
        Merchant(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class Scholar: public Piece {
    public:
        Scholar(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class Thief: public Piece {
    public:
        Thief(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};
class Emperor: public Piece {
    public:
        Emperor(string pieceType, int r0, int c0) : Piece(pieceType, r0, c0) {}
        vector<string> getMoves();
};

class ai {
    public: 
        ai(string boardAsString);
        ~ai();
        void findBestMove();
        void loadBoard(string boardAsString);
        void evaluate();
        void printBoard();
        vector<string> getPossibleMoves(int r, int c);
        bool isOnBoard(int r, int c);
        vector<Move> calcDiagonalMoves(int r, int c, int distance, bool addDefendingMoves);

    private:
        vector<vector<Piece *> > m_Board;
        unordered_set<ProtectedSquare> m_ProtectedSquares;
        int m_bestEvaluation;
        string m_bestMove;
};