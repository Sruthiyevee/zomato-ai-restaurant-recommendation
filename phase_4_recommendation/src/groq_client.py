"""
Groq LLM Client Module for Phase 4
Handles integration with Groq API for LLM inference
"""

import logging
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GroqClient:
    """Client for interacting with Groq LLM API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model name (defaults to GROQ_MODEL env var or llama-3.1-70b-versatile)
            temperature: Temperature for responses (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = model or os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.temperature = float(os.getenv('GROQ_TEMPERATURE', temperature))
        self.max_tokens = int(os.getenv('GROQ_MAX_TOKENS', max_tokens))
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Groq client initialized with model: {self.model}")
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Generate completion using Groq API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            Dictionary with API response
            
        Raises:
            Exception: If API call fails
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens
            }
            
            logger.info(f"Sending request to Groq API (model: {self.model})")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("Groq API request successful")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Groq API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq API response: {str(e)}")
            raise Exception(f"Invalid response from Groq API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Groq API call: {str(e)}")
            raise
    
    def extract_content(self, response: Dict) -> str:
        """
        Extract content from Groq API response
        
        Args:
            response: API response dictionary
            
        Returns:
            Content string from response
        """
        try:
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                raise ValueError("No content in API response")
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from response: {str(e)}")
            raise ValueError(f"Invalid response structure: {str(e)}")
    
    def generate_recommendations(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate restaurant recommendations using Groq
        
        Args:
            prompt: User prompt with restaurant data
            system_prompt: Optional system prompt
            
        Returns:
            Generated recommendation text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.generate_completion(messages)
        content = self.extract_content(response)
        
        return content
    
    def test_connection(self) -> bool:
        """
        Test connection to Groq API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_messages = [{
                "role": "user",
                "content": "Say 'OK' if you can read this."
            }]
            
            response = self.generate_completion(test_messages, max_tokens=10)
            content = self.extract_content(response)
            
            logger.info("Groq API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Groq API connection test failed: {str(e)}")
            return False
