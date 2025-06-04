"""
Game UI Module

Handles the main game UI, rendering, and user interaction.
"""

from typing import Tuple, List, Dict, Optional, Any, Callable
import sys
import os
import time
import random
import pygame
import logging

from chess_engine.board import Board
from chess_engine.move import Move
from chess_engine.ai_minimax import ChessAI
from ui.board_view import BoardView
from ui.components import Button, Label, Timer, MessageBox, Dropdown, Slider
from iq.progress_tracker import ProgressTracker
from utils.config import load_config

# Set up logging
logger = logging.getLogger(__name__)

class GameUI:
    """
    Main game UI class that handles rendering and user interaction.
    """
    
    def __init__(self, screen_size=(1200, 800)):
        """
        Initialize the game UI and pygame components.
        
        Args:
            screen_size: Tuple of (width, height) for the screen
        """
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Chess IQ Analyzer")
        
        # Set screen dimensions
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_size
        
        # Adjust board size based on screen height
        self.BOARD_SIZE = min(int(self.SCREEN_HEIGHT * 0.8), int(self.SCREEN_WIDTH * 0.6))
        self.BOARD_OFFSET_X = 50
        self.BOARD_OFFSET_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2
        self.SIDEBAR_X = self.BOARD_OFFSET_X + self.BOARD_SIZE + 20
        self.SIDEBAR_WIDTH = self.SCREEN_WIDTH - self.SIDEBAR_X - 20
        
        # Load configuration
        self.config = load_config()
        
        # Initialize the screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Initialize board view
        self.board_view = BoardView(self.BOARD_SIZE, self.BOARD_OFFSET_X, self.BOARD_OFFSET_Y)
        
        # Game state
        self.board = None
        self.selected_piece = None
        self.selected_pos = None
        self.legal_moves = []
        self.last_move = None
        self.current_turn = "white"
        self.game_over = False
        self.winner = None
        self.move_history = []
        
        # AI - default to enabled
        self.ai_enabled = True
        self.ai_difficulty = 3
        self.ai_thinking = False
        self.player_color = "white"
        self.ai = ChessAI(self.ai_difficulty)
        
        # Timers
        self.white_time = 10 * 60  # 10 minutes in seconds
        self.black_time = 10 * 60
        self.white_timer = Timer(self.white_time)
        self.black_timer = Timer(self.black_time)
        self.timer_active = True
        self.last_time_update = time.time()
        
        # Progress tracking
        self.progress_tracker = ProgressTracker()
        
        # UI elements
        self.running = True
        self.buttons = {}
        self.labels = {}
        self.message_box = None
        self._init_ui_elements()
        
        # Colors
        self.BG_COLOR = (40, 44, 52)
        self.HIGHLIGHT_COLOR = (124, 252, 0, 150)  # Semi-transparent light green
        self.MOVE_HIGHLIGHT = (255, 255, 0, 128)   # Semi-transparent yellow
        self.LAST_MOVE = (255, 165, 0, 180)        # Semi-transparent orange
        self.CHECK_HIGHLIGHT = (255, 0, 0, 180)    # Semi-transparent red
        
        # Sound effects
        self.sounds = {}
        self._load_sounds()
    
    def _init_ui_elements(self):
        """Initialize UI elements like buttons and labels."""
        # Create buttons
        button_width = 180
        button_height = 40
        button_x = self.SIDEBAR_X + (self.SIDEBAR_WIDTH - button_width) // 2
        button_y = 50
        button_spacing = 60
        
        self.buttons["new_game"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "New Game", 
            self.new_game
        )
        
        button_y += button_spacing
        self.buttons["ai_toggle"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Play vs AI: ON", 
            self.toggle_ai
        )
        
        button_y += button_spacing
        self.buttons["ai_difficulty"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            f"AI Difficulty: {self.ai_difficulty}", 
            self.cycle_ai_difficulty
        )
        
        button_y += button_spacing
        self.buttons["flip_board"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Flip Board", 
            self.flip_board
        )
        
        button_y += button_spacing
        self.buttons["undo_move"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Undo Move", 
            self.undo_move
        )
        
        button_y += button_spacing
        self.buttons["resign"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Resign", 
            self.resign_game
        )
        
        button_y += button_spacing
        self.buttons["stats"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Player Stats", 
            self.show_stats
        )
        
        button_y += button_spacing
        self.buttons["exit"] = Button(
            button_x, button_y, 
            button_width, button_height, 
            "Exit", 
            self.exit_game
        )
        
        # Create labels
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)
        
        label_x = self.SIDEBAR_X + 20
        label_y = self.SCREEN_HEIGHT - 200
        
        self.labels["turn"] = Label(
            label_x, label_y, 
            "Turn: White", 
            font_medium
        )
        
        label_y += 40
        self.labels["white_time"] = Label(
            label_x, label_y, 
            "White: 10:00", 
            font_medium
        )
        
        label_y += 30
        self.labels["black_time"] = Label(
            label_x, label_y, 
            "Black: 10:00", 
            font_medium
        )
        
        label_y += 40
        self.labels["status"] = Label(
            label_x, label_y, 
            "Game in progress", 
            font_medium
        )
        
        label_y += 30
        self.labels["last_move"] = Label(
            label_x, label_y, 
            "Last move: ", 
            font_small
        )
        
        # Create message box
        self.message_box = MessageBox(
            self.SCREEN_WIDTH // 2, 
            self.SCREEN_HEIGHT // 2, 
            400, 200, 
            font_medium
        )
    
    def _load_sounds(self):
        """Load sound effects."""
        sound_files = {
            "move": "move.wav",
            "capture": "capture.wav",
            "check": "check.wav",
            "castle": "castle.wav",
            "game_end": "game_end.wav"
        }
        
        # Create sounds directory if it doesn't exist
        os.makedirs(os.path.join("assets", "sounds"), exist_ok=True)
        
        # Try to load sound files
        for sound_name, file_name in sound_files.items():
            sound_path = os.path.join("assets", "sounds", file_name)
            try:
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
            except pygame.error:
                pass
        
        if not self.sounds:
            logger.warning("Sound files not found. Continuing without sound.")
    
    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def new_game(self) -> None:
        """Start a new chess game."""
        self.board = Board()
        self.selected_piece = None
        self.selected_pos = None
        self.legal_moves = []
        self.last_move = None
        self.game_over = False
        self.winner = None
        self.current_turn = "white"
        self.move_history = []
        
        # Reset timers
        self.white_time = 10 * 60
        self.black_time = 10 * 60
        self.last_time_update = time.time()
        self.timer_active = True
        
        # Update labels
        self.labels["turn"].set_text("Turn: White")
        self.labels["status"].set_text("Game started! White to move. Click on a piece to select it.")
        self.labels["white_time"].set_text("White: 10:00")
        self.labels["black_time"].set_text("Black: 10:00")
        self.labels["last_move"].set_text("Last move: ")
        
        # Make sure AI is enabled
        self.ai_enabled = True
        self.buttons["ai_toggle"].set_text("Play vs AI: ON")
        
        logger.info("New game started")
    
    def toggle_ai(self) -> None:
        """Toggle AI opponent on/off."""
        self.ai_enabled = not self.ai_enabled
        self.buttons["ai_toggle"].set_text(f"Play vs AI: {'ON' if self.ai_enabled else 'OFF'}")
        
        # Update AI difficulty button state
        self.buttons["ai_difficulty"].set_enabled(self.ai_enabled)
        
        logger.info(f"AI opponent {'enabled' if self.ai_enabled else 'disabled'}")
    
    def cycle_ai_difficulty(self) -> None:
        """Cycle through AI difficulty levels."""
        self.ai_difficulty = (self.ai_difficulty % 5) + 1
        self.buttons["ai_difficulty"].set_text(f"AI Difficulty: {self.ai_difficulty}")
        self.ai = ChessAI(self.ai_difficulty)
        
        logger.info(f"AI difficulty set to {self.ai_difficulty}")
    
    def flip_board(self) -> None:
        """Flip the board orientation."""
        self.board_view.flip_board()
        
        logger.info("Board flipped")
    
    def undo_move(self) -> None:
        """Undo the last move."""
        if not self.move_history:
            self.message_box.show("No moves to undo", 2)
            return
        
        # Undo the move on the board
        if self.board.undo_move():
            # Remove from move history
            self.move_history.pop()
            
            # Update last move
            self.last_move = self.move_history[-1] if self.move_history else None
            
            # Switch turns
            self.current_turn = "black" if self.current_turn == "white" else "white"
            self.labels["turn"].set_text(f"Turn: {self.current_turn.capitalize()}")
            
            # Clear selection
            self.selected_piece = None
            self.selected_pos = None
            self.legal_moves = []
            
            # Update status
            self.labels["status"].set_text(f"{self.current_turn.capitalize()}'s turn. Select a piece to move.")
            
            # Update last move label
            if self.last_move:
                move_text = f"{chr(97 + self.last_move.start_col)}{8 - self.last_move.start_row} → "
                move_text += f"{chr(97 + self.last_move.end_col)}{8 - self.last_move.end_row}"
                self.labels["last_move"].set_text(f"Last move: {move_text}")
            else:
                self.labels["last_move"].set_text("Last move: ")
            
            # Reset game over state
            self.game_over = False
            self.winner = None
            
            logger.info("Move undone")
    
    def resign_game(self) -> None:
        """Resign the current game."""
        if self.game_over:
            self.message_box.show("Game already over", 2)
            return
        
        self.game_over = True
        self.winner = "black" if self.current_turn == "white" else "white"
        self.labels["status"].set_text(f"Game over. {self.winner.capitalize()} wins by resignation")
        self.timer_active = False
        
        # Update player stats
        result = "loss" if self.winner != self.player_color else "win"
        self.progress_tracker.update_game_result(result)
        
        logger.info(f"Game resigned. {self.winner.capitalize()} wins")
    
    def show_stats(self) -> None:
        """Show player statistics."""
        # Get player stats
        stats = self.progress_tracker.get_stats()
        
        # Create a structured stats display
        self.render_stats_screen(stats)
        
        logger.info("Stats view shown")
        
    def render_stats_screen(self, stats):
        """
        Render a structured stats screen.
        
        Args:
            stats: Player statistics dictionary
        """
        # Create a surface for the stats screen
        stats_surface = pygame.Surface((self.SCREEN_WIDTH - 100, self.SCREEN_HEIGHT - 100))
        stats_surface.fill((50, 50, 60))
        
        # Create fonts
        title_font = pygame.font.Font(None, 36)
        header_font = pygame.font.Font(None, 28)
        text_font = pygame.font.Font(None, 24)
        
        # Title
        title = title_font.render("CHESS IQ ANALYZER - PLAYER STATISTICS", True, (255, 255, 255))
        stats_surface.blit(title, (stats_surface.get_width() // 2 - title.get_width() // 2, 20))
        
        # Draw horizontal separator
        pygame.draw.line(stats_surface, (200, 200, 200), (50, 60), (stats_surface.get_width() - 50, 60), 2)
        
        # IQ Section
        iq = stats.get("iq", {}).get("current", 110)
        iq_text = header_font.render(f"Chess IQ: {iq}", True, (255, 255, 100))
        stats_surface.blit(iq_text, (50, 80))
        
        # IQ Classification
        iq_class = "Beginner"
        if iq >= 140:
            iq_class = "Genius"
        elif iq >= 130:
            iq_class = "Advanced"
        elif iq >= 120:
            iq_class = "Intermediate"
        elif iq >= 110:
            iq_class = "Average"
        elif iq >= 100:
            iq_class = "Casual"
        elif iq >= 90:
            iq_class = "Novice"
        elif iq >= 80:
            iq_class = "Beginner"
        else:
            iq_class = "Needs Practice"
            
        class_text = text_font.render(f"Classification: {iq_class}", True, (200, 200, 200))
        stats_surface.blit(class_text, (50, 110))
        
        # Draw IQ bar
        bar_width = 300
        bar_height = 20
        bar_x = stats_surface.get_width() - bar_width - 50
        bar_y = 90
        
        # Background bar
        pygame.draw.rect(stats_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # IQ progress bar
        iq_ratio = (iq - 70) / (150 - 70)  # Scale to 0-1 range
        iq_width = int(bar_width * iq_ratio)
        
        # Color based on IQ
        if iq >= 130:
            bar_color = (50, 200, 50)  # Green
        elif iq >= 110:
            bar_color = (200, 200, 50)  # Yellow
        elif iq >= 90:
            bar_color = (200, 150, 50)  # Orange
        else:
            bar_color = (200, 50, 50)  # Red
            
        pygame.draw.rect(stats_surface, bar_color, (bar_x, bar_y, iq_width, bar_height))
        
        # IQ scale labels
        scale_font = pygame.font.Font(None, 18)
        scale_70 = scale_font.render("70", True, (200, 200, 200))
        scale_150 = scale_font.render("150", True, (200, 200, 200))
        stats_surface.blit(scale_70, (bar_x - 20, bar_y + 2))
        stats_surface.blit(scale_150, (bar_x + bar_width + 5, bar_y + 2))
        
        # Game Stats Section
        games = stats.get("games", {})
        total = games.get("total", 0)
        wins = games.get("wins", 0)
        losses = games.get("losses", 0)
        draws = games.get("draws", 0)
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        # Game stats header
        game_header = header_font.render("Game Statistics", True, (255, 255, 255))
        stats_surface.blit(game_header, (50, 150))
        
        # Game stats text
        game_stats = [
            f"Games Played: {total}",
            f"Wins: {wins}",
            f"Losses: {losses}",
            f"Draws: {draws}",
            f"Win Rate: {win_rate:.1f}%"
        ]
        
        for i, stat in enumerate(game_stats):
            stat_text = text_font.render(stat, True, (200, 200, 200))
            stats_surface.blit(stat_text, (70, 180 + i * 25))
        
        # Draw win/loss pie chart
        if total > 0:
            center_x = stats_surface.get_width() - 150
            center_y = 200
            radius = 60
            
            # Calculate angles
            win_angle = wins / total * 360
            loss_angle = losses / total * 360
            draw_angle = draws / total * 360
            
            # Draw pie segments
            if wins > 0:
                pygame.draw.arc(stats_surface, (50, 200, 50), (center_x - radius, center_y - radius, radius * 2, radius * 2), 
                               0, win_angle * 3.14159 / 180, radius)
            if losses > 0:
                pygame.draw.arc(stats_surface, (200, 50, 50), (center_x - radius, center_y - radius, radius * 2, radius * 2), 
                               win_angle * 3.14159 / 180, (win_angle + loss_angle) * 3.14159 / 180, radius)
            if draws > 0:
                pygame.draw.arc(stats_surface, (200, 200, 50), (center_x - radius, center_y - radius, radius * 2, radius * 2), 
                               (win_angle + loss_angle) * 3.14159 / 180, 2 * 3.14159, radius)
            
            # Legend
            legend_items = [
                ("Wins", (50, 200, 50)),
                ("Losses", (200, 50, 50)),
                ("Draws", (200, 200, 50))
            ]
            
            for i, (label, color) in enumerate(legend_items):
                pygame.draw.rect(stats_surface, color, (center_x - 50, center_y + 70 + i * 20, 15, 15))
                legend_text = text_font.render(label, True, (200, 200, 200))
                stats_surface.blit(legend_text, (center_x - 30, center_y + 70 + i * 20))
        
        # Piece Performance Section
        piece_header = header_font.render("Piece Performance", True, (255, 255, 255))
        stats_surface.blit(piece_header, (50, 320))
        
        # Count captures by piece type
        piece_captures = {
            'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0
        }
        
        for move in self.move_history:
            if move.piece_captured:
                piece_type = move.piece_moved.piece_type if move.piece_moved else 'P'
                if piece_type in piece_captures:
                    piece_captures[piece_type] += 1
        
        # Display piece performance as bar chart
        piece_names = {'P': 'Pawns', 'N': 'Knights', 'B': 'Bishops', 'R': 'Rooks', 'Q': 'Queen'}
        max_captures = max(piece_captures.values()) if piece_captures.values() else 1
        
        for i, (piece, name) in enumerate(piece_names.items()):
            # Piece name
            piece_text = text_font.render(name, True, (200, 200, 200))
            stats_surface.blit(piece_text, (70, 350 + i * 30))
            
            # Bar background
            pygame.draw.rect(stats_surface, (100, 100, 100), (170, 350 + i * 30, 200, 20))
            
            # Bar fill
            capture_width = int(200 * (piece_captures[piece] / max_captures)) if max_captures > 0 else 0
            pygame.draw.rect(stats_surface, (100, 150, 200), (170, 350 + i * 30, capture_width, 20))
            
            # Capture count
            count_text = text_font.render(str(piece_captures[piece]), True, (255, 255, 255))
            stats_surface.blit(count_text, (380, 350 + i * 30))
        
        # Improvement Tips Section
        tips_header = header_font.render("Improvement Tips", True, (255, 255, 255))
        stats_surface.blit(tips_header, (50, 500))
        
        # Add improvement suggestions
        suggestions = self.progress_tracker.get_improvement_suggestions()
        if suggestions:
            for i, suggestion in enumerate(suggestions[:3], 1):
                tip_text = text_font.render(f"{i}. {suggestion}", True, (200, 200, 200))
                stats_surface.blit(tip_text, (70, 530 + i * 25))
        else:
            no_tips = text_font.render("Play more games to get personalized tips!", True, (200, 200, 200))
            stats_surface.blit(no_tips, (70, 530))
        
        # Display the stats screen
        self.screen.blit(stats_surface, (50, 50))
        pygame.display.flip()
        
        # Wait for user to close the stats screen
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        
        # Redraw the game screen
        self.render()
    
    def exit_game(self) -> None:
        """Exit the game."""
        self.running = False
        
        logger.info("Game exited")
    
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            # Quit event
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Mouse button down
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if a button was clicked
                button_clicked = False
                for button in self.buttons.values():
                    if button.is_clicked(mouse_pos):
                        button.on_click()
                        button_clicked = True
                        break
                
                # If no button was clicked, check if the board was clicked
                if not button_clicked and not self.game_over:
                    self.handle_board_click(mouse_pos)
            
            # Key down
            elif event.type == pygame.KEYDOWN:
                # Escape key exits
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def handle_board_click(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Handle clicks on the chess board.
        
        Args:
            mouse_pos: Mouse position (x, y)
        """
        # Check if click is within board boundaries
        if not self.board_view.is_within_board(mouse_pos):
            return
            
        # Get board coordinates from mouse position
        board_pos = self.board_view.get_board_position(mouse_pos)
        
        # If it's not the player's turn in AI mode, ignore clicks
        if self.ai_enabled and self.current_turn != self.player_color:
            self.labels["status"].set_text(f"It's {self.current_turn.capitalize()}'s turn (AI). Please wait...")
            return
            
        # If a piece is already selected
        if self.selected_piece:
            # Create a move object
            move = Move(self.selected_pos, board_pos)
            
            # Check if the move is legal
            if self.board.is_valid_move(move):
                # Make the move
                self.make_move(move)
                self.selected_piece = None
                self.selected_pos = None
                self.legal_moves = []
                
                # If AI is enabled and it's AI's turn, trigger AI move
                if self.ai_enabled and self.current_turn != self.player_color and not self.game_over:
                    self.ai_thinking = True
                    # Process AI move immediately
                    self.process_ai_move()
            else:
                # Check if another piece of the same color was clicked
                piece = self.board.get_piece_at(board_pos[0], board_pos[1])
                if piece and piece.color == ('w' if self.current_turn == "white" else 'b'):
                    self.selected_piece = piece
                    self.selected_pos = board_pos
                    self.legal_moves = self.board.get_valid_moves(board_pos)
                    self.labels["status"].set_text(f"Selected {piece.piece_type if piece else 'piece'}. Click destination square to move.")
                else:
                    # Deselect if clicking elsewhere
                    self.selected_piece = None
                    self.selected_pos = None
                    self.legal_moves = []
                    self.labels["status"].set_text(f"{self.current_turn.capitalize()}'s turn. Select a piece to move.")
        else:
            # Select a piece if it's of the current turn's color
            piece = self.board.get_piece_at(board_pos[0], board_pos[1])
            if piece and piece.color == ('w' if self.current_turn == "white" else 'b'):
                self.selected_piece = piece
                self.selected_pos = board_pos
                self.legal_moves = self.board.get_valid_moves(board_pos)
                
                # Show available moves
                self.labels["status"].set_text(f"Selected {piece.piece_type if piece else 'piece'}. Click destination square to move.")
            else:
                if piece:
                    self.labels["status"].set_text(f"That's not your piece. It's {self.current_turn.capitalize()}'s turn.")
                else:
                    self.labels["status"].set_text(f"{self.current_turn.capitalize()}'s turn. Select a piece to move.")
    
    def make_move(self, move: Move) -> None:
        """
        Make a chess move on the board.
        
        Args:
            move: The move to make
        """
        # Update the move with board information
        move.piece_moved = self.board.board[move.start_row][move.start_col]
        move.piece_captured = self.board.board[move.end_row][move.end_col]
        
        # Store move in history
        self.move_history.append(move)
        
        # Check for special moves to play appropriate sounds
        is_capture = move.piece_captured is not None
        is_castle = (
            move.piece_moved and move.piece_moved.piece_type == 'K' and 
            abs(move.start_col - move.end_col) > 1
        )
        
        # Execute the move
        self.board.make_move(move)
        self.last_move = move
        
        # Update last move label
        move_text = f"{chr(97 + move.start_col)}{8 - move.start_row} → "
        move_text += f"{chr(97 + move.end_col)}{8 - move.end_row}"
        self.labels["last_move"].set_text(f"Last move: {move_text}")
        
        # Play appropriate sound
        if is_castle:
            self.play_sound("castle")
        elif is_capture:
            self.play_sound("capture")
        else:
            self.play_sound("move")
        
        # Switch turns
        self.current_turn = "black" if self.current_turn == "white" else "white"
        self.labels["turn"].set_text(f"Turn: {self.current_turn.capitalize()}")
        
        # Calculate and update IQ after each move
        current_result = "in_progress"
        if len(self.move_history) > 5:  # Only start calculating after a few moves
            # Calculate a provisional IQ based on current game state
            if self.current_turn == self.player_color:  # Player just made a move
                current_result = "provisional_win"
            else:  # AI just made a move
                current_result = "provisional_loss"
            
            iq_score = self._calculate_provisional_iq(current_result)
            self.progress_tracker.update_iq(iq_score)
        
        # Check for check
        if hasattr(self.board, 'in_check') and self.board.in_check:
            self.play_sound("check")
            self.labels["status"].set_text(f"{self.current_turn.capitalize()} is in check!")
            
        # Check for checkmate or stalemate
        if hasattr(self.board, 'checkmate') and self.board.checkmate:
            self.game_over = True
            self.winner = "white" if self.current_turn == "black" else "black"
            self.labels["status"].set_text(f"Checkmate! {self.winner.capitalize()} wins")
            self.timer_active = False
            self.play_sound("game_end")
            
            # Update player stats
            result = "win" if self.winner == self.player_color else "loss"
            self.progress_tracker.update_game_result(result)
            
            # Calculate and show IQ
            iq_score = self._calculate_iq_score(result)
            self.progress_tracker.update_iq(iq_score)
            
            # Show game over message with IQ
            self.message_box.show(f"Game Over! {self.winner.capitalize()} wins\n\nYour Chess IQ: {iq_score}", 5)
            
        elif hasattr(self.board, 'stalemate') and self.board.stalemate:
            self.game_over = True
            self.labels["status"].set_text("Stalemate! Game drawn")
            self.timer_active = False
            self.play_sound("game_end")
            
            # Update player stats
            self.progress_tracker.update_game_result("draw")
            
            # Calculate and show IQ
            iq_score = self._calculate_iq_score("draw")
            self.progress_tracker.update_iq(iq_score)
            
            # Show game over message with IQ
            self.message_box.show(f"Game Over! Draw by stalemate\n\nYour Chess IQ: {iq_score}", 5)
            
        # If AI is enabled and it's AI's turn, trigger AI move
        if self.ai_enabled and self.current_turn != self.player_color and not self.game_over:
            self.ai_thinking = True
            self.labels["status"].set_text("AI is thinking...")
        else:
            self.labels["status"].set_text(f"{self.current_turn.capitalize()}'s turn. Select a piece to move.")
    
    def process_ai_move(self) -> None:
        """Process AI move if it's AI's turn."""
        if not self.ai_thinking:
            return
            
        # Show thinking indicator
        self.labels["status"].set_text("AI is thinking...")
        
        # Add a delay to simulate AI thinking (2-5 seconds)
        thinking_time = random.uniform(2, 5)
        start_time = time.time()
        
        # Update the display while "thinking"
        while time.time() - start_time < thinking_time:
            # Handle events to keep the UI responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            
            # Update AI's timer while thinking
            if self.timer_active and not self.game_over:
                current_time = time.time()
                elapsed = current_time - self.last_time_update
                self.last_time_update = current_time
                
                if self.current_turn == "black":
                    self.black_time -= elapsed
                    minutes = int(self.black_time // 60)
                    seconds = int(self.black_time % 60)
                    self.labels["black_time"].set_text(f"Black: {minutes:02d}:{seconds:02d}")
                else:
                    self.white_time -= elapsed
                    minutes = int(self.white_time // 60)
                    seconds = int(self.white_time % 60)
                    self.labels["white_time"].set_text(f"White: {minutes:02d}:{seconds:02d}")
            
            # Render the game to show the thinking status
            self.render()
            pygame.display.flip()
            self.clock.tick(30)
        
        # Get AI move
        ai_move = None
        try:
            # Create a simple move for testing if AI is not properly implemented
            if hasattr(self.ai, 'get_best_move'):
                ai_move = self.ai.get_best_move(self.board, self.current_turn)
            
            # If AI didn't return a move, make a simple one
            if not ai_move:
                # Find a valid move for the AI
                valid_moves = self.board.get_valid_moves()
                if valid_moves:
                    # Prioritize capturing moves
                    capturing_moves = [move for move in valid_moves if move.piece_captured]
                    if capturing_moves:
                        ai_move = random.choice(capturing_moves)
                    else:
                        ai_move = random.choice(valid_moves)
        except Exception as e:
            print(f"Error getting AI move: {e}")
            # Find a valid move for the AI
            valid_moves = self.board.get_valid_moves()
            if valid_moves:
                ai_move = random.choice(valid_moves)
        
        if ai_move:
            # Make the move
            self.make_move(ai_move)
        else:
            # If no move could be made, end AI thinking
            self.labels["status"].set_text("AI couldn't find a move!")
        
        self.ai_thinking = False

    def update_timers(self) -> None:
        """Update game timers."""
        if not self.timer_active or self.game_over:
            return
        
        # Calculate elapsed time since last update
        current_time = time.time()
        elapsed = current_time - self.last_time_update
        self.last_time_update = current_time
            
        # Update the active timer
        if self.current_turn == "white":
            # Decrease white's time
            self.white_time -= elapsed
            
            # Check for time out
            if self.white_time <= 0:
                self.white_time = 0
                self.game_over = True
                self.winner = "black"
                self.labels["status"].set_text("White out of time! Black wins")
                self.timer_active = False
                self.play_sound("game_end")
                
                # Update player stats
                result = "loss" if self.player_color == "white" else "win"
                self.progress_tracker.update_game_result(result)
            
            # Update display
            minutes = int(self.white_time // 60)
            seconds = int(self.white_time % 60)
            self.labels["white_time"].set_text(f"White: {minutes:02d}:{seconds:02d}")
        else:
            # Decrease black's time
            self.black_time -= elapsed
            
            # Check for time out
            if self.black_time <= 0:
                self.black_time = 0
                self.game_over = True
                self.winner = "white"
                self.labels["status"].set_text("Black out of time! White wins")
                self.timer_active = False
                self.play_sound("game_end")
                
                # Update player stats
                result = "win" if self.player_color == "white" else "loss"
                self.progress_tracker.update_game_result(result)
            
            # Update display
            minutes = int(self.black_time // 60)
            seconds = int(self.black_time % 60)
            self.labels["black_time"].set_text(f"Black: {minutes:02d}:{seconds:02d}")
    
    def render(self) -> None:
        """Render the game UI."""
        # Fill background
        self.screen.fill(self.BG_COLOR)
        
        # Draw board
        self.board_view.draw(self.screen, self.board)
        
        # Draw selected piece highlight
        if self.selected_pos:
            self.board_view.draw_highlight(self.screen, self.selected_pos, self.HIGHLIGHT_COLOR)
        
        # Draw legal moves
        for move in self.legal_moves:
            self.board_view.draw_highlight(self.screen, (move.end_row, move.end_col), self.MOVE_HIGHLIGHT)
        
        # Draw last move highlight
        if self.last_move:
            self.board_view.draw_highlight(self.screen, (self.last_move.start_row, self.last_move.start_col), self.LAST_MOVE)
            self.board_view.draw_highlight(self.screen, (self.last_move.end_row, self.last_move.end_col), self.LAST_MOVE)
        
        # Draw check highlight
        if hasattr(self.board, 'in_check') and self.board.in_check:
            king_pos = self.board.white_king_location if self.current_turn == "white" else self.board.black_king_location
            self.board_view.draw_highlight(self.screen, king_pos, self.CHECK_HIGHLIGHT)
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw labels
        for label in self.labels.values():
            label.draw(self.screen)
        
        # Draw message box
        self.message_box.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def get_player_move(self, board, player_color: str, time_remaining: float) -> Optional[Move]:
        """
        Get a move from the player.
        
        Args:
            board: Chess board
            player_color: Player color ("white" or "black")
            time_remaining: Time remaining in seconds
            
        Returns:
            Move object or None if no move was made
        """
        # Store the board and player color
        self.board = board
        self.player_color = player_color
        
        # Update timers
        if player_color == "white":
            self.white_time = time_remaining
            self.white_timer = Timer(time_remaining)
        else:
            self.black_time = time_remaining
            self.black_timer = Timer(time_remaining)
        
        # Handle events
        self.handle_events()
        
        # Render the game
        self.render()
        
        # Return None (no move made yet)
        return None
    
    def run(self) -> None:
        """Run the main game loop."""
        self.new_game()  # Start a new game
        
        while self.running:
            # Handle events
            self.handle_events()
            
            # Process AI move if needed
            if self.ai_thinking:
                self.process_ai_move()
            
            # Update timers
            self.update_timers()
            
            # Update message box
            self.message_box.update()
            
            # Render the game
            self.render()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Clean up pygame
        pygame.quit()
        sys.exit()
    def _calculate_iq_score(self, result: str) -> int:
        """
        Calculate Chess IQ score based on game performance.
        
        Args:
            result: Game result ("win", "loss", or "draw")
            
        Returns:
            Chess IQ score
        """
        # Default IQ for loss
        if result == "loss":
            return 70
            
        # Base IQ score
        base_iq = 110  # Start with average IQ
        
        # Get previous IQ if available
        previous_iq = self.progress_tracker.get_stats().get("iq", {}).get("current", 110)
        
        # Piece values for material evaluation
        piece_values = {
            'P': 1,
            'N': 3,
            'B': 3,
            'R': 5,
            'Q': 9,
            'K': 0  # King doesn't count for material advantage
        }
        
        # Count material for both sides
        white_material = 0
        black_material = 0
        
        # Count material on the board
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece:
                    value = piece_values.get(piece.piece_type, 0)
                    if piece.color == 'w':
                        white_material += value
                    else:
                        black_material += value
        
        # Calculate material advantage
        if self.player_color == "white":
            material_advantage = white_material - black_material
        else:
            material_advantage = black_material - white_material
        
        # Material adjustment (more significant impact on IQ)
        material_adjustment = material_advantage * 3
        
        # Adjust based on result
        if result == "win":
            result_adjustment = 10 + (self.ai_difficulty * 2)
        elif result == "loss":
            result_adjustment = -15 - (self.ai_difficulty * 1)
        else:  # draw
            result_adjustment = 5
        
        # Adjust based on move quality
        good_moves = 0
        bad_moves = 0
        captures = 0
        checks = 0
        risks_taken = 0
        promotions = 0
        
        for i, move in enumerate(self.move_history):
            # Only count player moves
            if i % 2 == (0 if self.player_color == "white" else 1):
                continue
                
            # Count captures
            if move.piece_captured:
                captures += 1
                # Bonus for capturing higher value pieces
                if move.piece_captured.piece_type in ['Q', 'R']:
                    good_moves += 2
                elif move.piece_captured.piece_type in ['B', 'N']:
                    good_moves += 1
            
            # Check if move put opponent in check
            self.board.make_move(move)
            if self.board.in_check:
                checks += 1
                good_moves += 1
            
            # Check for pawn promotion
            if move.piece_moved and move.piece_moved.piece_type == 'P':
                if (move.piece_moved.color == 'w' and move.end_row == 0) or \
                   (move.piece_moved.color == 'b' and move.end_row == 7):
                    promotions += 1
                    good_moves += 3  # Big bonus for promotion
            
            self.board.undo_move()
            
            # Check if a piece was moved to a threatened square (risk taking)
            if self.board.square_under_attack(move.end_row, move.end_col):
                risks_taken += 1
                
                # If the risk resulted in a capture, it's a good risk
                if move.piece_captured:
                    good_moves += 1
                else:
                    bad_moves += 1
        
        # Adjust IQ based on move quality
        move_quality_adjustment = (good_moves * 2) - (bad_moves * 3) + (captures * 3) + (checks * 2) + (promotions * 5)
        
        # Adjust for risk-taking (strategic risks are rewarded)
        risk_adjustment = min(risks_taken * 1, 10)  # Cap at +10
        
        # Adjust based on game length
        game_length = len(self.move_history)
        if game_length < 10:
            game_length_adjustment = -5  # Penalize very short games
        elif game_length < 20:
            game_length_adjustment = 0
        else:
            game_length_adjustment = min((game_length - 20) // 10, 5)  # Bonus for longer games
        
        # Adjust based on AI difficulty if playing against AI
        ai_difficulty_adjustment = 0
        if self.ai_enabled:
            ai_difficulty_adjustment = (self.ai_difficulty - 3) * 5
        
        # Calculate final IQ
        final_iq = previous_iq + result_adjustment + move_quality_adjustment + game_length_adjustment + ai_difficulty_adjustment + risk_adjustment + material_adjustment
        
        # Ensure IQ is within the specified range (70-150)
        final_iq = max(min(final_iq, 150), 70)
        
        # Log the IQ calculation
        print(f"IQ Calculation:")
        print(f"  Previous IQ: {previous_iq}")
        print(f"  Material advantage: {material_adjustment} (player: {white_material if self.player_color == 'white' else black_material}, opponent: {black_material if self.player_color == 'white' else white_material})")
        print(f"  Result adjustment: {result_adjustment}")
        print(f"  Move quality: {move_quality_adjustment} (good: {good_moves}, bad: {bad_moves}, captures: {captures}, checks: {checks}, promotions: {promotions})")
        print(f"  Risk taking: {risk_adjustment} (risks: {risks_taken})")
        print(f"  Game length: {game_length_adjustment} (moves: {game_length})")
        print(f"  AI difficulty: {ai_difficulty_adjustment} (level: {self.ai_difficulty})")
        print(f"  Final IQ: {final_iq}")
        
        return int(final_iq)
    def _calculate_provisional_iq(self, result: str) -> int:
        """
        Calculate a provisional IQ score during the game.
        
        Args:
            result: Current game state ("provisional_win", "provisional_loss", "in_progress")
            
        Returns:
            Provisional IQ score
        """
        # Get previous IQ if available
        previous_iq = self.progress_tracker.get_stats().get("iq", {}).get("current", 110)
        
        # Count material for both sides
        white_material = 0
        black_material = 0
        
        # Piece values
        piece_values = {
            'P': 1,
            'N': 3,
            'B': 3,
            'R': 5,
            'Q': 9,
            'K': 0  # King doesn't count for material advantage
        }
        
        # Count material on the board
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece:
                    value = piece_values.get(piece.piece_type, 0)
                    if piece.color == 'w':
                        white_material += value
                    else:
                        black_material += value
        
        # Calculate material advantage
        if self.player_color == "white":
            material_advantage = white_material - black_material
        else:
            material_advantage = black_material - white_material
        
        # Adjust IQ based on material advantage
        material_adjustment = material_advantage * 2
        
        # Count captures by player
        player_captures = 0
        opponent_captures = 0
        
        for i, move in enumerate(self.move_history):
            is_player_move = (i % 2 == 0 and self.player_color == "white") or (i % 2 == 1 and self.player_color == "black")
            
            if move.piece_captured:
                if is_player_move:
                    player_captures += piece_values.get(move.piece_captured.piece_type, 0)
                else:
                    opponent_captures += piece_values.get(move.piece_captured.piece_type, 0)
        
        # Calculate capture advantage
        capture_advantage = player_captures - opponent_captures
        capture_adjustment = capture_advantage * 1
        
        # Calculate provisional IQ
        provisional_iq = previous_iq + material_adjustment + capture_adjustment
        
        # Adjust based on current game state
        if result == "provisional_win":
            provisional_iq += 5
        elif result == "provisional_loss":
            provisional_iq -= 3
        
        # Ensure IQ is within the specified range (70-150)
        provisional_iq = max(min(provisional_iq, 150), 70)
        
        return int(provisional_iq)
