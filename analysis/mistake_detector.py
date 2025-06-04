"""
Mistake detection for chess moves.
Detects blunders and inaccuracies by comparing played moves with best engine moves.
"""

import math
from chess_engine.move import Move
from .evaluation import PositionEvaluator

class MistakeDetector:
    """
    Detects mistakes, blunders, and inaccuracies in chess moves by comparing
    played moves with engine-recommended best moves.
    """
    
    def __init__(self):
        """Initialize the mistake detector with evaluation thresholds."""
        # Thresholds for mistake classification (in centipawns)
        self.inaccuracy_threshold = 50   # 0.5 pawns
        self.mistake_threshold = 100     # 1 pawn
        self.blunder_threshold = 200     # 2 pawns
        self.missed_win_threshold = 300  # 3 pawns
        
        # Initialize position evaluator
        self.evaluator = PositionEvaluator()
        
        # Mistake descriptions
        self.mistake_descriptions = {
            'blunder': "A serious mistake that significantly worsens the position",
            'mistake': "A mistake that worsens the position",
            'inaccuracy': "A small imprecision that slightly worsens the position",
            'missed_win': "A missed opportunity to gain a decisive advantage",
            'missed_tactic': "A missed tactical opportunity",
            'missed_mate': "A missed checkmate sequence"
        }
    
    def detect_mistake(self, board, move, depth=20):
        """
        Detect if a move is a mistake by comparing with engine best move.
        
        Args:
            board (Board): Board position before the move
            move (Move): Move to analyze
            depth (int): Analysis depth
            
        Returns:
            dict: Mistake analysis with detailed information
        """
        # Evaluate position before move
        eval_before = self.evaluator.evaluate_position(board, depth)
        
        # Find best moves in position
        best_moves = self.evaluator.find_best_moves(board, depth, count=3)
        best_move = best_moves[0] if best_moves else None
        best_eval = best_move['evaluation'] if best_move else eval_before
        
        # Make a copy of the board to avoid modifying the original
        board_copy = self._copy_board(board)
        
        # Make the move on the copy
        board_copy.make_move(move)
        
        # Evaluate position after move
        eval_after = -self.evaluator.evaluate_position(board_copy, depth)  # Negate because it's opponent's turn
        
        # Calculate evaluation loss
        eval_loss = best_eval - eval_after
        
        # Classify mistake
        mistake_info = self.classify_mistake(eval_loss)
        mistake_type = mistake_info['type']
        
        # Calculate move accuracy (0-100%)
        accuracy = self.calculate_accuracy(eval_loss)
        
        # Check if this was a missed checkmate
        missed_mate = self._check_for_missed_mate(best_moves)
        if missed_mate:
            mistake_type = 'missed_mate'
            mistake_info['description'] = self.mistake_descriptions['missed_mate']
        
        # Check if this was a missed tactic
        missed_tactic = self._check_for_missed_tactic(board, best_moves, move)
        if missed_tactic and not missed_mate:
            mistake_type = 'missed_tactic'
            mistake_info['description'] = self.mistake_descriptions['missed_tactic']
        
        # Check if this was a missed win
        if eval_before > self.missed_win_threshold and eval_loss > self.mistake_threshold:
            mistake_type = 'missed_win'
            mistake_info['description'] = self.mistake_descriptions['missed_win']
        
        # Generate detailed analysis
        return {
            'move': move.get_chess_notation(),
            'best_move': best_move['move'] if best_move else None,
            'best_move_description': best_move.get('description', '') if best_move else None,
            'alternative_moves': [m['move'] for m in best_moves[1:]] if len(best_moves) > 1 else [],
            'eval_before': eval_before,
            'eval_after': eval_after,
            'best_eval': best_eval,
            'eval_loss': eval_loss,
            'mistake_type': mistake_type,
            'mistake_description': mistake_info['description'],
            'accuracy': accuracy,
            'missed_mate': missed_mate,
            'missed_tactic': missed_tactic
        }
    
    def _copy_board(self, board):
        """
        Create a deep copy of a board.
        
        Args:
            board (Board): Board to copy
            
        Returns:
            Board: Copy of the board
        """
        # This is a simplified implementation
        # In a real implementation, you would need to properly copy the board state
        from ..chess_engine.board import Board
        new_board = Board()
        
        # Copy board state
        for row in range(8):
            for col in range(8):
                new_board.board[row][col] = board.board[row][col]
        
        new_board.white_to_move = board.white_to_move
        new_board.white_king_location = board.white_king_location
        new_board.black_king_location = board.black_king_location
        new_board.checkmate = board.checkmate
        new_board.stalemate = board.stalemate
        new_board.in_check = board.in_check
        new_board.pins = board.pins.copy() if board.pins else []
        new_board.checks = board.checks.copy() if board.checks else []
        new_board.en_passant_possible = board.en_passant_possible
        
        return new_board
    
    def classify_mistake(self, eval_loss):
        """
        Classify a mistake based on evaluation loss.
        
        Args:
            eval_loss (float): Evaluation loss in centipawns
            
        Returns:
            dict: Mistake classification with type and description
        """
        if eval_loss >= self.blunder_threshold:
            return {
                'type': 'blunder',
                'description': self.mistake_descriptions['blunder']
            }
        elif eval_loss >= self.mistake_threshold:
            return {
                'type': 'mistake',
                'description': self.mistake_descriptions['mistake']
            }
        elif eval_loss >= self.inaccuracy_threshold:
            return {
                'type': 'inaccuracy',
                'description': self.mistake_descriptions['inaccuracy']
            }
        else:
            return {
                'type': None,
                'description': "Good move"
            }
    
    def calculate_accuracy(self, eval_loss):
        """
        Calculate move accuracy based on evaluation loss.
        
        Args:
            eval_loss (float): Evaluation loss in centipawns
            
        Returns:
            float: Move accuracy (0-100%)
        """
        # Convert evaluation loss to accuracy percentage
        # The formula is designed to give:
        # - 100% accuracy for perfect moves (0 eval loss)
        # - ~90% accuracy for small inaccuracies
        # - ~70% accuracy for mistakes
        # - <50% accuracy for blunders
        
        if eval_loss <= 0:
            return 100.0
        
        # Exponential decay formula
        accuracy = 100 * (2 ** (-eval_loss / 100))
        
        # Clamp between 0 and 100
        return max(0, min(100, accuracy))
    
    def _check_for_missed_mate(self, best_moves):
        """
        Check if the best move was a checkmate sequence.
        
        Args:
            best_moves (list): List of best moves with evaluations
            
        Returns:
            bool: True if a checkmate was missed, False otherwise
        """
        if not best_moves:
            return False
        
        # Check if the best move has a very high evaluation (likely mate)
        # or if the description contains "mate"
        best_move = best_moves[0]
        
        if best_move['evaluation'] > 10000:  # Arbitrary high value
            return True
        
        if 'description' in best_move and 'mate' in best_move['description'].lower():
            return True
        
        return False
    
    def _check_for_missed_tactic(self, board, best_moves, played_move):
        """
        Check if the move missed a tactical opportunity.
        
        Args:
            board (Board): Board position
            best_moves (list): List of best moves with evaluations
            played_move (Move): The move that was played
            
        Returns:
            bool: True if a tactic was missed, False otherwise
        """
        if not best_moves:
            return False
        
        best_move = best_moves[0]
        
        # Check if the best move has a significantly better evaluation
        if best_move['evaluation'] - self.evaluator.evaluate_position(board) > self.mistake_threshold:
            # Check if the played move is not one of the top 3 moves
            played_notation = played_move.get_chess_notation()
            top_moves = [m['move'] for m in best_moves[:3]]
            
            if played_notation not in top_moves:
                return True
        
        return False
    
    def analyze_move_sequence(self, board, moves, depth=20):
        """
        Analyze a sequence of moves for mistakes.
        
        Args:
            board (Board): Starting board position
            moves (list): List of moves to analyze
            depth (int): Analysis depth
            
        Returns:
            list: Analysis for each move
        """
        results = []
        
        # Make a copy of the board
        current_board = self._copy_board(board)
        
        for move in moves:
            # Analyze the move
            analysis = self.detect_mistake(current_board, move, depth)
            results.append(analysis)
            
            # Make the move on the board
            current_board.make_move(move)
        
        return results
