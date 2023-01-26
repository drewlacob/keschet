#include <stdio.h>
#include <string>
#include <vector>
#include <unordered_set>
#include <set>

using namespace std;

class Move {
    public:
        int m_startRow;
        int m_startCol;
        int m_endRow;
        int m_endCol;

        Move();
        Move(int sRow, int sCol, int eRow, int eCol);
};
class ai;
class Piece {
    public:
        string m_type;
        int m_row;
        int m_col;
        ai * m_ai;

        Piece();
        Piece(string pieceType, int r0, int c0, ai * aiParent);
        virtual vector<Move> getMoves();
};

class Pawn: public Piece {
    public:
        Pawn(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class Archer: public Piece {
    public:
        Archer(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class General: public Piece {
    public:
        General(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class Lancer: public Piece {
    public:
        Lancer(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class Merchant: public Piece {
    public:
        Merchant(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class Scholar: public Piece {
    public:
        Scholar(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class Thief: public Piece {
    public:
        Thief(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};
class Emperor: public Piece {
    public:
        Emperor(string pieceType, int r0, int c0, ai * aiParent) : Piece(pieceType, r0, c0, aiParent) {}
        vector<Move> getMoves();
};

class ai {
    public: 
        ai(string boardAsString);
        ~ai();
        void findBestMove();
        void loadBoard(string boardAsString);
        void evaluate();
        void printBoard();
        // vector<Move> getPossibleMoves(int r, int c);
        bool isOnBoard(int r, int c);
        vector<Move> calcDiagonalMoves(int r, int c, int distance, bool addDefendingMoves);
        void calcSlidingMovesHelper(int rowMult, int colMult, int distance, int r, int c, bool addDefendingMoves, char pieceColor, char enemyColor, vector<Move> &moves);
        vector<Move> calcHorizontalOrVerticalMoves(int r, int c, int distance, bool addDefendingMoves);

    private:
        vector<vector<Piece *> > m_Board;
        set<pair <int, int> > m_ProtectedSquares; //possibly change to unordered set and create hash function for protected square class
        int m_bestEvaluation;
        Move m_bestMove;
};