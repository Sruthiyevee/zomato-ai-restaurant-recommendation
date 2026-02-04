"""
Test cases for Groq Client Module
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from groq_client import GroqClient


class TestGroqClient(unittest.TestCase):
    """Test cases for GroqClient"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_api_key = "test_api_key_12345"
        self.test_model = "llama-3.1-70b-versatile"
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_env_key'})
    def test_initialization_from_env(self):
        """Test initialization from environment variable"""
        client = GroqClient()
        self.assertEqual(client.api_key, 'test_env_key')
    
    def test_initialization_with_parameters(self):
        """Test initialization with explicit parameters"""
        client = GroqClient(
            api_key=self.test_api_key,
            model=self.test_model,
            temperature=0.5,
            max_tokens=1000
        )
        
        self.assertEqual(client.api_key, self.test_api_key)
        self.assertEqual(client.model, self.test_model)
        self.assertEqual(client.temperature, 0.5)
        self.assertEqual(client.max_tokens, 1000)
    
    def test_initialization_no_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                GroqClient()
    
    @patch('groq_client.requests.post')
    def test_generate_completion_success(self, mock_post):
        """Test successful completion generation"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Test response'
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        client = GroqClient(api_key=self.test_api_key)
        messages = [{'role': 'user', 'content': 'Test prompt'}]
        
        result = client.generate_completion(messages)
        
        self.assertIn('choices', result)
        mock_post.assert_called_once()
    
    @patch('groq_client.requests.post')
    def test_extract_content(self, mock_post):
        """Test content extraction from response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Extracted content'
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        client = GroqClient(api_key=self.test_api_key)
        messages = [{'role': 'user', 'content': 'Test'}]
        
        response = client.generate_completion(messages)
        content = client.extract_content(response)
        
        self.assertEqual(content, 'Extracted content')
    
    @patch('groq_client.requests.post')
    def test_generate_recommendations(self, mock_post):
        """Test generating recommendations"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Recommendation response'
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        client = GroqClient(api_key=self.test_api_key)
        result = client.generate_recommendations("Test prompt", "System prompt")
        
        self.assertEqual(result, 'Recommendation response')
    
    @patch('groq_client.requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        client = GroqClient(api_key=self.test_api_key)
        messages = [{'role': 'user', 'content': 'Test'}]
        
        with self.assertRaises(Exception):
            client.generate_completion(messages)
    
    @patch('groq_client.requests.post')
    def test_test_connection_success(self, mock_post):
        """Test connection test success"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'OK'
                }
            }]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        client = GroqClient(api_key=self.test_api_key)
        result = client.test_connection()
        
        self.assertTrue(result)
    
    @patch('groq_client.requests.post')
    def test_test_connection_failure(self, mock_post):
        """Test connection test failure"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection failed")
        
        client = GroqClient(api_key=self.test_api_key)
        result = client.test_connection()
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
