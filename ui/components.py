"""
UI Components Module

Provides reusable UI components like buttons, labels, timers, and message boxes.
"""

import time
import pygame
from typing import Tuple, List, Dict, Optional, Callable, Any

class Button:
    """
    Interactive button component.
    """
    
    # Colors
    NORMAL_BG = (70, 70, 70)
    HOVER_BG = (100, 100, 100)
    ACTIVE_BG = (50, 120, 200)
    TEXT_COLOR = (255, 255, 255)
    BORDER_COLOR = (40, 40, 40)
    DISABLED_BG = (50, 50, 50)
    DISABLED_TEXT = (150, 150, 150)
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, on_click: Callable = None, 
                 font_size: int = 24, enabled: bool = True):
        """
        Initialize a button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            on_click: Function to call when clicked
            font_size: Font size for button text
            enabled: Whether the button is enabled
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.on_click_handler = on_click
        self.font = pygame.font.Font(None, font_size)
        self.enabled = enabled
        self.hovered = False
        self.active = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button.
        
        Args:
            surface: Surface to draw on
        """
        # Determine button color
        if not self.enabled:
            color = self.DISABLED_BG
        elif self.active:
            color = self.ACTIVE_BG
        elif self.hovered:
            color = self.HOVER_BG
        else:
            color = self.NORMAL_BG
        
        # Draw button background
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 2)
        
        # Draw text
        text_color = self.DISABLED_TEXT if not self.enabled else self.TEXT_COLOR
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update button state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
        """
        if self.enabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Check if the button is clicked.
        
        Args:
            mouse_pos: Mouse position
            
        Returns:
            True if button is clicked, False otherwise
        """
        if self.enabled and self.rect.collidepoint(mouse_pos):
            return True
        return False
    
    def on_click(self) -> None:
        """Handle button click."""
        if self.enabled and self.on_click_handler:
            self.on_click_handler()
    
    def set_text(self, text: str) -> None:
        """
        Set button text.
        
        Args:
            text: New button text
        """
        self.text = text
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the button.
        
        Args:
            enabled: Whether the button should be enabled
        """
        self.enabled = enabled


class Label:
    """
    Text label component.
    """
    
    # Default colors
    DEFAULT_COLOR = (255, 255, 255)
    
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font, 
                 color: Tuple[int, int, int] = None, align: str = "left"):
        """
        Initialize a label.
        
        Args:
            x: X position
            y: Y position
            text: Label text
            font: Font to use
            color: Text color (default: white)
            align: Text alignment ("left", "center", "right")
        """
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color or self.DEFAULT_COLOR
        self.align = align
        
        # Create initial text surface
        self.text_surface = self.font.render(self.text, True, self.color)
        self.rect = self.text_surface.get_rect()
        
        # Set position based on alignment
        self._update_position()
    
    def _update_position(self) -> None:
        """Update text position based on alignment."""
        if self.align == "left":
            self.rect.topleft = (self.x, self.y)
        elif self.align == "center":
            self.rect.midtop = (self.x, self.y)
        elif self.align == "right":
            self.rect.topright = (self.x, self.y)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the label.
        
        Args:
            surface: Surface to draw on
        """
        surface.blit(self.text_surface, self.rect)
    
    def set_text(self, text: str) -> None:
        """
        Set label text.
        
        Args:
            text: New label text
        """
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.color)
        self.rect = self.text_surface.get_rect()
        self._update_position()
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        """
        Set text color.
        
        Args:
            color: New text color
        """
        self.color = color
        self.text_surface = self.font.render(self.text, True, self.color)
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set label position.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
        self._update_position()


class Timer:
    """
    Chess clock timer.
    """
    
    def __init__(self, initial_time: float):
        """
        Initialize a timer.
        
        Args:
            initial_time: Initial time in seconds
        """
        self.time_remaining = initial_time
        self.running = False
        self.start_time = 0
    
    def start(self) -> None:
        """Start the timer."""
        if not self.running:
            self.running = True
            self.start_time = time.time()
    
    def stop(self) -> None:
        """Stop the timer."""
        if self.running:
            self.time_remaining -= (time.time() - self.start_time)
            self.running = False
    
    def reset(self, new_time: float = None) -> None:
        """
        Reset the timer.
        
        Args:
            new_time: New time in seconds (optional)
        """
        self.running = False
        if new_time is not None:
            self.time_remaining = new_time
    
    def get_time(self) -> float:
        """
        Get current time remaining.
        
        Returns:
            Time remaining in seconds
        """
        if self.running:
            return max(0, self.time_remaining - (time.time() - self.start_time))
        return max(0, self.time_remaining)
    
    def get_formatted_time(self) -> str:
        """
        Get formatted time string (MM:SS).
        
        Returns:
            Formatted time string
        """
        time_seconds = self.get_time()
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def add_time(self, seconds: float) -> None:
        """
        Add time to the timer.
        
        Args:
            seconds: Seconds to add
        """
        self.time_remaining += seconds


class MessageBox:
    """
    Message box for displaying notifications.
    """
    
    # Colors
    BG_COLOR = (50, 50, 50, 220)  # Semi-transparent dark gray
    BORDER_COLOR = (200, 200, 200)
    TEXT_COLOR = (255, 255, 255)
    
    def __init__(self, x: int, y: int, width: int, height: int, font: pygame.font.Font):
        """
        Initialize a message box.
        
        Args:
            x: X position (center)
            y: Y position (center)
            width: Box width
            height: Box height
            font: Font to use
        """
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.font = font
        self.message = ""
        self.visible = False
        self.timeout = 0
        self.start_time = 0
        
        # Create background surface
        self.bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.bg_surface.fill(self.BG_COLOR)
    
    def show(self, message: str, timeout: float = 0) -> None:
        """
        Show a message.
        
        Args:
            message: Message to display
            timeout: Time to display message (0 for indefinite)
        """
        self.message = message
        self.visible = True
        self.timeout = timeout
        self.start_time = time.time() if timeout > 0 else 0
    
    def hide(self) -> None:
        """Hide the message box."""
        self.visible = False
    
    def update(self) -> None:
        """Update message box state."""
        if self.visible and self.timeout > 0:
            if time.time() - self.start_time >= self.timeout:
                self.visible = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the message box.
        
        Args:
            surface: Surface to draw on
        """
        if not self.visible:
            return
        
        # Draw background
        surface.blit(self.bg_surface, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 2)
        
        # Draw message text
        lines = self.message.split('\n')
        line_height = self.font.get_height()
        total_height = line_height * len(lines)
        start_y = self.rect.centery - total_height // 2
        
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, start_y + i * line_height))
            surface.blit(text_surface, text_rect)


class Dropdown:
    """
    Dropdown menu component.
    """
    
    # Colors
    BG_COLOR = (70, 70, 70)
    HOVER_BG = (100, 100, 100)
    TEXT_COLOR = (255, 255, 255)
    BORDER_COLOR = (40, 40, 40)
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 options: List[str], on_select: Callable = None, 
                 font_size: int = 24):
        """
        Initialize a dropdown menu.
        
        Args:
            x: X position
            y: Y position
            width: Dropdown width
            height: Dropdown height
            options: List of options
            on_select: Function to call when an option is selected
            font_size: Font size for options
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.on_select_handler = on_select
        self.font = pygame.font.Font(None, font_size)
        self.selected_index = 0
        self.expanded = False
        self.hovered_index = -1
        
        # Create option rects
        self.option_rects = []
        for i in range(len(options)):
            self.option_rects.append(
                pygame.Rect(x, y + height * (i + 1), width, height)
            )
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the dropdown.
        
        Args:
            surface: Surface to draw on
        """
        # Draw selected option
        pygame.draw.rect(surface, self.BG_COLOR, self.rect)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 2)
        
        text_surface = self.font.render(self.options[self.selected_index], True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery + 5),
            (self.rect.right - 30, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, self.TEXT_COLOR, arrow_points)
        
        # Draw options if expanded
        if self.expanded:
            for i, rect in enumerate(self.option_rects):
                color = self.HOVER_BG if i == self.hovered_index else self.BG_COLOR
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, self.BORDER_COLOR, rect, 2)
                
                text_surface = self.font.render(self.options[i], True, self.TEXT_COLOR)
                text_rect = text_surface.get_rect(center=rect.center)
                surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update dropdown state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
        """
        if self.expanded:
            self.hovered_index = -1
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_index = i
                    break
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Handle mouse click.
        
        Args:
            mouse_pos: Mouse position
            
        Returns:
            True if click was handled, False otherwise
        """
        if self.rect.collidepoint(mouse_pos):
            self.expanded = not self.expanded
            return True
        
        if self.expanded:
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    self.expanded = False
                    if self.on_select_handler:
                        self.on_select_handler(self.options[i])
                    return True
            
            # Click outside dropdown should close it
            self.expanded = False
            return True
        
        return False
    
    def get_selected(self) -> str:
        """
        Get selected option.
        
        Returns:
            Selected option text
        """
        return self.options[self.selected_index]
    
    def set_selected(self, option: str) -> None:
        """
        Set selected option.
        
        Args:
            option: Option to select
        """
        if option in self.options:
            self.selected_index = self.options.index(option)


class Slider:
    """
    Slider control component.
    """
    
    # Colors
    BG_COLOR = (70, 70, 70)
    HANDLE_COLOR = (200, 200, 200)
    ACTIVE_HANDLE_COLOR = (50, 120, 200)
    TRACK_COLOR = (100, 100, 100)
    TEXT_COLOR = (255, 255, 255)
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_value: float, max_value: float, initial_value: float = None,
                 on_change: Callable = None, label: str = ""):
        """
        Initialize a slider.
        
        Args:
            x: X position
            y: Y position
            width: Slider width
            height: Slider height
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Initial value
            on_change: Function to call when value changes
            label: Slider label
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value if initial_value is not None else min_value
        self.on_change_handler = on_change
        self.label = label
        self.font = pygame.font.Font(None, 24)
        self.active = False
        
        # Calculate handle position
        self.handle_width = max(height, 16)
        self.handle_rect = pygame.Rect(0, 0, self.handle_width, height + 4)
        self._update_handle_position()
    
    def _update_handle_position(self) -> None:
        """Update handle position based on current value."""
        value_range = self.max_value - self.min_value
        if value_range == 0:
            position = 0
        else:
            position = (self.value - self.min_value) / value_range
        
        handle_x = self.rect.x + int(position * (self.rect.width - self.handle_width))
        self.handle_rect.x = handle_x
        self.handle_rect.centery = self.rect.centery
    
    def _update_value_from_position(self, x: int) -> None:
        """
        Update value based on handle position.
        
        Args:
            x: X position
        """
        position = max(0, min(1, (x - self.rect.x) / self.rect.width))
        old_value = self.value
        self.value = self.min_value + position * (self.max_value - self.min_value)
        
        # Call on_change handler if value changed
        if self.on_change_handler and self.value != old_value:
            self.on_change_handler(self.value)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the slider.
        
        Args:
            surface: Surface to draw on
        """
        # Draw track
        track_rect = pygame.Rect(
            self.rect.x, self.rect.centery - 2,
            self.rect.width, 4
        )
        pygame.draw.rect(surface, self.TRACK_COLOR, track_rect)
        
        # Draw handle
        handle_color = self.ACTIVE_HANDLE_COLOR if self.active else self.HANDLE_COLOR
        pygame.draw.rect(surface, handle_color, self.handle_rect, 0, 3)
        
        # Draw label and value
        if self.label:
            label_surface = self.font.render(self.label, True, self.TEXT_COLOR)
            label_rect = label_surface.get_rect(bottomleft=(self.rect.x, self.rect.y - 5))
            surface.blit(label_surface, label_rect)
        
        value_text = f"{self.value:.1f}" if isinstance(self.value, float) else str(self.value)
        value_surface = self.font.render(value_text, True, self.TEXT_COLOR)
        value_rect = value_surface.get_rect(bottomright=(self.rect.right, self.rect.y - 5))
        surface.blit(value_surface, value_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.active = True
                return True
            elif self.rect.collidepoint(event.pos):
                self._update_value_from_position(event.pos[0])
                self._update_handle_position()
                self.active = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active:
                self.active = False
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.active:
            self._update_value_from_position(event.pos[0])
            self._update_handle_position()
            return True
        
        return False
    
    def set_value(self, value: float) -> None:
        """
        Set slider value.
        
        Args:
            value: New value
        """
        self.value = max(self.min_value, min(self.max_value, value))
        self._update_handle_position()
        
        if self.on_change_handler:
            self.on_change_handler(self.value)
    
    def get_value(self) -> float:
        """
        Get current value.
        
        Returns:
            Current slider value
        """
        return self.value
