import json
from pathlib import Path
from typing import Any, Optional, Union, List, Dict
from pydantic import BaseModel
from litellm import completion, Message
from litellm.exceptions import (
    AuthenticationError as LiteLLMAuthenticationError,
    ContextWindowExceededError as LiteLLMContextWindowExceededError
)
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type
import os

from .base_llm import BaseLLM, ContextLengthExceededError, OutputLengthExceededError

class LiteLLM(BaseLLM):
    """A wrapper around the LiteLLM library for language model inference."""
    
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the LiteLLM wrapper.
        
        Args:
            model_name: Name of the model to use (e.g., 'claude-4-opus')
            temperature: Sampling temperature (0-2)
            api_base: Custom API base URL if needed
            **kwargs: Additional arguments to pass to the model
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        self.temperature = max(0, min(2, temperature))  # Clamp temperature
        self.api_base = api_base
        
        # Print debug info
        print(f"Initializing LiteLLM with model: {model_name}")
        print(f"Using API base: {api_base or 'default'}")
        if 'ANTHROPIC_API_KEY' not in os.environ:
            print("WARNING: ANTHROPIC_API_KEY environment variable not set")
        else:
            print("ANTHROPIC_API_KEY is set")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=15),
        retry=retry_if_not_exception_type((
            ContextLengthExceededError,
            OutputLengthExceededError,
            LiteLLMAuthenticationError
        )),
    )
    def call(
        self,
        prompt: str,
        message_history: List[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Call the language model with the given prompt and message history.
        
        Args:
            prompt: The prompt to send to the model
            message_history: List of previous messages in the conversation
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            The model's response as a string
            
        Raises:
            ContextLengthExceededError: If the context length is exceeded
            OutputLengthExceededError: If the output length is exceeded
            LiteLLMAuthenticationError: If there's an authentication error
            Exception: For other errors
        """
        try:
            # Prepare messages
            messages = []
            if message_history:
                messages.extend(message_history)
            messages.append({"role": "user", "content": prompt})
            
            print(f"Sending request to {self.model_name} with {len(messages)} messages")
            
            # Make the API call
            response = completion(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                api_base=self.api_base,
                **kwargs
            )
            
            # Extract and return the response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise Exception("Unexpected response format from model")
                
        except LiteLLMContextWindowExceededError:
            raise ContextLengthExceededError("Context length exceeded")
        except LiteLLMAuthenticationError as e:
            raise LiteLLMAuthenticationError(f"Authentication failed: {str(e)}")
        except Exception as e:
            print(f"Error in LiteLLM call: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                print(f"Status code: {e.status_code}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def count_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Count the number of tokens in the given messages."""
        try:
            from litellm import token_counter
            return token_counter(model=self.model_name, messages=messages)
        except ImportError:
            # Fallback estimation if token_counter is not available
            return sum(len(str(msg).split()) for msg in messages)