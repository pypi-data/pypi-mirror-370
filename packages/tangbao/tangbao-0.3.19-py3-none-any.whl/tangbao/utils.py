from typing import Dict, Any
import openai
def extract_source(rag_output: Dict[str, Any]) -> str:
    text = ""
    titles = []
    for i, context in enumerate(rag_output["docs"], start=1):
        titles.append(context['metadata']['Source'])
        text += (
            f"<b>Chunk {i}:</b>"
            f"<br>"
            f"<u>Document name</u>: {context['metadata']['Source']}"
            f"<br>"
            f"<u>Page</u>: {context['metadata']['Page']}"
            f"<br>"
            f"<u>Content</u>: <em>{context['text']}</em>"
            f"<br><br>"
        )
    return text, titles

def parse_log_file(log_file):
    """
    Parse a log file to extract failed chunk IDs.
    
    Args:
        log_file (str): Path to the log file to parse
        
    Returns:
        list: List of chunk IDs that failed to be indexed
    """
    failed_chunks = []
    with open(log_file, 'r') as file:
        for line in file:
            if "Failed to index chunk with id" in line:
                parts = line.split('id ')[1].split(': ')
                id_ = parts[0]
                failed_chunks.append(id_)
    return failed_chunks

def clear_log_file(log_file):
    """
    Clear the contents of a log file.
    
    Args:
        log_file (str): Path to the log file to clear
    """
    open(log_file, 'w').close()
# delete
def get_content(response):
        """
        Extracts content from an Azure/OpenAI-style chat response.
        Returns the full content as a string for both streaming and non-streaming responses.

        Args:
            response: Either a ChatCompletion or Stream response from Azure/OpenAI

        Returns:
            str: The complete response content
        """
        # For streaming responses
        if isinstance(response, openai.Stream):
            content_chunks = []
            for chunk in response:
                try:
                    if chunk.choices and chunk.choices[0].delta.content is not None:
                        content_chunks.append(chunk.choices[0].delta.content)
                except (IndexError, AttributeError):
                    # Skip malformed chunks
                    continue
            return ''.join(content_chunks)
        # For non-streaming responses
        else:
            return response.choices[0].message.content
