"""
Stats View Module

Displays post-game stats such as accuracy, IQ graph, mistakes, and win/loss history
using Pygame overlay.
"""

import os
import pygame
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

from ui.components import Button, Label
from iq.progress_tracker import ProgressTracker
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class StatsView:
    """
    Displays player statistics and performance metrics in a Pygame overlay.
    Shows IQ trends, accuracy, mistakes, and win/loss history.
    """

    # Colors
    BG_COLOR = (30, 30, 30, 220)  # Semi-transparent dark gray
    TEXT_COLOR = (255, 255, 255)
    ACCENT_COLOR = (0, 120, 215)
    GRAPH_COLORS = [
        (0, 200, 0),    # Green for IQ
        (255, 165, 0),  # Orange for accuracy
        (255, 0, 0),    # Red for mistakes
        (0, 191, 255)   # Blue for win rate
    ]

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the stats view.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Create semi-transparent overlay surface
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 48)
        self.header_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        
        # Initialize UI components
        self.init_ui_components()
        
        # Stats data
        self.stats_data = {}
        self.current_tab = "overview"  # Default tab
        
        # Graph surfaces
        self.graph_surfaces = {}
        
    def init_ui_components(self):
        """Initialize UI components like buttons and labels."""
        # Tab buttons at the top
        btn_width = 150
        btn_height = 40
        btn_y = 50
        btn_spacing = 10
        
        self.buttons = {
            "overview": Button(
                self.width // 2 - btn_width * 2 - btn_spacing * 1.5, 
                btn_y, 
                btn_width, 
                btn_height,
                "Overview", 
                lambda: self.set_tab("overview")
            ),
            "iq_trend": Button(
                self.width // 2 - btn_width // 2 - btn_spacing // 2, 
                btn_y, 
                btn_width, 
                btn_height,
                "IQ Trend", 
                lambda: self.set_tab("iq_trend")
            ),
            "accuracy": Button(
                self.width // 2 + btn_width // 2 + btn_spacing // 2, 
                btn_y, 
                btn_width, 
                btn_height,
                "Accuracy", 
                lambda: self.set_tab("accuracy")
            ),
            "mistakes": Button(
                self.width // 2 + btn_width * 1.5 + btn_spacing * 1.5, 
                btn_y, 
                btn_width, 
                btn_height,
                "Mistakes", 
                lambda: self.set_tab("mistakes")
            ),
            "close": Button(
                self.width - 100, 
                self.height - 60, 
                80, 
                40,
                "Close", 
                self.close
            )
        }
        
        # Labels
        self.labels = {
            "title": Label(
                self.width // 2, 
                20, 
                "Chess Performance Statistics", 
                self.title_font,
                self.TEXT_COLOR,
                "center"
            )
        }
        
    def set_tab(self, tab_name: str) -> None:
        """
        Set the current tab to display.
        
        Args:
            tab_name: Name of the tab to display
        """
        self.current_tab = tab_name
        logger.info(f"Switched to {tab_name} tab")
        
    def close(self) -> None:
        """Close the stats view."""
        # This will be handled by the parent UI
        pass
        
    def update_data(self, progress_tracker: ProgressTracker) -> None:
        """
        Update the stats data from the progress tracker.
        
        Args:
            progress_tracker: ProgressTracker instance with player data
        """
        # Generate a progress report
        self.stats_data = progress_tracker.generate_progress_report()
        
        # Get trend data for graphs
        self.iq_scores, self.iq_dates = progress_tracker.get_iq_trend(limit=20)
        self.accuracy_values, self.accuracy_dates = progress_tracker.get_accuracy_trend(limit=20)
        self.mistake_distribution = progress_tracker.get_mistake_distribution()
        
        # Pre-render graphs
        self._render_graphs()
        
        logger.info("Stats data updated")
        
    def _render_graphs(self) -> None:
        """Pre-render graph surfaces for better performance."""
        # IQ trend graph
        if self.iq_scores:
            self.graph_surfaces["iq"] = self._create_line_graph(
                "Chess IQ Trend", 
                self.iq_scores, 
                self.iq_dates, 
                self.GRAPH_COLORS[0],
                600, 300
            )
        
        # Accuracy trend graph
        if self.accuracy_values:
            self.graph_surfaces["accuracy"] = self._create_line_graph(
                "Move Accuracy Trend (%)", 
                self.accuracy_values, 
                self.accuracy_dates, 
                self.GRAPH_COLORS[1],
                600, 300,
                y_min=0,
                y_max=100
            )
        
        # Mistake distribution graph
        if self.mistake_distribution:
            mistakes = self.mistake_distribution
            categories = ["Blunders", "Mistakes", "Inaccuracies"]
            values = [mistakes["blunders"], mistakes["mistakes"], mistakes["inaccuracies"]]
            self.graph_surfaces["mistakes"] = self._create_bar_graph(
                "Mistake Distribution", 
                categories, 
                values, 
                self.GRAPH_COLORS[2],
                600, 300
            )
        
        # Win/loss pie chart
        if "games" in self.stats_data:
            games = self.stats_data["games"]
            if games["total"] > 0:
                labels = ["Wins", "Losses", "Draws"]
                values = [games["wins"], games["losses"], games["draws"]]
                self.graph_surfaces["games"] = self._create_pie_chart(
                    "Game Results", 
                    labels, 
                    values, 
                    [
                        (0, 200, 0),    # Green for wins
                        (255, 0, 0),    # Red for losses
                        (0, 191, 255)   # Blue for draws
                    ],
                    300, 300
                )
        
    def _create_line_graph(self, title: str, values: List[float], labels: List[str], 
                          color: Tuple[int, int, int], width: int, height: int,
                          y_min: Optional[float] = None, y_max: Optional[float] = None) -> pygame.Surface:
        """
        Create a line graph surface.
        
        Args:
            title: Graph title
            values: Y values for the graph
            labels: X labels for the graph
            color: Line color
            width: Graph width
            height: Graph height
            y_min: Minimum Y value (optional)
            y_max: Maximum Y value (optional)
            
        Returns:
            Pygame surface with the rendered graph
        """
        if not values:
            return pygame.Surface((width, height), pygame.SRCALPHA)
            
        # Create surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((50, 50, 50))
        
        # Draw title
        title_font = pygame.font.Font(None, 32)
        title_surf = title_font.render(title, True, self.TEXT_COLOR)
        title_rect = title_surf.get_rect(midtop=(width // 2, 10))
        surface.blit(title_surf, title_rect)
        
        # Graph dimensions
        graph_margin = 50
        graph_width = width - graph_margin * 2
        graph_height = height - graph_margin * 2
        graph_rect = pygame.Rect(graph_margin, graph_margin, graph_width, graph_height)
        
        # Draw graph background
        pygame.draw.rect(surface, (30, 30, 30), graph_rect)
        pygame.draw.rect(surface, (100, 100, 100), graph_rect, 1)
        
        # Calculate value range
        if y_min is None:
            y_min = min(values) if values else 0
            # Add some padding
            y_range = max(values) - y_min if values else 1
            y_min = max(0, y_min - y_range * 0.1)
            
        if y_max is None:
            y_max = max(values) if values else 1
            # Add some padding
            y_range = y_max - y_min
            y_max = y_max + y_range * 0.1
            
        y_range = y_max - y_min
        
        # Draw horizontal grid lines and labels
        label_font = pygame.font.Font(None, 20)
        num_lines = 5
        for i in range(num_lines + 1):
            y = graph_rect.bottom - (i / num_lines) * graph_height
            # Grid line
            pygame.draw.line(surface, (70, 70, 70), (graph_rect.left, y), (graph_rect.right, y), 1)
            # Y-axis label
            value = y_min + (i / num_lines) * y_range
            label = label_font.render(f"{value:.1f}", True, self.TEXT_COLOR)
            surface.blit(label, (graph_rect.left - label.get_width() - 5, y - label.get_height() // 2))
        
        # Draw data points and lines
        if len(values) > 1:
            points = []
            for i, value in enumerate(values):
                x = graph_rect.left + (i / (len(values) - 1)) * graph_width
                y = graph_rect.bottom - ((value - y_min) / y_range) * graph_height
                points.append((x, y))
                
                # Draw point
                pygame.draw.circle(surface, color, (int(x), int(y)), 4)
            
            # Draw lines connecting points
            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 2)
        
        # Draw X-axis labels (dates)
        if labels:
            # Only show a subset of labels to avoid overcrowding
            num_labels = min(5, len(labels))
            indices = [i * (len(labels) - 1) // (num_labels - 1) for i in range(num_labels)] if num_labels > 1 else [0]
            
            for i in indices:
                if i < len(labels):
                    x = graph_rect.left + (i / (len(labels) - 1 if len(labels) > 1 else 1)) * graph_width
                    label = label_font.render(labels[i], True, self.TEXT_COLOR)
                    label_rect = label.get_rect(midtop=(x, graph_rect.bottom + 5))
                    surface.blit(label, label_rect)
        
        return surface
        
    def _create_bar_graph(self, title: str, categories: List[str], values: List[float], 
                         color: Tuple[int, int, int], width: int, height: int) -> pygame.Surface:
        """
        Create a bar graph surface.
        
        Args:
            title: Graph title
            categories: Category labels
            values: Values for each category
            color: Bar color
            width: Graph width
            height: Graph height
            
        Returns:
            Pygame surface with the rendered graph
        """
        if not values or not categories:
            return pygame.Surface((width, height), pygame.SRCALPHA)
            
        # Create surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((50, 50, 50))
        
        # Draw title
        title_font = pygame.font.Font(None, 32)
        title_surf = title_font.render(title, True, self.TEXT_COLOR)
        title_rect = title_surf.get_rect(midtop=(width // 2, 10))
        surface.blit(title_surf, title_rect)
        
        # Graph dimensions
        graph_margin = 50
        graph_width = width - graph_margin * 2
        graph_height = height - graph_margin * 2
        graph_rect = pygame.Rect(graph_margin, graph_margin, graph_width, graph_height)
        
        # Draw graph background
        pygame.draw.rect(surface, (30, 30, 30), graph_rect)
        pygame.draw.rect(surface, (100, 100, 100), graph_rect, 1)
        
        # Calculate maximum value for scaling
        max_value = max(values) if values else 1
        
        # Draw bars
        bar_width = graph_width / len(categories) * 0.8
        bar_spacing = graph_width / len(categories) * 0.2
        
        label_font = pygame.font.Font(None, 20)
        value_font = pygame.font.Font(None, 24)
        
        for i, (category, value) in enumerate(zip(categories, values)):
            # Calculate bar position and size
            bar_height = (value / max_value) * graph_height if max_value > 0 else 0
            bar_x = graph_rect.left + (i / len(categories)) * graph_width + bar_spacing / 2
            bar_y = graph_rect.bottom - bar_height
            bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            
            # Draw bar
            pygame.draw.rect(surface, color, bar_rect)
            pygame.draw.rect(surface, (200, 200, 200), bar_rect, 1)
            
            # Draw category label
            label = label_font.render(category, True, self.TEXT_COLOR)
            label_rect = label.get_rect(midtop=(bar_x + bar_width / 2, graph_rect.bottom + 5))
            surface.blit(label, label_rect)
            
            # Draw value on top of bar
            value_label = value_font.render(str(value), True, self.TEXT_COLOR)
            value_rect = value_label.get_rect(midbottom=(bar_x + bar_width / 2, bar_y - 5))
            surface.blit(value_label, value_rect)
        
        return surface
        
    def _create_pie_chart(self, title: str, labels: List[str], values: List[float], 
                         colors: List[Tuple[int, int, int]], width: int, height: int) -> pygame.Surface:
        """
        Create a pie chart surface.
        
        Args:
            title: Chart title
            labels: Slice labels
            values: Values for each slice
            colors: Colors for each slice
            width: Chart width
            height: Chart height
            
        Returns:
            Pygame surface with the rendered pie chart
        """
        if not values or not labels:
            return pygame.Surface((width, height), pygame.SRCALPHA)
            
        # Create surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((50, 50, 50))
        
        # Draw title
        title_font = pygame.font.Font(None, 32)
        title_surf = title_font.render(title, True, self.TEXT_COLOR)
        title_rect = title_surf.get_rect(midtop=(width // 2, 10))
        surface.blit(title_surf, title_rect)
        
        # Calculate total for percentages
        total = sum(values) if values else 0
        if total == 0:
            return surface
            
        # Pie chart dimensions
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 3
        
        # Draw pie slices
        start_angle = 0
        for i, (label, value, color) in enumerate(zip(labels, values, colors)):
            # Calculate slice angle
            slice_angle = 360 * (value / total)
            end_angle = start_angle + slice_angle
            
            # Draw slice
            pygame.draw.arc(surface, color, 
                           (center_x - radius, center_y - radius, radius * 2, radius * 2),
                           math.radians(start_angle), math.radians(end_angle), radius)
            
            # Calculate position for label
            mid_angle = math.radians(start_angle + slice_angle / 2)
            label_x = center_x + int(radius * 1.3 * math.cos(mid_angle))
            label_y = center_y - int(radius * 1.3 * math.sin(mid_angle))
            
            # Draw label and percentage
            label_font = pygame.font.Font(None, 24)
            percent = value / total * 100
            label_text = f"{label}: {percent:.1f}%"
            label_surf = label_font.render(label_text, True, color)
            label_rect = label_surf.get_rect(center=(label_x, label_y))
            surface.blit(label_surf, label_rect)
            
            # Update start angle for next slice
            start_angle = end_angle
        
        return surface
        
    def draw_overview_tab(self) -> None:
        """Draw the overview tab with summary statistics."""
        # Title
        header = self.header_font.render("Performance Overview", True, self.TEXT_COLOR)
        self.overlay.blit(header, (self.width // 2 - header.get_width() // 2, 120))
        
        # Draw stats in a grid layout
        stats_y = 180
        left_col_x = self.width // 4
        right_col_x = self.width * 3 // 4
        
        # Left column stats
        self._draw_stat("Current Chess IQ", f"{self.stats_data.get('current_iq', 0):.1f}", left_col_x, stats_y)
        self._draw_stat("IQ Change", f"{self.stats_data.get('iq_change', 0):+.1f}", left_col_x, stats_y + 60)
        self._draw_stat("Games Played", str(self.stats_data.get('games_played', 0)), left_col_x, stats_y + 120)
        self._draw_stat("Win Percentage", f"{self.stats_data.get('win_percentage', 0):.1f}%", left_col_x, stats_y + 180)
        
        # Right column stats
        self._draw_stat("Average Accuracy", f"{self.stats_data.get('average_accuracy', 0):.1f}%", right_col_x, stats_y)
        self._draw_stat("Accuracy Change", f"{self.stats_data.get('accuracy_change', 0):+.1f}%", right_col_x, stats_y + 60)
        self._draw_stat("Total Mistakes", str(self.stats_data.get('total_mistakes', 0)), right_col_x, stats_y + 120)
        self._draw_stat("Win/Loss Ratio", f"{self.stats_data.get('win_loss_ratio', 0):.2f}", right_col_x, stats_y + 180)
        
        # Strengths and improvement areas
        strengths_y = stats_y + 260
        self._draw_list("Strengths", self.stats_data.get('strengths', []), self.width // 4, strengths_y)
        self._draw_list("Areas to Improve", self.stats_data.get('improvement_areas', []), self.width * 3 // 4, strengths_y)
        
    def _draw_stat(self, label: str, value: str, x: int, y: int) -> None:
        """
        Draw a statistic with label and value.
        
        Args:
            label: Stat label
            value: Stat value
            x: Center x position
            y: Top y position
        """
        label_surf = self.text_font.render(label, True, self.TEXT_COLOR)
        value_surf = self.header_font.render(value, True, self.ACCENT_COLOR)
        
        label_rect = label_surf.get_rect(midtop=(x, y))
        value_rect = value_surf.get_rect(midtop=(x, y + 30))
        
        self.overlay.blit(label_surf, label_rect)
        self.overlay.blit(value_surf, value_rect)
        
    def _draw_list(self, title: str, items: List[str], x: int, y: int) -> None:
        """
        Draw a list of items with a title.
        
        Args:
            title: List title
            items: List items
            x: Center x position
            y: Top y position
        """
        title_surf = self.header_font.render(title, True, self.TEXT_COLOR)
        title_rect = title_surf.get_rect(midtop=(x, y))
        self.overlay.blit(title_surf, title_rect)
        
        if not items:
            none_surf = self.text_font.render("None", True, self.TEXT_COLOR)
            none_rect = none_surf.get_rect(midtop=(x, y + 40))
            self.overlay.blit(none_surf, none_rect)
            return
            
        for i, item in enumerate(items[:5]):  # Limit to 5 items
            item_surf = self.text_font.render(f"• {item}", True, self.TEXT_COLOR)
            item_rect = item_surf.get_rect(midtop=(x, y + 40 + i * 25))
            self.overlay.blit(item_surf, item_rect)
        
    def draw_graph_tab(self, graph_key: str, title: str) -> None:
        """
        Draw a tab with a graph.
        
        Args:
            graph_key: Key for the graph surface
            title: Tab title
        """
        # Title
        header = self.header_font.render(title, True, self.TEXT_COLOR)
        self.overlay.blit(header, (self.width // 2 - header.get_width() // 2, 120))
        
        # Draw graph if available
        if graph_key in self.graph_surfaces:
            graph = self.graph_surfaces[graph_key]
            graph_rect = graph.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.overlay.blit(graph, graph_rect)
        else:
            # No data message
            no_data = self.header_font.render("No data available", True, self.TEXT_COLOR)
            self.overlay.blit(no_data, (self.width // 2 - no_data.get_width() // 2, self.height // 2))
        
    def handle_click(self, pos: Tuple[int, int]) -> None:
        """
        Handle mouse clicks.
        
        Args:
            pos: Mouse position (x, y)
        """
        # Check if any button was clicked
        for button in self.buttons.values():
            if button.is_clicked(pos):
                button.on_click()
                break
        
    def draw(self) -> None:
        """Draw the stats view on the screen."""
        # Clear overlay
        self.overlay.fill((0, 0, 0, 0))
        
        # Draw semi-transparent background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.BG_COLOR)
        self.overlay.blit(bg_surface, (0, 0))
        
        # Draw title and buttons
        self.labels["title"].draw(self.overlay)
        for button in self.buttons.values():
            button.draw(self.overlay)
        
        # Draw current tab content
        if self.current_tab == "overview":
            self.draw_overview_tab()
        elif self.current_tab == "iq_trend":
            self.draw_graph_tab("iq", "Chess IQ Trend")
        elif self.current_tab == "accuracy":
            self.draw_graph_tab("accuracy", "Move Accuracy Trend")
        elif self.current_tab == "mistakes":
            self.draw_graph_tab("mistakes", "Mistake Distribution")
        
        # Draw overlay on screen
        self.screen.blit(self.overlay, (0, 0))


# Add missing imports
import math
