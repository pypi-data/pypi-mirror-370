# tangbao

This is a Python package for building LLM-based applications in Boehringer. It provides utilities for document processing, RAG (Retrieval-Augmented Generation), and LLM integration.

"tangbao" is Chinese for "soup dumpling", a type of dim sum popular in Shanghai. It is made by filling a dumpling with meat and a mixture of ice and lard. When the dumpling steams, the frozen part melts and imparts the "tang" to the "bao". The word "bao" is also the name for a package or library in coding.

Contact [Steven Brooks](mailto:steven.brooks@boehringer-ingelheim.com) or [Pietro Mascheroni](mailto:pietro.mascheroni@boehringer-ingelheim.com) for feedback/support.

## For Users

### Installation

Everything below assumes you have a python venv already created. If you dont, then run

```bash
python -m venv .venv
source .venv/bin/activate
```

To install the package run `pip install tangbao`.

### Other dependencies

You might need to install additional dependencies based on the types of documents you plan to parse.

See the `unstructured` documentation here: https://pypi.org/project/unstructured/

In this package, we only install the minimal dependencies necessary.

### Configuration

This project requires certain environment variables to be set. These variables are used for connecting to external APIs and services.

1. Create a `.env` file in the root directory of the project.
2. Add the following content to the `.env` file, replacing placeholder values with your actual credentials:

#### Apollo

```env
APOLLO_CLIENT_ID=your_client_id
APOLLO_CLIENT_SECRET=your_client_secret
APOLLO_BASE_URL=https://api-mgmt.boehringer-ingelheim.com:8065/apollo
# Optional: Set this to your index name if you want to use the RAG functionality, see below for more details
INDEX_NAME=your_index_name
```
To obtain the client id and client secret, please refer to the [guide](https://boehringer.sharepoint.com/sites/z365apollocontrolcenter/SitePages/Marketplace.aspx) in the apollo website. We recommend starting from the "Experimentation Use Case" route for new projects. 

**Important**: New Apollo API keys (Apollo v2) require you to set the `APOLLO_BASE_URL` environment variable. If you have an existing API key created in Apollo v1, this variable is optional and the package will use the default URL for backwards compatibility. *If you're using Apollo v2, many of the methods are not working yet, notably the RAG functionality. We are working on it.*

Once that is set, you can use the chat completions as follows:

```python
from tangbao.apollo import Apollo

# Initialize the client
apollo = Apollo()

# Simple chat completion
messages = [{"role": "user", "content": "Hello, Apollo!"}]
response = apollo.chat_completion(messages=messages)
print(apollo.get_content(response))

# Chat completion with parameters
response = apollo.chat_completion(
    messages=messages,
    model="gpt-4o",
    temperature=0.7,
    top_p=0.1,
    seed=42,
    max_tokens=100,
    is_stream=False
)
```

There are also several other methods that can be used:

```python
from tangbao.apollo import Apollo

apollo = Apollo()

# Get the model info
model_info = apollo.get_model_info()
print(model_info)

# Get token usage
messages = [{"role": "user", "content": "Hello, Apollo!"}]
response = apollo.chat_completion(messages=messages)
print(apollo.get_token_usage(response))

# Get customer info like total expenditures
apollo.get_customer_info()

# Retrieve your registered use case ID
apollo.iam()
```

#### Azure

The Azure class provides an interface to Azure OpenAI services that mirrors the Apollo interface. Here's how to use it:

1. First, ensure you have the required environment variables in your `.env` file:

```env
AZURE_BASE_URL=your_azure_endpoint
AZURE_API_KEY=your_azure_api_key
AZURE_DEPLOYMENT_VERSION=your_api_version
AZURE_DEPLOYMENT_NAME=your_deployment_name
AZURE_EMBEDDING_DEPLOYMENT_NAME=your_embedding_deployment_name  # Optional, for embeddings
```

2. Basic usage for chat completions:

```python
from tangbao.azure import Azure

# Initialize the client
azure = Azure()

# Simple chat completion
messages = [{"role": "user", "content": "Hello, Azure!"}]
response = azure.chat_completion(messages=messages)
print(azure.get_content(response))

# Chat completion with parameters
response = azure.chat_completion(
    messages=messages,
    model="GPT-4o",
    temperature=0.7,
    top_p=0.1,
    seed=42,
    max_tokens=100,
    is_stream=False
)
```
**Note**: If `model="o1"` or `model="o1-mini"`, then temperature must be set to `1`, and top_p must be set to `None`. 

As with Apollo, the same methods are available for the Azure class for getting model info, token usage, and monthly costs.

#### Embedding Endpoint

Whether you're using Azure or Apollo, you can use the same syntax to get embeddings.

```python
# Get embeddings for a single text
embeddings = azure.get_embeddings("Hello, world!") # you can also use apollo.get_embeddings("Hello, world!")

# Get embeddings for multiple texts
texts = ["Hello, world!", "Another text"]
embeddings = azure.get_embeddings(texts) # you can also use apollo.get_embeddings(texts)
```

**Note**:The Azure class supports different model deployments through the `model` parameter in both `chat_completion` and `get_embeddings` methods. If not specified, it uses the deployment name from your environment variables.

### RAG Workflow

- [Step 1: Parse Documents](#step-1-parse-documents)
- [Step 2: Index the RAG Database](#step-2-index-the-rag-database)
- [Step 3: Build a Streamlit App](#step-3-build-a-streamlit-app)

#### Step 1: Parse Documents

**Note:** This guide, and all following guides assume you've set up your environment properly. See above for instructions.

Before we can build the RAG, we need to parse the documents. This package provides functions to make that easier.

**IMPORTANT**: PDF images are not be parsed with the current release.

We provide a basic chunking strategy, i.e., unstructured chunking. This means that meta-information such as the chapter or section level is missed when chunking the documents.

Two parameters control the chunking structure:

- CHUNK_SIZE: controls the maximum number of characters in one text chunk
- CHUNK_OVERLAP: controls the characters that overlap between following chunks.

The chunk size controls the granularity in which the text is divided: small chunks provide very specific, almost keyword based, matches to the query.
Larger chunks allow to grasp more context and subtle meaning of the text.

To start with, we suggest to go for CHUNK_SIZE = 500, CHUNK_OVERLAP = 0. From our experiments, these values provide a good starting point for many situations.

The following is a simple example to setup a parsing strategy. Please follow these steps:

1. Store PDF documents in a folder named `./documents`
2. Create a script like the following:

```python
from tangbao import parse_docs

CHUNK_SIZE = 500
CHUNK_OVERLAP = 0

filenames_df = parse_docs.get_filenames("./documents")
processed_docs = parse_docs.process_documents(filenames_df, CHUNK_SIZE, CHUNK_OVERLAP)
processed_docs["Metadata"] = processed_docs["Metadata"].apply(parse_docs.parse_metadata)
# Save file for the next step
processed_docs.to_parquet(f'my_docs_cs_{CHUNK_SIZE}_co_{CHUNK_OVERLAP}.parquet')
```

#### Step 2: Index the RAG Database

After we've parsed the documents in Step 1, we can index the RAG's vector database with the
document chunks and metadata.

1. Make sure to use the same CHUNK_SIZE and CHUNK_OVERLAP values from the previous step.
2. Make sure you have the `.parquet` file in your working directory.
3. The INDEX_NAME should have the following format: `app-id_your-index-name`. 
The `app-id` for your use case can be retrieven by following the code snippet below. 
For the index name, consider that it can have underscores, dashes, numbers and lower-case characters only. 
**Note**: The index name scheme for Apollo is set to be changed soon, so this code will need to be updated.

**IMPORTANT**: It is very important that you keep your index name a secret so others won't overwrite it with their documents. 
Consider using an environment variable for this, similar to how we treat an API Key. Another level of assurance that no one 
will overwrite your index with their documents would be to generate a unique index name, e.g., with

```python
import uuid
from tangbao.apollo import Apollo
your_index_name = str(uuid.uuid4()) # can only include lower case alpha-numeric, underscores, and dashes
apollo = Apollo()
iam = apollo.iam()
app_id = iam["id"]
INDEX_NAME=f'{app_id}_{your_index_name}'
```
But then just remember to record this index name in your `.env` for use later on. If you call it `INDEX_NAME`, then
you can call on it with e.g., `os.getenv("INDEX_NAME")`.

4. Index the RAG DB. This can be done following a similar script:

```python
from tangbao.apollo import Apollo
from tangbao.parse_docs import separate_for_indexing
from tangbao import config
import pandas as pd
import os

# use the same values from Step 1
CHUNK_SIZE = 500 
CHUNK_OVERLAP = 0
PARQUET_FILE = f'my_docs_cs_{CHUNK_SIZE}_co_{CHUNK_OVERLAP}.parquet'
INDEX_NAME = os.getenv("INDEX_NAME")
EMBEDDING_MODEL = "openai-text-embedding-3-large" # you can see other embedding models with apollo.get_model_info()
processed_docs = pd.read_parquet(PARQUET_FILE, engine='pyarrow')
texts, ids, metadatas = separate_for_indexing(processed_docs)

# this can take a long time to run, depending on how many documents you have
apollo.index_multi_threaded(
    texts=texts, 
    ids=ids,
    metadatas=metadatas, 
    index_name=INDEX_NAME,
    embedding_model=EMBEDDING_MODEL,
    max_workers=8
)
```
If there are any failures in indexing doc chunks, they will be written to a log file. You can resubmit those chunks using this method:

```python
if os.path.exists(config.LOG_FILE):
    apollo.resubmit_failed_chunks(
        log_file=config.LOG_FILE, 
        texts=texts, 
        ids=ids, 
        metadatas=metadatas, 
        index_name=INDEX_NAME, 
        embedding_model=EMBEDDING_MODEL,
        max_workers=8
    )
```
After the indexing is completed, it is possible to query the RAG dataset with a test question.
This can be accomplished using the following script:

```python
apollo.query_index(
    user_query="YOUR QUERY HERE",
    num_chunks=5,
    index_name=INDEX_NAME,
    embedding_model=EMBEDDING_MODEL
)
```

##### Alternative Retrievers 

It is possible to also use alternative retrievers. To use a BM25 retriever (keyword based), follow this code. The vector store will be created in memory, so it will be necessary to index the documents inside the app.

```python
from tangbao.parse_docs import separate_for_BM25
from tangbao.retrievers import BM25Retriever

# parse the documents according to the structure needed for BM25 
documents = separate_for_BM25(processed_docs)

# create an instance of the BM25Retriever class
bm25_retriever = BM25Retriever(documents)

# index the corpus
bm25_retriever.index_corpus()

# query the corpus
output = bm25_retriever.query_corpus("YOUR QUERY HERE")
print(output)
```

It is also possible to call a hybrid retrieval that combines keyword-based and semantic searches. This is supported by the class `HybridRetrieverApollo` that combines a BM25 retriever with the vector database from apollo. Note that this requires the documents to be already indexed in the apollo vector store before performing the search (see step 4 above).

```python
from tangbao.retrievers import HybridRetrieverApollo

INDEX_NAME = os.getenv("INDEX_NAME") # the index name used during indexing
EMBEDDING_MODEL = "openai-text-embedding-3-large" # the embedding model used during indexing

# define a sample query
sample_query = "YOUR QUERY HERE"

# initialize the retriever with the pandas dataframe that was used during indexing
hybrid_retriever = HybridRetrieverApollo(processed_docs, INDEX_NAME, EMBEDDING_MODEL)

# query the BM25 and apollo indices
combined_scores = hybrid_retriever.query_indices(sample_query, num_chunks=2)

# print the sorted documents and their scores
for doc in combined_scores:
    print(f'{doc["text"]}: {doc["rank"]:.4f}, metadata: {doc["metadata"]}')
```
Note that it is also possible to assign a weight to the importance of keyword-based retrieval (relative to embedding-based).

```python
# example usage with keyword weight
combined_scores = hybrid_retriever.query_indices(sample_query, num_chunks=2, keyword_weight=0.1)

# print the sorted documents and their scores
for doc in combined_scores:
    print(f'{doc["text"]}: {doc["rank"]:.4f}, metadata: {doc["metadata"]}')
```
The weight controls the importance that is given to keyword-based retrieval when ranking the documents in the hybrid search.
If the user is looking for very specific terms, than it would make sense to impose more weight to keyword-based retriever.
On the other hand, if the user is unsure about the content and wordings that are present in the documents, then it is possible to assign more freedom in the search by selecting a lower weight. By default, an equal weight is assigned to both keyword- and embedding-based retrievers.

We also support an in-memory retriever from [LangChain](https://python.langchain.com/docs/introduction/). This is convenient for relatively small documents that don't have to be stored between sessions (the in-memory retriever will indeed be erased when the application or notebook is closed). It performs a similarity search in the embedding space using cosine similarity (please see the full details at this [link](https://python.langchain.com/api_reference/core/vectorstores/langchain_core.vectorstores.in_memory.InMemoryVectorStore.html).)
Here is a code snippet that shows how to initialize the retriever and use it for a simple query:

```python
from tangbao.parse_docs import separate_for_indexing
from tangbao.retrievers import ApolloEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

# pre-process the documents in the format required for indexing
texts, ids, metadatas = separate_for_indexing(processed_docs)

# initialize the embedding model to be used with LangChain
embeddings = ApolloEmbeddings(model="openai-text-embedding-3-large", dimensions=3072)

# index the text chunks and their metadata in the vector store
vectorstore = InMemoryVectorStore.from_texts(
    texts=texts,
    embedding=embeddings,
    ids=ids,
    metadatas=metadatas,
)

# use the vectorstore as a retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# retrieve the most similar chunks
retrieved_documents = retriever.invoke("YOUR QUERY HERE")

# show the retrieved documents
for doc in retrieved_documents:
    print(doc.page_content)
```
Note that it is also possible to use a hybrid retriever that combines the in-memory embedding-based retrieval with keyword-based search. This is implemented through the class `HybridRetrieverInMemory`. See the following code snippet:

```python
from tangbao.retrievers import HybridRetrieverInMemory

# define a sample query
sample_query = "YOUR QUERY HERE"

# initialize the retriever with the pandas dataframe that was used during indexing
hybrid_retriever = HybridRetrieverInMemory(processed_docs, emb_model="openai-text-embedding-3-large", emb_dimensions=3072)

# query the BM25 and apollo indices
combined_scores = hybrid_retriever.query_indices(sample_query, num_chunks=2, keyword_weight=0.2)

# print the sorted documents and their scores
for doc in combined_scores:
    print(f'{doc["text"]}: RANK {doc["rank"]:.4f}, metadata: {doc["metadata"]}')
```

##### Reranking of retrieved documents

To improve the outcome of retrieval, it is possible to add a reranking step that improves the match between the user query and the retrieved chunks. This is supported through the `ReRanker` class and works for all the supported retrieval frameworks (keyword-, embedding-based and hybrid). Here is a code snippet showing how to setup reranking for documents retrieved using the apollo vector database:

```bash
pip install tangbao[rerank] # installs torch and sentence-transformers for reranking
```

```python
from tangbao.retrievers import extract_docs_from_apollo_vs
from tangbao.rerankers import ReRanker

# define a sample user query
example_user_query = "YOUR QUERY HERE"

# query the apollo vector database
response_apollo_query_index = apollo.query_index(
    user_query=example_user_query,
    num_chunks=5,
    index_name=INDEX_NAME,
    embedding_model=EMBEDDING_MODEL
)

# reformat the retrieved chunks for further processing
example_docs_retrieved = extract_docs_from_apollo_vs(response_apollo_query_index)

# initialize the reranker with the default options
reranker = ReRanker()

# rerank the documents with the default options
reranker.rerank(example_user_query, example_docs_retrieved)
```

**NOTE**: the re-formatting of the retrieved chunks is not needed for BM25 and hybrid retrieval, since the output of these methods is already compatible with the `ReRanker` class. For documents retrieved using the in-memory retrieval strategy, the function `extract_docs_from_langchain_re` can be used to pre-process the documents before reranking. Check the docs of `ReRanker` by typing `help(ReRanker)` for additional reranking options.

Apollo also offers reranking as a service. Please check [this link](https://boehringer.sharepoint.com/:u:/r/sites/z365apollocontrolcenter/SitePages/3.2.4-Re-Rank-Guide.aspx?csf=1&web=1&e=4hb4qi) for more information.

#### Step 3: Build a Streamlit App (Optional Example)

This is an example of how to build a chat interface using Streamlit. First, install Streamlit:

```bash
pip install streamlit==1.31.0
```

Now that we have indexed our documents in the RAG database, we can build a Streamlit
app to let users 'chat' with the document store.

To create the app, follow these steps:

1. Make sure you have the INDEX_NAME from the previous step
2. Create a file called `app.py` and use the following template. Make sure to change the custom prompt below if needed!
Changing the prompt is a crucial step to assure that the generation phase of the RAG conforms to your specific use case.
Invest some time in prompt engineering, to get the best out of the LLM used to generate the answers to the user queries.

#### Compliance

**Important!**

It is important that your users are aware of the usage guidelines of using AI and LLMs at Boehringer Ingelheim. This can be done by rendering a modal on app startup, displaying a dropdown in the sidebar, or both. In the example below, we do both, but you can choose one or the other. 

Import the `ui` module to render the usage guidelines (install the `ui` optional dependency with `pip install tangbao[ui]`).

You can also render a prototype banner to inform users that the application is a prototype.

```python
import streamlit as st
import pandas as pd
from tangbao import utils
from tangbao.apollo import Apollo
from tangbao import ui # run `pip install tangbao[ui]` to install this
import os

INDEX_NAME = os.getenv("INDEX_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") # make sure its the same one you used for indexing above!

st.title("Chat with Docs")

ui.render_prototype_banner()

USAGE_GUIDELINES = ui.get_usage_guidelines(
   main_purpose="allow users to chat with BDS documents",
   business_process="preparing for a regulatory submission"
)

if not ui.render_guidance_modal(USAGE_GUIDELINES):
    st.stop()

with st.sidebar:
    ui.render_guidance_dropdown(USAGE_GUIDELINES)

# Define Session State
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

if "used_tokens" not in st.session_state:
   st.session_state.used_tokens = 0

# Display chat messages  
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

apollo = Apollo()

@st.cache_data
def cached_model_info(_apollo_client):
   return _apollo_client.get_model_info()

model_info = cached_model_info(apollo)
chat_models = [model["model_name"] for model in model_info if model["model_info"]["mode"] == "chat"]

# Define Sidebar
with st.sidebar:
   selected_model = st.selectbox("Select LLM:", chat_models)
   CONTEXT_WINDOW = [model['model_info']['max_input_tokens'] for model in model_info if model['model_name'] == selected_model][0]
   token_display = st.empty()
   with token_display.container():
      st.progress(st.session_state.used_tokens/CONTEXT_WINDOW, text = f"Context window used ({st.session_state.used_tokens} out of {CONTEXT_WINDOW})")
   temperature = st.slider("Select model creativity (temperature)", min_value=0.0, max_value=1.0, value = 0.0)
   chunk_num = st.slider("Select number of chunks", min_value=1, max_value=8, value=4)

# User Input
if user_query := st.chat_input("Ask a question"):
   st.session_state.messages.append({"role": "user", "content": user_query})
   with st.chat_message("user"):
      st.markdown(user_query)

if st.session_state.messages[-1]["role"] != "assistant":  
   # RAG Output
   with st.chat_message("assistant"):
      with st.spinner("Thinking..."):
        context = apollo.query_index(user_query, chunk_num, INDEX_NAME)
        #### ADAPT THE FOLLOWING PROMPT TO YOUR SPECIFIC NEEDS ####
        prompt = f"""\
            Use the following CONTEXT delimited by triple backticks to answer the QUESTION at the end.
            
            If you don't know the answer, just say that you don't know.
            
            Use three to five sentences and keep the answer as concise as possible.
            
            You are also a language expert, and so can translate your responses to other languages upon request.
            
            CONTEXT: ```
            {context['docs']}
            ```

            QUESTION: ```
            {user_query}
            ```

            Helpful Answer:"""
        
        response_full = apollo.chat_completion(
            messages=[{'role': 'user', 'content': prompt}] + 
            [{'role': m['role'], 'content': m['content']} for m in st.session_state.messages],
            model=selected_model,
            temperature=temperature,
            seed=42,
            is_stream=False
        )
        
        response = apollo.get_content(response_full)
        st.session_state.used_tokens = apollo.get_token_usage(response_full)
        st.write(response)

        with st.sidebar:
            with token_display.container():
                st.progress(st.session_state.used_tokens/CONTEXT_WINDOW, text = f"Context window used ({st.session_state.used_tokens} out of {CONTEXT_WINDOW})")
            sources, titles = utils.extract_source(context)
            st.header("Sources:")
            st.table(pd.DataFrame({"Documents referenced": titles}))
            st.markdown(sources, unsafe_allow_html=True)
    
        st.session_state.messages.append({"role": "assistant", "content": response})
```

Then run `streamlit run app.py` to see if it works!

## For Developers

### Testing

```bash
pip install -e .
```

The `-e` flag in `pip install -e .` installs the package in "editable" mode, which means:
- Changes you make to the source code will be reflected immediately without reinstalling
- The package will be available in your Python environment just like a normal installed package
- You can import it with `import tangbao` in your scripts

For unit testing, we'll use the `pytest` framework.

```bash
source .venv/bin/activate
python -m pytest tests/
```

### Build

```bash
source .venv/bin/activate
pip install -e .
pip install --upgrade build wheel bumpversion
bumpversion patch # or major or minor
rm -rf dist
python -m build
```

### Upload to PyPI

Requires a PyPI API Token. Get one at https://pypi.org

Set the token in your environment as `TWINE_PASSWORD`

```bash
source .venv/bin/activate
pip install --upgrade twine
twine upload --repository pypi dist/*
```
