from sentence_transformers import CrossEncoder

class ReRanker:
    """
    A class to rerank retrieved documents based on a given query using a cross-encoder model.

    Attributes
    ----------
    cross_encoder_model : CrossEncoder
        An instance of the CrossEncoder model used for reranking. The model is taken from the sentence-transformers library.
    
    Methods
    -------
    rerank(query: str, retrieved_docs: list, top_k: int=None, threshold: float=None) -> list
        Reranks the retrieved documents based on the given query. 
        Returns a list of the top_k reranked documents after applying the specified threshold.
    """
    def __init__(self, model_name: str="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the ReRanker with the specified cross-encoder model.

        Parameters
        ----------
        model_name : str, optional
            The name of the cross-encoder model to use for reranking.
            The default model is "cross-encoder/ms-marco-MiniLM-L-6-v2".
            An alternative, more powerful and supporting multi-language queries, is "BAAI/bge-reranker-v2-m3".
            Please check https://www.sbert.net/docs/cross_encoder/pretrained_models.html#community-models for additional model recommendations.
        """
        self.cross_encoder_model = CrossEncoder(
            model_name=model_name,
            cache_dir="./models"
        )
        
    def rerank(self, query: str, retrieved_docs: list, top_k: int=None, threshold: float=None) -> list:
        """
        Reranks the retrieved documents based on the given query.

        Parameters
        ----------
        query : str
            The query string based on which the documents will be reranked.
        retrieved_docs : list
            A list of dictionaries representing the retrieved documents. Each dictionary should have a 'text' field containing the document text and a 'metadata' field containing additional information.
        top_k : int, optional
            The number of top documents to return after reranking (default is None, which returns all documents).
        threshold : float, optional
            The minimum score threshold for a document to be included in the reranked results (default is None, which includes all documents).

        Returns
        -------
        list
            A list of dictionaries representing the reranked documents. Each dictionary contains 'text', 'score', and 'metadata' fields.
        """
        # extract the "text" field from the passages
        passages = [doc['text'] for doc in retrieved_docs]
        # perform the reranking
        ranks = self.cross_encoder_model.rank(query, passages, top_k=top_k)
        # initialize a list to store the reranked documents after applying the threshold
        reranked_docs = []
        # loop through the ranks and apply the threshold
        for rank in ranks:
            if threshold is not None and rank['score'] < threshold:
                continue
            reranked_docs.append({
                "text": passages[rank['corpus_id']],
                "score": rank['score'],
                "metadata": retrieved_docs[rank['corpus_id']]['metadata']
            })

        return reranked_docs