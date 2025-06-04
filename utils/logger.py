"""
Logger Module

Logs key events like moves, game outcomes, and analysis results to console and file.
Provides consistent logging format and levels across the application.
"""

import os
import logging
import datetime
from typing import Optional


# Create logs directory if it doesn't exist
os.makedirs(os.path.join("logs"), exist_ok=True)

# Configure default logging format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels dictionary for easy reference
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


def setup_logger(name: str = "chess_iq", level: str = "info", 
               log_to_file: bool = True, 
               log_to_console: bool = True,
               log_format: str = DEFAULT_FORMAT,
               date_format: str = DEFAULT_DATE_FORMAT) -> logging.Logger:
    """
    Set up and return a logger with the specified configuration.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Log level (debug, info, warning, error, critical)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_format: Log message format
        date_format: Date format in log messages
        
    Returns:
        Configured logger instance
    """
    # Map string level to logging level
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    log_level = level_map.get(level.lower(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        # Create log filename with date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join("logs", f"chess_iq_{today}.log")
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_game_start(logger: logging.Logger, player_white: str, player_black: str) -> None:
    """
    Log the start of a new game.
    
    Args:
        logger: Logger instance
        player_white: Name of player with white pieces
        player_black: Name of player with black pieces
    """
    logger.info(f"New game started: {player_white} (White) vs {player_black} (Black)")


def log_move(logger: logging.Logger, move_notation: str, player: str, 
             move_number: int, time_taken: Optional[float] = None) -> None:
    """
    Log a chess move.
    
    Args:
        logger: Logger instance
        move_notation: Move in algebraic notation (e.g., "e4", "Nf3")
        player: Player making the move ("white" or "black")
        move_number: Move number in the game
        time_taken: Time taken to make the move in seconds (optional)
    """
    time_str = f" in {time_taken:.1f}s" if time_taken is not None else ""
    logger.info(f"Move {move_number}: {player.capitalize()} played {move_notation}{time_str}")


def log_game_end(logger: logging.Logger, result: str, reason: str) -> None:
    """
    Log the end of a game.
    
    Args:
        logger: Logger instance
        result: Game result ("white_win", "black_win", "draw")
        reason: Reason for the result (e.g., "checkmate", "resignation", "time")
    """
    result_str = {
        "white_win": "White wins",
        "black_win": "Black wins",
        "draw": "Game drawn"
    }.get(result, "Game ended")
    
    logger.info(f"Game ended: {result_str} by {reason}")


def log_analysis_result(logger: logging.Logger, accuracy: float, 
                       blunders: int, mistakes: int, inaccuracies: int, 
                       iq_score: float) -> None:
    """
    Log game analysis results.
    
    Args:
        logger: Logger instance
        accuracy: Move accuracy percentage
        blunders: Number of blunders
        mistakes: Number of mistakes
        inaccuracies: Number of inaccuracies
        iq_score: Calculated Chess IQ score
    """
    logger.info(f"Game analysis: Accuracy {accuracy:.1f}%, "
               f"Blunders: {blunders}, Mistakes: {mistakes}, Inaccuracies: {inaccuracies}, "
               f"Chess IQ: {iq_score:.1f}")


def log_error(logger: logging.Logger, error_type: str, details: str) -> None:
    """
    Log an error.
    
    Args:
        logger: Logger instance
        error_type: Type of error
        details: Error details
    """
    logger.error(f"{error_type}: {details}")


if __name__ == "__main__":
    # Example usage
    test_logger = get_logger("test")
    log_game_start(test_logger, "Player", "AI")
    log_move(test_logger, "e4", "white", 1, 2.5)
    log_move(test_logger, "e5", "black", 1, 1.8)
    log_game_end(test_logger, "white_win", "checkmate")
    log_analysis_result(test_logger, 85.5, 1, 2, 3, 1450.0)
def get_logger(name: str, level: str = "info", 
               log_to_file: bool = True, 
               log_to_console: bool = True,
               log_format: str = DEFAULT_FORMAT,
               date_format: str = DEFAULT_DATE_FORMAT) -> logging.Logger:
    """
    Alias for setup_logger for backward compatibility.
    """
    return setup_logger(name, level, log_to_file, log_to_console, log_format, date_format)
