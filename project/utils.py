from tkinter import Toplevel, Label

def format_time(seconds):
    """Format seconds into mm:ss.t format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    minutes = int(seconds // 60)
    seconds = seconds % 60
    tenths = int((seconds * 10) % 10)
    
    return f"{minutes:02d}:{int(seconds):02d}.{tenths}"

def create_tooltip(widget, text):
    """Create a tooltip for a widget.
    
    Args:
        widget: The widget to add a tooltip to
        text: Tooltip text
    """
    def enter(event):
        x, y, _, _ = widget.bbox("all")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        label = Label(tooltip, text=text, justify="left",
                     background="#2D2D2D", relief="solid", borderwidth=1,
                     font=("SF Pro Text", 10), foreground="#FFFFFF", padx=5, pady=2)
        label.pack(ipadx=3)
        
        widget.tooltip = tooltip
        
    def leave(event):
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()
            
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)