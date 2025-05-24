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

class LLmClientInterface:
# Would like to see advanced 'auto' implementation used in the future:
# Where logic would access available models from OpenRouter and LM Studio.
# I.E, All :Free models from OpenRouter, as well as just-in-time loading of LM Studio models.
# Also text embedding / reranking models to be used from LM Studio. 
    """
    Interface for interacting with Language Model APIs.
    Supports both OpenRouter and locally hosted LM Studio models.
    """
    
    def __init__(self, provider: str = "openrouter", logger=None):
        """
        Initialize the LLM interface.
        
        Args:
            provider: Which provider to use ('openrouter', 'lmstudio', or 'auto')
            logger: Optional logger instance to use for logging
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Load API configurations from environment variables
        self.OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick:free")
        self.or_api_key = os.getenv("OPENROUTER_API_KEY")
        self.or_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        self.LOCAL_MODEL = os.getenv("LOCAL_MODEL")
        self.lm_api_key = os.getenv("LOCAL_API_KEY")
        self.lm_base_url = os.getenv("LOCAL_BASE_URL")
        
        # # # Set the provider
        # if provider == "auto":
        #     # Prefer local LM Studio if available, otherwise use OpenRouter
        #     if self._check_lmstudio_availability():
        #         self.provider = "lmstudio"
        #     else:
        #         self.provider = "openrouter"
        # else:
        
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
            # Use the correct OpenAI-compatible endpoint for LM Studio
            models_url = f"{self.lm_base_url}/v1/models"
            headers = {"Content-Type": "application/json"}
            
            # Add authorization if API key is available
            if self.lm_api_key:
                headers["Authorization"] = f"Bearer {self.lm_api_key}"
                
            response = requests.get(models_url, headers=headers, timeout=2)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"LM Studio not available: {e}")
            return False

    def complete_json(self, prompt: str, json_schema: Optional[Dict[str, Any]] = None, 
                     temperature: float = 0.7, max_tokens: int = 500) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Get a JSON completion from the configured provider.
        This method delegates to the appropriate provider implementation.
        
        Args:
            prompt: The prompt to send to the LLM
            json_schema: Optional JSON schema for validation
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Tuple of (parsed JSON response, metadata)
        """
        if self.provider == "openrouter":
            # Create an OpenRouterLLM instance and delegate to it
            openrouter_llm = OpenRouterLLM(logger=self.logger)
            return openrouter_llm.complete_json(prompt, json_schema, temperature, max_tokens)
        elif self.provider == "lmstudio":
            # Create an LocalLMStudio instance and delegate to it
            lmstudio_llm = LocalLMStudio(logger=self.logger)
            return lmstudio_llm.complete_json(prompt, json_schema, temperature=temperature, max_tokens=max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")


# Minimal concrete subclasses for compatibility with CLI and imports

class OpenRouterLLM(LLmClientInterface):
    def __init__(self, api_key=None, model=None, logger=None):
        super().__init__(provider="openrouter", logger=logger)
        if api_key:
            self.or_api_key = api_key
        if model:
            self.OPENROUTER_MODEL = model
            
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
            "model": self.OPENROUTER_MODEL,
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
            OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
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
                self.logger.error(f"Request URL: {OPENROUTER_BASE_URL}/chat/completions")
                self.logger.error(f"Request headers: {headers}")
                self.logger.error(f"Response status: {response.status_code}")
                
                detailed_error = f"OpenRouter API returned error {response.status_code}.\nMessage: {error_message}"
                
                if response.status_code == 400:
                    if "invalid_api_key" in error_message.lower() or "authentication" in error_message.lower():
                        detailed_error += "\nPossible cause: Invalid API key or authentication issue"
                    elif "quota" in error_message.lower() or "exceed" in error_message.lower():
                        detailed_error += "\nPossible cause: API quota exceeded"
                    elif "model" in error_message.lower():
                        detailed_error += f"\nPossible cause: Invalid model name '{self.OPENROUTER_MODEL}'"
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
                return parsed_content, {"model": data.get("model", self.OPENROUTER_MODEL), "usage": data.get("usage", {})}
            except json.JSONDecodeError:
                # Try to extract JSON from non-JSON response
                self.logger.warning("Response is not valid JSON, attempting to extract...")
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    try:
                        parsed_content = json.loads(json_str)
                        return parsed_content, {"model": data.get("model", self.OPENROUTER_MODEL), "usage": data.get("usage", {})}
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


class LocalLMStudio(LLmClientInterface):
    def __init__(self, model=None, logger=None):
        super().__init__(provider="lmstudio", logger=logger)
        # Initialize model name from parameter or environment variable
        self.model_name = model or self.LOCAL_MODEL or "default_model"
        # Set up api_url for LM Studio's OpenAI-compatible endpoint
        self.host = self.lm_base_url or "http://localhost:1234"  # LM Studio default port
        self.api_url = f"{self.host}/v1/chat/completions"
    
    def complete(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a text completion using LM Studio's OpenAI-compatible API.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters for the completion
            
        Returns:
            Tuple of (completion_text, metadata)
        """
        # Default parameters
        params = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 500),
        }
        
        # Prepare the OpenAI-compatible request
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            **params
        }
        
        # Set up headers for LM Studio
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization if API key is available
        if self.lm_api_key:
            headers["Authorization"] = f"Bearer {self.lm_api_key}"
        
        # Send the request
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            completion_text = data["choices"][0]["message"]["content"]
            
            # Extract metadata
            metadata = {
                "model": data.get("model", self.model_name),
                "usage": data.get("usage", {})
            }
            
            return completion_text, metadata
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to LM Studio API: {e}")
            raise ConnectionError(f"Failed to connect to LM Studio API: {e}")
        except (KeyError, IndexError) as e:
            self.logger.error(f"Unexpected response format from LM Studio: {e}")
            raise ValueError(f"Unexpected response format from LM Studio: {e}")
    
    def complete_json(self, 
                     prompt: str, 
                     json_schema: Dict[str, Any],
                     **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate a JSON completion using LM Studio's OpenAI-compatible API.
        
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
        
        # Use the OpenAI-compatible chat completions endpoint
        params = {
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 500),
        }
        
        # Prepare the OpenAI-compatible request
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": json_prompt}],
            **params
        }
        
        # Set up headers for LM Studio
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authorization if API key is available
        if self.lm_api_key:
            headers["Authorization"] = f"Bearer {self.lm_api_key}"
        
        # Send the request
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            completion_text = data["choices"][0]["message"]["content"]
            
            # Extract metadata
            metadata = {
                "model": data.get("model", self.model_name),
                "usage": data.get("usage", {})
            }
            
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
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to LM Studio API: {e}")
            raise ConnectionError(f"Failed to connect to LM Studio API: {e}")
        except (KeyError, IndexError) as e:
            self.logger.error(f"Unexpected response format from LM Studio: {e}")
            raise ValueError(f"Unexpected response format from LM Studio: {e}")

