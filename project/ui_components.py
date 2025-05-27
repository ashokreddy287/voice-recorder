import tkinter as tk
from tkinter import ttk

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="Button", command=None, bg_color="#2D2D2D", 
                 text_color="#FFFFFF", width=100, height=36, corner_radius=18, **kwargs):
        """Create a rounded button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Function to call when button is clicked
            bg_color: Background color of the button
            text_color: Text color
            width: Button width
            height: Button height
            corner_radius: Radius for rounded corners
            **kwargs: Additional arguments for tk.Canvas
        """
        super().__init__(parent, width=width, height=height, 
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        
        self.bg_color = bg_color
        self.text_color = text_color
        self.command = command
        self.state = "normal"  # or "disabled"
        
        # Draw the rounded rectangle
        self.button_shape = self.create_rounded_rect(0, 0, width, height, corner_radius, 
                                                     fill=bg_color, outline="")
        
        # Add text
        self.button_text = self.create_text(width//2, height//2, text=text, 
                                            fill=text_color, font=("SF Pro Text", 12))
        
        # Bind events
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle on the canvas."""
        points = [
            x1+radius, y1,          # Top left after corner
            x2-radius, y1,          # Top right before corner
            x2, y1,                 # Top right corner top
            x2, y1+radius,          # Top right corner right
            x2, y2-radius,          # Bottom right corner before
            x2, y2,                 # Bottom right corner bottom
            x2-radius, y2,          # Bottom right after corner
            x1+radius, y2,          # Bottom left before corner
            x1, y2,                 # Bottom left corner bottom
            x1, y2-radius,          # Bottom left corner left
            x1, y1+radius,          # Top left corner before
            x1, y1,                 # Top left corner top
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_press(self, event):
        """Handle button press event."""
        if self.state == "normal":
            self.itemconfig(self.button_shape, fill=self._darken_color(self.bg_color))
            if self.command:
                self.command()
    
    def _on_release(self, event):
        """Handle button release event."""
        if self.state == "normal":
            self.itemconfig(self.button_shape, fill=self.bg_color)
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        if self.state == "normal":
            self.itemconfig(self.button_shape, fill=self._lighten_color(self.bg_color))
            self.configure(cursor="hand2")
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        if self.state == "normal":
            self.itemconfig(self.button_shape, fill=self.bg_color)
            self.configure(cursor="")
    
    def _lighten_color(self, hex_color):
        """Lighten a hex color by 15%."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, hex_color):
        """Darken a hex color by 15%."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        r = max(0, r - 25)
        g = max(0, g - 25)
        b = max(0, b - 25)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def configure(self, **kwargs):
        """Configure button properties."""
        if "text" in kwargs:
            self.itemconfig(self.button_text, text=kwargs.pop("text"))
        if "bg_color" in kwargs:
            self.bg_color = kwargs.pop("bg_color")
            self.itemconfig(self.button_shape, fill=self.bg_color)
        if "text_color" in kwargs:
            self.text_color = kwargs.pop("text_color")
            self.itemconfig(self.button_text, fill=self.text_color)
        
        super().configure(**kwargs)
    
    def disable(self):
        """Disable the button."""
        self.state = "disabled"
        self.itemconfig(self.button_shape, fill="#555555")
        self.itemconfig(self.button_text, fill="#888888")
        self.configure(cursor="")
    
    def enable(self):
        """Enable the button."""
        self.state = "normal"
        self.itemconfig(self.button_shape, fill=self.bg_color)
        self.itemconfig(self.button_text, fill=self.text_color)


class DigitalTimer(tk.Canvas):
    def __init__(self, parent, width=120, height=30, **kwargs):
        """Create a digital timer display.
        
        Args:
            parent: Parent widget
            width: Canvas width
            height: Canvas height
            **kwargs: Additional arguments for tk.Canvas
        """
        super().__init__(parent, width=width, height=height, 
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        
        # Create the timer text
        self.timer_text = self.create_text(
            width//2, height//2,
            text="00:00.0",
            fill="#FFFFFF",
            font=("SF Mono", 14, "bold")
        )
    
    def update(self, time_text):
        """Update the timer display.
        
        Args:
            time_text: Formatted time text (mm:ss.t)
        """
        self.itemconfig(self.timer_text, text=time_text)


class VolumeIndicator(tk.Canvas):
    def __init__(self, parent, width=150, height=20, **kwargs):
        """Create a volume level indicator.
        
        Args:
            parent: Parent widget
            width: Canvas width
            height: Canvas height
            **kwargs: Additional arguments for tk.Canvas
        """
        super().__init__(parent, width=width, height=height, 
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        
        # Create background bar
        self.background = self.create_rectangle(
            0, 0, width, height,
            fill="#333333", outline=""
        )
        
        # Create level indicator
        self.level = self.create_rectangle(
            0, 0, 0, height,
            fill="#4CAF50", outline=""
        )
        
        # Label
        self.create_text(
            width//2, height//2,
            text="Volume",
            fill="#FFFFFF",
            font=("SF Pro Text", 10)
        )
    
    def update(self, level):
        """Update the volume level display.
        
        Args:
            level: Volume level between 0 and 1
        """
        width = self.winfo_width() * level
        self.itemconfig(self.level, width=width)
        
        # Change color based on level
        if level < 0.3:
            color = "#4CAF50"  # Green
        elif level < 0.7:
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red
        
        self.itemconfig(self.level, fill=color)