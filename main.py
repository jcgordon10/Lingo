import database
import transcribe_speech
import generate_response
import generate_audio
import asyncio
from config import MF, NAME
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from langdetect import detect

def output(text: str, audio_file: BytesIO) -> None:
    """
    Prints the text and plays back the audio file.

    Parameters:
    text (str): The text to be printed.
    language (str): The language of the text (e.g. 'en' for English).
    audio_file (BytesIO): The audio file to be played.
    """
    # print the text
    print("\nLINGO: " + text + "\n\n----------------------------------------\n")

    # load the audio from the BytesIO object using pydub
    audio_segment = AudioSegment.from_file(audio_file, format='mp3')

    # play the audio
    play(audio_segment)

def process_voice_question() -> None:
    """
    Handles the user's button click event by capturing the spoken input,
    transcribing it, generating a response, converting the response to speech,
    and displaying the text response while playing the audio output.
    """
    # Capture user's spoken input and transcribe it
    transcript = transcribe_speech.main()
    if transcript is not None:
        transcript = transcript.strip()
    else:
        print("Error: Transcript is empty.")
        return
    print("ME: " + transcript + "\n")
    
    # Generate a response using NLP
    response_text = generate_response.converse(transcript)

    language_code = detect(response_text)

    # Convert the response text to speech
    audio_file = asyncio.run(get_audio_file(response_text, language_code, MF))

    # Display the text response and play the audio
    output(response_text, audio_file)

async def get_audio_file(text, language, voice_type):
    return await generate_audio.generate_audio(text, language, voice_type)

def process_text_question(text: str) -> None:
    """
    Handles the user's typed input, generating a response, converting the response to speech,
    and displaying the text response while playing the audio output.
    """
    
    # Generate a response using NLP
    response_text = generate_response.converse(text)

    language_code = detect(response_text)

    # Convert the response text to speech
    audio_file = asyncio.run(get_audio_file(response_text, language_code, MF))

    # Display the text response and play the audio
    output(response_text, audio_file)

def main() -> None:
    """
    The main loop of the application that waits for the user's button press
    (Enter key) and starts the recording process.
    """
    database.initialize_memory()

    global NAME     
    NAME = input("Please enter your name: ")

    while True:
        # Wait for the user to press a button (Enter key in this case)
        user_input = input("Press Enter to speak, or type your question... (type 'goodbye' to quit)")
        
        if user_input.lower() == "":
            # Start the recording process
            process_voice_question()
        elif user_input.lower() == "goodbye":
            # Call a different function to handle the "exit" command
            generate_response.exit_program()
            break  # exit the loop and terminate the program
        else:
            process_text_question(user_input)
            

if __name__ == "__main__":
    main()