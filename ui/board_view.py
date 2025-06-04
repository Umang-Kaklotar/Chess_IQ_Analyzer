"""
Board View Module

Handles the rendering of the chess board, pieces, and board-related UI elements.
"""

import os
import pygame
from typing import Tuple, List, Dict, Optional

class BoardView:
    """
    Handles rendering of the chess board and pieces.
    """
    
    # Colors
    LIGHT_SQUARE = (240, 217, 181)  # Light brown
    DARK_SQUARE = (181, 136, 99)    # Dark brown
    HIGHLIGHT_COLOR = (124, 252, 0, 150)  # Semi-transparent light green
    MOVE_HIGHLIGHT = (255, 255, 0, 128)   # Semi-transparent yellow
    LAST_MOVE = (255, 165, 0, 180)        # Semi-transparent orange
    CHECK_HIGHLIGHT = (255, 0, 0, 180)    # Semi-transparent red
    NOTATION_LIGHT = (100, 100, 100)      # Dark gray for notation on light squares
    NOTATION_DARK = (200, 200, 200)       # Light gray for notation on dark squares
    
    def __init__(self, board_size: int, offset_x: int, offset_y: int):
        """
        Initialize the board view.
        
        Args:
            board_size: Size of the board in pixels
            offset_x: X offset from the left edge of the screen
            offset_y: Y offset from the top edge of the screen
        """
        self.board_size = board_size
        self.square_size = board_size // 8
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.flipped = False
        
        # Load piece images
        self.piece_images = self._load_piece_images()
        
        # Create transparent surfaces for highlights
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.highlight_surface.fill(self.HIGHLIGHT_COLOR)
        
        self.move_highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.move_highlight_surface.fill(self.MOVE_HIGHLIGHT)
        
        self.last_move_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.last_move_surface.fill(self.LAST_MOVE)
        
        self.check_highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.check_highlight_surface.fill(self.CHECK_HIGHLIGHT)
        
        # Font for board notation
        self.notation_font = pygame.font.Font(None, max(14, self.square_size // 5))
    
    def _load_piece_images(self) -> Dict[str, pygame.Surface]:
        """
        Load chess piece images.
        
        Returns:
            Dictionary mapping piece codes to images
        """
        pieces = {}
        piece_types = ['P', 'N', 'B', 'R', 'Q', 'K']
        colors = ['w', 'b']
        
        # Create a directory for piece images if it doesn't exist
        os.makedirs(os.path.join("assets", "pieces"), exist_ok=True)
        
        # Try to load piece images
        for color in colors:
            for piece_type in piece_types:
                piece_code = color + piece_type
                image_path = os.path.join("assets", "pieces", f"{piece_code}.png")
                
                # Check if the image file exists
                if os.path.exists(image_path):
                    try:
                        # Load and scale the image
                        image = pygame.image.load(image_path)
                        pieces[piece_code] = pygame.transform.scale(
                            image, (self.square_size, self.square_size)
                        )
                    except pygame.error:
                        # If loading fails, create a placeholder
                        pieces[piece_code] = self._create_placeholder_piece(color, piece_type)
                else:
                    # Create a placeholder if the image doesn't exist
                    pieces[piece_code] = self._create_placeholder_piece(color, piece_type)
                    
                    # Also create the image file for future use
                    self._create_piece_image(color, piece_type, image_path)
        
        return pieces
        
    def _create_piece_image(self, color: str, piece_type: str, image_path: str) -> None:
        """
        Create a piece image file.
        
        Args:
            color: Piece color ('w' or 'b')
            piece_type: Piece type ('P', 'N', 'B', 'R', 'Q', 'K')
            image_path: Path to save the image
        """
        # Create a surface for the piece
        surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        
        # Set colors
        bg_color = (200, 200, 200) if color == 'w' else (50, 50, 50)
        text_color = (50, 50, 50) if color == 'w' else (200, 200, 200)
        
        # Draw a circle for the piece
        radius = self.square_size // 2 - 4
        pygame.draw.circle(
            surface,
            bg_color,
            (self.square_size // 2, self.square_size // 2),
            radius
        )
        
        # Add piece type text
        font = pygame.font.Font(None, self.square_size // 2)
        text = font.render(piece_type, True, text_color)
        text_rect = text.get_rect(center=(self.square_size // 2, self.square_size // 2))
        surface.blit(text, text_rect)
        
        # Save the image
        try:
            pygame.image.save(surface, image_path)
        except:
            pass  # Ignore errors if we can't save the image
    
    def _create_placeholder_piece(self, color: str, piece_type: str) -> pygame.Surface:
        """
        Create a placeholder piece image.
        
        Args:
            color: Piece color ('w' or 'b')
            piece_type: Piece type ('P', 'N', 'B', 'R', 'Q', 'K')
            
        Returns:
            Placeholder image surface
        """
        # Create a surface for the piece
        surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        
        # Set colors
        bg_color = (200, 200, 200) if color == 'w' else (50, 50, 50)
        text_color = (50, 50, 50) if color == 'w' else (200, 200, 200)
        
        # Draw a circle for the piece
        radius = self.square_size // 2 - 4
        pygame.draw.circle(
            surface,
            bg_color,
            (self.square_size // 2, self.square_size // 2),
            radius
        )
        
        # Add piece type text
        font = pygame.font.Font(None, self.square_size // 2)
        text = font.render(piece_type, True, text_color)
        text_rect = text.get_rect(center=(self.square_size // 2, self.square_size // 2))
        surface.blit(text, text_rect)
        
        return surface
    
    def flip_board(self) -> None:
        """Toggle board orientation (flipped or normal)."""
        self.flipped = not self.flipped
    
    def is_within_board(self, pos: Tuple[int, int]) -> bool:
        """
        Check if a screen position is within the board.
        
        Args:
            pos: Screen position (x, y)
            
        Returns:
            True if position is within the board, False otherwise
        """
        x, y = pos
        return (self.offset_x <= x < self.offset_x + self.board_size and
                self.offset_y <= y < self.offset_y + self.board_size)
    
    def get_board_position(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert screen position to board position.
        
        Args:
            pos: Screen position (x, y)
            
        Returns:
            Board position (row, col)
        """
        x, y = pos
        col = (x - self.offset_x) // self.square_size
        row = (y - self.offset_y) // self.square_size
        
        if self.flipped:
            row = 7 - row
            col = 7 - col
        
        return (row, col)
    
    def get_screen_position(self, board_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert board position to screen position.
        
        Args:
            board_pos: Board position (row, col)
            
        Returns:
            Screen position (x, y)
        """
        row, col = board_pos
        
        if self.flipped:
            row = 7 - row
            col = 7 - col
        
        x = self.offset_x + col * self.square_size
        y = self.offset_y + row * self.square_size
        
        return (x, y)
    
    def draw(self, screen: pygame.Surface, board) -> None:
        """
        Draw the chess board and pieces.
        
        Args:
            screen: Pygame surface to draw on
            board: Chess board object containing piece positions
        """
        # Draw board squares
        self._draw_board(screen)
        
        # Draw board notation (ranks and files)
        self._draw_notation(screen)
        
        # Draw pieces
        self._draw_pieces(screen, board)
        
    def _draw_board(self, screen: pygame.Surface) -> None:
        """
        Draw the chess board squares.
        
        Args:
            screen: Pygame surface to draw on
        """
        for row in range(8):
            for col in range(8):
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                
                # Calculate position
                x = self.offset_x + col * self.square_size
                y = self.offset_y + row * self.square_size
                
                # Draw square
                pygame.draw.rect(
                    screen,
                    color,
                    (x, y, self.square_size, self.square_size)
                )
    
    def _draw_notation(self, screen: pygame.Surface) -> None:
        """
        Draw board notation (ranks and files).
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw file notation (a-h)
        for col in range(8):
            # Determine actual file based on board orientation
            file_idx = col if not self.flipped else 7 - col
            file_char = chr(97 + file_idx)  # 'a' is ASCII 97
            
            # Determine text color based on square color
            is_light_square = col % 2 == 0
            color = self.NOTATION_DARK if is_light_square else self.NOTATION_LIGHT
            
            # Draw at bottom of board
            x = self.offset_x + col * self.square_size + self.square_size - 12
            y = self.offset_y + self.board_size - 12
            
            text = self.notation_font.render(file_char, True, color)
            screen.blit(text, (x, y))
        
        # Draw rank notation (1-8)
        for row in range(8):
            # Determine actual rank based on board orientation
            rank_idx = row if not self.flipped else 7 - row
            rank_num = str(8 - rank_idx)  # Ranks go from 8 to 1
            
            # Determine text color based on square color
            is_light_square = row % 2 == 0
            color = self.NOTATION_DARK if is_light_square else self.NOTATION_LIGHT
            
            # Draw at left of board
            x = self.offset_x + 4
            y = self.offset_y + row * self.square_size + 4
            
            text = self.notation_font.render(rank_num, True, color)
            screen.blit(text, (x, y))
    
    def _draw_pieces(self, screen: pygame.Surface, board) -> None:
        """
        Draw chess pieces on the board.
        
        Args:
            screen: Pygame surface to draw on
            board: Chess board object containing piece positions
        """
        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at(row, col)
                if piece:
                    # Create piece code (e.g., 'wP' for white pawn)
                    piece_code = ('w' if piece.color == 'w' else 'b') + piece.piece_type
                    
                    # Skip if image not found
                    if piece_code not in self.piece_images:
                        continue
                    
                    # Get screen position
                    screen_pos = self.get_screen_position((row, col))
                    
                    # Draw piece
                    screen.blit(self.piece_images[piece_code], screen_pos)
    
    def draw_highlight(self, screen: pygame.Surface, pos: Tuple[int, int], color: Tuple) -> None:
        """
        Draw a highlight on a board square.
        
        Args:
            screen: Pygame surface to draw on
            pos: Board position (row, col)
            color: Highlight color
        """
        # Get screen position
        screen_pos = self.get_screen_position(pos)
        
        # Choose the appropriate highlight surface
        if color == self.HIGHLIGHT_COLOR:
            surface = self.highlight_surface
        elif color == self.MOVE_HIGHLIGHT:
            surface = self.move_highlight_surface
        elif color == self.LAST_MOVE:
            surface = self.last_move_surface
        elif color == self.CHECK_HIGHLIGHT:
            surface = self.check_highlight_surface
        else:
            # Create a custom highlight surface
            surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            surface.fill(color)
        
        # Draw highlight
        screen.blit(surface, screen_pos)
    
    def draw_move_indicator(self, screen: pygame.Surface, pos: Tuple[int, int]) -> None:
        """
        Draw a move indicator on a board square.
        
        Args:
            screen: Pygame surface to draw on
            pos: Board position (row, col)
        """
        # Get screen position
        x, y = self.get_screen_position(pos)
        
        # Draw a circle in the center of the square
        center_x = x + self.square_size // 2
        center_y = y + self.square_size // 2
        radius = self.square_size // 6
        
        pygame.draw.circle(
            screen,
            (0, 0, 0, 128),  # Semi-transparent black
            (center_x, center_y),
            radius
        )
    
    def draw_capture_indicator(self, screen: pygame.Surface, pos: Tuple[int, int]) -> None:
        """
        Draw a capture indicator on a board square.
        
        Args:
            screen: Pygame surface to draw on
            pos: Board position (row, col)
        """
        # Get screen position
        x, y = self.get_screen_position(pos)
        
        # Draw a circle around the square
        rect = pygame.Rect(x, y, self.square_size, self.square_size)
        pygame.draw.rect(
            screen,
            (255, 0, 0, 128),  # Semi-transparent red
            rect,
            width=3
        )
    
    def resize(self, board_size: int, offset_x: int, offset_y: int) -> None:
        """
        Resize the board view.
        
        Args:
            board_size: New board size in pixels
            offset_x: New X offset
            offset_y: New Y offset
        """
        self.board_size = board_size
        self.square_size = board_size // 8
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # Reload piece images at new size
        self.piece_images = self._load_piece_images()
        
        # Recreate highlight surfaces
        self.highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.highlight_surface.fill(self.HIGHLIGHT_COLOR)
        
        self.move_highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.move_highlight_surface.fill(self.MOVE_HIGHLIGHT)
        
        self.last_move_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.last_move_surface.fill(self.LAST_MOVE)
        
        self.check_highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        self.check_highlight_surface.fill(self.CHECK_HIGHLIGHT)
        
        # Update font size
        self.notation_font = pygame.font.Font(None, max(14, self.square_size // 5))
