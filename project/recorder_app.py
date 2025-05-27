import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
import threading
from PIL import Image, ImageTk

from audio_recorder import AudioRecorder
from waveform_display import WaveformDisplay
from ui_components import RoundedButton, DigitalTimer, VolumeIndicator
from file_manager import FileManager
from utils import format_time, create_tooltip

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Initialize components
        self.audio_recorder = AudioRecorder(self.update_volume_callback)
        self.file_manager = FileManager()
        
        # App state
        self.recording = False
        self.playing = False
        self.current_file = None
        self.recording_thread = None
        self.timer_thread = None
        self.recording_time = 0
        
        # Create UI
        self.create_ui()
        self.setup_keyboard_shortcuts()
        
        # Set theme colors
        self.colors = {
            "bg_dark": "#121212",
            "card_bg": "#1E1E1E",
            "text_primary": "#FFFFFF",
            "text_secondary": "#AAAAAA",
            "accent": "#FF5252",
            "button_bg": "#2D2D2D",
            "button_hover": "#3D3D3D",
            "success": "#4CAF50",
            "waveform": "#4F7CAC"
        }
        self.apply_theme()

    def setup_window(self):
        """Configure the main window."""
        self.root.geometry("900x600")
        self.root.minsize(600, 400)
        self.root.configure(bg="#121212")
        
        # Make the window responsive
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def create_ui(self):
        """Create the user interface."""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Header
        self.main_frame.rowconfigure(1, weight=1)  # Content
        
        # Header section
        self.create_header()
        
        # Main content
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.rowconfigure(1, weight=0)
        
        # Waveform and recording controls
        self.create_recording_section()
        
        # Recordings list
        self.create_recordings_list()

    def create_header(self):
        """Create the header with title and info."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Voice Recorder",
            font=("SF Pro Display", 24, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Version info
        version_label = ttk.Label(
            header_frame,
            text="v1.0",
            font=("SF Pro Text", 12)
        )
        version_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

    def create_recording_section(self):
        """Create the recording interface with waveform display."""
        recording_frame = ttk.Frame(self.content_frame)
        recording_frame.grid(row=0, column=0, sticky="nsew", pady=10)
        recording_frame.columnconfigure(0, weight=1)
        
        # Waveform display
        self.waveform_display = WaveformDisplay(recording_frame, height=150)
        self.waveform_display.grid(row=0, column=0, sticky="ew", pady=10)
        
        # Timer and volume indicator
        info_frame = ttk.Frame(recording_frame)
        info_frame.grid(row=1, column=0, sticky="ew", pady=5)
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        
        # Digital timer
        self.timer = DigitalTimer(info_frame)
        self.timer.grid(row=0, column=0, sticky="w", padx=10)
        
        # Volume level indicator
        self.volume_indicator = VolumeIndicator(info_frame)
        self.volume_indicator.grid(row=0, column=1, sticky="e", padx=10)
        
        # Control buttons
        control_frame = ttk.Frame(recording_frame)
        control_frame.grid(row=2, column=0, sticky="ew", pady=15)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        
        # Record button
        self.record_button = RoundedButton(
            control_frame,
            text="Record",
            command=self.toggle_recording,
            bg_color=self.colors["accent"],
            width=120
        )
        self.record_button.grid(row=0, column=0, padx=10)
        create_tooltip(self.record_button, "Start/Stop Recording (Ctrl+R)")
        
        # Play button (initially disabled)
        self.play_button = RoundedButton(
            control_frame,
            text="Play",
            command=self.play_recording,
            bg_color=self.colors["button_bg"],
            width=120
        )
        self.play_button.grid(row=0, column=1, padx=10)
        self.play_button.disable()
        create_tooltip(self.play_button, "Play Current Recording (Space)")
        
        # Save button (initially disabled)
        self.save_button = RoundedButton(
            control_frame,
            text="Save",
            command=self.save_recording,
            bg_color=self.colors["button_bg"],
            width=120
        )
        self.save_button.grid(row=0, column=2, padx=10)
        self.save_button.disable()
        create_tooltip(self.save_button, "Save Recording (Ctrl+S)")

    def create_recordings_list(self):
        """Create the list of saved recordings."""
        recordings_frame = ttk.Frame(self.content_frame)
        recordings_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        recordings_frame.columnconfigure(0, weight=1)
        
        # Header
        recordings_header = ttk.Frame(recordings_frame)
        recordings_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        recordings_label = ttk.Label(
            recordings_header,
            text="Saved Recordings",
            font=("SF Pro Display", 16, "bold")
        )
        recordings_label.grid(row=0, column=0, sticky="w")
        
        refresh_button = RoundedButton(
            recordings_header,
            text="Refresh",
            command=self.refresh_recordings,
            bg_color=self.colors["button_bg"],
            width=100
        )
        refresh_button.grid(row=0, column=1, sticky="e")
        
        # Recordings listbox with scrollbar
        list_frame = ttk.Frame(recordings_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.recordings_listbox = tk.Listbox(
            list_frame,
            bg=self.colors["card_bg"],
            fg=self.colors["text_primary"],
            selectbackground=self.colors["accent"],
            font=("SF Pro Text", 12),
            height=6,
            borderwidth=0
        )
        self.recordings_listbox.grid(row=0, column=0, sticky="nsew")
        self.recordings_listbox.bind("<<ListboxSelect>>", self.on_recording_selected)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.recordings_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.recordings_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Populate the list
        self.refresh_recordings()

    def apply_theme(self):
        """Apply the color theme to UI elements."""
        self.root.configure(bg=self.colors["bg_dark"])
        
        style = ttk.Style()
        style.configure("TFrame", background=self.colors["bg_dark"])
        style.configure("TLabel", 
                         background=self.colors["bg_dark"], 
                         foreground=self.colors["text_primary"])
        
        # Custom styling for specific elements
        self.recordings_listbox.configure(
            bg=self.colors["card_bg"],
            fg=self.colors["text_primary"],
            selectbackground=self.colors["accent"]
        )

    def toggle_recording(self):
        """Start or stop recording."""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start audio recording."""
        self.recording = True
        self.recording_time = 0
        self.record_button.configure(text="Stop", bg_color="#E53935")
        self.play_button.disable()
        self.save_button.disable()
        
        # Reset and start the waveform animation
        self.waveform_display.reset()
        self.waveform_display.start_animation()
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self.audio_recorder.start_recording)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Start timer
        self.start_timer()

    def stop_recording(self):
        """Stop audio recording."""
        if not self.recording:
            return
            
        self.recording = False
        self.audio_recorder.stop_recording()
        self.record_button.configure(text="Record", bg_color=self.colors["accent"])
        
        # Stop the waveform animation
        self.waveform_display.stop_animation()
        
        # Stop the timer
        if self.timer_thread:
            self.timer_thread = None
        
        # Enable playback and save buttons
        self.play_button.enable()
        self.save_button.enable()
        
        # Set the current file to the temporary recording
        self.current_file = self.audio_recorder.get_temp_file()

    def play_recording(self):
        """Play the current recording."""
        if self.current_file and os.path.exists(self.current_file):
            # Use a thread to avoid UI freezing
            threading.Thread(
                target=self.audio_recorder.play_audio,
                args=(self.current_file,)
            ).start()
        else:
            messagebox.showerror("Error", "No recording available to play.")

    def save_recording(self):
        """Save the current recording to a file."""
        if not self.current_file or not os.path.exists(self.current_file):
            messagebox.showerror("Error", "No recording available to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("Wave files", "*.wav"), ("All files", "*.*")],
            title="Save Recording As"
        )
        
        if file_path:
            try:
                self.file_manager.save_recording(self.current_file, file_path)
                messagebox.showinfo("Success", f"Recording saved as {os.path.basename(file_path)}")
                self.refresh_recordings()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save recording: {str(e)}")

    def refresh_recordings(self):
        """Refresh the list of saved recordings."""
        self.recordings_listbox.delete(0, tk.END)
        recordings = self.file_manager.get_saved_recordings()
        
        if not recordings:
            self.recordings_listbox.insert(tk.END, "No saved recordings found")
        else:
            for recording in recordings:
                self.recordings_listbox.insert(tk.END, recording)

    def on_recording_selected(self, event):
        """Handle selection of a recording from the list."""
        selection = self.recordings_listbox.curselection()
        if not selection:
            return
            
        recording_name = self.recordings_listbox.get(selection[0])
        if recording_name == "No saved recordings found":
            return
            
        # Set as current file and enable playback
        self.current_file = self.file_manager.get_recording_path(recording_name)
        self.play_button.enable()
        self.save_button.disable()  # Already saved

    def start_timer(self):
        """Start the recording timer."""
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def update_timer(self):
        """Update the timer display."""
        start_time = time.time()
        while self.recording and self.timer_thread:
            elapsed = time.time() - start_time
            self.recording_time = elapsed
            self.timer.update(format_time(elapsed))
            time.sleep(0.1)

    def update_volume_callback(self, volume_level):
        """Callback to update UI with current volume level."""
        self.volume_indicator.update(volume_level)
        self.waveform_display.update_amplitude(volume_level)

    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for common actions."""
        self.root.bind("<Control-r>", lambda e: self.toggle_recording())
        self.root.bind("<Control-s>", lambda e: self.save_recording())
        self.root.bind("<space>", lambda e: self.play_recording())
        self.root.bind("<F5>", lambda e: self.refresh_recordings())