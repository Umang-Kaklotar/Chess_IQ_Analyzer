"""
AI Minimax Module

Implements a chess AI using the minimax algorithm with alpha-beta pruning.
"""

import random
from typing import List, Tuple, Optional
from .move import Move

class ChessAI:
    """
    Chess AI using minimax algorithm with alpha-beta pruning.
    """
    
    # Piece values
    PIECE_VALUES = {
        'P': 10,   # Pawn
        'N': 30,   # Knight
        'B': 30,   # Bishop
        'R': 50,   # Rook
        'Q': 90,   # Queen
        'K': 900   # King
    }
    
    # Position bonuses for pieces (simplified)
    POSITION_BONUSES = {
        'P': [  # Pawn position bonuses
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        'N': [  # Knight position bonuses
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ],
        'B': [  # Bishop position bonuses
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ],
        'R': [  # Rook position bonuses
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ],
        'Q': [  # Queen position bonuses
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ],
        'K': [  # King position bonuses (middlegame)
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]
    }
    
    def __init__(self, difficulty: int = 3):
        """
        Initialize the chess AI.
        
        Args:
            difficulty: AI difficulty level (1-5)
        """
        self.difficulty = difficulty
        self.max_depth = self._get_depth_from_difficulty(difficulty)
        self.nodes_evaluated = 0
    
    def _get_depth_from_difficulty(self, difficulty: int) -> int:
        """
        Convert difficulty level to search depth.
        
        Args:
            difficulty: Difficulty level (1-5)
            
        Returns:
            Search depth
        """
        depth_map = {
            1: 1,  # Very easy
            2: 2,  # Easy
            3: 3,  # Medium
            4: 4,  # Hard
            5: 5   # Very hard
        }
        return depth_map.get(difficulty, 3)
    
    def get_best_move(self, board, color: str) -> Optional[Move]:
        """
        Get the best move for the current position.
        
        Args:
            board: Chess board
            color: Player color ("white" or "black")
            
        Returns:
            Best move or None if no moves available
        """
        self.nodes_evaluated = 0
        
        # Get all valid moves
        valid_moves = board.get_valid_moves()
        
        if not valid_moves:
            return None
        
        # For very easy difficulty, just return a random move
        if self.difficulty == 1:
            return random.choice(valid_moves)
        
        # For other difficulties, use minimax with alpha-beta pruning
        best_move = None
        best_score = float('-inf') if color == "white" else float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Determine if we're maximizing or minimizing
        is_maximizing = color == "white"
        
        # Prioritize capturing moves
        capturing_moves = [move for move in valid_moves if move.piece_captured]
        if capturing_moves and random.random() < 0.8:  # 80% chance to prioritize captures
            # Sort capturing moves by value of captured piece
            capturing_moves.sort(
                key=lambda m: self.PIECE_VALUES.get(m.piece_captured.piece_type, 0),
                reverse=True
            )
            # Take one of the top capturing moves
            top_n = min(3, len(capturing_moves))
            return capturing_moves[random.randint(0, top_n-1)]
        
        # Evaluate each move
        for move in valid_moves:
            # Make the move
            board.make_move(move)
            
            # Evaluate the position
            score = self._minimax(board, self.max_depth - 1, alpha, beta, not is_maximizing)
            
            # Undo the move
            board.undo_move()
            
            # Update best move
            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, best_score)
        
        # Add some randomness for lower difficulties
        if self.difficulty <= 3 and random.random() < 0.3:
            return random.choice(valid_moves)
        
        return best_move
    
    def _minimax(self, board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Chess board
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            is_maximizing: Whether we're maximizing or minimizing
            
        Returns:
            Position evaluation score
        """
        self.nodes_evaluated += 1
        
        # Base case: reached maximum depth or game over
        if depth == 0 or board.checkmate or board.stalemate:
            return self._evaluate_position(board)
        
        # Get all valid moves
        valid_moves = board.get_valid_moves()
        
        if is_maximizing:
            max_score = float('-inf')
            for move in valid_moves:
                # Make the move
                board.make_move(move)
                
                # Evaluate the position
                score = self._minimax(board, depth - 1, alpha, beta, False)
                
                # Undo the move
                board.undo_move()
                
                # Update max score and alpha
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return max_score
        else:
            min_score = float('inf')
            for move in valid_moves:
                # Make the move
                board.make_move(move)
                
                # Evaluate the position
                score = self._minimax(board, depth - 1, alpha, beta, True)
                
                # Undo the move
                board.undo_move()
                
                # Update min score and beta
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                
                # Alpha-beta pruning
                if beta <= alpha:
                    break
            
            return min_score
    
    def _evaluate_position(self, board) -> float:
        """
        Evaluate the current board position.
        
        Args:
            board: Chess board
            
        Returns:
            Position evaluation score
        """
        # Check for checkmate
        if board.checkmate:
            if board.white_to_move:
                return -10000  # Black wins
            else:
                return 10000   # White wins
        
        # Check for stalemate
        if board.stalemate:
            return 0  # Draw
        
        # Material evaluation
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    # Base piece value
                    piece_value = self.PIECE_VALUES.get(piece.piece_type, 0)
                    
                    # Position bonus
                    position_bonus = 0
                    if piece.piece_type in self.POSITION_BONUSES:
                        # Adjust row index based on piece color
                        pos_row = row if piece.color == 'b' else 7 - row
                        position_bonus = self.POSITION_BONUSES[piece.piece_type][pos_row][col]
                    
                    # Add to score (positive for white, negative for black)
                    if piece.color == 'w':
                        score += piece_value + position_bonus
                    else:
                        score -= piece_value + position_bonus
        
        return score
