"""
Main analyzer for chess games, accuracy, mistakes, and IQ scoring.
Analyzes player's moves to compute accuracy, top 3 mistakes, and overall performance metrics.
"""

import time
import math
from .evaluation import PositionEvaluator
from .mistake_detector import MistakeDetector
from iq.iq_model import IQModel

class Analyzer:
    """
    Analyzes chess games for accuracy, mistakes, and IQ scoring.
    """
    
    def __init__(self, engine_depth=20):
        """
        Initialize the game analyzer.
        
        Args:
            engine_depth (int): Depth for engine analysis
        """
        self.evaluator = PositionEvaluator()
        self.mistake_detector = MistakeDetector()
        self.iq_model = IQModel()
        self.engine_depth = engine_depth
    
    def analyze_game(self, game_moves, player_color='both', board=None):
        """
        Analyze a complete chess game.
        
        Args:
            game_moves (list): List of moves in the game
            player_color (str): Color to analyze ('white', 'black', or 'both')
            board: Optional board object to use (will create a new one if None)
            
        Returns:
            dict: Analysis results including accuracy, mistakes, and IQ score
        """
        # Initialize analysis results
        results = {
            'white': {
                'accuracy': 0,
                'mistakes': [],
                'blunders': [],
                'best_moves': 0,
                'missed_wins': 0,
                'inaccuracies': 0,
                'avg_centipawn_loss': 0,
                'iq_score': 0
            },
            'black': {
                'accuracy': 0,
                'mistakes': [],
                'blunders': [],
                'best_moves': 0,
                'missed_wins': 0,
                'inaccuracies': 0,
                'avg_centipawn_loss': 0,
                'iq_score': 0
            },
            'game_quality': 0,
            'analysis_time': 0,
            'analysis_depth': self.engine_depth
        }
        
        start_time = time.time()
        
        # Reconstruct the game
        if board is None:
            from ..chess_engine.board import Board
            board = Board()
        else:
            # Make a copy to avoid modifying the original
            board = self._copy_board(board)
        
        # Analyze each move
        move_analyses = self._analyze_moves(game_moves, board)
        
        # Calculate accuracy and count mistakes
        if player_color in ['white', 'both']:
            results['white'] = self._calculate_player_stats(move_analyses, 'white')
        
        if player_color in ['black', 'both']:
            results['black'] = self._calculate_player_stats(move_analyses, 'black')
        
        # Calculate overall game quality
        white_weight = 1.0 if player_color in ['white', 'both'] else 0.0
        black_weight = 1.0 if player_color in ['black', 'both'] else 0.0
        
        if white_weight + black_weight > 0:
            results['game_quality'] = (
                results['white']['accuracy'] * white_weight + 
                results['black']['accuracy'] * black_weight
            ) / (white_weight + black_weight)
        
        # Record analysis time
        results['analysis_time'] = time.time() - start_time
        
        return results
    
    def _copy_board(self, board):
        """
        Create a copy of a board.
        
        Args:
            board: Board to copy
            
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
    
    def _analyze_moves(self, game_moves, board):
        """
        Analyze each move in the game.
        
        Args:
            game_moves (list): List of moves in the game
            board: Board to analyze
            
        Returns:
            list: Analysis for each move
        """
        move_analyses = []
        
        # For each move, evaluate the position before and after
        for i, move_notation in enumerate(game_moves):
            is_white = i % 2 == 0
            player = 'white' if is_white else 'black'
            move_number = i // 2 + 1
            
            # Convert notation to move object
            from ..chess_engine.move import Move
            move = Move.from_chess_notation(move_notation, board)
            
            if not move:
                print(f"Warning: Could not parse move {move_notation}")
                continue
            
            # Evaluate position before move
            eval_before = self.evaluator.evaluate_position(board, self.engine_depth)
            
            # Find best move in position
            best_moves = self.evaluator.find_best_moves(board, self.engine_depth, count=3)
            best_move = best_moves[0] if best_moves else None
            best_move_eval = best_move['evaluation'] if best_move else eval_before
            
            # Make the move
            board.make_move(move)
            
            # Evaluate position after move
            eval_after = -self.evaluator.evaluate_position(board, self.engine_depth)
            
            # Calculate evaluation loss
            eval_loss = best_move_eval - eval_after
            
            # Detect mistake type
            mistake_info = self.mistake_detector.classify_mistake(eval_loss)
            mistake_type = mistake_info['type']
            
            # Calculate move accuracy
            accuracy = self.mistake_detector.calculate_accuracy(eval_loss)
            
            # Check if this was the best move
            is_best_move = False
            if best_move and move.get_chess_notation() == best_move['move']:
                is_best_move = True
            
            # Create move analysis
            analysis = {
                'move_number': move_number,
                'player': player,
                'move': move_notation,
                'evaluation_before': eval_before,
                'evaluation_after': eval_after,
                'best_move': best_move['move'] if best_move else None,
                'best_move_eval': best_move_eval,
                'eval_loss': eval_loss,
                'accuracy': accuracy,
                'mistake_type': mistake_type,
                'is_best_move': is_best_move,
                'position_snapshot': self._get_position_snapshot(board),
                'mistake_description': mistake_info['description'] if mistake_type else None
            }
            
            move_analyses.append(analysis)
        
        return move_analyses
    
    def _get_position_snapshot(self, board):
        """
        Get a snapshot of the current board position.
        
        Args:
            board: Current board state
            
        Returns:
            str: FEN representation of the position
        """
        # This is a simplified implementation
        # In a real implementation, you would convert the board to FEN notation
        return board.get_board_representation()
    
    def _calculate_player_stats(self, move_analyses, player_color):
        """
        Calculate statistics for a player.
        
        Args:
            move_analyses (list): Analysis for each move
            player_color (str): 'white' or 'black'
            
        Returns:
            dict: Player statistics
        """
        # Filter moves by player
        player_moves = [m for m in move_analyses if m['player'] == player_color]
        
        if not player_moves:
            return {
                'accuracy': 0,
                'mistakes': [],
                'blunders': [],
                'best_moves': 0,
                'missed_wins': 0,
                'inaccuracies': 0,
                'avg_centipawn_loss': 0,
                'iq_score': 0
            }
        
        # Count mistakes, blunders, and best moves
        mistakes = [m for m in player_moves if m['mistake_type'] == 'mistake']
        blunders = [m for m in player_moves if m['mistake_type'] == 'blunder']
        inaccuracies = [m for m in player_moves if m['mistake_type'] == 'inaccuracy']
        best_moves = [m for m in player_moves if m['is_best_move']]
        
        # Find missed wins (positions where player had a winning advantage but didn't capitalize)
        missed_wins = [m for m in player_moves if 
                      m['best_move_eval'] > 300 and  # Winning advantage
                      m['eval_loss'] > 200 and       # Significant loss
                      not m['is_best_move']]         # Didn't play best move
        
        # Calculate average centipawn loss
        total_loss = sum(m['eval_loss'] for m in player_moves)
        avg_centipawn_loss = total_loss / len(player_moves) if player_moves else 0
        
        # Calculate average accuracy
        accuracy = sum(m['accuracy'] for m in player_moves) / len(player_moves) if player_moves else 0
        
        # Get top 3 mistakes by evaluation loss
        all_mistakes = mistakes + blunders + inaccuracies
        top_mistakes = sorted(all_mistakes, key=lambda m: m['eval_loss'], reverse=True)[:3]
        
        # Format top mistakes for display
        formatted_mistakes = []
        for m in top_mistakes:
            formatted_mistake = {
                'move_number': m['move_number'],
                'move': m['move'],
                'type': m['mistake_type'],
                'eval_loss': m['eval_loss'],
                'best_move': m['best_move'],
                'position': m['position_snapshot'],
                'description': m['mistake_description']
            }
            formatted_mistakes.append(formatted_mistake)
        
        # Calculate IQ score based on performance
        iq_score = self.iq_model.calculate_iq(
            accuracy=accuracy,
            mistake_count=len(mistakes),
            blunder_count=len(blunders),
            best_move_count=len(best_moves),
            move_count=len(player_moves),
            avg_centipawn_loss=avg_centipawn_loss
        )
        
        return {
            'accuracy': accuracy,
            'mistakes': formatted_mistakes,
            'blunders': len(blunders),
            'best_moves': len(best_moves),
            'missed_wins': len(missed_wins),
            'inaccuracies': len(inaccuracies),
            'avg_centipawn_loss': avg_centipawn_loss,
            'iq_score': iq_score,
            'move_count': len(player_moves)
        }
    
    def analyze_position(self, board, depth=None):
        """
        Analyze a specific position.
        
        Args:
            board: Board position to analyze
            depth (int): Analysis depth (uses default if None)
            
        Returns:
            dict: Position analysis including evaluation and best moves
        """
        if depth is None:
            depth = self.engine_depth
        
        # Evaluate the position
        evaluation = self.evaluator.evaluate_position(board, depth)
        
        # Find best moves
        best_moves = self.evaluator.find_best_moves(board, depth, count=3)
        
        # Get position features
        features = self._extract_position_features(board)
        
        return {
            'evaluation': evaluation,
            'best_moves': best_moves,
            'features': features,
            'in_check': board.in_check,
            'is_endgame': self._is_endgame(board)
        }
    
    def _extract_position_features(self, board):
        """
        Extract features from a position for analysis.
        
        Args:
            board: Board position
            
        Returns:
            dict: Position features
        """
        features = {
            'material_balance': self._calculate_material_balance(board),
            'piece_activity': self._calculate_piece_activity(board),
            'king_safety': self._evaluate_king_safety(board),
            'pawn_structure': self._evaluate_pawn_structure(board),
            'center_control': self._evaluate_center_control(board)
        }
        
        return features
    
    def _calculate_material_balance(self, board):
        """
        Calculate material balance in the position.
        
        Args:
            board: Board position
            
        Returns:
            dict: Material balance information
        """
        # Piece values
        values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        
        # Count pieces
        white_material = {'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0}
        black_material = {'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0}
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at(row, col)
                if piece and piece.piece_type != 'K':  # Exclude kings
                    if piece.color == 'w':
                        white_material[piece.piece_type] += 1
                    else:
                        black_material[piece.piece_type] += 1
        
        # Calculate total values
        white_value = sum(count * values[piece] for piece, count in white_material.items())
        black_value = sum(count * values[piece] for piece, count in black_material.items())
        
        return {
            'white': white_material,
            'black': black_material,
            'white_value': white_value,
            'black_value': black_value,
            'advantage': white_value - black_value
        }
    
    def _calculate_piece_activity(self, board):
        """
        Calculate piece activity in the position.
        
        Args:
            board: Board position
            
        Returns:
            dict: Piece activity information
        """
        # This is a simplified implementation
        # In a real implementation, you would calculate mobility for each piece
        
        # Save current turn
        original_turn = board.white_to_move
        
        # Calculate white mobility
        board.white_to_move = True
        white_moves = len(board.get_valid_moves())
        
        # Calculate black mobility
        board.white_to_move = False
        black_moves = len(board.get_valid_moves())
        
        # Restore original turn
        board.white_to_move = original_turn
        
        return {
            'white_mobility': white_moves,
            'black_mobility': black_moves,
            'mobility_advantage': white_moves - black_moves
        }
    
    def _evaluate_king_safety(self, board):
        """
        Evaluate king safety in the position.
        
        Args:
            board: Board position
            
        Returns:
            dict: King safety information
        """
        # Get king positions
        white_king_row, white_king_col = board.white_king_location
        black_king_row, black_king_col = board.black_king_location
        
        # Check pawn shield for white king
        white_shield_count = 0
        for r_offset in [-1, 0, 1]:
            for c_offset in [-1, 0, 1]:
                r, c = white_king_row - 1, white_king_col + c_offset
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = board.get_piece_at(r, c)
                    if piece and piece.piece_type == 'P' and piece.color == 'w':
                        white_shield_count += 1
        
        # Check pawn shield for black king
        black_shield_count = 0
        for r_offset in [-1, 0, 1]:
            for c_offset in [-1, 0, 1]:
                r, c = black_king_row + 1, black_king_col + c_offset
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = board.get_piece_at(r, c)
                    if piece and piece.piece_type == 'P' and piece.color == 'b':
                        black_shield_count += 1
        
        # Check if kings are in check
        original_turn = board.white_to_move
        
        board.white_to_move = True
        white_in_check = board.in_check
        
        board.white_to_move = False
        black_in_check = board.in_check
        
        # Restore original turn
        board.white_to_move = original_turn
        
        return {
            'white_shield': white_shield_count,
            'black_shield': black_shield_count,
            'white_in_check': white_in_check,
            'black_in_check': black_in_check
        }
    
    def _evaluate_pawn_structure(self, board):
        """
        Evaluate pawn structure in the position.
        
        Args:
            board: Board position
            
        Returns:
            dict: Pawn structure information
        """
        # Count pawns in each file
        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at(row, col)
                if piece and piece.piece_type == 'P':
                    if piece.color == 'w':
                        white_pawn_files[col] += 1
                    else:
                        black_pawn_files[col] += 1
        
        # Count doubled pawns
        white_doubled = sum(1 for count in white_pawn_files if count > 1)
        black_doubled = sum(1 for count in black_pawn_files if count > 1)
        
        # Count isolated pawns
        white_isolated = 0
        black_isolated = 0
        
        for col in range(8):
            # White isolated pawns
            if white_pawn_files[col] > 0:
                is_isolated = True
                if col > 0 and white_pawn_files[col - 1] > 0:
                    is_isolated = False
                if col < 7 and white_pawn_files[col + 1] > 0:
                    is_isolated = False
                
                if is_isolated:
                    white_isolated += 1
            
            # Black isolated pawns
            if black_pawn_files[col] > 0:
                is_isolated = True
                if col > 0 and black_pawn_files[col - 1] > 0:
                    is_isolated = False
                if col < 7 and black_pawn_files[col + 1] > 0:
                    is_isolated = False
                
                if is_isolated:
                    black_isolated += 1
        
        return {
            'white_doubled': white_doubled,
            'black_doubled': black_doubled,
            'white_isolated': white_isolated,
            'black_isolated': black_isolated
        }
    
    def _evaluate_center_control(self, board):
        """
        Evaluate center control in the position.
        
        Args:
            board: Board position
            
        Returns:
            dict: Center control information
        """
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        
        white_center_pieces = 0
        black_center_pieces = 0
        white_center_attacks = 0
        black_center_attacks = 0
        
        for row, col in center_squares:
            piece = board.get_piece_at(row, col)
            if piece:
                if piece.color == 'w':
                    white_center_pieces += 1
                else:
                    black_center_pieces += 1
            
            if board.is_square_under_attack(row, col, 'w'):
                white_center_attacks += 1
            if board.is_square_under_attack(row, col, 'b'):
                black_center_attacks += 1
        
        return {
            'white_pieces': white_center_pieces,
            'black_pieces': black_center_pieces,
            'white_attacks': white_center_attacks,
            'black_attacks': black_center_attacks,
            'white_control': white_center_pieces + white_center_attacks,
            'black_control': black_center_pieces + black_center_attacks
        }
    
    def _is_endgame(self, board):
        """
        Check if the position is in the endgame.
        
        Args:
            board: Board position
            
        Returns:
            bool: True if in endgame, False otherwise
        """
        # Count major pieces (queens and rooks)
        white_major_pieces = 0
        black_major_pieces = 0
        
        # Count minor pieces (bishops and knights)
        white_minor_pieces = 0
        black_minor_pieces = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at(row, col)
                if not piece:
                    continue
                
                if piece.piece_type in ['Q', 'R']:
                    if piece.color == 'w':
                        white_major_pieces += 1
                    else:
                        black_major_pieces += 1
                elif piece.piece_type in ['B', 'N']:
                    if piece.color == 'w':
                        white_minor_pieces += 1
                    else:
                        black_minor_pieces += 1
        
        # Endgame conditions:
        # 1. Both sides have no queens
        # 2. Both sides have at most one major piece
        # 3. One side has a queen and no other pieces, other side has at most one minor piece
        
        no_queens = not any(board.get_piece_at(row, col) and board.get_piece_at(row, col).piece_type == 'Q'
                           for row in range(8) for col in range(8))
        
        few_major_pieces = white_major_pieces <= 1 and black_major_pieces <= 1
        
        queen_vs_minor = ((white_major_pieces == 1 and white_minor_pieces == 0 and 
                          black_major_pieces == 0 and black_minor_pieces <= 1) or
                         (black_major_pieces == 1 and black_minor_pieces == 0 and 
                          white_major_pieces == 0 and white_minor_pieces <= 1))
        
        return no_queens or few_major_pieces or queen_vs_minor
    
    def detect_mistakes(self, board, move, depth=None):
        """
        Detect if a move is a mistake.
        
        Args:
            board: Board position before the move
            move: Move to analyze
            depth (int): Analysis depth (uses default if None)
            
        Returns:
            dict: Mistake analysis
        """
        if depth is None:
            depth = self.engine_depth
        
        return self.mistake_detector.detect_mistake(board, move, depth)
