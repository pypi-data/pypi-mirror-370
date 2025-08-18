import unittest
from tangbao.azure import Azure
import os

class TestAzure(unittest.TestCase):
    def setUp(self):
        self.azure = Azure()

    def test_initialize_client(self):
        client = self.azure.client
        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'chat'))
        self.assertTrue(hasattr(client, 'embeddings'))

    def test_chat_completion(self):
        messages = [{"role": "user", "content": "Say 'test' and nothing else"}]
        response = self.azure.chat_completion(messages)
        self.assertIsNotNone(response)
        content = self.azure.get_content(response)
        self.assertIsInstance(content, str)
        self.assertTrue(len(content) > 0)

    def test_streaming_chat(self):
        messages = [{"role": "user", "content": "Say 'test' and nothing else"}]
        response = self.azure.chat_completion(messages, is_stream=True)
        self.assertIsNotNone(response)
        content = ""
        for chunk in self.azure.get_content(response):
            content += chunk
        self.assertTrue(len(content) > 0)

    def test_get_embeddings(self):
        # Skip if no embedding model is configured
        if not self.azure._embedding_model_deployment:
            self.skipTest("No embedding model configured")
        
        text = "This is a test"
        response = self.azure.get_embeddings(text)
        self.assertIsNotNone(response)
        self.assertTrue(hasattr(response, 'data'))
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(len(response.data[0].embedding) > 0)

    def test_not_implemented_methods(self):
        # Test that unimplemented methods raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            self.azure.get_monthly_costs()

        with self.assertRaises(NotImplementedError):
            self.azure.get_model_info()

        with self.assertRaises(NotImplementedError):
            self.azure.iam()

        with self.assertRaises(NotImplementedError):
            self.azure.index_multi_threaded([], [], [], "test_index")

        with self.assertRaises(NotImplementedError):
            self.azure.query_index("test query", 5, "test_index")

        with self.assertRaises(NotImplementedError):
            self.azure.resubmit_failed_chunks("test.log", [], [], [], "test_index", "test_model")

    def test_o1_models(self):
        """Test chat completion with o1 models that use max_completion_tokens"""
        messages = [{"role": "user", "content": "Say 'test' and nothing else"}]
        for model in ["o1", "o1-mini"]:
            response = self.azure.chat_completion(messages, model=model)
            self.assertIsNotNone(response)
            content = self.azure.get_content(response)
            self.assertIsInstance(content, str)
            self.assertTrue(len(content) > 0)

    def test_token_usage(self):
        messages = [{"role": "user", "content": "Say 'test' and nothing else"}]
        response = self.azure.chat_completion(messages)
        usage = self.azure.get_token_usage(response)
        self.assertIsInstance(usage, int)
        self.assertTrue(usage > 0)

if __name__ == '__main__':
    unittest.main() 