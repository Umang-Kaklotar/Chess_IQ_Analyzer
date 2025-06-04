import unittest
from chess_engine.board import Board
from chess_engine.move import Move
from chess_engine.pieces import Pawn, Rook, Knight, Bishop, Queen, King


class TestBoard(unittest.TestCase):
    """Unit tests for board setup, move validation, and position updates."""

    def setUp(self):
        """Set up a fresh board before each test."""
        self.board = Board()

    def test_initial_board_setup(self):
        """Test that the board is correctly initialized with all pieces."""
        # Test board dimensions
        self.assertEqual(len(self.board.squares), 8)
        self.assertEqual(len(self.board.squares[0]), 8)

        # Test white pawns
        for col in range(8):
            self.assertIsInstance(self.board.squares[6][col], Pawn)
            self.assertEqual(self.board.squares[6][col].color, "white")

        # Test black pawns
        for col in range(8):
            self.assertIsInstance(self.board.squares[1][col], Pawn)
            self.assertEqual(self.board.squares[1][col].color, "black")

        # Test white pieces
        self.assertIsInstance(self.board.squares[7][0], Rook)
        self.assertIsInstance(self.board.squares[7][1], Knight)
        self.assertIsInstance(self.board.squares[7][2], Bishop)
        self.assertIsInstance(self.board.squares[7][3], Queen)
        self.assertIsInstance(self.board.squares[7][4], King)
        self.assertIsInstance(self.board.squares[7][5], Bishop)
        self.assertIsInstance(self.board.squares[7][6], Knight)
        self.assertIsInstance(self.board.squares[7][7], Rook)

        # Test black pieces
        self.assertIsInstance(self.board.squares[0][0], Rook)
        self.assertIsInstance(self.board.squares[0][1], Knight)
        self.assertIsInstance(self.board.squares[0][2], Bishop)
        self.assertIsInstance(self.board.squares[0][3], Queen)
        self.assertIsInstance(self.board.squares[0][4], King)
        self.assertIsInstance(self.board.squares[0][5], Bishop)
        self.assertIsInstance(self.board.squares[0][6], Knight)
        self.assertIsInstance(self.board.squares[0][7], Rook)

        # Test empty squares
        for row in range(2, 6):
            for col in range(8):
                self.assertIsNone(self.board.squares[row][col])

    def test_get_legal_moves_pawn(self):
        """Test legal moves for pawns in different positions."""
        # Test initial pawn moves (two squares forward)
        pawn_moves = self.board.get_legal_moves((6, 0))  # White pawn at a2
        self.assertEqual(len(pawn_moves), 2)
        self.assertIn((5, 0), [move.end_pos for move in pawn_moves])  # a3
        self.assertIn((4, 0), [move.end_pos for move in pawn_moves])  # a4

        # Test pawn capture
        # Place a black piece in capture range
        self.board.squares[5][1] = Pawn("black")
        pawn_moves = self.board.get_legal_moves((6, 0))  # White pawn at a2
        self.assertEqual(len(pawn_moves), 3)
        self.assertIn((5, 1), [move.end_pos for move in pawn_moves])  # Capture at b3

    def test_get_legal_moves_knight(self):
        """Test legal moves for knights."""
        # Knight at b1
        knight_moves = self.board.get_legal_moves((7, 1))
        self.assertEqual(len(knight_moves), 2)
        self.assertIn((5, 0), [move.end_pos for move in knight_moves])  # a3
        self.assertIn((5, 2), [move.end_pos for move in knight_moves])  # c3

    def test_get_legal_moves_bishop(self):
        """Test legal moves for bishops."""
        # Clear some space for the bishop
        self.board.squares[6][2] = None  # Remove pawn in front of bishop
        bishop_moves = self.board.get_legal_moves((7, 2))  # White bishop at c1
        self.assertTrue(len(bishop_moves) > 0)
        # Bishop should be able to move diagonally
        self.assertIn((6, 1), [move.end_pos for move in bishop_moves])  # b2
        self.assertIn((5, 0), [move.end_pos for move in bishop_moves])  # a3

    def test_get_legal_moves_rook(self):
        """Test legal moves for rooks."""
        # Clear some space for the rook
        self.board.squares[6][0] = None  # Remove pawn in front of rook
        rook_moves = self.board.get_legal_moves((7, 0))  # White rook at a1
        self.assertTrue(len(rook_moves) > 0)
        # Rook should be able to move vertically
        self.assertIn((6, 0), [move.end_pos for move in rook_moves])  # a2
        self.assertIn((5, 0), [move.end_pos for move in rook_moves])  # a3

    def test_get_legal_moves_queen(self):
        """Test legal moves for queens."""
        # Clear some space for the queen
        self.board.squares[6][3] = None  # Remove pawn in front of queen
        queen_moves = self.board.get_legal_moves((7, 3))  # White queen at d1
        self.assertTrue(len(queen_moves) > 0)
        # Queen should be able to move vertically
        self.assertIn((6, 3), [move.end_pos for move in queen_moves])  # d2
        self.assertIn((5, 3), [move.end_pos for move in queen_moves])  # d3

    def test_get_legal_moves_king(self):
        """Test legal moves for kings."""
        # Clear some space for the king
        self.board.squares[6][4] = None  # Remove pawn in front of king
        king_moves = self.board.get_legal_moves((7, 4))  # White king at e1
        self.assertTrue(len(king_moves) > 0)
        # King should be able to move one square vertically
        self.assertIn((6, 4), [move.end_pos for move in king_moves])  # e2

    def test_make_move(self):
        """Test making a move updates the board correctly."""
        # Move pawn from e2 to e4
        start_pos = (6, 4)
        end_pos = (4, 4)
        pawn = self.board.squares[start_pos[0]][start_pos[1]]
        move = Move(start_pos, end_pos)
        
        self.board.make_move(move)
        
        # Check that the pawn is now at e4
        self.assertIsNone(self.board.squares[start_pos[0]][start_pos[1]])
        self.assertEqual(self.board.squares[end_pos[0]][end_pos[1]], pawn)

    def test_is_check(self):
        """Test detection of check condition."""
        # Set up a check scenario
        self.board = Board(empty=True)  # Start with empty board
        self.board.squares[0][4] = King("black")
        self.board.squares[7][4] = King("white")
        self.board.squares[0][0] = Rook("white")  # White rook checking black king
        
        self.assertTrue(self.board.is_check("black"))
        self.assertFalse(self.board.is_check("white"))

    def test_is_checkmate(self):
        """Test detection of checkmate condition."""
        # Set up a checkmate scenario
        self.board = Board(empty=True)  # Start with empty board
        self.board.squares[0][4] = King("black")
        self.board.squares[7][4] = King("white")
        self.board.squares[0][0] = Rook("white")  # White rook at a8
        self.board.squares[1][0] = Rook("white")  # White rook at a7
        
        self.assertTrue(self.board.is_checkmate("black"))
        self.assertFalse(self.board.is_checkmate("white"))

    def test_is_stalemate(self):
        """Test detection of stalemate condition."""
        # Set up a stalemate scenario
        self.board = Board(empty=True)  # Start with empty board
        self.board.squares[0][0] = King("black")
        self.board.squares[2][1] = King("white")
        self.board.squares[1][2] = Queen("white")
        
        self.assertTrue(self.board.is_stalemate("black"))
        self.assertFalse(self.board.is_stalemate("white"))

    def test_pawn_promotion(self):
        """Test pawn promotion."""
        # Set up a pawn promotion scenario
        self.board = Board(empty=True)  # Start with empty board
        self.board.squares[1][0] = Pawn("white")  # White pawn about to promote
        self.board.squares[0][4] = King("black")
        self.board.squares[7][4] = King("white")
        
        move = Move((1, 0), (0, 0), promotion_piece="Queen")
        self.board.make_move(move)
        
        # Check that the pawn was promoted to a queen
        self.assertIsInstance(self.board.squares[0][0], Queen)
        self.assertEqual(self.board.squares[0][0].color, "white")

    def test_castling(self):
        """Test castling moves."""
        # Set up a castling scenario
        self.board = Board(empty=True)  # Start with empty board
        self.board.squares[7][4] = King("white")
        self.board.squares[7][7] = Rook("white")
        
        # Kingside castling
        move = Move((7, 4), (7, 6), is_castling=True)
        self.board.make_move(move)
        
        # Check that both king and rook moved correctly
        self.assertIsInstance(self.board.squares[7][6], King)
        self.assertIsInstance(self.board.squares[7][5], Rook)
        self.assertIsNone(self.board.squares[7][4])
        self.assertIsNone(self.board.squares[7][7])

    def test_en_passant(self):
        """Test en passant capture."""
        # Set up an en passant scenario
        self.board = Board(empty=True)  # Start with empty board
        self.board.squares[3][1] = Pawn("white")
        self.board.squares[1][2] = Pawn("black")
        
        # Move black pawn two squares forward
        move = Move((1, 2), (3, 2))
        self.board.make_move(move)
        
        # White pawn captures en passant
        en_passant_move = Move((3, 1), (2, 2), is_en_passant=True)
        self.board.make_move(en_passant_move)
        
        # Check that the capture worked correctly
        self.assertIsInstance(self.board.squares[2][2], Pawn)
        self.assertEqual(self.board.squares[2][2].color, "white")
        self.assertIsNone(self.board.squares[3][1])  # Original white pawn position is empty
        self.assertIsNone(self.board.squares[3][2])  # Captured black pawn is gone


if __name__ == "__main__":
    unittest.main()
