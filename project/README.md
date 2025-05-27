# Voice Recorder Application

A beautiful and intuitive voice recording application built with Python.

## Features

- Record audio with a single click
- Visualize audio input with animated waveforms
- Play back recordings
- Save recordings with custom file names
- View and manage saved recordings
- Keyboard shortcuts for common actions

## Requirements

- Python 3.6+
- PyAudio
- pydub
- matplotlib
- numpy
- Pillow
- tkinter (usually comes with Python)

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python main.py
```

### Keyboard Shortcuts

- `Ctrl+R`: Start/Stop recording
- `Ctrl+S`: Save recording
- `Space`: Play current recording
- `F5`: Refresh recordings list

## Project Structure

- `main.py`: Entry point
- `recorder_app.py`: Main application class
- `audio_recorder.py`: Audio recording functionality
- `waveform_display.py`: Waveform visualization
- `ui_components.py`: Custom UI components
- `file_manager.py`: File operations for recordings
- `utils.py`: Utility functions

## License

MIT