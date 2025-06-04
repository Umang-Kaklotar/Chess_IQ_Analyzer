import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import datetime
from iq.iq_model import IQModel
from iq.progress_tracker import ProgressTracker


class TestIQ(unittest.TestCase):
    """Unit tests for IQ scoring logic and progress tracking."""

    def setUp(self):
        """Set up test environment before each test."""
        self.iq_model = IQModel()
        self.progress_tracker = ProgressTracker()
        
        # Sample performance data
        self.sample_performance = {
            "accuracy": 90.5,
            "mistakes": {
                "good": 25,
                "inaccuracy": 3,
                "mistake": 1,
                "blunder": 0
            },
            "game_count": 10,
            "win_rate": 0.7,
            "avg_opponent_rating": 1500
        }

    def test_iq_calculation_basic(self):
        """Test basic IQ calculation from accuracy and mistakes."""
        iq = self.iq_model.calculate_iq(90.5, {
            "good": 25,
            "inaccuracy": 3,
            "mistake": 1,
            "blunder": 0
        })
        
        # IQ should be in a reasonable range
        self.assertGreaterEqual(iq, 70)
        self.assertLessEqual(iq, 150)

    def test_iq_calculation_perfect_play(self):
        """Test IQ calculation with perfect play."""
        iq = self.iq_model.calculate_iq(100.0, {
            "good": 40,
            "inaccuracy": 0,
            "mistake": 0,
            "blunder": 0
        })
        
        # Perfect play should result in very high IQ
        self.assertGreaterEqual(iq, 140)

    def test_iq_calculation_poor_play(self):
        """Test IQ calculation with poor play."""
        iq = self.iq_model.calculate_iq(60.0, {
            "good": 10,
            "inaccuracy": 10,
            "mistake": 8,
            "blunder": 5
        })
        
        # Poor play should result in lower IQ
        self.assertLessEqual(iq, 90)

    def test_iq_weighting_factors(self):
        """Test that different factors are weighted appropriately in IQ calculation."""
        # Base IQ
        base_iq = self.iq_model.calculate_iq(90.0, {
            "good": 20,
            "inaccuracy": 5,
            "mistake": 2,
            "blunder": 1
        })
        
        # IQ with better accuracy
        accuracy_iq = self.iq_model.calculate_iq(95.0, {
            "good": 20,
            "inaccuracy": 5,
            "mistake": 2,
            "blunder": 1
        })
        
        # IQ with fewer blunders
        blunder_iq = self.iq_model.calculate_iq(90.0, {
            "good": 20,
            "inaccuracy": 5,
            "mistake": 2,
            "blunder": 0
        })
        
        # IQ with fewer mistakes
        mistake_iq = self.iq_model.calculate_iq(90.0, {
            "good": 20,
            "inaccuracy": 5,
            "mistake": 0,
            "blunder": 1
        })
        
        # Verify that each factor improves IQ
        self.assertGreater(accuracy_iq, base_iq)
        self.assertGreater(blunder_iq, base_iq)
        self.assertGreater(mistake_iq, base_iq)
        
        # Verify that blunders have more impact than mistakes
        blunder_improvement = blunder_iq - base_iq
        mistake_improvement = mistake_iq - base_iq
        self.assertGreater(blunder_improvement, mistake_improvement)

    def test_iq_consistency(self):
        """Test that IQ calculation is consistent for the same inputs."""
        iq1 = self.iq_model.calculate_iq(90.5, {
            "good": 25,
            "inaccuracy": 3,
            "mistake": 1,
            "blunder": 0
        })
        
        iq2 = self.iq_model.calculate_iq(90.5, {
            "good": 25,
            "inaccuracy": 3,
            "mistake": 1,
            "blunder": 0
        })
        
        self.assertEqual(iq1, iq2)

    def test_iq_adjustment_by_opponent_strength(self):
        """Test IQ adjustment based on opponent strength."""
        # Base IQ against average opponent
        base_iq = self.iq_model.calculate_iq_with_context(
            90.0,
            {"good": 20, "inaccuracy": 5, "mistake": 2, "blunder": 1},
            opponent_rating=1500
        )
        
        # IQ against stronger opponent
        strong_opponent_iq = self.iq_model.calculate_iq_with_context(
            90.0,
            {"good": 20, "inaccuracy": 5, "mistake": 2, "blunder": 1},
            opponent_rating=1800
        )
        
        # IQ against weaker opponent
        weak_opponent_iq = self.iq_model.calculate_iq_with_context(
            90.0,
            {"good": 20, "inaccuracy": 5, "mistake": 2, "blunder": 1},
            opponent_rating=1200
        )
        
        # Playing well against stronger opponents should boost IQ more
        self.assertGreater(strong_opponent_iq, base_iq)
        self.assertLess(weak_opponent_iq, base_iq)

    def test_iq_adjustment_by_time_control(self):
        """Test IQ adjustment based on time control."""
        # Base IQ with standard time control
        base_iq = self.iq_model.calculate_iq_with_context(
            90.0,
            {"good": 20, "inaccuracy": 5, "mistake": 2, "blunder": 1},
            time_control="standard"
        )
        
        # IQ with blitz time control
        blitz_iq = self.iq_model.calculate_iq_with_context(
            90.0,
            {"good": 20, "inaccuracy": 5, "mistake": 2, "blunder": 1},
            time_control="blitz"
        )
        
        # IQ with bullet time control
        bullet_iq = self.iq_model.calculate_iq_with_context(
            90.0,
            {"good": 20, "inaccuracy": 5, "mistake": 2, "blunder": 1},
            time_control="bullet"
        )
        
        # Faster time controls should be more forgiving
        self.assertGreater(blitz_iq, base_iq)
        self.assertGreater(bullet_iq, blitz_iq)

    def test_progress_tracking_initialization(self):
        """Test initialization of progress tracker."""
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data="{}")) as mock_file:
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Check that the file was opened for reading
            mock_file.assert_called_with("mock_stats.json", "r")

    def test_progress_tracking_update(self):
        """Test updating player stats with new game results."""
        # Mock initial stats data
        initial_stats = {
            "games_played": 5,
            "wins": 3,
            "losses": 1,
            "draws": 1,
            "iq_history": [
                {"date": "2023-01-01", "iq": 100},
                {"date": "2023-01-02", "iq": 105}
            ],
            "accuracy_history": [
                {"date": "2023-01-01", "accuracy": 85.0},
                {"date": "2023-01-02", "accuracy": 87.5}
            ],
            "mistake_counts": {
                "good": 100,
                "inaccuracy": 10,
                "mistake": 5,
                "blunder": 2
            }
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(initial_stats))) as mock_file:
            with patch("json.dump") as mock_json_dump:
                # Create tracker with mocked file
                tracker = ProgressTracker(stats_file="mock_stats.json")
                
                # Update with new game result
                new_game_result = {
                    "result": "win",
                    "iq": 110,
                    "accuracy": 92.0,
                    "mistakes": {
                        "good": 30,
                        "inaccuracy": 2,
                        "mistake": 1,
                        "blunder": 0
                    }
                }
                
                # Mock the current date
                with patch("datetime.date") as mock_date:
                    mock_date.today.return_value = datetime.date(2023, 1, 3)
                    mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
                    
                    tracker.update_stats(new_game_result)
                
                # Check that stats were updated correctly
                updated_stats = tracker.stats
                self.assertEqual(updated_stats["games_played"], 6)
                self.assertEqual(updated_stats["wins"], 4)
                self.assertEqual(len(updated_stats["iq_history"]), 3)
                self.assertEqual(updated_stats["iq_history"][-1]["iq"], 110)
                self.assertEqual(updated_stats["iq_history"][-1]["date"], "2023-01-03")
                self.assertEqual(updated_stats["mistake_counts"]["good"], 130)
                self.assertEqual(updated_stats["mistake_counts"]["blunder"], 2)
                
                # Check that the file was written
                mock_file.assert_called_with("mock_stats.json", "w")
                mock_json_dump.assert_called()

    def test_progress_tracking_get_iq_trend(self):
        """Test getting IQ trend over time."""
        # Mock stats data with IQ history
        stats_data = {
            "iq_history": [
                {"date": "2023-01-01", "iq": 100},
                {"date": "2023-01-02", "iq": 105},
                {"date": "2023-01-03", "iq": 103},
                {"date": "2023-01-04", "iq": 108},
                {"date": "2023-01-05", "iq": 112}
            ]
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(stats_data))):
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Get IQ trend
            trend = tracker.get_iq_trend()
            
            # Check trend calculation
            self.assertEqual(trend, 3.0)  # (112 - 100) / 4 days = 3.0 points per day

    def test_progress_tracking_get_accuracy_trend(self):
        """Test getting accuracy trend over time."""
        # Mock stats data with accuracy history
        stats_data = {
            "accuracy_history": [
                {"date": "2023-01-01", "accuracy": 85.0},
                {"date": "2023-01-02", "accuracy": 87.5},
                {"date": "2023-01-03", "accuracy": 86.0},
                {"date": "2023-01-04", "accuracy": 88.0},
                {"date": "2023-01-05", "accuracy": 90.0}
            ]
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(stats_data))):
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Get accuracy trend
            trend = tracker.get_accuracy_trend()
            
            # Check trend calculation
            self.assertEqual(trend, 1.25)  # (90.0 - 85.0) / 4 days = 1.25 points per day

    def test_progress_tracking_get_mistake_distribution(self):
        """Test getting mistake distribution."""
        # Mock stats data with mistake counts
        stats_data = {
            "mistake_counts": {
                "good": 100,
                "inaccuracy": 20,
                "mistake": 10,
                "blunder": 5
            }
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(stats_data))):
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Get mistake distribution
            distribution = tracker.get_mistake_distribution()
            
            # Check distribution calculation
            total_moves = 100 + 20 + 10 + 5
            self.assertAlmostEqual(distribution["good"], 100 / total_moves * 100, places=1)
            self.assertAlmostEqual(distribution["inaccuracy"], 20 / total_moves * 100, places=1)
            self.assertAlmostEqual(distribution["mistake"], 10 / total_moves * 100, places=1)
            self.assertAlmostEqual(distribution["blunder"], 5 / total_moves * 100, places=1)

    def test_progress_tracking_get_win_rate(self):
        """Test getting win rate."""
        # Mock stats data with game results
        stats_data = {
            "games_played": 20,
            "wins": 12,
            "losses": 5,
            "draws": 3
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(stats_data))):
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Get win rate
            win_rate = tracker.get_win_rate()
            
            # Check win rate calculation
            self.assertEqual(win_rate, 60.0)  # 12/20 * 100 = 60%

    def test_progress_tracking_get_improvement_suggestions(self):
        """Test getting improvement suggestions based on stats."""
        # Mock stats data with various issues
        stats_data = {
            "mistake_counts": {
                "good": 100,
                "inaccuracy": 20,
                "mistake": 10,
                "blunder": 15  # High blunder rate
            },
            "accuracy_history": [
                {"date": "2023-01-01", "accuracy": 85.0},
                {"date": "2023-01-02", "accuracy": 84.0},
                {"date": "2023-01-03", "accuracy": 82.0}  # Declining accuracy
            ],
            "game_phase_stats": {
                "opening": {"accuracy": 90.0},
                "middlegame": {"accuracy": 85.0},
                "endgame": {"accuracy": 70.0}  # Weak endgame
            }
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(stats_data))):
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Get improvement suggestions
            suggestions = tracker.get_improvement_suggestions()
            
            # Check that appropriate suggestions are made
            self.assertTrue(any("blunder" in suggestion.lower() for suggestion in suggestions))
            self.assertTrue(any("accuracy" in suggestion.lower() for suggestion in suggestions))
            self.assertTrue(any("endgame" in suggestion.lower() for suggestion in suggestions))

    def test_progress_tracking_get_strength_weaknesses(self):
        """Test identifying player strengths and weaknesses."""
        # Mock stats data with various patterns
        stats_data = {
            "opening_repertoire": {
                "e4": {"games": 10, "win_rate": 80.0},  # Strong with e4
                "d4": {"games": 5, "win_rate": 40.0}    # Weak with d4
            },
            "game_phase_stats": {
                "opening": {"accuracy": 90.0},  # Strong in opening
                "middlegame": {"accuracy": 75.0},
                "endgame": {"accuracy": 65.0}   # Weak in endgame
            },
            "piece_movement": {
                "knight": {"accuracy": 92.0},  # Strong with knights
                "bishop": {"accuracy": 88.0},
                "rook": {"accuracy": 80.0},
                "queen": {"accuracy": 75.0}    # Weaker with queen
            }
        }
        
        # Mock the file operations
        with patch("builtins.open", mock_open(read_data=json.dumps(stats_data))):
            tracker = ProgressTracker(stats_file="mock_stats.json")
            
            # Get strengths and weaknesses
            strengths, weaknesses = tracker.get_strengths_and_weaknesses()
            
            # Check that appropriate strengths are identified
            self.assertTrue(any("e4" in strength.lower() for strength in strengths))
            self.assertTrue(any("opening" in strength.lower() for strength in strengths))
            self.assertTrue(any("knight" in strength.lower() for strength in strengths))
            
            # Check that appropriate weaknesses are identified
            self.assertTrue(any("d4" in weakness.lower() for weakness in weaknesses))
            self.assertTrue(any("endgame" in weakness.lower() for weakness in weaknesses))
            self.assertTrue(any("queen" in weakness.lower() for weakness in weaknesses))

    def test_progress_tracking_save_stats(self):
        """Test saving stats to file."""
        # Mock the file operations
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_json_dump:
                tracker = ProgressTracker(stats_file="mock_stats.json")
                
                # Set some stats
                tracker.stats = {
                    "games_played": 10,
                    "wins": 6,
                    "iq_history": [{"date": "2023-01-01", "iq": 105}]
                }
                
                # Save stats
                tracker.save_stats()
                
                # Check that the file was written
                mock_file.assert_called_with("mock_stats.json", "w")
                mock_json_dump.assert_called_once()
                # Check that the stats were passed to json.dump
                args, _ = mock_json_dump.call_args
                self.assertEqual(args[0], tracker.stats)


if __name__ == "__main__":
    unittest.main()
