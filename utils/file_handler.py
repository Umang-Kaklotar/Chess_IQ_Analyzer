"""
File Handler Module

Reads/writes game history, move data, and player stats JSON files.
Provides utility functions for data persistence.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional, Union

from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Default file paths
DATA_DIR = "data"
GAME_HISTORY_FILE = os.path.join(DATA_DIR, "game_history.json")
PLAYER_STATS_FILE = os.path.join(DATA_DIR, "player_stats.json")
MOVES_INPUT_FILE = os.path.join(DATA_DIR, "moves_input.json")


def ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the loaded data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise


def save_json(data: Union[Dict[str, Any], List[Any]], file_path: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save (dictionary or list)
        file_path: Path to save the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {e}")
        return False


def load_game_history() -> List[Dict[str, Any]]:
    """
    Load game history from the default file.
    
    Returns:
        List of game history entries
    """
    try:
        return load_json(GAME_HISTORY_FILE)
    except FileNotFoundError:
        # Create empty game history file
        save_json([], GAME_HISTORY_FILE)
        return []
    except json.JSONDecodeError:
        # Backup corrupted file and create new one
        backup_file = f"{GAME_HISTORY_FILE}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.warning(f"Corrupted game history file. Backing up to {backup_file}")
        os.rename(GAME_HISTORY_FILE, backup_file)
        save_json([], GAME_HISTORY_FILE)
        return []


def save_game_history(game_history: List[Dict[str, Any]]) -> bool:
    """
    Save game history to the default file.
    
    Args:
        game_history: List of game history entries
        
    Returns:
        True if successful, False otherwise
    """
    return save_json(game_history, GAME_HISTORY_FILE)


def add_game_to_history(game_data: Dict[str, Any]) -> bool:
    """
    Add a new game entry to the game history.
    
    Args:
        game_data: Game data to add
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load existing history
        history = load_game_history()
        
        # Add timestamp if not present
        if "timestamp" not in game_data:
            game_data["timestamp"] = datetime.datetime.now().isoformat()
            
        # Add the new game
        history.append(game_data)
        
        # Save updated history
        return save_game_history(history)
    except Exception as e:
        logger.error(f"Error adding game to history: {e}")
        return False


def load_player_stats() -> Dict[str, Any]:
    """
    Load player statistics from the default file.
    
    Returns:
        Dictionary containing player statistics
    """
    try:
        return load_json(PLAYER_STATS_FILE)
    except FileNotFoundError:
        # Create empty player stats file
        save_json({}, PLAYER_STATS_FILE)
        return {}
    except json.JSONDecodeError:
        # Backup corrupted file and create new one
        backup_file = f"{PLAYER_STATS_FILE}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.warning(f"Corrupted player stats file. Backing up to {backup_file}")
        os.rename(PLAYER_STATS_FILE, backup_file)
        save_json({}, PLAYER_STATS_FILE)
        return {}


def save_player_stats(player_stats: Dict[str, Any]) -> bool:
    """
    Save player statistics to the default file.
    
    Args:
        player_stats: Player statistics dictionary
        
    Returns:
        True if successful, False otherwise
    """
    return save_json(player_stats, PLAYER_STATS_FILE)


def load_moves_input() -> Dict[str, Any]:
    """
    Load moves input data from the default file.
    
    Returns:
        Dictionary containing moves input data
    """
    try:
        return load_json(MOVES_INPUT_FILE)
    except FileNotFoundError:
        # Create empty moves input file
        save_json({}, MOVES_INPUT_FILE)
        return {}
    except json.JSONDecodeError:
        # Backup corrupted file and create new one
        backup_file = f"{MOVES_INPUT_FILE}.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.warning(f"Corrupted moves input file. Backing up to {backup_file}")
        os.rename(MOVES_INPUT_FILE, backup_file)
        save_json({}, MOVES_INPUT_FILE)
        return {}


def save_moves_input(moves_data: Dict[str, Any]) -> bool:
    """
    Save moves input data to the default file.
    
    Args:
        moves_data: Moves input data dictionary
        
    Returns:
        True if successful, False otherwise
    """
    return save_json(moves_data, MOVES_INPUT_FILE)


def save_pgn(pgn_text: str, file_path: Optional[str] = None) -> str:
    """
    Save a game in PGN format.
    
    Args:
        pgn_text: PGN text to save
        file_path: Path to save the PGN file (optional)
        
    Returns:
        Path to the saved file
    """
    if file_path is None:
        # Generate a filename based on date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(DATA_DIR, f"game_{timestamp}.pgn")
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(pgn_text)
        
        logger.info(f"PGN saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving PGN to {file_path}: {e}")
        return ""


def load_pgn(file_path: str) -> str:
    """
    Load a PGN file.
    
    Args:
        file_path: Path to the PGN file
        
    Returns:
        PGN text content
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    try:
        with open(file_path, 'r') as f:
            pgn_text = f.read()
        return pgn_text
    except FileNotFoundError:
        logger.warning(f"PGN file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading PGN from {file_path}: {e}")
        raise


def export_analysis_to_json(analysis_data: Dict[str, Any], file_path: Optional[str] = None) -> str:
    """
    Export analysis results to a JSON file.
    
    Args:
        analysis_data: Analysis data to export
        file_path: Path to save the JSON file (optional)
        
    Returns:
        Path to the saved file
    """
    if file_path is None:
        # Generate a filename based on date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(DATA_DIR, f"analysis_{timestamp}.json")
    
    try:
        # Add timestamp if not present
        if "timestamp" not in analysis_data:
            analysis_data["timestamp"] = datetime.datetime.now().isoformat()
        
        # Save the analysis data
        save_json(analysis_data, file_path)
        
        logger.info(f"Analysis exported to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error exporting analysis to {file_path}: {e}")
        return ""


def backup_data_files() -> bool:
    """
    Create backups of important data files.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = os.path.join(DATA_DIR, "backups", timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Files to backup
        files_to_backup = [
            GAME_HISTORY_FILE,
            PLAYER_STATS_FILE,
            MOVES_INPUT_FILE
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                logger.info(f"Backed up {file_path} to {backup_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating backups: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    ensure_data_dir()
    
    # Test saving and loading game history
    game_data = {
        "white_player": "Player",
        "black_player": "AI",
        "result": "1-0",
        "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Nf6"]
    }
    
    add_game_to_history(game_data)
    history = load_game_history()
    print(f"Game history entries: {len(history)}")
    
    # Test saving and loading player stats
    player_stats = {
        "default": {
            "games_played": 10,
            "wins": 5,
            "losses": 3,
            "draws": 2,
            "average_iq": 1200
        }
    }
    
    save_player_stats(player_stats)
    loaded_stats = load_player_stats()
    print(f"Player stats: {loaded_stats}")
    
    # Test PGN saving
    pgn = """[Event "Example Game"]
[Site "Chess IQ Analyzer"]
[Date "2023.01.01"]
[White "Player"]
[Black "AI"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 d5 5. exd5 Na5 1-0"""
    
    pgn_path = save_pgn(pgn)
    print(f"PGN saved to: {pgn_path}")
