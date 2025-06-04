"""
Move class for chess moves.
Represents a chess move with start and end positions, piece moved, piece captured, etc.
"""

class Move:
    """
    Represents a chess move.
    """
    
    # Map ranks to rows
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    # Map rows to ranks
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    
    # Map files to columns
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    # Map columns to files
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    
    def __init__(self, start_pos, end_pos, board=None):
        """
        Initialize a move.
        
        Args:
            start_pos: Starting position (row, col)
            end_pos: Ending position (row, col)
            board: Optional board to get additional move information
        """
        self.start_row = start_pos[0]
        self.start_col = start_pos[1]
        self.end_row = end_pos[0]
        self.end_col = end_pos[1]
        
        # Additional move information
        self.piece_moved = None
        self.piece_captured = None
        self.is_castle_move = False
        self.is_en_passant_move = False
        self.is_pawn_promotion = False
        self.promotion_choice = 'Q'  # Default to queen promotion
        
        # If board is provided, get additional information
        if board:
            self.piece_moved = board.board[self.start_row][self.start_col]
            self.piece_captured = board.board[self.end_row][self.end_col]
            
            # Check for en passant
            if (self.piece_moved and self.piece_moved.piece_type == 'P' and
                (self.end_row, self.end_col) == board.en_passant_possible):
                self.is_en_passant_move = True
                self.piece_captured = board.board[self.start_row][self.end_col]
            
            # Check for castling
            if (self.piece_moved and self.piece_moved.piece_type == 'K' and
                abs(self.end_col - self.start_col) == 2):
                self.is_castle_move = True
            
            # Check for pawn promotion
            if (self.piece_moved and self.piece_moved.piece_type == 'P' and
                (self.end_row == 0 or self.end_row == 7)):
                self.is_pawn_promotion = True
    
    def get_chess_notation(self):
        """
        Get the move in chess notation (e.g., "e2e4").
        
        Returns:
            str: Move in chess notation
        """
        return (self.get_rank_file(self.start_row, self.start_col) +
                self.get_rank_file(self.end_row, self.end_col))
    
    def get_rank_file(self, row, col):
        """
        Convert row and column to rank and file notation.
        
        Args:
            row: Board row (0-7)
            col: Board column (0-7)
            
        Returns:
            str: Rank and file notation (e.g., "e4")
        """
        return self.cols_to_files[col] + self.rows_to_ranks[row]
    
    def __eq__(self, other):
        """
        Check if two moves are equal.
        
        Args:
            other: Another Move object
            
        Returns:
            bool: True if moves are equal, False otherwise
        """
        if isinstance(other, Move):
            return (self.start_row == other.start_row and
                    self.start_col == other.start_col and
                    self.end_row == other.end_row and
                    self.end_col == other.end_col)
        return False
    
    def __str__(self):
        """
        Get string representation of the move.
        
        Returns:
            str: String representation
        """
        # Castle move
        if self.is_castle_move:
            if self.end_col == 6:
                return "O-O"  # Kingside castle
            else:
                return "O-O-O"  # Queenside castle
        
        # Regular move
        end_square = self.get_rank_file(self.end_row, self.end_col)
        
        # Pawn moves
        if self.piece_moved and self.piece_moved.piece_type == 'P':
            if self.piece_captured:  # Capture
                return f"{self.cols_to_files[self.start_col]}x{end_square}"
            else:
                return end_square
        
        # Piece moves
        move_string = self.piece_moved.piece_type if self.piece_moved else ""
        
        if self.piece_captured:
            move_string += "x"
        
        return move_string + end_square
