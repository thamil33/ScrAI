"""
LLM Interface module for interacting with various LLM providers.
"""
import os
import json
import logging
from typing import Dict, Any, Tuple, Optional, Union
from dotenv import load_dotenv
import requests
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

class LLMInterface:
    """
    Interface for interacting with Language Model APIs.
    Supports both OpenRouter and locally hosted LM Studio models.
    """
    
    def __init__(self, provider: str = "auto", logger=None):
        """
        Initialize the LLM interface.
        
        Args:
            provider: Which provider to use ('openrouter', 'lmstudio', or 'auto')
            logger: Optional logger instance to use for logging
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Load API configurations from environment variables
        self.or_model = os.getenv("or_model", "meta-llama/llama-4-maverick:free")
        self.or_api_key = os.getenv("OPENROUTER_API_KEY")
        self.or_base_url = os.getenv("base_url", "https://openrouter.ai/api/v1")
        
        self.lm_model = os.getenv("lm_model")
        self.lm_api_key = os.getenv("LLMSTUDIO_API_KEY")
        self.lm_base_url = os.getenv("LMSTUDIO_API_BASE")
        
        # Set the provider
        if provider == "auto":
            # Prefer local LM Studio if available, otherwise use OpenRouter
            if self._check_lmstudio_availability():
                self.provider = "lmstudio"
            else:
                self.provider = "openrouter"
        else:
            self.provider = provider
            
        self.logger.info(f"LLM Interface initialized with provider: {self.provider}")

    def _check_lmstudio_availability(self) -> bool:
        """
        Check if LM Studio is available by sending a simple request.

        Returns:
            True if LM Studio is available, False otherwise
        """
        if not self.lm_base_url:
            return False

        try:
            response = requests.get(f"{self.lm_base_url}/models", 
                                   headers={"Authorization": f"Bearer {self.lm_api_key}"},
                                   timeout=2)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"LM Studio not available: {e}")
            return False


# Minimal concrete subclasses for compatibility with CLI and imports

class OpenRouterLLM(LLMInterface):
    def __init__(self, api_key=None, model=None, logger=None):
        super().__init__(provider="openrouter", logger=logger)
        if api_key:
            self.or_api_key = api_key
        if model:
            self.or_model = model
            
    def complete_json(self, prompt: str, json_schema: Optional[Dict[str, Any]] = None, 
                     temperature: float = 0.7, max_tokens: int = 500) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Get a JSON completion from OpenRouter.
        
        Args:
            prompt: The prompt to send to the LLM
            json_schema: Optional JSON schema for validation
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (parsed JSON response, metadata)
        """
        headers = {
            "Authorization": f"Bearer {self.or_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tyler/ScrAi",  # Site URL for OpenRouter analytics
            "X-Title": "ScrAi Agent Simulation"  # Site name for OpenRouter analytics
        }
        
        payload = {
            "model": self.or_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if json_schema:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            # Log the request payload for debugging (removing sensitive information)
            debug_payload = payload.copy()
            if len(prompt) > 100:
                debug_payload["messages"] = [{"role": "user", "content": prompt[:100] + "..."}]
            self.logger.debug(f"Sending request to OpenRouter API: {json.dumps(debug_payload)}")
            
            # Use the correct base URL and endpoint
            base_url = "https://openrouter.ai/api/v1"
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
              # Check for specific error cases
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                except Exception:
                    error_message = response.text or f"HTTP Error {response.status_code}"
                
                # Log detailed error information
                self.logger.error(f"OpenRouter API error: {error_message}")
                self.logger.error(f"Request URL: {base_url}/chat/completions")
                self.logger.error(f"Request headers: {headers}")
                self.logger.error(f"Response status: {response.status_code}")
                
                detailed_error = f"OpenRouter API returned error {response.status_code}.\nMessage: {error_message}"
                
                if response.status_code == 400:
                    if "invalid_api_key" in error_message.lower() or "authentication" in error_message.lower():
                        detailed_error += "\nPossible cause: Invalid API key or authentication issue"
                    elif "quota" in error_message.lower() or "exceed" in error_message.lower():
                        detailed_error += "\nPossible cause: API quota exceeded"
                    elif "model" in error_message.lower():
                        detailed_error += f"\nPossible cause: Invalid model name '{self.or_model}'"
                    else:
                        detailed_error += "\nPossible cause: Bad request format or invalid parameters"
                
                # Show a simplified version of the request payload for debug purposes
                debug_json = json.dumps({
                    "model": payload["model"],
                    "temperature": payload["temperature"],
                    "max_tokens": payload["max_tokens"],
                    "messages": [{"role": "user", "content": "[PROMPT TRUNCATED]"}]
                })
                self.logger.error(f"Request payload: {debug_json}")
                
                # Fall back to a deterministic response instead of failing completely
                response_json = {
                    "type": "wait",
                    "reason": f"API Error: {error_message[:100]}..."
                }
                return response_json, {"model": "api_error_fallback", "usage": {}}
            
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Try to parse the JSON response
            try:
                parsed_content = json.loads(content)
                return parsed_content, {"model": data.get("model", self.or_model), "usage": data.get("usage", {})}
            except json.JSONDecodeError:
                # Try to extract JSON from non-JSON response
                self.logger.warning("Response is not valid JSON, attempting to extract...")
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    try:
                        parsed_content = json.loads(json_str)
                        return parsed_content, {"model": data.get("model", self.or_model), "usage": data.get("usage", {})}
                    except json.JSONDecodeError:
                        raise ValueError(f"Failed to extract valid JSON from response: {content}")
                else:
                    raise ValueError(f"No JSON object found in response: {content}")
                    
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error with OpenRouter API: {str(e)}")
            raise ValueError(f"Network error when contacting OpenRouter API: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error with OpenRouter API: {str(e)}")
            raise


class LMStudioLLM(LLMInterface):
    def __init__(self, model=None, logger=None):
        super().__init__(provider="lmstudio", logger=logger)
        # Initialize model name from parameter or environment variable
        self.model_name = model or self.lm_model or "default_model"
        # Set up api_url for test compatibility
        self.host = self.lm_base_url or "http://localhost:11434"
        self.api_url = f"{self.host}/api/generate"
    
    def complete(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a text completion using lm_studio API.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the completion
            
        Returns:
            Tuple of (completion_text, metadata)
        """
        # Default parameters
        params = {
            "temperature": 0.7,
            "top_p": 1.0,
            "top_k": 40,
            "repeat_penalty": 1.1
        }
        
        # Override with any provided kwargs
        params.update(kwargs)
        
        # Prepare the request
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            **params
        }
        
        # Send the request
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to lm_studio API: {e}")
        
        # lm_studio streams responses, but we'll collect the full response
        completion_text = response.text.strip()
        
        # Extract metadata - limited for lm_studio
        metadata = {
            "model": self.model_name
        }
        
        return completion_text, metadata
    
    def complete_json(self, 
                     prompt: str, 
                     json_schema: Dict[str, Any],
                     **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate a JSON completion using lm_studio API.
        
        Args:
            prompt: The prompt to send to the LLM
            json_schema: JSON schema defining the expected output structure
            **kwargs: Additional parameters for the completion
            
        Returns:
            Tuple of (parsed_json_response, metadata)
        """
        # Enhance the prompt with instructions to return JSON
        json_prompt = f"{prompt}\n\nRespond with valid JSON that matches the following schema:\n{json.dumps(json_schema, indent=2)}"
        
        # Set a lower temperature for JSON generation
        if "temperature" not in kwargs:
            kwargs["temperature"] = 0.2
        
        # Get a completion
        completion_text, metadata = self.complete(json_prompt, **kwargs)
        
        # Extract JSON from the completion
        try:
            # Try to find JSON in the response
            json_start = completion_text.find("{")
            json_end = completion_text.rfind("}")
            
            if json_start >= 0 and json_end > json_start:
                json_text = completion_text[json_start:json_end + 1]
                parsed_json = json.loads(json_text)
            else:
                # If no JSON markers found, try parsing the entire response
                parsed_json = json.loads(completion_text)
                
        except json.JSONDecodeError:
            # If JSON parsing fails, return a formatted error
            parsed_json = {
                "error": "Failed to parse JSON from completion",
                "completion_text": completion_text
            }
        
        return parsed_json, metadata

