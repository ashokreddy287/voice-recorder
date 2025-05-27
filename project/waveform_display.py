import tkinter as tk
import numpy as np
import threading
import time
import random

class WaveformDisplay(tk.Canvas):
    def __init__(self, parent, width=None, height=100, **kwargs):
        """Create a canvas for displaying audio waveforms.
        
        Args:
            parent: Parent widget
            width: Canvas width (default: parent width)
            height: Canvas height
            **kwargs: Additional arguments for tk.Canvas
        """
        super().__init__(parent, width=width, height=height, 
                         bg="#1E1E1E", highlightthickness=0, **kwargs)
        
        self.height = height
        self.width = width if width else parent.winfo_width()
        
        # Initialize with a flat line in the middle
        self.amplitude = 0
        self.bars = 60  # Number of bars to display
        self.bar_width = 8
        self.bar_gap = 2
        self.animation_running = False
        self.animation_thread = None
        
        # Draw initial flat line
        self.draw_waveform()
        
        # Bind to parent resize events
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        """Handle resizing of the canvas."""
        if event.width > 1:  # Ignore events with width <= 1
            self.width = event.width
            self.draw_waveform()
    
    def draw_waveform(self):
        """Draw the waveform visualization."""
        self.delete("all")  # Clear canvas
        
        # Draw grid lines (horizontal)
        for i in range(5):
            y = self.height * (i + 1) / 6
            self.create_line(0, y, self.width, y, fill="#333333", dash=(2, 4))
        
        # Calculate max bars that can fit in the width
        available_width = self.width - 20  # Add some padding
        max_bars = available_width // (self.bar_width + self.bar_gap)
        bars_to_draw = min(self.bars, max_bars)
        
        # Center the waveform
        start_x = (self.width - (bars_to_draw * (self.bar_width + self.bar_gap))) // 2
        
        # Draw the bars
        for i in range(bars_to_draw):
            # When not recording, show a flat line in the middle
            if not self.animation_running:
                bar_height = 2
                y = (self.height // 2) - (bar_height // 2)
                
                self.create_rectangle(
                    start_x + (i * (self.bar_width + self.bar_gap)),
                    y,
                    start_x + (i * (self.bar_width + self.bar_gap)) + self.bar_width,
                    y + bar_height,
                    fill="#4F7CAC",
                    width=0
                )
            else:
                # Use random heights for the animation, influenced by amplitude
                # Generate slightly different heights for adjacent bars for natural look
                if i > 0:
                    prev_height = int(self.heights[i-1])
                    max_diff = max(5, int(self.amplitude * 20))
                    random_factor = random.randint(-max_diff, max_diff)
                    bar_height = max(2, min(int(self.height * 0.8), 
                                            prev_height + random_factor))
                else:
                    bar_height = int(self.amplitude * self.height * 0.8)
                    bar_height = max(2, min(int(self.height * 0.8), bar_height))
                
                self.heights[i] = bar_height
                
                # Draw the bar centered vertically
                y = (self.height // 2) - (bar_height // 2)
                
                self.create_rectangle(
                    start_x + (i * (self.bar_width + self.bar_gap)),
                    y,
                    start_x + (i * (self.bar_width + self.bar_gap)) + self.bar_width,
                    y + bar_height,
                    fill="#4F7CAC",
                    width=0
                )
    
    def update_amplitude(self, amplitude):
        """Update the amplitude of the waveform.
        
        Args:
            amplitude: Audio amplitude value between 0 and 1
        """
        # Scale the amplitude for better visualization
        self.amplitude = min(1.0, amplitude * 1.5)
    
    def start_animation(self):
        """Start the waveform animation."""
        self.animation_running = True
        self.heights = [2] * self.bars  # Initialize with flat line heights
        
        # Start animation thread
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def stop_animation(self):
        """Stop the waveform animation."""
        self.animation_running = False
        if self.animation_thread:
            self.animation_thread = None
        
        # Reset to flat line
        self.amplitude = 0
        self.draw_waveform()
    
    def reset(self):
        """Reset the waveform to its initial state."""
        self.stop_animation()
        self.heights = [2] * self.bars
        self.amplitude = 0
        self.draw_waveform()
    
    def _animate(self):
        """Animation loop for the waveform."""
        while self.animation_running and self.animation_thread:
            self.draw_waveform()
            time.sleep(0.05)  # Update at ~20fps