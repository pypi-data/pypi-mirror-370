import pytest
from unittest.mock import Mock, patch
from tangbao.rerankers import ReRanker

@pytest.fixture
def mock_cross_encoder():
    with patch('tangbao.rerankers.CrossEncoder') as mock:
        # Configure the mock to return reasonable fake results
        instance = mock.return_value
        # Return different results based on input length
        def mock_rank(query, passages, top_k=None):
            if not passages:  # Handle empty input
                return []
            
            # Create base results
            results = [
                {'corpus_id': 0, 'score': 0.9},
                {'corpus_id': 1, 'score': 0.7},
                {'corpus_id': 2, 'score': 0.4}
            ]
            
            # If top_k is specified, return only that many results
            if top_k is not None:
                results = results[:top_k]
            
            return results
            
        instance.rank.side_effect = mock_rank
        yield mock

@pytest.fixture
def reranker(mock_cross_encoder):
    return ReRanker()

@pytest.fixture
def sample_docs():
    return [
        {
            'text': 'The quick brown fox jumps over the lazy dog.',
            'metadata': {'id': 1, 'source': 'test'}
        },
        {
            'text': 'A lazy dog sleeps all day long.',
            'metadata': {'id': 2, 'source': 'test'}
        },
        {
            'text': 'The fox is quick and brown.',
            'metadata': {'id': 3, 'source': 'test'}
        }
    ]

def test_reranker_initialization():
    with patch('tangbao.rerankers.CrossEncoder') as mock:
        # Test default model initialization
        reranker = ReRanker()
        mock.assert_called_once_with(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
            cache_dir="./models"
        )
        assert reranker.cross_encoder_model is not None
        
        # Test custom model initialization
        mock.reset_mock()
        custom_reranker = ReRanker("BAAI/bge-reranker-v2-m3")
        mock.assert_called_once_with(
            model_name="BAAI/bge-reranker-v2-m3",
            cache_dir="./models"
        )
        assert custom_reranker.cross_encoder_model is not None

def test_rerank_basic(reranker, sample_docs):
    query = "quick fox"
    results = reranker.rerank(query, sample_docs)
    
    assert len(results) == len(sample_docs)
    assert all(isinstance(doc, dict) for doc in results)
    assert all('text' in doc for doc in results)
    assert all('score' in doc for doc in results)
    assert all('metadata' in doc for doc in results)

def test_rerank_with_top_k(reranker, sample_docs):
    query = "lazy dog"
    top_k = 2
    results = reranker.rerank(query, sample_docs, top_k=top_k)
    
    assert len(results) == top_k
    assert all('score' in doc for doc in results)
    # Check if scores are in descending order
    scores = [doc['score'] for doc in results]
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

def test_rerank_with_threshold(reranker, sample_docs):
    query = "quick fox"
    threshold = 0.5
    results = reranker.rerank(query, sample_docs, threshold=threshold)
    
    assert all(doc['score'] >= threshold for doc in results)

def test_rerank_with_top_k_and_threshold(reranker, sample_docs):
    query = "lazy dog"
    top_k = 2
    threshold = 0.5
    results = reranker.rerank(query, sample_docs, top_k=top_k, threshold=threshold)
    
    assert len(results) <= top_k
    assert all(doc['score'] >= threshold for doc in results)

def test_rerank_empty_docs(reranker):
    query = "test query"
    results = reranker.rerank(query, [])
    assert len(results) == 0

def test_rerank_preserves_metadata(reranker, sample_docs):
    query = "quick fox"
    results = reranker.rerank(query, sample_docs)
    
    # Check if all metadata is preserved
    original_metadata = {doc['metadata']['id'] for doc in sample_docs}
    result_metadata = {doc['metadata']['id'] for doc in results}
    assert result_metadata == original_metadata 