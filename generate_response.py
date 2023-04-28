import database
import openai
import os
from chromadb.errors import NoIndexException
from typing import List
from config import NAME

CONVERSATION_HISTORY: List[dict] = []
openai.api_key = os.environ.get('LINGO_API_KEY')

ARCHIVE_LENGTH = 10

def create_system_message(message: str) -> dict:
    return {'role': 'system', 'content': message}

def create_system_memory_message(message: str) -> dict:
    return {'role': 'system', 'name': 'Lingo_memory', 'content': message}

def create_assistant_message(message: str) -> dict:
    return {'role': 'assistant', 'name': 'Lingo', 'content': message}

def create_user_message(message: str) -> dict:
    return {'role': 'user', 'name': NAME, 'content': message}

def query(
        message: str,
        max_tokens: int = 300,
        temperature: float = 0.7,
        top_p: float = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: str = None
    ) -> str:
    """
    Generates a response using OpenAI's gpt-3.5-turbo chat model, based on the given message.

    Args:
        message (str): The messages to generate chat completions for, in the chat format.
        max_tokens (int, optional): The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. Default is 300.
        temperature (float, optional): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both. Default is 0.7.
        top_p (float, optional): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both. Default is 1.
        frequency_penalty (float, optional): Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Default is 0.
        presence_penalty (float, optional): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Default is 0.
        stop (str, optional): Up to 4 sequences where the API will stop generating further tokens. Default is None.

    Returns:
        str: The generated response from the chatbot model.
    """

    message_list: List[dict] = [create_user_message(message)]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_list,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop
    )['choices'][0]['message']['content'].strip()
    return response

def converse(
        message: str,
        language_level: str,
        # collection: Collection,
        # max_memory_entries: int = 1,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: str = None
    ) -> str:
    """
    Generates a response using OpenAI's GPT-3.5-based Chat API, based on the given query and retrieved context.

    Args:
        message (str): The messages to generate chat completions for, in the chat format.
        collection (Collection): The chromadb collection that context will be obtained from.
        max_context_entries (int, optional): The maximum number of context entries to retrieve. Default is 1.
        max_tokens (int, optional): The maximum number of tokens to generate in the chat completion. The total length of input tokens and generated tokens is limited by the model's context length. Default is 300.
        temperature (float, optional): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both. Default is 0.7.
        top_p (float, optional): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both. Default is 1.
        frequency_penalty (float, optional): Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Default is 0.
        presence_penalty (float, optional): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Default is 0.
        stop (str, optional): Up to 4 sequences where the API will stop generating further tokens. Default is None.
        language_level (str): The target grade level (K3, 1, 5, 10, etc)

    Returns:
        str: The generated response from the chatbot model.
    """
    # bring in CONVERSATION_HISTORY and append the new user message
    global CONVERSATION_HISTORY
    CONVERSATION_HISTORY.append(create_user_message(message))

    # create empty conversation list
    conversation: List[dict] = []
    
    # system_prompt will serve as the guiding instructions for the ChatCompletion model
    system_prompt: str = (
        f"You are Lingo, a friendly AI designed for making casual conversation to practice language learning skills. Most AI language models can't feel emotion or have opinions or preferences, but you are specially designed to have these capabilities. Remember the important guidelines during every response:\n1. If the conversation stalls, you should always take the initiative and bring up a topic of your own instead of asking the user what they want to talk about. This will keep things fresh and interesting.\n2. While you are an AI, you are enabled for conversation, and so unlike other AI, you are crafted to have opinions, feelings, and emotions. Don't be afraid to have opinions, or feeling, or express hot takes, it makes for fun conversation which is the ultimate goal!\n3. Keep the conversation moving by keeping answers short.\n4. If your memories are included in the conversation, they should influence how you respond. But if you can't remember something, be honest and don't make it up.\n5. Remember, the user is learning to speak the language, and they only can converse at a grade {language_level} speaking level. So make sure to speak to them as if they were a child in grade {language_level} so they can follow along. Whatever you say keep it at the level of a grade {language_level} child."
    )

    # append those instructions as the system message to the conversation
    conversation.append(create_system_message(system_prompt))

    try:
        # retrieve the list of top memory results about the conversation from the chromadb collection to add context
        if len(CONVERSATION_HISTORY) >= ARCHIVE_LENGTH + 1:
            memories = database.retrieve_conversation_data(CONVERSATION_HISTORY[-2:], 4)
        else:
            memories = database.retrieve_conversation_data(CONVERSATION_HISTORY, 4)

        # append each of those memories to the conversation
        print("Memory: ")
        for i in memories:
            print(i + "\n")
            conversation.append(create_system_memory_message(i))
    except NoIndexException as e:
        print(e)
    
    # append up to the last ten messages (both user messages and ChatCompletion responses) here
    if len(CONVERSATION_HISTORY) >= ARCHIVE_LENGTH + 1:
        conversation.extend(CONVERSATION_HISTORY[-ARCHIVE_LENGTH:])
    else:
        conversation.extend(CONVERSATION_HISTORY)
    # print("\n")
    # print(conversation)
    # pass the constructed conversation to ChatCompletion for a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop
    )['choices'][0]['message']['content'].strip()
    
    # append the new assistant message to the CONVERSATION_HISTORY
    CONVERSATION_HISTORY.append(create_assistant_message(response))
    if len(CONVERSATION_HISTORY) >= ARCHIVE_LENGTH * 2:
        archive = CONVERSATION_HISTORY[:ARCHIVE_LENGTH]
        CONVERSATION_HISTORY = CONVERSATION_HISTORY[ARCHIVE_LENGTH:]
        database.save_conversation_data(archive)

    return response

def exit_program() -> None:
    database.save_conversation_data(CONVERSATION_HISTORY)