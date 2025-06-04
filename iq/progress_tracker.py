"""
Progress Tracker Module

Tracks player progress, statistics, and improvement over time.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

class ProgressTracker:
    """
    Tracks player progress and statistics.
    """
    
    def __init__(self, stats_file: str = "data/player_stats.json"):
        """
        Initialize the progress tracker.
        
        Args:
            stats_file: Path to the player stats file
        """
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """
        Load player statistics from file.
        
        Returns:
            Dictionary containing player statistics
        """
        # Create default stats
        default_stats = {
            "games": {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0
            },
            "iq": {
                "current": 1000,
                "history": []
            },
            "accuracy": {
                "average": 0,
                "history": []
            },
            "mistakes": {
                "blunders": 0,
                "mistakes": 0,
                "inaccuracies": 0,
                "good_moves": 0
            },
            "openings": {},
            "improvement_areas": []
        }
        
        # Try to load stats from file
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            
            # Load stats if file exists
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading stats file: {e}")
        
        return default_stats
    
    def _save_stats(self) -> None:
        """Save player statistics to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            
            # Save stats to file
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except IOError as e:
            print(f"Error saving stats file: {e}")
    
    def update_game_result(self, result: str) -> None:
        """
        Update game result statistics.
        
        Args:
            result: Game result ("win", "loss", or "draw")
        """
        # Initialize stats if needed
        if "games" not in self.stats:
            self.stats["games"] = {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
            
        # Update game counts
        self.stats["games"]["total"] += 1
        
        if result == "win":
            self.stats["games"]["wins"] += 1
        elif result == "loss":
            self.stats["games"]["losses"] += 1
        elif result == "draw":
            self.stats["games"]["draws"] += 1
        
        # Save stats
        self._save_stats()
    
    def update_iq(self, iq: int) -> None:
        """
        Update player IQ.
        
        Args:
            iq: New IQ score
        """
        # Update current IQ
        self.stats["iq"]["current"] = iq
        
        # Add to history
        self.stats["iq"]["history"].append({
            "timestamp": int(time.time()),
            "iq": iq
        })
        
        # Save stats
        self._save_stats()
    
    def update_accuracy(self, accuracy: float) -> None:
        """
        Update player accuracy.
        
        Args:
            accuracy: Game accuracy percentage (0-100)
        """
        # Update average accuracy
        total_games = self.stats["games"]["total"]
        if total_games > 0:
            current_avg = self.stats["accuracy"]["average"]
            self.stats["accuracy"]["average"] = (current_avg * (total_games - 1) + accuracy) / total_games
        else:
            self.stats["accuracy"]["average"] = accuracy
        
        # Add to history
        self.stats["accuracy"]["history"].append({
            "timestamp": int(time.time()),
            "accuracy": accuracy
        })
        
        # Save stats
        self._save_stats()
    
    def update_mistakes(self, blunders: int, mistakes: int, inaccuracies: int, good_moves: int) -> None:
        """
        Update mistake statistics.
        
        Args:
            blunders: Number of blunders
            mistakes: Number of mistakes
            inaccuracies: Number of inaccuracies
            good_moves: Number of good moves
        """
        # Update mistake counts
        self.stats["mistakes"]["blunders"] += blunders
        self.stats["mistakes"]["mistakes"] += mistakes
        self.stats["mistakes"]["inaccuracies"] += inaccuracies
        self.stats["mistakes"]["good_moves"] += good_moves
        
        # Save stats
        self._save_stats()
    
    def update_opening(self, opening_name: str) -> None:
        """
        Update opening statistics.
        
        Args:
            opening_name: Name of the opening played
        """
        # Initialize opening if not exists
        if opening_name not in self.stats["openings"]:
            self.stats["openings"][opening_name] = {
                "played": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
        
        # Update opening count
        self.stats["openings"][opening_name]["played"] += 1
        
        # Save stats
        self._save_stats()
    
    def update_opening_result(self, opening_name: str, result: str) -> None:
        """
        Update opening result statistics.
        
        Args:
            opening_name: Name of the opening played
            result: Game result ("win", "loss", or "draw")
        """
        # Initialize opening if not exists
        if opening_name not in self.stats["openings"]:
            self.update_opening(opening_name)
        
        # Update opening result
        if result == "win":
            self.stats["openings"][opening_name]["wins"] += 1
        elif result == "loss":
            self.stats["openings"][opening_name]["losses"] += 1
        elif result == "draw":
            self.stats["openings"][opening_name]["draws"] += 1
        
        # Save stats
        self._save_stats()
    
    def add_improvement_area(self, area: str) -> None:
        """
        Add an improvement area.
        
        Args:
            area: Improvement area description
        """
        # Add to improvement areas if not already present
        if area not in self.stats["improvement_areas"]:
            self.stats["improvement_areas"].append(area)
            
            # Save stats
            self._save_stats()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get all player statistics.
        
        Returns:
            Dictionary containing player statistics
        """
        # Initialize stats if needed
        if "games" not in self.stats:
            self.stats["games"] = {
                "total": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
        
        if "iq" not in self.stats:
            self.stats["iq"] = {
                "current": 110,  # Start with average IQ
                "history": []
            }
            
        if "accuracy" not in self.stats:
            self.stats["accuracy"] = {
                "average": 0,
                "history": []
            }
            
        if "mistakes" not in self.stats:
            self.stats["mistakes"] = {
                "blunders": 0,
                "mistakes": 0,
                "inaccuracies": 0,
                "good_moves": 0
            }
            
        if "improvement_areas" not in self.stats:
            self.stats["improvement_areas"] = []
            
        # Ensure IQ is within the 70-150 range
        if "iq" in self.stats and "current" in self.stats["iq"]:
            self.stats["iq"]["current"] = max(min(self.stats["iq"]["current"], 150), 70)
            
        return self.stats
    
    def get_win_rate(self) -> float:
        """
        Get player win rate.
        
        Returns:
            Win rate percentage (0-100)
        """
        total_games = self.stats["games"]["total"]
        if total_games > 0:
            return (self.stats["games"]["wins"] / total_games) * 100
        return 0
    
    def get_iq_trend(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get IQ trend history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of IQ history entries
        """
        return self.stats["iq"]["history"][-limit:]
    
    def get_accuracy_trend(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get accuracy trend history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of accuracy history entries
        """
        return self.stats["accuracy"]["history"][-limit:]
    
    def get_best_openings(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get best openings by win rate.
        
        Args:
            limit: Maximum number of openings to return
            
        Returns:
            List of opening statistics
        """
        # Calculate win rates for each opening
        opening_stats = []
        for name, stats in self.stats["openings"].items():
            if stats["played"] > 0:
                win_rate = (stats["wins"] / stats["played"]) * 100
                opening_stats.append({
                    "name": name,
                    "played": stats["played"],
                    "win_rate": win_rate
                })
        
        # Sort by win rate (descending)
        opening_stats.sort(key=lambda x: x["win_rate"], reverse=True)
        
        return opening_stats[:limit]
    
    def get_improvement_suggestions(self) -> List[str]:
        """
        Get improvement suggestions based on statistics.
        
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check mistake distribution
        total_mistakes = (self.stats["mistakes"]["blunders"] + 
                         self.stats["mistakes"]["mistakes"] + 
                         self.stats["mistakes"]["inaccuracies"])
        
        if total_mistakes > 0:
            blunder_rate = self.stats["mistakes"]["blunders"] / total_mistakes
            
            if blunder_rate > 0.3:
                suggestions.append("Focus on reducing blunders by double-checking your moves")
            
            if self.stats["mistakes"]["blunders"] > self.stats["mistakes"]["good_moves"]:
                suggestions.append("Work on tactical awareness to increase good move percentage")
        
        # Check accuracy trend
        accuracy_trend = self.get_accuracy_trend(5)
        if len(accuracy_trend) >= 3:
            recent_avg = sum(entry["accuracy"] for entry in accuracy_trend[-3:]) / 3
            if recent_avg < 50:
                suggestions.append("Practice calculation to improve your move accuracy")
        
        # Add default suggestions if none generated
        if not suggestions:
            suggestions = [
                "Analyze your games to identify recurring mistakes",
                "Study basic tactical patterns",
                "Practice endgames to improve your technique"
            ]
        
        return suggestions
