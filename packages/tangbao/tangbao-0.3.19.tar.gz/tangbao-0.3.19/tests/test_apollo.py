import unittest
from tangbao.apollo import Apollo

class TestApollo(unittest.TestCase):
    def setUp(self):
        self.apollo = Apollo()

    def test_initialize_client(self):
        client = self.apollo._initialize_client()
        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'chat'))
        self.assertTrue(hasattr(client, 'embeddings'))

    def test_get_monthly_costs(self):
        response = self.apollo.get_monthly_costs()
        self.assertIsInstance(response, dict)
        # Add specific key checks based on the actual response structure
        self.assertIn('spend', response)

    def test_get_model_info(self):
        response = self.apollo.get_model_info()
        self.assertIsInstance(response, list)
        self.assertTrue(len(response) > 0)
        # Check for expected keys in model info
        self.assertIn('model_name', response[0])
        self.assertIn('model_info', response[0])

    def test_iam(self):
        response = self.apollo.iam()
        self.assertIsInstance(response, dict)
        self.assertIn('id', response)

    def test_chat_completion(self):
        messages = [{"role": "user", "content": "Say 'test' and nothing else"}]
        response = self.apollo.chat_completion(messages)
        self.assertIsNotNone(response)
        content = self.apollo.get_content(response)
        self.assertIsInstance(content, str)
        self.assertTrue(len(content) > 0)

    def test_get_embeddings(self):
        text = "This is a test"
        response = self.apollo.get_embeddings(text)
        self.assertIsNotNone(response)
        # Check if we got embeddings back
        self.assertTrue(hasattr(response, 'data'))
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(len(response.data[0].embedding) > 0)

    def test_streaming_chat(self):
        messages = [{"role": "user", "content": "Say 'test' and nothing else"}]
        response = self.apollo.chat_completion(messages, is_stream=True)
        self.assertIsNotNone(response)
        content = ""
        for chunk in self.apollo.get_content(response):
            content += chunk
        self.assertTrue(len(content) > 0)

    def test_token_refresh(self):
        # Test token refresh mechanism
        initial_token = self.apollo.token
        self.assertIsNotNone(initial_token)
        # Force token refresh
        self.apollo._token_data['expiry_time'] = 0
        new_token = self.apollo.token
        self.assertIsNotNone(new_token)
        self.assertNotEqual(initial_token, new_token)

if __name__ == '__main__':
    unittest.main()