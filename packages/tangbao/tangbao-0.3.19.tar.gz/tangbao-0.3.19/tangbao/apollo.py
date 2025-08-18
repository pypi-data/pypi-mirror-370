from . import config
from . import utils
import logging
import requests
import openai
from concurrent.futures import ThreadPoolExecutor
from retrying import retry
import time
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
from httpx_auth import OAuth2ClientCredentials
import httpx

class Apollo:
    
    class ApolloOpenAI(openai.OpenAI):
        def __init__(self, client_id: str, client_secret_str, token_url: str, base_url: str, cert_path: str):
            # Create a custom httpx client with our certificate
            self._cert_path = cert_path
            self._http_client = httpx.Client(verify=self._cert_path)
            
            # Configure OAuth with our custom client
            self._apollo_credentials = OAuth2ClientCredentials(
                client_id=client_id,
                client_secret=client_secret_str,
                token_url=token_url,
                client=self._http_client  # Use our configured client
            )
            
            # Initialize OpenAI with our certificate
            super().__init__(
                api_key=self._apollo_credentials.request_new_token(), 
                base_url=base_url,
                http_client=self._http_client  # Use the same httpx client
            )

        def __del__(self):
            if hasattr(self, '_http_client'):
                self._http_client.close()

        @property
        def custom_auth(self) -> OAuth2ClientCredentials:
            return self._apollo_credentials
    
    def __init__(self):
        # Get the certificate path relative to this file
        self._cert_path = os.path.join(os.path.dirname(__file__), 'certs', 'apimgmt.crt')
        
        # Set up logging
        # Set up dedicated logger for tangbao
        self.logger = logging.getLogger('tangbao.apollo')
        self.logger.setLevel(logging.ERROR)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        # Create file handler
        handler = logging.FileHandler(config.LOG_FILE)
        handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to logger if it doesn't already have one
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        # Define required environment variables
        self.REQUIRED_VARS = [ 
            "APOLLO_CLIENT_ID", "APOLLO_CLIENT_SECRET"
            # Removed REQUESTS_CA_BUNDLE as we're using explicit cert path
        ]
        
        # Load and validate environment variables
        self.env_vars = config.load_and_validate_env_vars(self.REQUIRED_VARS)
        
        # Initialize private variables
        self._client = None
        self._token_data = {
            'access_token': None,
            'expiry_time': -1
        }
        self._token_url = "https://api-mgmt.boehringer-ingelheim.com:8065/api/oauth/token"
        # Use APOLLO_BASE_URL environment variable if provided, otherwise use default
        self._base_url = os.getenv("APOLLO_BASE_URL", "https://api-mgmt.boehringer-ingelheim.com:8065/apollo")
        self._api_headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    @property
    def token(self):
        """Property that ensures the token is always valid when accessed"""
        current_timestamp = int(time.time())
        if (self._token_data['access_token'] is None or 
            current_timestamp >= self._token_data['expiry_time']):
            self._refresh_token()
        return self._token_data['access_token']

    def _refresh_token(self):
        """Private method to handle token refresh"""
        client = BackendApplicationClient(client_id=self.env_vars['APOLLO_CLIENT_ID'])
        # Create session with explicit cert verification
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url=self._token_url,
            client_id=self.env_vars['APOLLO_CLIENT_ID'],
            client_secret=self.env_vars['APOLLO_CLIENT_SECRET'],
            verify=self._cert_path  # Add this line to use our certificate
        )
        self._token_data['access_token'] = token['access_token']
        self._token_data['expiry_time'] = int(time.time()) + token['expires_in'] - 30

    @property
    def client(self):
        """Property that ensures the client is always valid when accessed"""
        if self._client is None:
            self._client = self._initialize_client()
        return self._client

    def _initialize_client(self):
        """Initialize the OpenAI client with the Apollo configuration"""
        return self.ApolloOpenAI(
            client_id=self.env_vars["APOLLO_CLIENT_ID"],
            client_secret_str=self.env_vars["APOLLO_CLIENT_SECRET"],
            token_url=self._token_url,
            base_url=self._base_url if self._base_url.endswith("/llm-api") else self._base_url + "/llm-api",
            cert_path=self._cert_path  # Pass the cert path to the client
        )
    
    # delete
    def get_content(self, response):
        """
        Extract content from an OpenAI-style response
        
        Returns:
            For non-streaming: content string
            For streaming: generator yielding content chunks
        """
        return utils.get_content(response)
    
    # delete
    def get_token_usage(self, response):
        """
        Extract token usage from an OpenAI-style response
        
        Returns:
            For non-streaming: total tokens used
            For streaming: None (token usage not available in streaming mode)
        """
        if type(response) != openai.Stream:
            return response.usage.total_tokens
        return 0
    
    # delete
    def chat_completion(self, messages, model="gpt-4o-mini", temperature=0.0, top_p=None, seed=None, is_stream=False, **kwargs):
        """
        Send a chat completion request to Apollo using OpenAI's chat format
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            model (str): Model to use (e.g., "gpt-4", "claude_2_1")
            temperature (float): Temperature for response generation
            max_tokens (int, optional): Maximum tokens in response
        
        Returns:
            openai.types.chat.ChatCompletion: OpenAI-style response
        """
        try:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                seed=seed,
                stream=is_stream,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Chat completion request failed: {e}")
            raise
    
    @retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def get_embeddings(self, texts, model="openai-text-embedding-3-large", dimensions=512, **kwargs):
        """
        Get embeddings for provided texts
        
        Args:
            texts (str or list): Text(s) to embed
            model (str): Embedding model to use
            dimensions (int): Dimensions of the embedding space
        
        Returns:
            openai.types.CreateEmbeddingResponse: OpenAI-style embedding response
        """
        try:
            # Ensure texts is a list
            if isinstance(texts, str):
                texts = [texts]
                
            return self.client.embeddings.create(
                model=model,
                input=texts,
                encoding_format="float",
              	dimensions=dimensions,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Embedding request failed: {e}")
            raise
    
    def get_customer_info(self):
        try:        
            if "/apollo" in self._base_url: # Apollo v2
                api_url = f'{self._base_url}/llm-api/customer/info'
            else:
                api_url = f'{self._base_url}/application/cost'
            response = requests.get(api_url, headers=self._api_headers, verify=self._cert_path)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get customer info: {e}")
            raise

    #delete
    @retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def get_model_info(self):
        try:
            api_url = f'{self._base_url}/llm-api/model/info' if "/apollo" in self._base_url else f'{self._base_url}/model/info'
            response = requests.get(
                api_url, 
                headers=self._api_headers,
                verify=self._cert_path
            )
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to get model info: {e}")
            raise
    
    def _index_chunk(self, text, text_id, metadata, index_name, embedding_model="openai-text-embedding-3-large", dimensions=512):
        if "/apollo" in self._base_url: # Apollo v2
            raise NotImplementedError("_index_chunk() is not available yet with Apollo v2")
        else:
            return self._index_chunk_v1(text, text_id, metadata, index_name, embedding_model, dimensions)

    @retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def _index_chunk_v1(self, text, text_id, metadata, index_name, embedding_model="openai-text-embedding-3-large", dimensions=512):
        """Helper method for indexing a single document chunk"""
        try:
            json_data = {
                "index_name": index_name,
                "embedding_model": embedding_model,
                "texts": [text],
                "metadatas": [metadata],
                "dimensions": dimensions
            }
            
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            print(f"Indexing chunk with metadata: {metadata}")
            response = requests.post(
                f"{self._base_url}/vector_search/index",
                headers=headers,
                json=json_data,
                verify=self._cert_path
            )
            response.raise_for_status()
            return f"Indexed chunk with metadata: {metadata}"
            
        except Exception as e:
            self.logger.error(f"Failed to index chunk with id {text_id}: {e}")
            raise

    def index_multi_threaded(self, texts, ids, metadatas, index_name, embedding_model="openai-text-embedding-3-large", dimensions=512, max_workers=8):
        """
        Add documents to an index using multiple threads.
        
        If the index does not exist, it will be created. The index name needs to begin with your 
        user ID followed by an underscore. Use the .iam method to find your user ID. Only lower-case 
        characters, hyphens and underscores are allowed.

        Please use the get_model_info() method to find the list of supported embedding models. 
        Only these models can be used with Apollo at the moment.

        Important: the index uses the embedding model specified in this request. Any subsequent request 
        to index more documents or query the index must use the exactly same model.
        
        Args:
            texts (list): List of texts to index
            ids (list): List of ids for each text
            metadatas (list): List of metadata dicts for each text
            index_name (str): Name of the index. Must begin with user ID followed by underscore.
            embedding_model (str): Model to use for embeddings. Must be supported by Apollo.
            dimensions (int): Dimensions of the embedding space. Should match the one used in the query stage.
            max_workers (int): Maximum number of concurrent threads
        
        Returns:
            list: List of indexing results
        
        Raises:
            ValueError: If inputs are invalid or mismatched
            Exception: If indexing request fails
        """
        if "/apollo" in self._base_url: # Apollo v2
            raise NotImplementedError("index_multi_threaded() is not available yet with Apollo v2")
        else:
            if len(texts) != len(metadatas):
                raise ValueError("Number of documents must match number of metadata entries")

            # Validate index name format
            if not index_name.islower() or any(c not in "-_" for c in index_name if not c.isalnum()):
                raise ValueError("Index name must contain only lowercase letters, hyphens, and underscores")
            
            # TODO - provide better print outs to user in console about what's happening
            print(f"Starting multi-threaded indexing with {max_workers} workers for {len(texts)} documents")
            
            with ThreadPoolExecutor(max_workers=min(len(ids), max_workers)) as executor:
                # Create iterables for map
                index_names = [index_name] * len(texts)
                embedding_models = [embedding_model] * len(texts)
                dimensions_list = [dimensions] * len(texts)
                
                # Map the indexing function across all documents
                futures = executor.map(
                    self._index_chunk,
                    texts,
                    ids,
                    metadatas,
                    index_names,
                    embedding_models,
                    dimensions_list
                )
                
                # Process results as they complete
                results = []
                for result in futures:
                    if result:
                        self.logger.info(result)
                        results.append(result)
                
                return results
        
    def query_index(self, user_query, num_chunks, index_name, embedding_model="openai-text-embedding-3-large", dimensions=512):
        if "/apollo" in self._base_url: # Apollo v2
            raise NotImplementedError("query_index() is not available yet with Apollo v2")
        else:
            return self.query_index_v1(user_query, num_chunks, index_name, embedding_model, dimensions)

    @retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def query_index_v1(self, user_query, num_chunks, index_name, embedding_model="openai-text-embedding-3-large", dimensions=512):
        """
        Queries the RAG system with a user query.

        Args:
            user_query (str): The query to send to the RAG system.
            num_chunks (int): Number of chunks to retrieve.
            dimensions (int): Dimensions of the embedding space. Should match the one used when creating embeddings.

        Returns:
            dict: The response from the RAG system.

        Example:
            response = query_rag("What is the capital of France?", 5)
            print(response)
        """
        json_data = {
            "dimensions": dimensions,
            "index_name": index_name,
            "embedding_model": embedding_model,
            "query": user_query,
            "num_neighbors": num_chunks
        }
        try:
            response = requests.post(
                f"{self._base_url}/vector_search/query", 
                headers=self._api_headers, 
                json=json_data,
                verify=self._cert_path
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Request failed for apollo.query_index: {e}")
            raise

    @retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def iam(self):
        """
        Get the user ID
        """
        try:
            response = requests.get(
                f"{self._base_url}/application/iam", 
                headers=self._api_headers,
                verify=self._cert_path
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get IAM: {e}")
            raise
    
    def parse_log_file(self, log_file): 
        return utils.parse_log_file(log_file)
    
    def clear_log_file(self, log_file):
        utils.clear_log_file(log_file)

    def resubmit_failed_chunks(self, log_file, texts, ids, metadatas, index_name, embedding_model, max_workers=8):
        """
        Resubmit failed chunks from a log file.
        """
        if "/apollo" in self._base_url: # Apollo v2
            raise NotImplementedError("resubmit_failed_chunks() is not available with Apollo v2")
        else:
            failed_chunks = self.parse_log_file(log_file)
            # Map document IDs to documents and metadata
            id_to_text = {id: doc for id, doc in zip(ids, texts)} 
            id_to_metadata = {id: meta for id, meta in zip(ids, metadatas)} 
            # Prepare lists for resubmission
            resubmit_texts = [] 
            resubmit_ids = [] 
            resubmit_metadatas = [] 

            for id in failed_chunks: 
                if id in id_to_text and id in id_to_metadata: 
                    resubmit_texts.append(id_to_text[id]) 
                    resubmit_metadatas.append(id_to_metadata[id]) 
                    resubmit_ids.append(id)
            if len(resubmit_texts):
                self.clear_log_file(log_file)
                # Resubmit failed chunks
                print("Resubmitting failed chunks")
                self.index_multi_threaded(
                    texts=resubmit_texts,
                    ids=resubmit_ids,
                    metadatas=resubmit_metadatas,
                    index_name=index_name,
                    embedding_model=embedding_model,
                    max_workers=min(len(resubmit_ids), max_workers)
                )
            else:
                print("Log file clean, no docs to resubmit!")
