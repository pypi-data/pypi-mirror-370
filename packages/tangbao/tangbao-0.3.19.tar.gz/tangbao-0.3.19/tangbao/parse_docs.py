import os
import pandas as pd
from langchain_community.document_loaders import UnstructuredFileLoader
from unstructured.cleaners.core import group_broken_paragraphs
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_filenames(directory):
    """
    Creates a list with the names and paths of the files in a directory.

    Args:
        directory (str): The directory path to search for files.

    Returns:
        pd.DataFrame: A DataFrame containing filenames and their paths.

    Example:
        filenames = get_filenames('/path/to/directory')
        print(filenames)
    """
    listfilenames = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            listfilenames.append({
                "name": filename,
                "path": f
            })
    return pd.DataFrame(listfilenames)

def split_pages_with_metadata(file_path, ID_name):
    """
    Loads a file and extracts its pages along with metadata.

    Args:
        file_path (str): Path to the file.
        ID_name (str): Identifier based on the file name.

    Returns:
        pd.DataFrame: DataFrame with the extracted data.

    Example:
        df = split_pages_with_metadata('/path/to/file.pdf', 'file_id')
        print(df)
    """
    try:
        loader = UnstructuredFileLoader(
            file_path,
            mode="paged",
            strategy="fast"
        )
        data = loader.load()
        data_list = []
        for page_number, item in enumerate(data):
            page_content = " ".join(item.page_content.split())
            source = ID_name
            last_modified = item.metadata.get("last_modified", "N/A")
            page_id = f"{ID_name} {page_number + 1}"
            # Append the extracted data to a list with a unique ID for each page
            data_list.append({
                "ID": page_id,  # Unique identifier for each page
                "Content": page_content,
                "Metadata": f"Source: {source}, Page: {page_number + 1}, Last Modified: {last_modified}"
            })
        return pd.DataFrame(data_list)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return pd.DataFrame()

def create_chunks_with_unique_ids(doc_df, text_splitter):
    """
    Splits document content into chunks and assigns unique IDs.

    Args:
        doc_df (pd.DataFrame): DataFrame with document data.
        text_splitter (RecursiveCharacterTextSplitter): Text splitter instance.

    Returns:
        pd.DataFrame: DataFrame with chunked content and unique IDs.

    Example:
        chunks = create_chunks_with_unique_ids(doc_df, text_splitter)
        print(chunks)
    """
    chunks = []
    for _, row in doc_df.iterrows():
        content = row['Content']
        content_chunks = text_splitter.split_text(content)
        doc_id = row['ID']
        for chunk_index, chunk_content in enumerate(content_chunks, start=1):
            chunk_id = f"{doc_id} - Chunk {chunk_index}"
            chunks.append({
                'Chunk_ID': chunk_id,
                'Content': chunk_content,
                'Metadata': row['Metadata']
            })
    return pd.DataFrame(chunks)

def process_documents(filenames, chunk_size, chunk_overlap):
    """
    Processes files and returns a dataframe

    Args:
        filenames (pd.DataFrame): DataFrame with filenames and paths.

    Returns:
        pd.DataFrame: DataFrame with processed and chunked content.

    Example:
        filenames = get_filenames('/path/to/directory')
        processed_data = process_documents(filenames)
        print(processed_data)
    """
    recursive_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    total_doc_df = pd.DataFrame()
    n = len(filenames)
    for i, row in filenames.iterrows():
        print(f"---working on document {i+1}/{n}: {row['path']}---")
        doc_df = split_pages_with_metadata(row['path'], row['name'])
        doc_df['Content'] = doc_df['Content'].apply(group_broken_paragraphs)
        doc_df = create_chunks_with_unique_ids(doc_df, recursive_text_splitter)
        total_doc_df = pd.concat([total_doc_df, doc_df], ignore_index=True)
    return total_doc_df

def parse_metadata(metadata_str):
    """Transforms relevant data from a Dataframe column into a dict format for better compatibility with chroma
    Args:
        metadata_str (pandas.Dataframe -> str): column of a dataframe

    Returns:
        pandas.Dataframe -> str: column in a dict format
    """
    metadata_dict = {}
    if pd.notna(metadata_str):
        # Assuming metadata is a string formatted as "key: value, key: value"
        for part in metadata_str.split(", "):
            if ": " in part:
                key, value = part.split(": ", 1)
            else:
                # not formated as a key value pair -> return dummy key and value
                key, value = ("None", "")
            metadata_dict[key.strip()] = value.strip()
    return metadata_dict

def separate_for_indexing(processed_docs):
    """
    Prepares documents and metadata for indexing.

    Args:
        processed_docs (pd.DataFrame): DataFrame containing document data.

    Returns:
        tuple: Tuple containing lists of documents ids, and metadata.

    Example:
        texts, ids, metadatas = separate_for_indexing(processed_docs)
        print(texts, ids, metadatas)
    """
    texts = processed_docs[['Content']].apply(lambda x: ' '.join(x.dropna().values.tolist()), axis=1).tolist() 
    ids = processed_docs[['Chunk_ID']].apply(lambda x: ' '.join(x.dropna().values.tolist()), axis=1).tolist()
    metadatas = processed_docs["Metadata"].tolist()
    return texts, ids, metadatas


def separate_for_BM25(processed_docs):
    """
    Prepares documents and metadata for indexing with the BM25 retriever.

    Args:
        processed_docs (pd.DataFrame): DataFrame containing document data.

    Returns:
        corpus_with_metadata: List of dictionaries containing text and metadata for the documents.

    Example:
        corpus_with_metadata = separate_for_BM25(processed_docs)
        print(corpus_with_metadata)
    """
    corpus_with_metadata = processed_docs[['Content', 'Metadata']].rename(
        columns={'Content': 'text', 'Metadata': 'metadata'}).to_dict(orient='records')
    return corpus_with_metadata