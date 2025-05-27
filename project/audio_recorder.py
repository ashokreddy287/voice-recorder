import pyaudio
import wave
import threading
import tempfile
import os
import numpy as np
from pydub import AudioSegment
from pydub.playback import play

class AudioRecorder:
    def __init__(self, volume_callback=None):
        """Initialize the audio recorder.
        
        Args:
            volume_callback: Function to call with volume level updates
        """
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        self.stream = None
        self.pyaudio_instance = None
        self.is_recording = False
        self.temp_file = None
        self.volume_callback = volume_callback
        
    def start_recording(self):
        """Start recording audio."""
        self.is_recording = True
        self.frames = []
        
        # Initialize PyAudio
        self.pyaudio_instance = pyaudio.PyAudio()
        
        # Open audio stream
        self.stream = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        # Create temporary file
        temp_fd, self.temp_file = tempfile.mkstemp(suffix='.wav')
        os.close(temp_fd)
        
        # Record audio
        while self.is_recording:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            self.frames.append(data)
            
            # Calculate volume level for visualization
            if self.volume_callback:
                # Convert audio data to numpy array for volume calculation
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_data).mean() / 32768.0  # Normalize to 0-1
                
                # Call the callback with the volume level
                self.volume_callback(volume)
        
        # Stop and close the stream
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio_instance.terminate()
        
        # Save the recording to the temporary file
        self._save_to_temp_file()
    
    def stop_recording(self):
        """Stop the current recording."""
        self.is_recording = False
    
    def _save_to_temp_file(self):
        """Save the recorded frames to a temporary WAV file."""
        if not self.frames:
            return
            
        try:
            with wave.open(self.temp_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
        except Exception as e:
            print(f"Error saving temporary file: {e}")
    
    def play_audio(self, file_path):
        """Play an audio file.
        
        Args:
            file_path: Path to the audio file to play
        """
        try:
            sound = AudioSegment.from_wav(file_path)
            play(sound)
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def get_temp_file(self):
        """Get the path to the temporary recording file.
        
        Returns:
            str: Path to the temporary file
        """
        return self.temp_file