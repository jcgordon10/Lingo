import edge_tts
import random
from config import VOICES
from edge_tts import VoicesManager
from io import BytesIO

async def generate_audio(text: str, language: str, gender: str) -> BytesIO:
    """
    Generate an audio file from a string of text using edge_tts library and returns the file as BytesIO object.

    Parameters:
    text (str): The text to be converted to audio.
    language (str): The language of the text (e.g. 'en' for English).
    MF (str): The sex, male or female of the voice.

    Output:
    BytesIO: The generated audio file as a BytesIO object.
    """
    print("gender = " + gender)
    print("lan = " + language)
    # Map input MF value to edge_tts Gender enum value
    gender_map = {"M": "Male", "F": "Female"}
    if gender not in gender_map:
        raise Exception("audio voice variable MF must either be male 'M' or female 'F'")

    voice_key = f"{language.upper()}_{gender_map[gender].upper()}"
    print("voice_key = " + voice_key)
    print(VOICES)

    if voice_key in VOICES:
        selected_voice = VOICES[voice_key]
    else:
        voices_manager = await VoicesManager.create()
        voice_candidates = voices_manager.find(Gender=gender_map[gender], Language=language)

        if not voice_candidates:
            raise Exception(f"No voices found for language '{language}' and gender '{gender}'")

        print()
        selected_voice = random.choice(voice_candidates)["ShortName"]

    # Create an edge_tts Communicate object with the text and the voice
    communicate = edge_tts.Communicate(text, selected_voice)

    # Create a BytesIO object to hold the audio file
    audio_file = BytesIO()

    # Write the audio data to the BytesIO object
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_file.write(chunk["data"])

    # Reset the file pointer to the beginning of the BytesIO object
    audio_file.seek(0)

    return audio_file