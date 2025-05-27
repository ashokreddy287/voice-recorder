import React, { useState, useRef } from 'react';
import { Mic, Square, Play, Save, RefreshCw, Trash2 } from 'lucide-react';

interface Recording {
  id: string;
  blob: Blob;
  url: string;
  timestamp: Date;
}

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0);

  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const animationFrame = useRef<number>();
  const audioContext = useRef<AudioContext>();
  const analyser = useRef<AnalyserNode>();
  const startTime = useRef<number>(0);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      // Set up audio analysis
      audioContext.current = new AudioContext();
      analyser.current = audioContext.current.createAnalyser();
      const source = audioContext.current.createMediaStreamSource(stream);
      source.connect(analyser.current);
      analyser.current.fftSize = 256;

      // Start recording
      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        const newRecording: Recording = {
          id: Date.now().toString(),
          blob,
          url,
          timestamp: new Date(),
        };
        setRecordings(prev => [newRecording, ...prev]);
        setSelectedRecording(newRecording);
      };

      mediaRecorder.current.start();
      startTime.current = Date.now();
      setIsRecording(true);
      updateVolumeMeter();
    } catch (err) {
      console.error('Error accessing microphone:', err);
      alert('Unable to access microphone. Please ensure you have granted permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      if (animationFrame.current) {
        cancelAnimationFrame(animationFrame.current);
      }
      setVolume(0);
    }
  };

  const updateVolumeMeter = () => {
    if (!analyser.current) return;

    const dataArray = new Uint8Array(analyser.current.frequencyBinCount);
    analyser.current.getByteFrequencyData(dataArray);
    const volume = dataArray.reduce((acc, val) => acc + val, 0) / dataArray.length;
    setVolume(volume / 255);

    setDuration((Date.now() - startTime.current) / 1000);
    animationFrame.current = requestAnimationFrame(updateVolumeMeter);
  };

  const playRecording = (recording: Recording) => {
    const audio = new Audio(recording.url);
    audio.play();
  };

  const saveRecording = (recording: Recording) => {
    const a = document.createElement('a');
    a.href = recording.url;
    a.download = `recording-${new Date(recording.timestamp).toISOString()}.wav`;
    a.click();
  };

  const deleteRecording = (recordingId: string) => {
    setRecordings(prev => prev.filter(rec => rec.id !== recordingId));
    if (selectedRecording?.id === recordingId) {
      setSelectedRecording(null);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">Voice Recorder</h1>

        {/* Recording Interface */}
        <div className="bg-gray-800 rounded-lg p-8 mb-8 shadow-xl">
          <div className="flex flex-col items-center gap-6">
            {/* Volume Meter */}
            <div className="w-full h-4 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-blue-500 transition-all duration-100"
                style={{ width: `${volume * 100}%` }}
              />
            </div>

            {/* Timer */}
            <div className="text-4xl font-mono">
              {formatTime(duration)}
            </div>

            {/* Controls */}
            <div className="flex gap-4">
              <button
                onClick={isRecording ? stopRecording : startRecording}
                className={`p-4 rounded-full ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600' 
                    : 'bg-blue-500 hover:bg-blue-600'
                } transition-colors`}
              >
                {isRecording ? <Square size={24} /> : <Mic size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Recordings List */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Recordings</h2>
            <button 
              onClick={() => setRecordings([])}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <RefreshCw size={20} />
            </button>
          </div>

          <div className="space-y-3">
            {recordings.map(recording => (
              <div 
                key={recording.id}
                className={`flex items-center justify-between p-3 rounded-lg ${
                  selectedRecording?.id === recording.id 
                    ? 'bg-gray-700' 
                    : 'bg-gray-900'
                }`}
              >
                <span className="text-sm">
                  {new Date(recording.timestamp).toLocaleString()}
                </span>
                <div className="flex gap-3">
                  <button 
                    onClick={() => playRecording(recording)}
                    className="text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    <Play size={20} />
                  </button>
                  <button 
                    onClick={() => saveRecording(recording)}
                    className="text-green-400 hover:text-green-300 transition-colors"
                  >
                    <Save size={20} />
                  </button>
                  <button 
                    onClick={() => deleteRecording(recording.id)}
                    className="text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>
            ))}

            {recordings.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                No recordings yet
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;