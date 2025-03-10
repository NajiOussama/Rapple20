import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import threading
import logging
import queue


#Pour choisir le périphérique :
#print(sd.query_devices())

# Recording settings
device_info = sd.query_devices(21, "input")  # Get mic info
SAMPLE_RATE = int(device_info["default_samplerate"])
OUTPUT_FILE = "recorded_audio.wav"
recording = False  # Flag to check if recording is active
audio_data = []  # Store recorded audio
DEVICE_INDEX = 21
stream = None

def callback(indata, frames, time, status):
    """Callback function to continuously store audio data."""
    if status:
        logging.error(f"Error in audio callback: {status}")
    if recording:
        audio_data.append(indata.copy())

def start_recording():
    """Start recording the audio."""
    global recording, audio_data, stream
    audio_data = []  # Reset audio data
    recording = True
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback, device=DEVICE_INDEX)
    stream.start()
    logging.info("Recording started.")
    print("Recording started...")

def stop_recording():
    """Stop recording and transcribe."""
    global recording, stream
    recording = False
    stream.stop()
    stream.close()
    logging.info("Recording stopped. Processing audio...")

    # Convert recorded chunks to a NumPy array
    audio_np = np.concatenate(audio_data, axis=0)

    # Save as WAV file
    wav.write(OUTPUT_FILE, SAMPLE_RATE, audio_np)

    # Queue to get the transcription result
    transcription_queue = queue.Queue()

    # Start transcription in a separate thread
    thread = threading.Thread(target=lambda: transcription_queue.put(transcribe_audio()))
    thread.start()
    thread.join()  # Wait for the thread to finish

    # Get the transcription result from the queue
    print(transcription_queue.get())

def transcribe_audio():
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(OUTPUT_FILE)
    result = []
    for segment in segments:
        result.append(segment.text)
    return "".join(result)

#-------------------------------------------------------------------
import time

for i in range(3, 0, -1):
    print(f"Recording in {i} seconds")
    time.sleep(1)

start_recording()

time.sleep(10)

print("Did you just say :")
stop_recording()
print("??")
#-------------------------------------------------------------------



