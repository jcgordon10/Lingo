import os
import whisper
from typing import Optional, List, Any
import tempfile
import pyaudio
import wave
import threading


def record_audio(frames: List[Any], stream: pyaudio.Stream, CHUNK: int, stop_recording: threading.Event) -> None:
    """
    Records audio data and appends it to the frames list.

    Args:
        frames (List[Any]): A list to store audio data.
        stream (pyaudio.Stream): The audio stream from which to record audio.
        CHUNK (int): The size of audio data to read in a single iteration.
        stop_recording (threading.Event): An event to signal when to stop recording.
    """
    while not stop_recording.is_set():
        data = stream.read(CHUNK)
        frames.append(data)


def capture_audio() -> Optional[str]:
    """
    Captures the user's spoken input using a microphone and saves it to a temporary file.

    Returns:
        audio_file (Optional[str]): The name of the temporary audio file or None if an error occurred.
    """
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Speak now... (Press Enter to stop recording.)")
    frames = []
    stop_recording = threading.Event()
    record_thread = threading.Thread(target=record_audio, args=(frames, stream, CHUNK, stop_recording))
    record_thread.start()

    input()  # Wait for Enter key to be pressed
    stop_recording.set()  # Signal to the recording thread to stop recording
    record_thread.join()  # Wait for the recording thread to finish

    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            wf = wave.open(temp_file.name, "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))
            wf.close()

            return temp_file.name
    except Exception as e:
        print(f"Error capturing audio: {e}")
        return None


def transcribe_speech(filename: str) -> Optional[str]:
    """
    Transcribes the given audio file using the Whisper ASR model.

    Args:
        filename (str): The name of the audio file to transcribe.

    Returns:
        transcript (Optional[str]): The transcribed text or None if an error occurred.
    """
    try:
        model = whisper.load_model("tiny")
        result = model.transcribe(filename, fp16=False)
        transcript = result["text"]
        return transcript
    except Exception as e:
        print(f"Error transcribing speech: {e}")
        return None


def main() -> None:
    """
    Captures user's spoken input, transcribes it, and prints the transcript.
    """
    # Capture user's spoken input
    audio_file = capture_audio()
    print("Recording complete.")
    if audio_file:
        # Transcribe the spoken input
        transcript = transcribe_speech(audio_file)
        os.remove(audio_file)
        return transcript