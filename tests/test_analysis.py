import unittest
from unittest.mock import patch, MagicMock
import json
import os
from chess_engine.board import Board
from chess_engine.move import Move
from analysis.analyzer import Analyzer
from analysis.evaluation import Evaluation
from analysis.mistake_detector import MistakeDetector
from iq.iq_model import IQModel


class TestAnalysis(unittest.TestCase):
    """Tests accuracy calculations, mistake detection, and IQ output."""

    def setUp(self):
        """Set up test environment before each test."""
        self.board = Board()
        self.analyzer = Analyzer()
        self.mistake_detector = MistakeDetector()
        self.iq_model = IQModel()
        
        # Sample game moves (e4, e5, Nf3, Nc6, Bb5)
        self.sample_moves = [
            Move((6, 4), (4, 4)),  # e2-e4
            Move((1, 4), (3, 4)),  # e7-e5
            Move((7, 6), (5, 5)),  # g1-f3 (Nf3)
            Move((0, 1), (2, 2)),  # b8-c6 (Nc6)
            Move((7, 5), (3, 1)),  # f1-b5 (Bb5)
        ]
        
        # Apply moves to board
        for move in self.sample_moves:
            self.board.make_move(move)

    def test_position_evaluation(self):
        """Test basic position evaluation."""
        evaluation = Evaluation()
        
        # Test initial position evaluation (should be balanced)
        initial_board = Board()
        score = evaluation.evaluate_position(initial_board)
        self.assertAlmostEqual(score, 0.0, delta=0.1)
        
        # Test position with material advantage
        advantage_board = Board(empty=True)
        # Add kings
        advantage_board.place_piece(7, 4, "King", "white")
        advantage_board.place_piece(0, 4, "King", "black")
        # Add extra queen for white
        advantage_board.place_piece(3, 3, "Queen", "white")
        
        score = evaluation.evaluate_position(advantage_board)
        self.assertGreater(score, 8.0)  # Queen is worth ~9 points

    def test_move_accuracy_calculation(self):
        """Test calculation of move accuracy."""
        # Mock the evaluation to return specific values
        with patch('analysis.evaluation.Evaluation.evaluate_position') as mock_eval:
            # Set up mock to return different values for different positions
            mock_eval.side_effect = [0.0, 0.2, 0.0, -0.3]
            
            # Calculate accuracy for a good move (small evaluation change)
            accuracy = self.analyzer.calculate_move_accuracy(self.board, self.sample_moves[0], "white")
            self.assertGreaterEqual(accuracy, 90)  # Good move should have high accuracy
            
            # Calculate accuracy for a mistake (larger evaluation change)
            accuracy = self.analyzer.calculate_move_accuracy(self.board, self.sample_moves[1], "black")
            self.assertLessEqual(accuracy, 80)  # Mistake should have lower accuracy

    def test_game_accuracy_calculation(self):
        """Test calculation of overall game accuracy."""
        # Mock individual move accuracies
        with patch('analysis.analyzer.Analyzer.calculate_move_accuracy') as mock_acc:
            # Set up mock to return different accuracy values
            mock_acc.side_effect = [95, 85, 92, 78, 90]
            
            # Calculate game accuracy
            white_acc, black_acc = self.analyzer.calculate_game_accuracy(self.board)
            
            # White played moves 0, 2, 4 (indices)
            self.assertAlmostEqual(white_acc, (95 + 92 + 90) / 3)
            
            # Black played moves 1, 3 (indices)
            self.assertAlmostEqual(black_acc, (85 + 78) / 2)

    def test_mistake_detection(self):
        """Test detection of mistakes, blunders, and inaccuracies."""
        # Mock the evaluation differences
        with patch('analysis.mistake_detector.MistakeDetector._get_eval_difference') as mock_diff:
            # Small difference (good move)
            mock_diff.return_value = 0.2
            result = self.mistake_detector.classify_move(self.board, self.sample_moves[0])
            self.assertEqual(result, "good")
            
            # Medium difference (inaccuracy)
            mock_diff.return_value = 0.8
            result = self.mistake_detector.classify_move(self.board, self.sample_moves[1])
            self.assertEqual(result, "inaccuracy")
            
            # Large difference (mistake)
            mock_diff.return_value = 1.5
            result = self.mistake_detector.classify_move(self.board, self.sample_moves[2])
            self.assertEqual(result, "mistake")
            
            # Very large difference (blunder)
            mock_diff.return_value = 3.0
            result = self.mistake_detector.classify_move(self.board, self.sample_moves[3])
            self.assertEqual(result, "blunder")

    def test_best_move_finding(self):
        """Test finding the best move in a position."""
        # Mock the evaluation to make a specific move appear best
        with patch('analysis.evaluation.Evaluation.evaluate_position') as mock_eval:
            # Make e4 appear to be the best move from the starting position
            def eval_side_effect(board):
                # Check if e4 was played
                if board.move_history and board.move_history[-1].end_pos == (4, 4):
                    return 0.5  # Good evaluation after e4
                return 0.0  # Default evaluation
            
            mock_eval.side_effect = eval_side_effect
            
            initial_board = Board()
            best_move = self.analyzer.find_best_move(initial_board, "white", depth=3)
            
            # Best move should be e4
            self.assertEqual(best_move.start_pos, (6, 4))
            self.assertEqual(best_move.end_pos, (4, 4))

    def test_missed_win_detection(self):
        """Test detection of missed winning opportunities."""
        # Set up a position with a winning tactic
        winning_board = Board(empty=True)
        # Add kings
        winning_board.place_piece(7, 7, "King", "white")
        winning_board.place_piece(0, 0, "King", "black")
        # Add pieces for a winning combination
        winning_board.place_piece(2, 0, "Queen", "white")  # Queen at a6
        
        # Mock the evaluation to indicate a winning position after Qa8#
        with patch('analysis.evaluation.Evaluation.evaluate_position') as mock_eval:
            def eval_side_effect(board):
                # Check if Qa8# was played
                if board.move_history and board.move_history[-1].end_pos == (0, 0):
                    return 100.0  # Checkmate
                return 5.0  # Good but not winning yet
            
            mock_eval.side_effect = eval_side_effect
            
            # Make a non-winning move
            non_winning_move = Move((2, 0), (2, 1))  # Qb6
            
            # Check if a missed win is detected
            is_missed_win = self.analyzer.is_missed_win(winning_board, non_winning_move, "white")
            self.assertTrue(is_missed_win)

    def test_iq_calculation(self):
        """Test calculation of Chess IQ based on performance metrics."""
        # Mock the accuracy and mistake counts
        accuracy = 92.5
        mistakes = {
            "good": 30,
            "inaccuracy": 5,
            "mistake": 2,
            "blunder": 1
        }
        
        # Calculate IQ
        iq = self.iq_model.calculate_iq(accuracy, mistakes)
        
        # IQ should be in a reasonable range (e.g., 70-150)
        self.assertGreaterEqual(iq, 70)
        self.assertLessEqual(iq, 150)
        
        # Higher accuracy should result in higher IQ
        higher_accuracy = 98.0
        higher_iq = self.iq_model.calculate_iq(higher_accuracy, mistakes)
        self.assertGreater(higher_iq, iq)
        
        # More mistakes should result in lower IQ
        more_mistakes = {
            "good": 20,
            "inaccuracy": 10,
            "mistake": 5,
            "blunder": 3
        }
        lower_iq = self.iq_model.calculate_iq(accuracy, more_mistakes)
        self.assertLess(lower_iq, iq)

    def test_analysis_report_generation(self):
        """Test generation of a complete analysis report."""
        # Mock the component analysis functions
        with patch.multiple(
            'analysis.analyzer.Analyzer',
            calculate_game_accuracy=MagicMock(return_value=(92.5, 87.3)),
            count_mistakes=MagicMock(return_value={
                "white": {"good": 15, "inaccuracy": 2, "mistake": 1, "blunder": 0},
                "black": {"good": 12, "inaccuracy": 3, "mistake": 2, "blunder": 1}
            }),
            find_critical_positions=MagicMock(return_value=[
                {"move_number": 10, "position": "critical position 1"},
                {"move_number": 24, "position": "critical position 2"}
            ])
        ):
            # Generate report
            report = self.analyzer.generate_analysis_report(self.board)
            
            # Check report structure
            self.assertIn("white_accuracy", report)
            self.assertIn("black_accuracy", report)
            self.assertIn("white_mistakes", report)
            self.assertIn("black_mistakes", report)
            self.assertIn("critical_positions", report)
            
            # Check report values
            self.assertEqual(report["white_accuracy"], 92.5)
            self.assertEqual(report["black_accuracy"], 87.3)
            self.assertEqual(len(report["critical_positions"]), 2)

    def test_pgn_analysis(self):
        """Test analysis of a game from PGN format."""
        # Sample PGN content
        pgn_content = """
        [Event "Test Game"]
        [Site "Test Site"]
        [Date "2023.01.01"]
        [Round "1"]
        [White "Player 1"]
        [Black "Player 2"]
        [Result "1-0"]
        
        1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 O-O 1-0
        """
        
        # Create a temporary PGN file
        with open("temp_test.pgn", "w") as f:
            f.write(pgn_content)
        
        try:
            # Mock the analysis functions
            with patch('analysis.analyzer.Analyzer.analyze_game_from_moves') as mock_analyze:
                mock_analyze.return_value = {
                    "white_accuracy": 94.2,
                    "black_accuracy": 89.7,
                    "white_mistakes": {"good": 7, "inaccuracy": 0, "mistake": 0, "blunder": 0},
                    "black_mistakes": {"good": 6, "inaccuracy": 1, "mistake": 0, "blunder": 0},
                    "white_iq": 120,
                    "black_iq": 110
                }
                
                # Analyze the PGN
                result = self.analyzer.analyze_pgn("temp_test.pgn")
                
                # Check the result
                self.assertEqual(result["white_accuracy"], 94.2)
                self.assertEqual(result["black_accuracy"], 89.7)
                self.assertEqual(result["white_iq"], 120)
                self.assertEqual(result["black_iq"], 110)
        finally:
            # Clean up
            if os.path.exists("temp_test.pgn"):
                os.remove("temp_test.pgn")

    def test_save_analysis_to_file(self):
        """Test saving analysis results to a file."""
        # Sample analysis data
        analysis_data = {
            "white_accuracy": 92.5,
            "black_accuracy": 87.3,
            "white_mistakes": {"good": 15, "inaccuracy": 2, "mistake": 1, "blunder": 0},
            "black_mistakes": {"good": 12, "inaccuracy": 3, "mistake": 2, "blunder": 1},
            "white_iq": 115,
            "black_iq": 105,
            "critical_positions": [
                {"move_number": 10, "position": "critical position 1"},
                {"move_number": 24, "position": "critical position 2"}
            ]
        }
        
        # Save to a temporary file
        temp_file = "temp_analysis.json"
        self.analyzer.save_analysis_to_file(analysis_data, temp_file)
        
        try:
            # Check that the file was created
            self.assertTrue(os.path.exists(temp_file))
            
            # Check the file content
            with open(temp_file, "r") as f:
                loaded_data = json.load(f)
            
            # Verify the data
            self.assertEqual(loaded_data["white_accuracy"], 92.5)
            self.assertEqual(loaded_data["black_accuracy"], 87.3)
            self.assertEqual(loaded_data["white_iq"], 115)
            self.assertEqual(loaded_data["black_iq"], 105)
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    unittest.main()
