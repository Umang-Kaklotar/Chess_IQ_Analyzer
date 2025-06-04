"""
Chess pieces module.
Defines classes for each chess piece type with their movement patterns.
"""

class Piece:
    """Base class for all chess pieces."""
    
    def __init__(self, color):
        """
        Initialize a chess piece.
        
        Args:
            color: Piece color ('w' for white, 'b' for black)
        """
        self.color = color
        self.piece_type = None
        self.has_moved = False
    
    def __str__(self):
        """String representation of the piece."""
        return f"{self.color}{self.piece_type}"


class Pawn(Piece):
    """Pawn chess piece."""
    
    def __init__(self, color):
        """Initialize a pawn."""
        super().__init__(color)
        self.piece_type = 'P'


class Rook(Piece):
    """Rook chess piece."""
    
    def __init__(self, color):
        """Initialize a rook."""
        super().__init__(color)
        self.piece_type = 'R'


class Knight(Piece):
    """Knight chess piece."""
    
    def __init__(self, color):
        """Initialize a knight."""
        super().__init__(color)
        self.piece_type = 'N'


class Bishop(Piece):
    """Bishop chess piece."""
    
    def __init__(self, color):
        """Initialize a bishop."""
        super().__init__(color)
        self.piece_type = 'B'


class Queen(Piece):
    """Queen chess piece."""
    
    def __init__(self, color):
        """Initialize a queen."""
        super().__init__(color)
        self.piece_type = 'Q'


class King(Piece):
    """King chess piece."""
    
    def __init__(self, color):
        """Initialize a king."""
        super().__init__(color)
        self.piece_type = 'K'
