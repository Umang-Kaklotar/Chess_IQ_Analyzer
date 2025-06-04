"""
Chess rules and game state validation.
Handles chess rules like castling, en passant, promotion, and check detection.
"""

from .move import Move

class GameState:
    """
    Manages the state of a chess game including rules enforcement.
    """
    
    def __init__(self, board):
        """
        Initialize game state.
        
        Args:
            board: The chess board
        """
        self.board = board
        self.move_history = []
        self.half_move_clock = 0  # For 50-move rule
        self.full_move_number = 1  # Increments after black's move
        self.repetition_count = {}  # For threefold repetition
        self.game_over = False
        self.result = None
        self.result_reason = None
    
    def make_move(self, move):
        """
        Make a move and update the game state.
        
        Args:
            move: Move to make
            
        Returns:
            bool: True if the move was made, False otherwise
        """
        # Check if the move is legal
        if not move.is_legal(self.board):
            return False
        
        # Make the move on the board
        self.board.make_move(move)
        
        # Update move history
        self.move_history.append(move)
        
        # Update half-move clock (reset on pawn move or capture)
        if move.piece_moved.piece_type == 'P' or move.piece_captured:
            self.half_move_clock = 0
        else:
            self.half_move_clock += 1
        
        # Update full move number
        if not self.board.white_to_move:  # After black's move
            self.full_move_number += 1
        
        # Update repetition count
        board_state = self.get_board_state()
        self.repetition_count[board_state] = self.repetition_count.get(board_state, 0) + 1
        
        # Check for game end conditions
        self.check_game_end()
        
        return True
    
    def undo_move(self):
        """
        Undo the last move and update the game state.
        
        Returns:
            bool: True if a move was undone, False otherwise
        """
        if not self.move_history:
            return False
        
        # Get the last move
        last_move = self.move_history.pop()
        
        # Update repetition count
        board_state = self.get_board_state()
        self.repetition_count[board_state] -= 1
        if self.repetition_count[board_state] == 0:
            del self.repetition_count[board_state]
        
        # Undo the move on the board
        self.board.undo_move()
        
        # Update half-move clock
        if last_move.piece_moved.piece_type == 'P' or last_move.piece_captured:
            # Need to restore the previous half-move clock
            # This is a simplification; in a real implementation, you would need to store the clock with each move
            self.half_move_clock = max(0, self.half_move_clock - 1)
        else:
            self.half_move_clock -= 1
        
        # Update full move number
        if self.board.white_to_move:  # After undoing black's move
            self.full_move_number -= 1
        
        # Reset game end flags
        self.game_over = False
        self.result = None
        self.result_reason = None
        
        return True
    
    def get_board_state(self):
        """
        Get a hashable representation of the board state for repetition detection.
        
        Returns:
            tuple: Board state representation
        """
        # Create a tuple of piece positions, castling rights, en passant, and turn
        board_repr = []
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece:
                    board_repr.append((row, col, piece.color, piece.piece_type))
        
        return (
            tuple(sorted(board_repr)),
            self.board.current_castling_rights.wks,
            self.board.current_castling_rights.wqs,
            self.board.current_castling_rights.bks,
            self.board.current_castling_rights.bqs,
            self.board.en_passant_possible,
            self.board.white_to_move
        )
    
    def check_game_end(self):
        """Check if the game has ended and update game state accordingly."""
        # Check for checkmate or stalemate
        valid_moves = self.board.get_valid_moves()
        if not valid_moves:
            self.game_over = True
            if self.board.in_check:
                # Checkmate
                self.result = "1-0" if not self.board.white_to_move else "0-1"
                self.result_reason = "Checkmate"
            else:
                # Stalemate
                self.result = "1/2-1/2"
                self.result_reason = "Stalemate"
            return
        
        # Check for draw by insufficient material
        if self.has_insufficient_material():
            self.game_over = True
            self.result = "1/2-1/2"
            self.result_reason = "Insufficient material"
            return
        
        # Check for draw by 50-move rule
        if self.half_move_clock >= 100:  # 50 moves = 100 half-moves
            self.game_over = True
            self.result = "1/2-1/2"
            self.result_reason = "50-move rule"
            return
        
        # Check for draw by threefold repetition
        board_state = self.get_board_state()
        if self.repetition_count.get(board_state, 0) >= 3:
            self.game_over = True
            self.result = "1/2-1/2"
            self.result_reason = "Threefold repetition"
            return
    
    def has_insufficient_material(self):
        """
        Check if there is insufficient material for checkmate.
        
        Returns:
            bool: True if there is insufficient material, False otherwise
        """
        # Count pieces
        white_knights = white_bishops = white_rooks = white_queens = white_pawns = 0
        black_knights = black_bishops = black_rooks = black_queens = black_pawns = 0
        white_bishop_colors = set()
        black_bishop_colors = set()
        
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if not piece:
                    continue
                
                if piece.color == 'w':
                    if piece.piece_type == 'N':
                        white_knights += 1
                    elif piece.piece_type == 'B':
                        white_bishops += 1
                        # Track bishop color (light or dark square)
                        white_bishop_colors.add((row + col) % 2)
                    elif piece.piece_type == 'R':
                        white_rooks += 1
                    elif piece.piece_type == 'Q':
                        white_queens += 1
                    elif piece.piece_type == 'P':
                        white_pawns += 1
                else:
                    if piece.piece_type == 'N':
                        black_knights += 1
                    elif piece.piece_type == 'B':
                        black_bishops += 1
                        # Track bishop color (light or dark square)
                        black_bishop_colors.add((row + col) % 2)
                    elif piece.piece_type == 'R':
                        black_rooks += 1
                    elif piece.piece_type == 'Q':
                        black_queens += 1
                    elif piece.piece_type == 'P':
                        black_pawns += 1
        
        # King vs King
        if white_knights == 0 and white_bishops == 0 and white_rooks == 0 and white_queens == 0 and white_pawns == 0 and \
           black_knights == 0 and black_bishops == 0 and black_rooks == 0 and black_queens == 0 and black_pawns == 0:
            return True
        
        # King + minor piece vs King
        if (white_knights + white_bishops == 1 and white_rooks == 0 and white_queens == 0 and white_pawns == 0 and \
            black_knights == 0 and black_bishops == 0 and black_rooks == 0 and black_queens == 0 and black_pawns == 0) or \
           (black_knights + black_bishops == 1 and black_rooks == 0 and black_queens == 0 and black_pawns == 0 and \
            white_knights == 0 and white_bishops == 0 and white_rooks == 0 and white_queens == 0 and white_pawns == 0):
            return True
        
        # King + 2 knights vs King
        if (white_knights == 2 and white_bishops == 0 and white_rooks == 0 and white_queens == 0 and white_pawns == 0 and \
            black_knights == 0 and black_bishops == 0 and black_rooks == 0 and black_queens == 0 and black_pawns == 0) or \
           (black_knights == 2 and black_bishops == 0 and black_rooks == 0 and black_queens == 0 and black_pawns == 0 and \
            white_knights == 0 and white_bishops == 0 and white_rooks == 0 and white_queens == 0 and white_pawns == 0):
            return True
        
        # King + bishop vs King + bishop (same color bishops)
        if white_knights == 0 and white_bishops == 1 and white_rooks == 0 and white_queens == 0 and white_pawns == 0 and \
           black_knights == 0 and black_bishops == 1 and black_rooks == 0 and black_queens == 0 and black_pawns == 0 and \
           len(white_bishop_colors) == 1 and len(black_bishop_colors) == 1 and \
           list(white_bishop_colors)[0] == list(black_bishop_colors)[0]:
            return True
        
        return False
    
    def get_fen(self):
        """
        Get the Forsyth-Edwards Notation (FEN) for the current position.
        
        Returns:
            str: FEN string
        """
        fen = ""
        
        # 1. Piece placement
        for row in range(8):
            empty_count = 0
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece:
                    if empty_count > 0:
                        fen += str(empty_count)
                        empty_count = 0
                    
                    # Add piece symbol (uppercase for white, lowercase for black)
                    symbol = piece.piece_type
                    if piece.color == 'b':
                        symbol = symbol.lower()
                    fen += symbol
                else:
                    empty_count += 1
            
            if empty_count > 0:
                fen += str(empty_count)
            
            if row < 7:
                fen += "/"
        
        # 2. Active color
        fen += " " + ("w" if self.board.white_to_move else "b")
        
        # 3. Castling availability
        castling = ""
        if self.board.current_castling_rights.wks:
            castling += "K"
        if self.board.current_castling_rights.wqs:
            castling += "Q"
        if self.board.current_castling_rights.bks:
            castling += "k"
        if self.board.current_castling_rights.bqs:
            castling += "q"
        
        if not castling:
            castling = "-"
        
        fen += " " + castling
        
        # 4. En passant target square
        if self.board.en_passant_possible:
            row, col = self.board.en_passant_possible
            file = Move.cols_to_files[col]
            rank = Move.rows_to_ranks[row]
            fen += " " + file + rank
        else:
            fen += " -"
        
        # 5. Halfmove clock
        fen += " " + str(self.half_move_clock)
        
        # 6. Fullmove number
        fen += " " + str(self.full_move_number)
        
        return fen
    
    @classmethod
    def from_fen(cls, fen, board):
        """
        Create a game state from a FEN string.
        
        Args:
            fen (str): FEN string
            board: Chess board to update
            
        Returns:
            GameState: Game state from the FEN
        """
        # Clear the board
        for row in range(8):
            for col in range(8):
                board.board[row][col] = None
        
        # Parse FEN
        parts = fen.split()
        if len(parts) != 6:
            raise ValueError("Invalid FEN: wrong number of fields")
        
        # 1. Piece placement
        rows = parts[0].split('/')
        if len(rows) != 8:
            raise ValueError("Invalid FEN: wrong number of rows")
        
        for row_idx, row_str in enumerate(rows):
            col_idx = 0
            for char in row_str:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    color = 'w' if char.isupper() else 'b'
                    piece_type = char.upper()
                    
                    # Create the appropriate piece
                    from .pieces import Pawn, Rook, Knight, Bishop, Queen, King
                    if piece_type == 'P':
                        board.board[row_idx][col_idx] = Pawn(color)
                    elif piece_type == 'R':
                        board.board[row_idx][col_idx] = Rook(color)
                    elif piece_type == 'N':
                        board.board[row_idx][col_idx] = Knight(color)
                    elif piece_type == 'B':
                        board.board[row_idx][col_idx] = Bishop(color)
                    elif piece_type == 'Q':
                        board.board[row_idx][col_idx] = Queen(color)
                    elif piece_type == 'K':
                        board.board[row_idx][col_idx] = King(color)
                        # Update king location
                        if color == 'w':
                            board.white_king_location = (row_idx, col_idx)
                        else:
                            board.black_king_location = (row_idx, col_idx)
                    
                    col_idx += 1
        
        # 2. Active color
        board.white_to_move = parts[1] == 'w'
        
        # 3. Castling availability
        board.current_castling_rights.wks = 'K' in parts[2]
        board.current_castling_rights.wqs = 'Q' in parts[2]
        board.current_castling_rights.bks = 'k' in parts[2]
        board.current_castling_rights.bqs = 'q' in parts[2]
        
        # 4. En passant target square
        if parts[3] != '-':
            file = parts[3][0]
            rank = parts[3][1]
            col = Move.files_to_cols[file]
            row = Move.ranks_to_rows[rank]
            board.en_passant_possible = (row, col)
        else:
            board.en_passant_possible = ()
        
        # Create game state
        game_state = cls(board)
        
        # 5. Halfmove clock
        game_state.half_move_clock = int(parts[4])
        
        # 6. Fullmove number
        game_state.full_move_number = int(parts[5])
        
        return game_state
    
    def get_pgn(self, headers=None):
        """
        Get the Portable Game Notation (PGN) for the game.
        
        Args:
            headers (dict): Optional PGN headers
            
        Returns:
            str: PGN string
        """
        pgn = ""
        
        # Add headers
        if headers:
            for key, value in headers.items():
                pgn += f'[{key} "{value}"]\n'
        
        # Add result header if game is over
        if self.game_over and self.result and not headers.get('Result'):
            pgn += f'[Result "{self.result}"]\n'
        
        pgn += "\n"
        
        # Add moves
        move_pairs = []
        for i, move in enumerate(self.move_history):
            if i % 2 == 0:
                # White's move
                move_num = i // 2 + 1
                move_pairs.append(f"{move_num}. {move.get_san(self.board)}")
            else:
                # Black's move
                move_pairs[-1] += f" {move.get_san(self.board)}"
        
        # Add result
        if self.game_over and self.result:
            move_pairs.append(self.result)
        
        # Format moves with line breaks
        line_length = 0
        formatted_moves = []
        for move_pair in move_pairs:
            if line_length + len(move_pair) + 1 > 80:
                formatted_moves.append("\n" + move_pair)
                line_length = len(move_pair)
            else:
                if formatted_moves:
                    formatted_moves.append(" " + move_pair)
                    line_length += len(move_pair) + 1
                else:
                    formatted_moves.append(move_pair)
                    line_length = len(move_pair)
        
        pgn += "".join(formatted_moves)
        
        return pgn
