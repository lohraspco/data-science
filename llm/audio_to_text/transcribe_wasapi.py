import numpy as np
import time
import threading
import queue
from typing import Optional
import wave
import tempfile
import os
import pyaudio

try:
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install pyaudio faster-whisper")
    exit(1)

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class SimpleWASAPITranscriber:
    def __init__(self, 
                 model_size: str = "base",
                 device: str = "cpu",
                 chunk_duration: float = 3.0,
                 language: Optional[str] = None):
        """
        Simple WASAPI Loopback Transcriber using PyAudio
        Much more reliable than raw COM programming
        
        Args:
            model_size: Whisper model size
            device: "cpu" or "cuda" 
            chunk_duration: Audio chunk duration for transcription
            language: Language code (None for auto-detection)
        """
        self.chunk_duration = chunk_duration
        self.language = language
        
        # Load Faster-Whisper model
        print(f"Loading Faster-Whisper model: {model_size}")
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
        
        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.sample_rate = 16000  # Standard rate for speech recognition
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paFloat32
        
        # Find loopback device
        self.loopback_device = self._find_loopback_device()
        
        # Threading
        self.running = False
        self.audio_queue = queue.Queue(maxsize=50)
        self.result_queue = queue.Queue()
        self.stream = None
        
    def _find_loopback_device(self):
        """Find Windows loopback audio device"""
        print("\nSearching for loopback audio devices...")
        
        loopback_device = None
        device_count = self.audio.get_device_count()
        
        print(f"Found {device_count} audio devices:")
        
        for i in range(device_count):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                device_name = device_info['name'].lower()
                max_input_channels = device_info['maxInputChannels']
                
                print(f"  {i}: {device_info['name']} (inputs: {max_input_channels})")
                
                # Look for common loopback device names
                loopback_keywords = [
                    'stereo mix', 'wave out mix', 'what u hear', 
                    'loopback', 'speakers', 'headphones'
                ]
                
                if max_input_channels > 0:
                    for keyword in loopback_keywords:
                        if keyword in device_name:
                            loopback_device = i
                            print(f"  -> Found potential loopback device: {device_info['name']}")
                            break
                    
                    if loopback_device is not None:
                        break
                        
            except Exception as e:
                print(f"  Error reading device {i}: {e}")
        
        if loopback_device is None:
            print("\nNo clear loopback device found.")
            print("Common solutions:")
            print("1. Enable 'Stereo Mix' in Windows Sound settings")
            print("2. Use 'Listen to this device' on your main audio device")
            print("3. Install VB-Cable or similar virtual audio cable")
            print("\nTrying default input device...")
            loopback_device = None  # Will use default
        else:
            print(f"\nUsing device {loopback_device} for loopback recording")
        
        return loopback_device
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for real-time audio processing"""
        if status:
            print(f"Audio status: {status}")
        
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            # Simple voice activity detection
            rms_level = np.sqrt(np.mean(audio_data**2))
            
            if rms_level > 0.001:  # Threshold for silence detection
                # Add to queue for transcription
                try:
                    self.audio_queue.put_nowait((audio_data.copy(), time.time()))
                except queue.Full:
                    # Remove oldest item if queue is full
                    try:
                        self.audio_queue.get_nowait()
                        self.audio_queue.put_nowait((audio_data.copy(), time.time()))
                    except queue.Empty:
                        pass
        
        except Exception as e:
            print(f"Audio callback error: {e}")
        
        return (in_data, pyaudio.paContinue)
    
    def _transcription_worker(self):
        """Worker thread for audio transcription"""
        audio_buffer = []
        buffer_duration = 0.0
        
        while self.running:
            try:
                # Get audio data from queue
                audio_chunk, timestamp = self.audio_queue.get(timeout=1.0)
                
                # Add to buffer
                audio_buffer.extend(audio_chunk)
                buffer_duration += len(audio_chunk) / self.sample_rate
                
                # Process when we have enough audio
                if buffer_duration >= self.chunk_duration:
                    # Convert to numpy array
                    audio_array = np.array(audio_buffer, dtype=np.float32)
                    
                    # Keep some overlap for next chunk
                    overlap_duration = 0.5  # 0.5 seconds
                    overlap_samples = int(self.sample_rate * overlap_duration)
                    
                    if len(audio_buffer) > overlap_samples:
                        audio_buffer = audio_buffer[-overlap_samples:]
                        buffer_duration = overlap_duration
                    else:
                        audio_buffer = []
                        buffer_duration = 0.0
                    
                    # Transcribe audio
                    try:
                        segments, info = self.model.transcribe(
                            audio_array,
                            language=self.language,
                            beam_size=5,
                            vad_filter=True,
                            vad_parameters=dict(min_silence_duration_ms=500)
                        )
                        
                        # Collect text from segments
                        text_parts = []
                        for segment in segments:
                            if segment.text.strip():
                                text_parts.append(segment.text.strip())
                        
                        if text_parts:
                            full_text = " ".join(text_parts)
                            
                            # Add result to queue
                            self.result_queue.put({
                                'text': full_text,
                                'timestamp': timestamp,
                                'language': info.language,
                                'probability': info.language_probability
                            })
                    
                    except Exception as e:
                        print(f"Transcription error: {e}")
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Transcription worker error: {e}")
    
    def start_transcription(self):
        """Start live transcription"""
        if self.running:
            print("Already running!")
            return
        
        self.running = True
        
        try:
            # Start transcription worker thread
            self.transcription_thread = threading.Thread(target=self._transcription_worker)
            self.transcription_thread.start()
            
            # Start audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.loopback_device,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            
            print("Live transcription started!")
            print("Play some audio to see transcription results...")
            
        except Exception as e:
            print(f"Error starting transcription: {e}")
            self.running = False
            raise
    
    def stop_transcription(self):
        """Stop transcription"""
        self.running = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        
        if hasattr(self, 'transcription_thread'):
            self.transcription_thread.join(timeout=2.0)
        
        print("Transcription stopped.")
    
    def get_results(self):
        """Get transcription results"""
        results = []
        while not self.result_queue.empty():
            try:
                results.append(self.result_queue.get_nowait())
            except queue.Empty:
                break
        return results
    
    def __del__(self):
        """Cleanup"""
        self.stop_transcription()
        if hasattr(self, 'audio'):
            self.audio.terminate()

# Alternative: Record to file then transcribe
class FileBasedTranscriber:
    def __init__(self, model_size="base", language=None):
        """File-based transcriber - simpler approach"""
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.language = language
        self.audio = pyaudio.PyAudio()
        
    def find_audio_devices(self):
        """List all audio devices"""
        print("Available audio devices:")
        device_count = self.audio.get_device_count()
        
        for i in range(device_count):
            try:
                info = self.audio.get_device_info_by_index(i)
                print(f"  {i}: {info['name']} (in: {info['maxInputChannels']}, out: {info['maxOutputChannels']})")
            except:
                pass
    
    def record_and_transcribe(self, duration=10, device_index=None):
        """Record audio to file then transcribe"""
        print(f"Recording {duration} seconds...")
        
        # Recording parameters
        sample_rate = 16000
        channels = 1
        chunk_size = 1024
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            # Record audio
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk_size
            )
            
            print("Recording...")
            frames = []
            
            for i in range(int(sample_rate / chunk_size * duration)):
                data = stream.read(chunk_size)
                frames.append(data)
                
                # Show progress
                if i % (sample_rate // chunk_size) == 0:
                    print(f"  {i // (sample_rate // chunk_size) + 1}/{duration} seconds")
            
            stream.stop_stream()
            stream.close()
            
            # Save to WAV file
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paFloat32))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"Recording saved to: {temp_filename}")
            
            # Transcribe
            print("Transcribing...")
            segments, info = self.model.transcribe(
                temp_filename,
                language=self.language,
                vad_filter=True
            )
            
            print(f"\nTranscription (Language: {info.language}):")
            print("-" * 40)
            
            for segment in segments:
                print(f"[{segment.start:.1f}s -> {segment.end:.1f}s] {segment.text}")
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_filename)
            except:
                pass
    
    def __del__(self):
        if hasattr(self, 'audio'):
            self.audio.terminate()

def main():
    """Main function with multiple options"""
    print("WASAPI Loopback Transcription Options")
    print("====================================")
    print("1. Live transcription (real-time)")
    print("2. Record to file then transcribe")
    print("3. List audio devices")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "3":
        # List devices
        transcriber = FileBasedTranscriber()
        transcriber.find_audio_devices()
        return
    
    elif choice == "2":
        # File-based transcription
        model_size = input("Model size (tiny/base/small) [base]: ").strip() or "base"
        duration = int(input("Recording duration in seconds [10]: ").strip() or "10")
        
        transcriber = FileBasedTranscriber(model_size=model_size)
        transcriber.find_audio_devices()
        
        device_input = input("Enter device number (or press Enter for default): ").strip()
        device_index = int(device_input) if device_input else None
        
        transcriber.record_and_transcribe(duration=duration, device_index=device_index)
    
    else:
        # Live transcription
        model_size = input("Model size (tiny/base/small) [base]: ").strip() or "base"
        language = input("Language (en/es/fr/de or auto) [auto]: ").strip()
        if language.lower() in ['auto', '']:
            language = None
        
        transcriber = SimpleWASAPITranscriber(
            model_size=model_size,
            language=language,
            chunk_duration=3.0
        )
        
        try:
            transcriber.start_transcription()
            
            print("\nTranscription Results:")
            print("-" * 30)
            
            while True:
                results = transcriber.get_results()
                
                for result in results:
                    timestamp = time.strftime("%H:%M:%S", time.localtime(result['timestamp']))
                    lang_info = f"[{result['language']}]" if result['language'] else ""
                    print(f"[{timestamp}] {lang_info} {result['text']}")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            transcriber.stop_transcription()

if __name__ == "__main__":
    main()