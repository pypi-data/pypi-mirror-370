"""
Response Importance Rating Dialog

This module provides a star-based importance rating dialog for multi-objective optimization responses.
Users can assign 1-5 star importance ratings that are converted to numerical weights for 
acquisition function calculations.

Key Features:
- 5-star rating system for intuitive importance assessment
- Visual star display with interactive rating
- Automatic weight calculation from star ratings
- Integration with responses_config for global optimization weights
- Professional UI design following PyMBO standards

Classes:
    ResponseImportanceDialog: Main dialog for setting response importance ratings
    StarRatingWidget: Custom widget for star-based rating input

Functions:
    show_importance_dialog: Factory function for creating importance dialogs
    convert_stars_to_weights: Converts star ratings to normalized weights

Author: PyMBO Development Team
Version: 3.6.6 Enhanced
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Callable, List, Optional, Tuple
import math

# Import color constants from main GUI module
try:
    from .gui import (
        COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, 
        COLOR_ERROR, COLOR_BACKGROUND, COLOR_SURFACE
    )
except ImportError:
    # Fallback color scheme if import fails
    COLOR_PRIMARY = "#1976D2"
    COLOR_SECONDARY = "#424242"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_WARNING = "#FF9800"
    COLOR_ERROR = "#F44336"
    COLOR_BACKGROUND = "#FAFAFA"
    COLOR_SURFACE = "#FFFFFF"

logger = logging.getLogger(__name__)


class StarRatingWidget:
    """
    Custom widget for displaying and setting star-based ratings.
    
    This widget provides an interactive 5-star rating system where users can click
    to set ratings from 1-5 stars. Visual feedback shows filled and empty stars.
    """
    
    def __init__(self, parent: tk.Widget, initial_rating: int = 3, callback: Callable = None):
        """
        Initialize the star rating widget.
        
        Args:
            parent: Parent Tkinter widget
            initial_rating: Initial star rating (1-5)
            callback: Function to call when rating changes
        """
        self.parent = parent
        self.rating = max(1, min(5, initial_rating))  # Ensure rating is 1-5
        self.callback = callback
        
        # Create frame for stars
        self.frame = tk.Frame(parent, bg=COLOR_SURFACE)
        
        # Create star buttons
        self.star_buttons = []
        for i in range(5):
            btn = tk.Button(
                self.frame,
                text="★",
                font=("Arial", 16),
                width=2,
                height=1,
                relief="flat",
                bd=0,
                command=lambda star_num=i+1: self._set_rating(star_num)
            )
            btn.pack(side=tk.LEFT, padx=1)
            self.star_buttons.append(btn)
        
        # Update visual display
        self._update_stars()
    
    def _set_rating(self, rating: int) -> None:
        """Set the rating and update visual display."""
        self.rating = rating
        self._update_stars()
        if self.callback:
            self.callback(rating)
    
    def _update_stars(self) -> None:
        """Update the visual appearance of stars based on current rating."""
        for i, btn in enumerate(self.star_buttons):
            if i < self.rating:
                # Filled star
                btn.config(
                    fg=COLOR_WARNING,  # Gold/orange color for filled stars
                    bg=COLOR_SURFACE,
                    activeforeground=COLOR_WARNING,
                    activebackground=COLOR_BACKGROUND
                )
            else:
                # Empty star
                btn.config(
                    fg=COLOR_SECONDARY,  # Gray color for empty stars
                    bg=COLOR_SURFACE,
                    activeforeground=COLOR_SECONDARY,
                    activebackground=COLOR_BACKGROUND
                )
    
    def get_rating(self) -> int:
        """Get the current star rating."""
        return self.rating
    
    def set_rating(self, rating: int) -> None:
        """Set the rating programmatically."""
        self._set_rating(rating)
    
    def pack(self, **kwargs) -> None:
        """Pack the star widget frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs) -> None:
        """Grid the star widget frame."""
        self.frame.grid(**kwargs)


class ResponseImportanceDialog:
    """
    Dialog for setting importance ratings for optimization responses.
    
    This dialog allows users to assign 1-5 star importance ratings to each response
    variable in a multi-objective optimization problem. The ratings are converted
    to numerical weights that influence the acquisition function.
    """
    
    def __init__(self, parent: tk.Widget, responses_config: Dict[str, Any], 
                 callback: Callable = None):
        """
        Initialize the response importance dialog.
        
        Args:
            parent: Parent Tkinter widget
            responses_config: Dictionary of response configurations
            callback: Function to call when ratings are confirmed
        """
        self.parent = parent
        self.responses_config = responses_config
        self.callback = callback
        
        # Store response names and their current importance ratings
        self.response_names = list(responses_config.keys())
        self.importance_ratings = {}
        
        # Initialize ratings - check for existing importance, default to 3 stars
        for name in self.response_names:
            existing_importance = responses_config[name].get('importance', 3)
            self.importance_ratings[name] = max(1, min(5, existing_importance))
        
        # Dialog window
        self.dialog = None
        self.star_widgets = {}
        self.result = None
        
        # Create and show dialog
        self._create_dialog()
        
        logger.info(f"Response importance dialog initialized for {len(self.response_names)} responses")
    
    def _create_dialog(self) -> None:
        """Create the main dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Set Response Importance")
        self.dialog.geometry("500x600")
        self.dialog.resizable(True, True)
        
        # Set minimum size
        self.dialog.minsize(450, 500)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create dialog content
        self._create_header()
        self._create_ratings_section()
        self._create_preview_section()
        self._create_buttons()
        
        # Handle window closing
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Focus on dialog
        self.dialog.focus_set()
    
    def _center_dialog(self) -> None:
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate centered position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_header(self) -> None:
        """Create the dialog header with title and instructions."""
        header_frame = tk.Frame(self.dialog, bg=COLOR_PRIMARY, height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Response Importance Ratings",
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            font=("Arial", 14, "bold")
        )
        title_label.pack(expand=True)
        
        # Instructions
        instructions_frame = tk.Frame(self.dialog, bg=COLOR_SURFACE)
        instructions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        instructions_text = (
            "Set the importance of each response for optimization:\n"
            "★☆☆☆☆ = Low importance    ★★★☆☆ = Medium importance    ★★★★★ = Very high importance\n"
            "These ratings will affect how the algorithm prioritizes different objectives."
        )
        
        instructions_label = tk.Label(
            instructions_frame,
            text=instructions_text,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            justify=tk.LEFT,
            wraplength=450
        )
        instructions_label.pack(anchor="w")
    
    def _create_ratings_section(self) -> None:
        """Create the section with star ratings for each response."""
        # Main frame for ratings with fixed height to leave space for preview and buttons
        main_frame = tk.Frame(self.dialog, bg=COLOR_SURFACE)
        main_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Set a reasonable height for the ratings area
        ratings_height = min(250, len(self.response_names) * 70 + 50)  # Dynamic but capped
        main_frame.config(height=ratings_height)
        main_frame.pack_propagate(False)  # Maintain fixed height
        
        # Create scrollable frame for responses
        canvas = tk.Canvas(main_frame, bg=COLOR_SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_SURFACE)
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create rating rows for each response
        for i, response_name in enumerate(self.response_names):
            self._create_rating_row(scrollable_frame, response_name, i)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
    
    def _create_rating_row(self, parent: tk.Widget, response_name: str, row_index: int) -> None:
        """Create a rating row for a single response."""
        # Row frame
        row_frame = tk.Frame(
            parent, 
            bg=COLOR_BACKGROUND if row_index % 2 == 0 else COLOR_SURFACE,
            relief="flat",
            bd=1
        )
        row_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Response info frame
        info_frame = tk.Frame(row_frame, bg=row_frame['bg'])
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Response name and goal
        response_config = self.responses_config[response_name]
        goal = response_config.get('goal', 'Unknown')
        
        name_label = tk.Label(
            info_frame,
            text=f"{response_name}",
            bg=row_frame['bg'],
            fg=COLOR_SECONDARY,
            font=("Arial", 11, "bold")
        )
        name_label.pack(side=tk.LEFT)
        
        goal_label = tk.Label(
            info_frame,
            text=f"({goal})",
            bg=row_frame['bg'],
            fg=COLOR_WARNING,
            font=("Arial", 9, "italic")
        )
        goal_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Star rating widget
        def on_rating_change(rating):
            self.importance_ratings[response_name] = rating
            self._update_preview()
        
        star_widget = StarRatingWidget(
            info_frame,
            initial_rating=self.importance_ratings[response_name],
            callback=on_rating_change
        )
        star_widget.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Store reference to star widget
        self.star_widgets[response_name] = star_widget
    
    def _create_preview_section(self) -> None:
        """Create the section showing calculated weights preview."""
        preview_frame = tk.LabelFrame(
            self.dialog,
            text="Calculated Weights Preview",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        preview_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Preview text widget
        self.preview_text = tk.Text(
            preview_frame,
            height=4,
            bg=COLOR_BACKGROUND,
            fg=COLOR_SECONDARY,
            font=("Courier", 9),
            state="disabled",
            wrap=tk.WORD
        )
        self.preview_text.pack(fill=tk.X, pady=5)
        
        # Update preview initially
        self._update_preview()
    
    def _update_preview(self) -> None:
        """Update the weights preview based on current star ratings."""
        # Calculate weights from star ratings
        weights = convert_stars_to_weights(self.importance_ratings)
        
        # Format preview text
        preview_lines = []
        preview_lines.append("Response Weights (normalized):")
        preview_lines.append("-" * 35)
        
        for response_name in self.response_names:
            stars = "★" * self.importance_ratings[response_name] + "☆" * (5 - self.importance_ratings[response_name])
            weight = weights[response_name]
            preview_lines.append(f"{response_name:<15} {stars} → {weight:.3f}")
        
        preview_lines.append("-" * 35)
        preview_lines.append(f"Total: {sum(weights.values()):.3f}")
        
        # Update text widget
        self.preview_text.config(state="normal")
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, "\n".join(preview_lines))
        self.preview_text.config(state="disabled")
    
    def _create_buttons(self) -> None:
        """Create the dialog action buttons."""
        button_frame = tk.Frame(self.dialog, bg=COLOR_SURFACE)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            bg=COLOR_SECONDARY,
            fg=COLOR_SURFACE,
            font=("Arial", 10),
            relief="flat",
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Apply button
        apply_btn = tk.Button(
            button_frame,
            text="Apply Importance Ratings",
            command=self._on_apply,
            bg=COLOR_SUCCESS,
            fg=COLOR_SURFACE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8
        )
        apply_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Reset to equal importance button
        reset_btn = tk.Button(
            button_frame,
            text="Reset to Equal (3★)",
            command=self._on_reset,
            bg=COLOR_WARNING,
            fg=COLOR_SURFACE,
            font=("Arial", 9),
            relief="flat",
            padx=15,
            pady=8
        )
        reset_btn.pack(side=tk.LEFT)
    
    def _on_apply(self) -> None:
        """Handle apply button click."""
        try:
            # Calculate final weights
            weights = convert_stars_to_weights(self.importance_ratings)
            
            # Prepare result
            self.result = {
                'ratings': self.importance_ratings.copy(),
                'weights': weights,
                'applied': True
            }
            
            # Call callback if provided
            if self.callback:
                self.callback(self.result)
            
            logger.info(f"Applied importance ratings: {self.importance_ratings}")
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Error applying importance ratings: {e}")
            messagebox.showerror("Error", f"Failed to apply importance ratings: {e}")
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = {'applied': False}
        if self.callback:
            self.callback(self.result)
        self.dialog.destroy()
    
    def _on_reset(self) -> None:
        """Reset all ratings to 3 stars (equal importance)."""
        for response_name in self.response_names:
            self.importance_ratings[response_name] = 3
            if response_name in self.star_widgets:
                self.star_widgets[response_name].set_rating(3)
        
        self._update_preview()
        logger.info("Reset all importance ratings to 3 stars")


def convert_stars_to_weights(star_ratings: Dict[str, int]) -> Dict[str, float]:
    """
    Convert star ratings (1-5) to normalized weights for optimization.
    
    This function uses an exponential scaling approach where higher star ratings
    receive disproportionately more weight, reflecting the intuitive understanding
    that 5-star importance should have much more influence than 1-star.
    
    Args:
        star_ratings: Dictionary mapping response names to star ratings (1-5)
    
    Returns:
        Dictionary mapping response names to normalized weights (sum = 1.0)
    
    Example:
        >>> ratings = {'yield': 5, 'cost': 2, 'quality': 4}
        >>> weights = convert_stars_to_weights(ratings)
        >>> weights
        {'yield': 0.625, 'cost': 0.063, 'quality': 0.312}
    """
    if not star_ratings:
        return {}
    
    # Convert stars to raw weights using exponential scaling
    # This ensures that higher ratings get disproportionately more weight
    raw_weights = {}
    
    for response_name, stars in star_ratings.items():
        # Ensure stars is in valid range
        stars = max(1, min(5, stars))
        
        # Exponential scaling: weight = stars^2
        # This gives: 1★→1, 2★→4, 3★→9, 4★→16, 5★→25
        raw_weights[response_name] = stars ** 2
    
    # Normalize weights to sum to 1.0
    total_weight = sum(raw_weights.values())
    
    if total_weight == 0:
        # Fallback to equal weights if something goes wrong
        equal_weight = 1.0 / len(star_ratings)
        return {name: equal_weight for name in star_ratings.keys()}
    
    normalized_weights = {
        name: weight / total_weight 
        for name, weight in raw_weights.items()
    }
    
    return normalized_weights


def show_importance_dialog(parent: tk.Widget, responses_config: Dict[str, Any], 
                          callback: Callable = None) -> ResponseImportanceDialog:
    """
    Factory function for creating and showing response importance dialogs.
    
    Args:
        parent: Parent Tkinter widget
        responses_config: Dictionary of response configurations
        callback: Function to call when dialog is completed
    
    Returns:
        ResponseImportanceDialog instance
    
    Example:
        >>> def on_complete(result):
        ...     if result['applied']:
        ...         print(f"New weights: {result['weights']}")
        >>> 
        >>> dialog = show_importance_dialog(main_window, responses, on_complete)
    """
    try:
        logger.info(f"Creating importance dialog for {len(responses_config)} responses")
        return ResponseImportanceDialog(parent, responses_config, callback)
    except Exception as e:
        logger.error(f"Failed to create importance dialog: {e}")
        raise


# Example usage and testing
if __name__ == "__main__":
    # Test the star rating conversion
    test_ratings = {
        'yield': 5,      # Very important
        'cost': 2,       # Low importance  
        'quality': 4,    # High importance
        'efficiency': 3  # Medium importance
    }
    
    weights = convert_stars_to_weights(test_ratings)
    print("Star Ratings to Weights Conversion Test:")
    print("-" * 40)
    for name, rating in test_ratings.items():
        stars = "★" * rating + "☆" * (5 - rating)
        weight = weights[name]
        print(f"{name:<12} {stars} → {weight:.3f}")
    print("-" * 40)
    print(f"Total weight: {sum(weights.values()):.3f}")