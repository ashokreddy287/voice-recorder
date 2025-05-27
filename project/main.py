import tkinter as tk
from recorder_app import RecorderApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Voice Recorder")
    app = RecorderApp(root)
    root.mainloop()