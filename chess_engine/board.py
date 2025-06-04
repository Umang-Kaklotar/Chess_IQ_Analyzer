"""
Chess board representation and state management.
Handles an 8x8 chess board, initializes pieces, updates positions, and provides legal move validation.
"""

from .pieces import Pawn, Rook, Knight, Bishop, Queen, King
from .move import Move

class Board:
    """
    Represents a chess board with pieces and their positions.
    Manages the state of the game board.
    """
    
    def __init__(self):
        """Initialize a new chess board with pieces in starting positions."""
        # 8x8 board representation
        # Each square contains either a piece or None for empty
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.move_log = []
        self.white_to_move = True
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.en_passant_possible = ()  # coordinates for the square where en passant capture is possible
        self.en_passant_log = []
        self.current_castling_rights = CastlingRights(True, True, True, True)
        self.castling_rights_log = [CastlingRights(self.current_castling_rights.wks, 
                                                  self.current_castling_rights.bks,
                                                  self.current_castling_rights.wqs, 
                                                  self.current_castling_rights.bqs)]
        self._initialize_board()
    
    def _initialize_board(self):
        """Initialize the board with pieces in their starting positions."""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Pawn('b')  # Black pawns
            self.board[6][col] = Pawn('w')  # White pawns
        
        # Place rooks
        self.board[0][0] = Rook('b')
        self.board[0][7] = Rook('b')
        self.board[7][0] = Rook('w')
        self.board[7][7] = Rook('w')
        
        # Place knights
        self.board[0][1] = Knight('b')
        self.board[0][6] = Knight('b')
        self.board[7][1] = Knight('w')
        self.board[7][6] = Knight('w')
        
        # Place bishops
        self.board[0][2] = Bishop('b')
        self.board[0][5] = Bishop('b')
        self.board[7][2] = Bishop('w')
        self.board[7][5] = Bishop('w')
        
        # Place queens
        self.board[0][3] = Queen('b')
        self.board[7][3] = Queen('w')
        
        # Place kings
        self.board[0][4] = King('b')
        self.board[7][4] = King('w')
    
    def get_piece_at(self, row, col):
        """
        Get the piece at a specific position.
        
        Args:
            row: Board row (0-7)
            col: Board column (0-7)
            
        Returns:
            Piece object or None if square is empty
        """
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def is_valid_move(self, move):
        """
        Check if a move is valid.
        
        Args:
            move: Move to check
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Check if the move is within the board boundaries
        if not (0 <= move.start_row < 8 and 0 <= move.start_col < 8 and 
                0 <= move.end_row < 8 and 0 <= move.end_col < 8):
            return False
            
        # Get the piece at the start position
        piece = self.get_piece_at(move.start_row, move.start_col)
        if not piece:
            return False
            
        # Check if it's the correct player's turn
        if (piece.color == 'w' and not self.white_to_move) or \
           (piece.color == 'b' and self.white_to_move):
            return False
            
        # Check if the destination has a piece of the same color
        dest_piece = self.get_piece_at(move.end_row, move.end_col)
        if dest_piece and dest_piece.color == piece.color:
            return False
            
        # Get all valid moves for this piece
        valid_moves = self.get_valid_moves(pos=(move.start_row, move.start_col))
        
        # Check if the move is in the list of valid moves
        for valid_move in valid_moves:
            if move.start_row == valid_move.start_row and move.start_col == valid_move.start_col and \
               move.end_row == valid_move.end_row and move.end_col == valid_move.end_col:
                
                # Check if this move would leave or put the king in check
                # Make the move temporarily
                piece_moved = self.board[move.start_row][move.start_col]
                piece_captured = self.board[move.end_row][move.end_col]
                
                # Update the board temporarily
                self.board[move.end_row][move.end_col] = piece_moved
                self.board[move.start_row][move.start_col] = None
                
                # Update king position if king is moved
                king_moved = False
                king_pos = None
                if piece_moved and piece_moved.piece_type == 'K':
                    if piece_moved.color == 'w':
                        king_pos = self.white_king_location
                        self.white_king_location = (move.end_row, move.end_col)
                        king_moved = True
                    else:
                        king_pos = self.black_king_location
                        self.black_king_location = (move.end_row, move.end_col)
                        king_moved = True
                
                # Check if the king is in check after the move
                in_check = self.is_in_check()
                
                # Restore the board
                self.board[move.start_row][move.start_col] = piece_moved
                self.board[move.end_row][move.end_col] = piece_captured
                
                # Restore king position if it was moved
                if king_moved:
                    if piece_moved.color == 'w':
                        self.white_king_location = king_pos
                    else:
                        self.black_king_location = king_pos
                
                # If the move would leave the king in check, it's not valid
                if in_check:
                    return False
                    
                return True
                
        return False
        
    def get_valid_moves(self, pos=None):
        """
        Get all valid moves for the current position or for a specific piece.
        Takes into account checks and pins.
        
        Args:
            pos: Optional tuple (row, col) to get moves for a specific piece
            
        Returns:
            list: List of valid Move objects
        """
        # If position is specified, get moves for that piece only
        if pos is not None:
            row, col = pos
            piece = self.board[row][col]
            if piece is None:
                return []
                
            # Make sure it's the correct color's turn
            if (piece.color == 'w' and not self.white_to_move) or \
               (piece.color == 'b' and self.white_to_move):
                return []
                
            # Get all possible moves for this piece
            moves = []
            if piece.piece_type == 'P':
                self._get_pawn_moves(row, col, moves)
            elif piece.piece_type == 'R':
                self._get_rook_moves(row, col, moves)
            elif piece.piece_type == 'N':
                self._get_knight_moves(row, col, moves)
            elif piece.piece_type == 'B':
                self._get_bishop_moves(row, col, moves)
            elif piece.piece_type == 'Q':
                self._get_queen_moves(row, col, moves)
            elif piece.piece_type == 'K':
                self._get_king_moves(row, col, moves)
                
            # Filter out moves that would leave the king in check
            valid_moves = []
            for move in moves:
                # Make the move temporarily
                piece_moved = self.board[move.start_row][move.start_col]
                piece_captured = self.board[move.end_row][move.end_col]
                
                # Update the board temporarily
                self.board[move.end_row][move.end_col] = piece_moved
                self.board[move.start_row][move.start_col] = None
                
                # Update king position if king is moved
                king_moved = False
                king_pos = None
                if piece_moved and piece_moved.piece_type == 'K':
                    if piece_moved.color == 'w':
                        king_pos = self.white_king_location
                        self.white_king_location = (move.end_row, move.end_col)
                        king_moved = True
                    else:
                        king_pos = self.black_king_location
                        self.black_king_location = (move.end_row, move.end_col)
                        king_moved = True
                
                # Switch turns temporarily
                self.white_to_move = not self.white_to_move
                
                # Check if the king is in check after the move
                in_check = self.is_in_check()
                
                # Switch turns back
                self.white_to_move = not self.white_to_move
                
                # Restore the board
                self.board[move.start_row][move.start_col] = piece_moved
                self.board[move.end_row][move.end_col] = piece_captured
                
                # Restore king position if it was moved
                if king_moved:
                    if piece_moved.color == 'w':
                        self.white_king_location = king_pos
                    else:
                        self.black_king_location = king_pos
                
                # If the move doesn't leave the king in check, it's valid
                if not in_check:
                    valid_moves.append(move)
                
            return valid_moves
            
        # Otherwise, get all valid moves
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    # Only get moves for the current player's pieces
                    if (piece.color == 'w' and self.white_to_move) or \
                       (piece.color == 'b' and not self.white_to_move):
                        if piece.piece_type == 'P':
                            self._get_pawn_moves(row, col, moves)
                        elif piece.piece_type == 'R':
                            self._get_rook_moves(row, col, moves)
                        elif piece.piece_type == 'N':
                            self._get_knight_moves(row, col, moves)
                        elif piece.piece_type == 'B':
                            self._get_bishop_moves(row, col, moves)
                        elif piece.piece_type == 'Q':
                            self._get_queen_moves(row, col, moves)
                        elif piece.piece_type == 'K':
                            self._get_king_moves(row, col, moves)
        
        return moves
    
    def _get_pawn_moves(self, row, col, moves):
        """
        Get all valid pawn moves.
        
        Args:
            row: Pawn row
            col: Pawn column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'P':
            return
            
        # Direction pawn moves (up for white, down for black)
        direction = -1 if piece.color == 'w' else 1
        
        # One square forward
        if 0 <= row + direction < 8 and self.board[row + direction][col] is None:
            moves.append(Move((row, col), (row + direction, col), self))
            
            # Two squares forward from starting position
            if ((row == 6 and piece.color == 'w') or (row == 1 and piece.color == 'b')) and \
               self.board[row + 2 * direction][col] is None:
                moves.append(Move((row, col), (row + 2 * direction, col), self))
        
        # Diagonal captures
        for c_offset in [-1, 1]:
            end_row = row + direction
            end_col = col + c_offset
            
            # Check if the square is on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                # Regular capture
                target_piece = self.board[end_row][end_col]
                if target_piece and target_piece.color != piece.color:
                    moves.append(Move((row, col), (end_row, end_col), self))
                
                # En passant capture
                elif (end_row, end_col) == self.en_passant_possible:
                    moves.append(Move((row, col), (end_row, end_col), self))
    
    def _get_rook_moves(self, row, col, moves):
        """
        Get all valid rook moves.
        
        Args:
            row: Rook row
            col: Rook column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'R':
            return
            
        # Directions: up, right, down, left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for d_row, d_col in directions:
            for i in range(1, 8):
                end_row = row + d_row * i
                end_col = col + d_col * i
                
                # Check if the square is on the board
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                    
                target_piece = self.board[end_row][end_col]
                if target_piece is None:
                    # Empty square
                    moves.append(Move((row, col), (end_row, end_col), self))
                elif target_piece.color != piece.color:
                    # Capture opponent's piece
                    moves.append(Move((row, col), (end_row, end_col), self))
                    break
                else:
                    # Own piece
                    break
    
    def _get_knight_moves(self, row, col, moves):
        """
        Get all valid knight moves.
        
        Args:
            row: Knight row
            col: Knight column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'N':
            return
            
        # Knight moves
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for d_row, d_col in knight_moves:
            end_row = row + d_row
            end_col = col + d_col
            
            # Check if the square is on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                target_piece = self.board[end_row][end_col]
                if target_piece is None or target_piece.color != piece.color:
                    # Empty square or capture
                    moves.append(Move((row, col), (end_row, end_col), self))
    
    def _get_bishop_moves(self, row, col, moves):
        """
        Get all valid bishop moves with restrictions on capturing AI pawns.
        
        Args:
            row: Bishop row
            col: Bishop column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'B':
            return
            
        # Directions: up-left, up-right, down-right, down-left
        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        
        # Track pawn capture moves separately
        pawn_captures = []
        normal_moves = []
        
        for d_row, d_col in directions:
            for i in range(1, 8):
                end_row = row + d_row * i
                end_col = col + d_col * i
                
                # Check if the square is on the board
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                    
                target_piece = self.board[end_row][end_col]
                if target_piece is None:
                    # Empty square - bishop can move here
                    move = Move((row, col), (end_row, end_col), self)
                    move.piece_moved = piece
                    normal_moves.append(move)
                elif target_piece.color != piece.color:
                    # Capture opponent's piece
                    move = Move((row, col), (end_row, end_col), self)
                    move.piece_moved = piece
                    move.piece_captured = target_piece
                    
                    # If it's a pawn, add to pawn captures list instead
                    if target_piece.piece_type == 'P':
                        pawn_captures.append(move)
                    else:
                        normal_moves.append(move)
                    break
                else:
                    # Own piece - can't move here or beyond
                    break
        
        # Add normal moves first
        moves.extend(normal_moves)
        
        # Only add pawn captures if there are no other moves available
        # This restricts the bishop from capturing AI pawns when other moves are possible
        if not normal_moves:
            moves.extend(pawn_captures)
    
    def _get_queen_moves(self, row, col, moves):
        """
        Get all valid queen moves with restrictions on capturing AI pawns.
        
        Args:
            row: Queen row
            col: Queen column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'Q':
            return
            
        # Queen moves are a combination of rook and bishop moves
        # Rook-like moves (horizontal and vertical)
        # Directions: up, right, down, left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Track pawn capture moves separately
        pawn_captures = []
        
        for d_row, d_col in directions:
            for i in range(1, 8):
                end_row = row + d_row * i
                end_col = col + d_col * i
                
                # Check if the square is on the board
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                    
                target_piece = self.board[end_row][end_col]
                if target_piece is None:
                    # Empty square
                    move = Move((row, col), (end_row, end_col), self)
                    move.piece_moved = piece
                    moves.append(move)
                elif target_piece.color != piece.color:
                    # Capture opponent's piece
                    move = Move((row, col), (end_row, end_col), self)
                    move.piece_moved = piece
                    move.piece_captured = target_piece
                    
                    # If it's a pawn, add to pawn captures list instead
                    if target_piece.piece_type == 'P':
                        pawn_captures.append(move)
                    else:
                        moves.append(move)
                    break
                else:
                    # Own piece
                    break
        
        # Bishop-like moves (diagonal)
        # Directions: up-left, up-right, down-right, down-left
        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        
        for d_row, d_col in directions:
            for i in range(1, 8):
                end_row = row + d_row * i
                end_col = col + d_col * i
                
                # Check if the square is on the board
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                    
                target_piece = self.board[end_row][end_col]
                if target_piece is None:
                    # Empty square
                    move = Move((row, col), (end_row, end_col), self)
                    move.piece_moved = piece
                    moves.append(move)
                elif target_piece.color != piece.color:
                    # Capture opponent's piece
                    move = Move((row, col), (end_row, end_col), self)
                    move.piece_moved = piece
                    move.piece_captured = target_piece
                    
                    # If it's a pawn, add to pawn captures list instead
                    if target_piece.piece_type == 'P':
                        pawn_captures.append(move)
                    else:
                        moves.append(move)
                    break
                else:
                    # Own piece
                    break
        
        # Only add pawn captures if there are no other moves available
        # This restricts the queen from capturing AI pawns when other moves are possible
        if not moves:
            moves.extend(pawn_captures)
# This section was causing indentation errors - fixed
    
    def _get_king_moves(self, row, col, moves):
        """
        Get all valid king moves.
        
        Args:
            row: King row
            col: King column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'K':
            return
            
        # King moves (all 8 surrounding squares)
        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                if d_row == 0 and d_col == 0:
                    continue
                    
                end_row = row + d_row
                end_col = col + d_col
                
                # Check if the square is on the board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    target_piece = self.board[end_row][end_col]
                    if target_piece is None or target_piece.color != piece.color:
                        # Empty square or capture
                        move = Move((row, col), (end_row, end_col), self)
                        moves.append(move)
        
        # Castling
        self._get_castle_moves(row, col, moves)
    
    def _get_castle_moves(self, row, col, moves):
        """
        Get castling moves for the king.
        
        Args:
            row: King row
            col: King column
            moves: List to add moves to
        """
        # Can't castle if in check
        if self.in_check:
            return
            
        # Can't castle if king has moved
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'K' or piece.has_moved:
            return
            
        # Check kingside castling
        if ((piece.color == 'w' and self.current_castling_rights.wks) or
            (piece.color == 'b' and self.current_castling_rights.bks)):
            # Check if squares between king and rook are empty
            if self.board[row][col+1] is None and self.board[row][col+2] is None:
                # Check if king passes through or ends up in check
                if not self.square_under_attack(row, col+1) and not self.square_under_attack(row, col+2):
                    moves.append(Move((row, col), (row, col+2), self))
        
        # Check queenside castling
        if ((piece.color == 'w' and self.current_castling_rights.wqs) or
            (piece.color == 'b' and self.current_castling_rights.bqs)):
            # Check if squares between king and rook are empty
            if (self.board[row][col-1] is None and 
                self.board[row][col-2] is None and 
                self.board[row][col-3] is None):
                # Check if king passes through or ends up in check
                if not self.square_under_attack(row, col-1) and not self.square_under_attack(row, col-2):
                    moves.append(Move((row, col), (row, col-2), self))
    
    def make_move(self, move):
        """
        Make a move on the board.
        
        Args:
            move: Move to make
        """
        # Check for pawn promotion
        piece_moved = self.board[move.start_row][move.start_col]
        is_promotion = False
        
        if piece_moved and piece_moved.piece_type == 'P':
            # Check if pawn reached the last rank
            if (piece_moved.color == 'w' and move.end_row == 0) or \
               (piece_moved.color == 'b' and move.end_row == 7):
                is_promotion = True
        
        # Update the board
        self.board[move.end_row][move.end_col] = self.board[move.start_row][move.start_col]
        self.board[move.start_row][move.start_col] = None
        
        # Handle pawn promotion - automatically promote to queen
        if is_promotion:
            self.board[move.end_row][move.end_col] = Queen(piece_moved.color)
            print(f"Pawn promoted to Queen at {chr(97 + move.end_col)}{8 - move.end_row}")
        
        # Update move log
        self.move_log.append(move)
        
        # Update king location if king moved
        if move.piece_moved and move.piece_moved.piece_type == 'K':
            if move.piece_moved.color == 'w':
                self.white_king_location = (move.end_row, move.end_col)
            else:
                self.black_king_location = (move.end_row, move.end_col)
        
        # Mark the piece as moved
        if move.piece_moved:
            move.piece_moved.has_moved = True
        
        # Switch turns
        self.white_to_move = not self.white_to_move
        
        # Check for check, checkmate, stalemate
        self.in_check = self.is_in_check()
        self.checkmate = self.is_checkmate()
        self.stalemate = self.is_stalemate()
        
    def undo_move(self):
        """
        Undo the last move.
        
        Returns:
            bool: True if a move was undone, False otherwise
        """
        if not self.move_log:
            return False
            
        move = self.move_log.pop()
        
        # Restore the board
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        
        # Restore king location if king moved
        if move.piece_moved and move.piece_moved.piece_type == 'K':
            if move.piece_moved.color == 'w':
                self.white_king_location = (move.start_row, move.start_col)
            else:
                self.black_king_location = (move.start_row, move.start_col)
        
        # Switch turns back
        self.white_to_move = not self.white_to_move
        
        # Update check status
        self.in_check = self.is_in_check()
        self.checkmate = False
        self.stalemate = False
        
        return True
    
    def is_in_check(self):
        """
        Check if the current player is in check.
        
        Returns:
            bool: True if in check, False otherwise
        """
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])
    
    def square_under_attack(self, row, col):
        """
        Check if a square is under attack by the opponent.
        
        Args:
            row: Row of the square
            col: Column of the square
            
        Returns:
            bool: True if the square is under attack, False otherwise
        """
        # Switch turns temporarily to get opponent's moves
        self.white_to_move = not self.white_to_move
        
        # Get all opponent's moves
        opponent_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and ((piece.color == 'w' and self.white_to_move) or 
                             (piece.color == 'b' and not self.white_to_move)):
                    # Get all possible moves for this piece
                    if piece.piece_type == 'P':
                        self._get_pawn_attacks(r, c, opponent_moves)
                    elif piece.piece_type == 'R':
                        self._get_rook_attacks(r, c, opponent_moves)
                    elif piece.piece_type == 'N':
                        self._get_knight_attacks(r, c, opponent_moves)
                    elif piece.piece_type == 'B':
                        self._get_bishop_attacks(r, c, opponent_moves)
                    elif piece.piece_type == 'Q':
                        self._get_queen_attacks(r, c, opponent_moves)
                    elif piece.piece_type == 'K':
                        self._get_king_attacks(r, c, opponent_moves)
        
        # Switch turns back
        self.white_to_move = not self.white_to_move
        
        # Check if any move attacks the square
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
                
        return False
    
    def _get_pawn_attacks(self, row, col, moves):
        """
        Get pawn attack moves (diagonal captures only).
        
        Args:
            row: Pawn row
            col: Pawn column
            moves: List to add moves to
        """
        piece = self.board[row][col]
        if not piece or piece.piece_type != 'P':
            return
            
        # Direction pawn moves (up for white, down for black)
        direction = -1 if piece.color == 'w' else 1
        
        # Diagonal captures
        for c_offset in [-1, 1]:
            end_row = row + direction
            end_col = col + c_offset
            
            # Check if the square is on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                moves.append(Move((row, col), (end_row, end_col)))
    
    def _get_rook_attacks(self, row, col, moves):
        """
        Get rook attack moves.
        
        Args:
            row: Rook row
            col: Rook column
            moves: List to add moves to
        """
        # Directions: up, right, down, left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for d_row, d_col in directions:
            for i in range(1, 8):
                end_row = row + d_row * i
                end_col = col + d_col * i
                
                # Check if the square is on the board
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                    
                moves.append(Move((row, col), (end_row, end_col)))
                
                # Stop if we hit a piece
                if self.board[end_row][end_col]:
                    break
    
    def _get_knight_attacks(self, row, col, moves):
        """
        Get knight attack moves.
        
        Args:
            row: Knight row
            col: Knight column
            moves: List to add moves to
        """
        # Knight moves
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for d_row, d_col in knight_moves:
            end_row = row + d_row
            end_col = col + d_col
            
            # Check if the square is on the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                moves.append(Move((row, col), (end_row, end_col)))
    
    def _get_bishop_attacks(self, row, col, moves):
        """
        Get bishop attack moves.
        
        Args:
            row: Bishop row
            col: Bishop column
            moves: List to add moves to
        """
        # Directions: up-left, up-right, down-right, down-left
        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        
        for d_row, d_col in directions:
            for i in range(1, 8):
                end_row = row + d_row * i
                end_col = col + d_col * i
                
                # Check if the square is on the board
                if not (0 <= end_row < 8 and 0 <= end_col < 8):
                    break
                    
                moves.append(Move((row, col), (end_row, end_col)))
                
                # Stop if we hit a piece
                if self.board[end_row][end_col]:
                    break
    
    def _get_queen_attacks(self, row, col, moves):
        """
        Get queen attack moves.
        
        Args:
            row: Queen row
            col: Queen column
            moves: List to add moves to
        """
        # Queen moves are a combination of rook and bishop moves
        self._get_rook_attacks(row, col, moves)
        self._get_bishop_attacks(row, col, moves)
    
    def _get_king_attacks(self, row, col, moves):
        """
        Get king attack moves.
        
        Args:
            row: King row
            col: King column
            moves: List to add moves to
        """
        # King moves (all 8 surrounding squares)
        for d_row in [-1, 0, 1]:
            for d_col in [-1, 0, 1]:
                if d_row == 0 and d_col == 0:
                    continue
                    
                end_row = row + d_row
                end_col = col + d_col
                
                # Check if the square is on the board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    moves.append(Move((row, col), (end_row, end_col)))
    
    def is_checkmate(self):
        """
        Check if the current player is in checkmate.
        
        Returns:
            bool: True if in checkmate, False otherwise
        """
        # If not in check, can't be checkmate
        if not self.is_in_check():
            return False
        
        # Check if there are any valid moves that can get out of check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and ((piece.color == 'w' and self.white_to_move) or 
                             (piece.color == 'b' and not self.white_to_move)):
                    # Get all possible moves for this piece
                    moves = []
                    if piece.piece_type == 'P':
                        self._get_pawn_moves(row, col, moves)
                    elif piece.piece_type == 'R':
                        self._get_rook_moves(row, col, moves)
                    elif piece.piece_type == 'N':
                        self._get_knight_moves(row, col, moves)
                    elif piece.piece_type == 'B':
                        self._get_bishop_moves(row, col, moves)
                    elif piece.piece_type == 'Q':
                        self._get_queen_moves(row, col, moves)
                    elif piece.piece_type == 'K':
                        self._get_king_moves(row, col, moves)
                    
                    # Check if any move can get out of check
                    for move in moves:
                        # Make the move temporarily
                        piece_moved = self.board[move.start_row][move.start_col]
                        piece_captured = self.board[move.end_row][move.end_col]
                        
                        # Update the board temporarily
                        self.board[move.end_row][move.end_col] = piece_moved
                        self.board[move.start_row][move.start_col] = None
                        
                        # Update king position if king is moved
                        king_moved = False
                        king_pos = None
                        if piece_moved and piece_moved.piece_type == 'K':
                            if piece_moved.color == 'w':
                                king_pos = self.white_king_location
                                self.white_king_location = (move.end_row, move.end_col)
                                king_moved = True
                            else:
                                king_pos = self.black_king_location
                                self.black_king_location = (move.end_row, move.end_col)
                                king_moved = True
                        
                        # Switch turns temporarily
                        self.white_to_move = not self.white_to_move
                        
                        # Check if the king is still in check after the move
                        still_in_check = self.is_in_check()
                        
                        # Switch turns back
                        self.white_to_move = not self.white_to_move
                        
                        # Restore the board
                        self.board[move.start_row][move.start_col] = piece_moved
                        self.board[move.end_row][move.end_col] = piece_captured
                        
                        # Restore king position if it was moved
                        if king_moved:
                            if piece_moved.color == 'w':
                                self.white_king_location = king_pos
                            else:
                                self.black_king_location = king_pos
                        
                        # If the move gets out of check, it's not checkmate
                        if not still_in_check:
                            return False
        
        # If no move can get out of check, it's checkmate
        return True
    
    def is_stalemate(self):
        """
        Check if the current position is a stalemate.
        
        Returns:
            bool: True if stalemate, False otherwise
        """
        # If in check, can't be stalemate
        if self.is_in_check():
            return False
            
        # If there are valid moves, not stalemate
        return len(self.get_valid_moves()) == 0


class CastlingRights:
    """Keeps track of castling rights for both players."""
    
    def __init__(self, wks, bks, wqs, bqs):
        """
        Initialize castling rights.
        
        Args:
            wks: White kingside castling right
            bks: Black kingside castling right
            wqs: White queenside castling right
            bqs: Black queenside castling right
        """
        self.wks = wks  # White kingside
        self.bks = bks  # Black kingside
        self.wqs = wqs  # White queenside
        self.bqs = bqs  # Black queenside
