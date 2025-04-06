import librosa
from nexa.gguf import NexaVoiceInference
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

model_path = "faster-whisper-large"
inference = NexaVoiceInference(
    model_path=model_path,
    local_path=None,
    beam_size=5,
    language=None,
    task="transcribe",
    temperature=0.0,
    compute_type="default"
)

# run() method
inference.run()

# run_streamlit() method
inference.run_streamlit()

# _transcribe_audio(audio_path) method
transcript  = inference.transcribe(r"C:\Users\mamma\Downloads\PTT-20250405-WA0001.mp3")
print("Transcript:")
print(transcript)