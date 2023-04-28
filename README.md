# Lingo Language Learning AI

<img src="./Lingo.jpeg" alt="Lingo Language Learning AI" width="200" />
</br>
</br>
Lingo is a friendly conversational AI designed for practicing language learning skills. Lingo is instructed to provide casual conversation for practicing language skills and is meant to make conversations fun and engaging.
</br>
</br>
## Features

* Transcribes spoken input via Whisper
* generates text responses via ChatGPT API
* Converts generated responses to speech via edge-tts
* Adapts conversation to a specific grade level
* Supports multiple languages and voices
* Remembers previous conversations via ChromaDB

## Usage

### Command Line Arguments

* `whisper_model`: Whisper model to be used. Choices: "tiny", "tiny.en", "base", "base.en", "small", "small.en"
* `language`: The language code of the conversation (e.g., 'en' for English, 'es' for Spanish). Default: 'en'
* `gender`: The desired gender of the voice. Choices: "M", "F".
* `grade_level`: The target grade level. Choices: "K3", "K4", "K5", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12".

### Example

```bash
python3 main.py tiny en M 5
```

## Dependencies

* `openai`
* `whisper-openai`
* `chromadb`
* `edge_tts`
* `pytz`
* `pydub`
* `pyaudio`

You will need to follow whisper's install guide in their [README](https://github.com/openai/whisper#setup)

You will also need to set your own OpenAI Chat API key in your environment variables or in your terminal, like this:

```bash
setx LINGO_API_KEY "your_api_key_here"
```

## License

[GPL-3.0 License](https://opensource.org/license/gpl-3-0/)