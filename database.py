import chromadb
import datetime
import pytz
import generate_response
from chromadb.api.local import LocalAPI
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings
from typing import List, Dict

CLIENT: LocalAPI = None
COLLECTION: Collection = None

def initialize_memory() -> None:
    global COLLECTION
    global CLIENT
    CLIENT = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=".chromadb/"
    ))
    COLLECTION = CLIENT.get_or_create_collection(name="lingo_conversation_memory")
    try:
        CLIENT.persist()
    except Exception as e:
        print(f"Error while initializing memory: {e}")
        raise

def format_conversation(archive: List[Dict[str, str]]) -> str:
    """
    Formats a conversation archive into a string, with each message on a new line
    and user messages prefixed with 'user: ', and assistant messages prefixed with
    the assistant's name followed by a colon.

    Args:
        archive: A list of dictionary objects representing each message in the conversation.
            Each dictionary should have the keys 'role' (with value 'user' or 'assistant'),
            'name' (only for assistant messages), and 'content' (the message text).

    Returns:
        A formatted string representing the conversation.
    """

    formatted_conversation = ""
    
    for entry in archive:
        formatted_conversation += f"{entry['name']}: {entry['content']}\n"
    
    return formatted_conversation.strip()

def save_conversation_data(archive: List[Dict[str, str]]) -> None:
    archived_conversation: str = format_conversation(archive)
    current_time = datetime.datetime.now(pytz.timezone('America/Indianapolis')).strftime("%Y-%m-%d %H-%M-%S %Z")
    summarization_prompt: str = f"you are Lingo, an AI designed to summarize conversations you've previously had, and provide synopsis of what was discussed so you can remember them later. Think of this as writing a note to yourself so you remember what you talked about. All summaries should be in the first person. Condense the summaries as small as possible, but write down anything that seems like it would be important to remember later, especially notes about the user. Please summarize the following conversation you just had:\n\n{archived_conversation}"
    summary: str = generate_response.query(summarization_prompt, max_tokens=100)
    COLLECTION.add(
        documents=summary,
        metadatas={"datetime": current_time},
        ids=str(COLLECTION.count() + 1)
    )
    CLIENT.persist()

def retrieve_conversation_data(conversation: List[Dict[str, str]], count: int):
    if count > COLLECTION.count():
        count = COLLECTION.count()
    formatted_conversation: str = format_conversation(conversation)
    results = COLLECTION.query(
        query_texts=[formatted_conversation],
        n_results=count
    )
    return results["documents"][0]