import edge_tts
from config import VOICES
from io import BytesIO

async def generate_audio(text: str, language: str, MF: str) -> BytesIO:
    """
    Generate an audio file from a string of text using edge_tts library and returns the file as BytesIO object.

    Parameters:
    text (str): The text to be converted to audio.
    language (str): The language of the text (e.g. 'en' for English).
    MF (str): The sex, male or female of the voice.

    Output:
    BytesIO: The generated audio file as a BytesIO object.
    """
    voice_type = ""
    match language:
        case "en":
            voice_type = voice_type + language.upper() + "_"
        case _:
            raise Exception("audio voice language code not implemented")

    match MF:
        case "M":
            voice_type = voice_type + "MALE"
        case "F":
            voice_type = voice_type + "FEMALE"
        case _:
            raise Exception("audio voice variable MF must either be male 'M' or female 'F'")

    voice = VOICES[voice_type]

    # Create an edge_tts Communicate object with the text and the voice
    communicate = edge_tts.Communicate(text, voice)

    # Create a BytesIO object to hold the audio file
    audio_file = BytesIO()

    # Write the audio data to the BytesIO object
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_file.write(chunk["data"])

    # Reset the file pointer to the beginning of the BytesIO object
    audio_file.seek(0)

    return audio_file