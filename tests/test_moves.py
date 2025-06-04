import unittest
from chess_engine.board import Board
from chess_engine.move import Move
from chess_engine.pieces import Pawn, Rook, Knight, Bishop, Queen, King


class TestMoves(unittest.TestCase):
    """Tests for move generation, notation parsing, and special move cases."""

    def setUp(self):
        """Set up a fresh board before each test."""
        self.board = Board()

    def test_move_creation(self):
        """Test basic move creation and properties."""
        move = Move((6, 4), (4, 4))  # e2-e4
        self.assertEqual(move.start_pos, (6, 4))
        self.assertEqual(move.end_pos, (4, 4))
        self.assertFalse(move.is_capture)
        self.assertFalse(move.is_castling)
        self.assertFalse(move.is_en_passant)
        self.assertIsNone(move.promotion_piece)

    def test_move_equality(self):
        """Test move equality comparison."""
        move1 = Move((6, 4), (4, 4))
        move2 = Move((6, 4), (4, 4))
        move3 = Move((6, 3), (4, 3))
        
        self.assertEqual(move1, move2)
        self.assertNotEqual(move1, move3)

    def test_move_string_representation(self):
        """Test string representation of moves."""
        move = Move((6, 4), (4, 4))  # e2-e4
        self.assertEqual(str(move), "e2-e4")
        
        # Test with capture
        move = Move((6, 4), (5, 5), is_capture=True)  # e2xe3
        self.assertEqual(str(move), "e2xe3")

    def test_algebraic_notation_conversion(self):
        """Test conversion between coordinates and algebraic notation."""
        # Test coordinate to algebraic
        self.assertEqual(Move.coord_to_algebraic((7, 0)), "a1")
        self.assertEqual(Move.coord_to_algebraic((0, 7)), "h8")
        self.assertEqual(Move.coord_to_algebraic((4, 3)), "d4")
        
        # Test algebraic to coordinate
        self.assertEqual(Move.algebraic_to_coord("a1"), (7, 0))
        self.assertEqual(Move.algebraic_to_coord("h8"), (0, 7))
        self.assertEqual(Move.algebraic_to_coord("d4"), (4, 3))

    def test_parse_algebraic_notation(self):
        """Test parsing of algebraic notation into moves."""
        # Simple pawn move
        move = Move.from_algebraic("e4", self.board, "white")
        self.assertEqual(move.start_pos, (6, 4))
        self.assertEqual(move.end_pos, (4, 4))
        
        # Knight move
        move = Move.from_algebraic("Nf3", self.board, "white")
        self.assertEqual(move.start_pos, (7, 1))  # Knight at b1
        self.assertEqual(move.end_pos, (5, 5))    # to f3
        
        # Capture
        # Set up a capture scenario
        self.board.squares[5][5] = Pawn("black")
        move = Move.from_algebraic("Nxf3", self.board, "white")
        self.assertEqual(move.start_pos, (7, 1))
        self.assertEqual(move.end_pos, (5, 5))
        self.assertTrue(move.is_capture)

    def test_ambiguous_move_resolution(self):
        """Test resolution of ambiguous moves in algebraic notation."""
        # Set up a scenario with two knights that can move to the same square
        self.board = Board(empty=True)
        self.board.squares[7][4] = King("white")
        self.board.squares[0][4] = King("black")
        self.board.squares[3][1] = Knight("white")  # Knight at b5
        self.board.squares[3][5] = Knight("white")  # Knight at f5
        
        # Specify which knight by file
        move = Move.from_algebraic("Nbd3", self.board, "white")
        self.assertEqual(move.start_pos, (3, 1))  # Knight at b5
        self.assertEqual(move.end_pos, (5, 3))    # to d3
        
        # Specify which knight by rank
        move = Move.from_algebraic("N5d3", self.board, "white")
        self.assertEqual(move.start_pos, (3, 1))  # Knight at b5 (5th rank)
        self.assertEqual(move.end_pos, (5, 3))    # to d3

    def test_castling_notation(self):
        """Test parsing of castling notation."""
        # Set up a castling scenario
        self.board = Board(empty=True)
        self.board.squares[7][4] = King("white")
        self.board.squares[7][7] = Rook("white")
        self.board.squares[7][0] = Rook("white")
        self.board.squares[0][4] = King("black")
        
        # Kingside castling
        move = Move.from_algebraic("O-O", self.board, "white")
        self.assertEqual(move.start_pos, (7, 4))
        self.assertEqual(move.end_pos, (7, 6))
        self.assertTrue(move.is_castling)
        
        # Queenside castling
        move = Move.from_algebraic("O-O-O", self.board, "white")
        self.assertEqual(move.start_pos, (7, 4))
        self.assertEqual(move.end_pos, (7, 2))
        self.assertTrue(move.is_castling)

    def test_pawn_promotion_notation(self):
        """Test parsing of pawn promotion notation."""
        # Set up a promotion scenario
        self.board = Board(empty=True)
        self.board.squares[1][4] = Pawn("white")  # White pawn about to promote
        self.board.squares[0][4] = None           # Empty square for promotion
        self.board.squares[7][4] = King("white")
        self.board.squares[0][0] = King("black")
        
        # Promotion to queen
        move = Move.from_algebraic("e8=Q", self.board, "white")
        self.assertEqual(move.start_pos, (1, 4))
        self.assertEqual(move.end_pos, (0, 4))
        self.assertEqual(move.promotion_piece, "Queen")
        
        # Promotion to knight
        move = Move.from_algebraic("e8=N", self.board, "white")
        self.assertEqual(move.start_pos, (1, 4))
        self.assertEqual(move.end_pos, (0, 4))
        self.assertEqual(move.promotion_piece, "Knight")

    def test_check_notation(self):
        """Test parsing of check and checkmate notation."""
        # Set up a check scenario
        self.board = Board(empty=True)
        self.board.squares[7][4] = King("white")
        self.board.squares[0][4] = King("black")
        self.board.squares[1][4] = Queen("white")  # White queen giving check
        
        # Move with check
        move = Move.from_algebraic("Qe7+", self.board, "white")
        self.assertEqual(move.start_pos, (1, 4))
        self.assertEqual(move.end_pos, (1, 4))  # Same position, just adding check
        self.assertTrue(move.is_check)
        
        # Move with checkmate
        move = Move.from_algebraic("Qe7#", self.board, "white")
        self.assertEqual(move.start_pos, (1, 4))
        self.assertEqual(move.end_pos, (1, 4))
        self.assertTrue(move.is_checkmate)

    def test_en_passant_notation(self):
        """Test parsing of en passant notation."""
        # Set up an en passant scenario
        self.board = Board(empty=True)
        self.board.squares[3][4] = Pawn("white")  # White pawn at e5
        self.board.squares[3][5] = Pawn("black")  # Black pawn at f5 (just moved from f7)
        self.board.squares[7][4] = King("white")
        self.board.squares[0][4] = King("black")
        self.board.last_move = Move((1, 5), (3, 5))  # f7-f5
        
        # En passant capture
        move = Move.from_algebraic("exf6", self.board, "white")
        self.assertEqual(move.start_pos, (3, 4))
        self.assertEqual(move.end_pos, (2, 5))
        self.assertTrue(move.is_en_passant)
        self.assertTrue(move.is_capture)

    def test_pgn_move_parsing(self):
        """Test parsing moves from PGN notation."""
        pgn_moves = ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O"]
        
        # Reset board to initial position
        self.board = Board()
        
        # Parse and apply each move
        for i, pgn in enumerate(pgn_moves):
            color = "white" if i % 2 == 0 else "black"
            move = Move.from_algebraic(pgn, self.board, color)
            self.assertIsNotNone(move)
            self.board.make_move(move)
        
        # Verify final position (after O-O)
        self.assertIsInstance(self.board.squares[7][6], King)  # White king at g1
        self.assertIsInstance(self.board.squares[7][5], Rook)  # White rook at f1

    def test_move_validation(self):
        """Test validation of legal and illegal moves."""
        # Legal move: e2-e4
        move = Move((6, 4), (4, 4))
        self.assertTrue(self.board.is_valid_move(move))
        
        # Illegal move: e2-e5 (pawn can't move 3 squares)
        move = Move((6, 4), (3, 4))
        self.assertFalse(self.board.is_valid_move(move))
        
        # Illegal move: e2-d3 (pawn can't move diagonally without capture)
        move = Move((6, 4), (5, 3))
        self.assertFalse(self.board.is_valid_move(move))

    def test_move_that_exposes_check(self):
        """Test that moves exposing the king to check are invalid."""
        # Set up a scenario where moving a piece would expose check
        self.board = Board(empty=True)
        self.board.squares[7][4] = King("white")
        self.board.squares[7][5] = Bishop("white")  # Bishop protecting the king
        self.board.squares[7][7] = Rook("black")    # Black rook threatening the king
        
        # Moving the bishop would expose the king to check
        move = Move((7, 5), (6, 6))
        self.assertFalse(self.board.is_valid_move(move))

    def test_move_history(self):
        """Test recording and retrieving move history."""
        # Make a series of moves
        moves = [
            Move((6, 4), (4, 4)),  # e2-e4
            Move((1, 4), (3, 4)),  # e7-e5
            Move((7, 6), (5, 5)),  # Nf3
        ]
        
        for move in moves:
            self.board.make_move(move)
        
        # Check that move history is correct
        self.assertEqual(len(self.board.move_history), 3)
        self.assertEqual(self.board.move_history[0], moves[0])
        self.assertEqual(self.board.move_history[1], moves[1])
        self.assertEqual(self.board.move_history[2], moves[2])

    def test_undo_move(self):
        """Test undoing a move restores the previous board state."""
        # Initial state
        initial_e2_piece = self.board.squares[6][4]
        
        # Make a move
        move = Move((6, 4), (4, 4))  # e2-e4
        self.board.make_move(move)
        
        # Verify the move was made
        self.assertIsNone(self.board.squares[6][4])
        self.assertEqual(self.board.squares[4][4], initial_e2_piece)
        
        # Undo the move
        self.board.undo_move()
        
        # Verify the board is back to initial state
        self.assertEqual(self.board.squares[6][4], initial_e2_piece)
        self.assertIsNone(self.board.squares[4][4])
        self.assertEqual(len(self.board.move_history), 0)


if __name__ == "__main__":
    unittest.main()
