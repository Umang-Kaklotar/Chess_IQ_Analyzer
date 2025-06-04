"""
Position evaluation logic for chess analysis.
"""

class PositionEvaluator:
    """
    Evaluates chess positions and finds best moves.
    """
    
    def __init__(self):
        """Initialize the position evaluator."""
        # Piece values in centipawns
        self.piece_values = {
            'P': 100,   # Pawn
            'N': 320,   # Knight
            'B': 330,   # Bishop
            'R': 500,   # Rook
            'Q': 900,   # Queen
            'K': 20000  # King (high value to prevent trading)
        }
        
        # Position evaluation tables
        self.position_tables = self._init_position_tables()
        
        # Evaluation parameters
        self.mobility_weight = 0.1
        self.center_control_weight = 0.2
        self.king_safety_weight = 0.3
        self.pawn_structure_weight = 0.2
    
    def _init_position_tables(self):
        """Initialize position evaluation tables for each piece type."""
        # These tables are the same as in ai_minimax.py
        # In a real implementation, you might want to use more sophisticated tables
        
        # Example: Pawns are more valuable in the center and as they advance
        pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        # Knights are better in the center and worse at the edges
        knight_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]
        
        # Simplified tables for other pieces
        bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]
        
        rook_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ]
        
        queen_table = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]
        
        # King is safer at the edges in the early/mid game
        king_table = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]
        
        return {
            'P': pawn_table,
            'N': knight_table,
            'B': bishop_table,
            'R': rook_table,
            'Q': queen_table,
            'K': king_table
        }
    
    def evaluate_position(self, board, depth=20):
        """
        Evaluate a chess position.
        
        Args:
            board (Board): Board position to evaluate
            depth (int): Evaluation depth
            
        Returns:
            float: Position evaluation in centipawns (positive for white advantage)
        """
        # Material evaluation
        material_score = self._evaluate_material(board)
        
        # Position evaluation
        position_score = self._evaluate_piece_positions(board)
        
        # Mobility evaluation
        mobility_score = self._evaluate_mobility(board) * self.mobility_weight
        
        # Center control evaluation
        center_score = self._evaluate_center_control(board) * self.center_control_weight
        
        # King safety evaluation
        king_safety_score = self._evaluate_king_safety(board) * self.king_safety_weight
        
        # Pawn structure evaluation
        pawn_structure_score = self._evaluate_pawn_structure(board) * self.pawn_structure_weight
        
        # Combine all evaluations
        total_score = (
            material_score + 
            position_score + 
            mobility_score + 
            center_score + 
            king_safety_score + 
            pawn_structure_score
        )
        
        return total_score
    
    def _evaluate_material(self, board):
        """
        Evaluate material balance.
        
        Args:
            board (Board): Board position to evaluate
            
        Returns:
            float: Material evaluation in centipawns
        """
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece != "--":
                    piece_value = self.piece_values[piece[1]]
                    if piece[0] == 'w':
                        score += piece_value
                    else:
                        score -= piece_value
        
        return score
    
    def _evaluate_piece_positions(self, board):
        """
        Evaluate piece positions using position tables.
        
        Args:
            board (Board): Board position to evaluate
            
        Returns:
            float: Position evaluation in centipawns
        """
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece != "--":
                    piece_type = piece[1]
                    if piece[0] == 'w':
                        # For white pieces, use the table as is
                        score += self.position_tables[piece_type][row][col]
                    else:
                        # For black pieces, flip the table and negate the score
                        score -= self.position_tables[piece_type][7 - row][col]
        
        return score
    
    def _evaluate_mobility(self, board):
        """
        Evaluate piece mobility (number of legal moves).
        
        Args:
            board (Board): Board position to evaluate
            
        Returns:
            float: Mobility evaluation
        """
        # This would calculate the number of legal moves for each side
        # For now, return a placeholder value
        return 0
    
    def _evaluate_center_control(self, board):
        """
        Evaluate control of the center squares.
        
        Args:
            board (Board): Board position to evaluate
            
        Returns:
            float: Center control evaluation
        """
        # This would evaluate control of e4, d4, e5, d5
        # For now, return a placeholder value
        return 0
    
    def _evaluate_king_safety(self, board):
        """
        Evaluate king safety.
        
        Args:
            board (Board): Board position to evaluate
            
        Returns:
            float: King safety evaluation
        """
        # This would evaluate pawn shield, king exposure, etc.
        # For now, return a placeholder value
        return 0
    
    def _evaluate_pawn_structure(self, board):
        """
        Evaluate pawn structure (doubled, isolated, passed pawns).
        
        Args:
            board (Board): Board position to evaluate
            
        Returns:
            float: Pawn structure evaluation
        """
        # This would evaluate pawn chains, isolated pawns, etc.
        # For now, return a placeholder value
        return 0
    
    def find_best_moves(self, board, depth=20, count=3):
        """
        Find the best moves in a position.
        
        Args:
            board (Board): Board position to analyze
            depth (int): Search depth
            count (int): Number of best moves to return
            
        Returns:
            list: List of best moves with evaluations
        """
        # This would use a chess engine to find the best moves
        # For now, return a placeholder list
        return [
            {'move': 'e2e4', 'evaluation': 0.5, 'description': 'King\'s Pawn Opening'},
            {'move': 'd2d4', 'evaluation': 0.4, 'description': 'Queen\'s Pawn Opening'},
            {'move': 'c2c4', 'evaluation': 0.3, 'description': 'English Opening'}
        ]
