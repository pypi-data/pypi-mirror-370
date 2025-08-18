import logging
import openai
from retrying import retry
from . import config
import os
from . import utils

class Azure:
    """
    A class to interact with Azure's OpenAI APIs in a manner similar to Apollo.
    Usage example:
        from tangbao.azure import Azure
        azure = Azure()
        response = azure.chat_completion(messages=[{"role": "user", "content": "Hello, Azure!"}])
        print(azure.get_content(response))
    """

    class AzureOpenAI(openai.AzureOpenAI):
        """
        A subclass to manage Azure-specific OpenAI client initialization.
        """
        def __init__(self, base_url: str, api_key: str, version: str):
            super().__init__(
                azure_endpoint=base_url,
                api_key=api_key,
                api_version=version
            )

    def __init__(self):
        # Define required environment variables
        self.REQUIRED_VARS = [
            "AZURE_BASE_URL", 
            "AZURE_API_KEY", 
            "AZURE_DEPLOYMENT_VERSION", 
            "AZURE_DEPLOYMENT_NAME"
        ]

        # Load and validate environment variables
        self.env_vars = config.load_and_validate_env_vars(self.REQUIRED_VARS)

        # Set up logging
        self.logger = logging.getLogger('tangbao.azure')
        self.logger.setLevel(logging.ERROR)

        # Prevent propagation to root logger
        self.logger.propagate = False

        # Create file handler
        log_file = getattr(config, 'LOG_FILE', 'azure.log')
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.ERROR)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add handler to logger if it doesn't already have one
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # Initialize private variables
        self._client = None
        self._model_deployment = self.env_vars["AZURE_DEPLOYMENT_NAME"]
        self._embedding_model_deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
        self._context_window = 128000

    @property
    def client(self):
        """
        Property that ensures the Azure OpenAI client is always valid when accessed.
        """
        if self._client is None:
            self._client = self.AzureOpenAI(
                base_url=self.env_vars["AZURE_BASE_URL"],
                version=self.env_vars["AZURE_DEPLOYMENT_VERSION"],
                api_key=self.env_vars["AZURE_API_KEY"]
            )
        return self._client

    def chat_completion(self, messages, model=None, temperature=0.1, top_p=0.1, seed=None, max_tokens=4096, is_stream=False, **kwargs):
        """
        Send a chat completion request to Azure OpenAI's chat endpoint.

        Args:
            messages (list): List of dicts with keys 'role' and 'content'.
            model (str): Optional model deployment name, otherwise uses AZURE_DEPLOYMENT_NAME.
            temperature (float): Sampling temperature.
            top_p (float): Top-p sampling parameter.
            seed (int): Random seed for deterministic outputs (if supported).
            max_tokens (int): Maximum tokens for output.
            is_stream (bool): Whether or not to stream responses.

        Returns:
            openai.types.ChatCompletion or openai.types.Stream (depending on is_stream).
        """
        try:
            deployment_name = model if model else self._model_deployment
            if deployment_name.startswith("o1"):
                return self.client.chat.completions.create(
                    model=deployment_name,
                    messages=messages,
                    seed=seed,
                    max_completion_tokens=max_tokens,
                    stream=is_stream,
                    **kwargs
                )
            else:
                return self.client.chat.completions.create(
                    model=deployment_name,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    seed=seed,
                    max_tokens=max_tokens,
                    stream=is_stream,
                    **kwargs
                )
        except Exception as e:
            self.logger.error(f"Chat completion request failed: {e}")
            raise

    def get_content(self, response):
        """
        Extracts content from an Azure OpenAI-style chat response.
        Returns the full content as a string for both streaming and non-streaming responses.

        Args:
            response: Either a ChatCompletion or Stream response from Azure OpenAI

        Returns:
            str: The complete response content
        """
        return utils.get_content(response)
    
    def get_token_usage(self, response):
        """
        Extract token usage from an Azure OpenAI-style response.

        Note: For streaming responses, usage isn't directly available in each chunk.
        """
        if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
            return response.usage.total_tokens
        return 0

    @retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def get_embeddings(self, texts, model=None, encoding_format='float', **kwargs):
        """
        Get embeddings for provided texts from Azure OpenAI.

        Args:
            texts (str or list): Text(s) to embed.
            model (str): Optional model deployment name, otherwise uses the default environment variable.
            encoding_format (str): Encoding for embeddings, e.g., 'float' for float array.

        Returns:
            openai.types.CreateEmbeddingResponse
        """
        try:
            if isinstance(texts, str):
                texts = [texts]  # Ensure it's a list

            deployment_name = model if model else self._embedding_model_deployment
            return self.client.embeddings.create(
                model=deployment_name,
                input=texts,
                encoding_format=encoding_format,
                **kwargs
            )
        except Exception as e:
            self.logger.error(f"Embedding request failed: {e}")
            raise

    def get_monthly_costs(self):
        """
        Placeholder for retrieving monthly costs from Azure (not standardized).
        """
        raise NotImplementedError("Azure monthly costs endpoint not implemented.")

    def get_model_info(self):
        """
        Placeholder method to fetch model info from Azure.
        """
        raise NotImplementedError("Azure model info endpoint not implemented.")

    def iam(self):
        """
        Placeholder method to demonstrate user identity retrieval on Azure.
        """
        raise NotImplementedError("IAM retrieval not implemented in Azure.")

    def index_multi_threaded(self, texts, ids, metadatas, index_name, embedding_model=None, dimensions=512, max_workers=8):
        """
        Placeholder for multi-threaded indexing in Azure.
        If you build a similar vector indexing pipeline for Azure, adapt here.
        """
        raise NotImplementedError("Multi-threaded indexing not implemented in Azure.")

    def query_index(self, user_query, num_chunks, index_name, embedding_model=None, dimensions=512):
        """
        Placeholder for indexing queries in Azure.
        """
        raise NotImplementedError("Index querying not implemented in Azure.")

    def parse_log_file(self, log_file):
        """
        Simple log parsing for error lines, if needed.
        """
        return utils.parse_log_file(log_file)

    def clear_log_file(self, log_file):
        """
        Clear an existing log file's contents.
        """
        utils.clear_log_file(log_file)

    def resubmit_failed_chunks(self, log_file, texts, ids, metadatas, index_name, embedding_model, max_workers=8):
        """
        Placeholder for resubmitting failed chunks in Azure.
        Intended for usage once indexing is implemented.
        """
        raise NotImplementedError("Resubmitting failed chunks not implemented in Azure.")