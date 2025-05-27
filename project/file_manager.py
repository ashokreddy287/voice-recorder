import os
import shutil
from datetime import datetime

class FileManager:
    def __init__(self, recordings_dir="recordings"):
        """Initialize the file manager.
        
        Args:
            recordings_dir: Directory to store saved recordings
        """
        self.recordings_dir = recordings_dir
        
        # Create recordings directory if it doesn't exist
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
    
    def save_recording(self, source_file, destination_file=None):
        """Save a recording file.
        
        Args:
            source_file: Path to the source recording file
            destination_file: Path where to save the file. If None, generate a name.
            
        Returns:
            str: Path to the saved file
        """
        if not destination_file:
            # Generate a filename based on current date and time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            destination_file = os.path.join(self.recordings_dir, f"recording_{timestamp}.wav")
        
        # Make sure the destination directory exists
        dest_dir = os.path.dirname(destination_file)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        # Copy the file
        shutil.copy2(source_file, destination_file)
        
        return destination_file
    
    def get_saved_recordings(self):
        """Get a list of saved recordings.
        
        Returns:
            list: List of recording filenames
        """
        if not os.path.exists(self.recordings_dir):
            return []
            
        # Get all .wav files in the recordings directory
        recordings = [f for f in os.listdir(self.recordings_dir) 
                      if f.endswith('.wav') and os.path.isfile(os.path.join(self.recordings_dir, f))]
        
        # Sort by modification time (newest first)
        recordings.sort(key=lambda x: os.path.getmtime(os.path.join(self.recordings_dir, x)), 
                        reverse=True)
        
        return recordings
    
    def delete_recording(self, filename):
        """Delete a recording file.
        
        Args:
            filename: Name of the recording file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        file_path = os.path.join(self.recordings_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
    
    def get_recording_path(self, filename):
        """Get the full path to a recording.
        
        Args:
            filename: Name of the recording file
            
        Returns:
            str: Full path to the recording
        """
        return os.path.join(self.recordings_dir, filename)