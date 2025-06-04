#!/usr/bin/env python3
"""
Main game runner: initializes game, handles loop, time control, move input, AI move, 
post-game analysis, and stat saving.
"""

import sys
import time
import argparse
import pygame
import json
import logging
from pathlib import Path

from chess_engine.board import Board
from chess_engine.move import Move
from chess_engine.ai_minimax import ChessAI
from analysis.analyzer import Analyzer
from iq.iq_model import IQModel
from iq.progress_tracker import ProgressTracker
from ui.game_ui import GameUI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('chess_iq')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chess IQ Analyzer')
    parser.add_argument('--ai', action='store_true', help='Play against AI')
    parser.add_argument('--difficulty', type=int, choices=range(1, 6), default=3, help='AI difficulty level (1-5)')
    parser.add_argument('--time-control', type=str, default='10+0', help='Time control in minutes+increment format (e.g., 10+5)')
    parser.add_argument('--no-analysis', action='store_true', help='Skip post-game analysis')
    parser.add_argument('--load-pgn', type=str, help='Load game from PGN file')
    
    return parser.parse_args()

def setup_time_control(time_control_str):
    """
    Set up time control from string format.
    
    Args:
        time_control_str: Time control string in format "minutes+increment"
        
    Returns:
        Tuple of (minutes, increment) in seconds
    """
    try:
        parts = time_control_str.split('+')
        minutes = int(parts[0]) * 60  # Convert to seconds
        increment = int(parts[1]) if len(parts) > 1 else 0
        return minutes, increment
    except (ValueError, IndexError):
        logger.warning(f"Invalid time control format: {time_control_str}. Using default 10+0.")
        return 10 * 60, 0

def main():
    """Main function to run the chess game."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up time control
    initial_time, increment = setup_time_control(args.time_control)
    
    # Initialize game components
    logger.info("Initializing Chess IQ Analyzer")
    board = Board()
    game_ui = GameUI()
    
    # Set up AI if enabled
    if args.ai:
        game_ui.ai_enabled = True
        game_ui.ai_difficulty = args.difficulty
        game_ui.ai = ChessAI(args.difficulty)
    
    # Run the game UI
    try:
        game_ui.run()
    except Exception as e:
        logger.error(f"Error in game loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Chess IQ Analyzer terminated")

if __name__ == "__main__":
    main()
